from __future__ import annotations

import itertools
import json
from collections import deque
from typing import Any

import numpy as np

try:
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


THEOREM_ID = "c985_d20_preserved_core_subcomplex"
STATUS = "C985_D20_PRESERVED_CORE_SUBCOMPLEX_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REWRITE_COMPLEX_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_rewrite_complex_hyperbolicity"
INTERVAL_SHEAF_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_geodesic_interval_sheaf"

REWRITE_COMPLEX_REPORT = REWRITE_COMPLEX_DIR / "report.json"
REWRITE_COMPLEX_JSON = REWRITE_COMPLEX_DIR / "rewrite_complex.json"
REWRITE_COMPLEX_TABLES = REWRITE_COMPLEX_DIR / "rewrite_complex_tables.npz"
REWRITE_COMPLEX_CERTIFICATE = REWRITE_COMPLEX_DIR / "rewrite_complex_certificate.json"
INTERVAL_SHEAF_REPORT = INTERVAL_SHEAF_DIR / "report.json"
INTERVAL_SHEAF_JSON = INTERVAL_SHEAF_DIR / "geodesic_interval_sheaf.json"
INTERVAL_SHEAF_TABLES = INTERVAL_SHEAF_DIR / "geodesic_interval_tables.npz"
INTERVAL_SHEAF_CERTIFICATE = INTERVAL_SHEAF_DIR / "geodesic_interval_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_preserved_core_subcomplex.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_preserved_core_subcomplex.py"

HIGH_SIGNATURE_THRESHOLD = 155
DISTANCE_SCALE = 10_000_000_000

CORE_NODE_COLUMNS = [
    "core_node_id",
    "node_id",
    "symbol_0_count",
    "symbol_1_count",
    "symbol_2_count",
    "symbol_3_count",
    "symbol_4_count",
    "symbol_5_count",
    "sector_union_mask",
    "sector_coverage_count",
    "signature_union_count",
    "tensor_path_support_sum",
    "tensor_path_coefficient_mass_sum",
    "core_internal_degree",
    "boundary_degree",
    "full_high_interval_cover_count",
    "is_boundary_node",
]

CORE_EDGE_COLUMNS = [
    "core_edge_id",
    "source_node_id",
    "target_node_id",
    "source_core_node_id",
    "target_core_node_id",
    "edge_sector_union_count",
    "source_signature_union_count",
    "target_signature_union_count",
    "signature_union_delta_abs",
    "poincare_barycenter_distance_x1e10",
]

BOUNDARY_EDGE_COLUMNS = [
    "boundary_edge_id",
    "core_node_id",
    "frontier_node_id",
    "core_local_node_id",
    "frontier_local_node_id",
    "core_signature_union_count",
    "frontier_signature_union_count",
    "frontier_sector_coverage_count",
    "poincare_barycenter_distance_x1e10",
]

PRESERVED_INTERVAL_COLUMNS = [
    "core_interval_id",
    "source_node_id",
    "target_node_id",
    "graph_distance",
    "interval_node_count",
    "shortest_path_count",
    "min_signature_union_count",
    "endpoint_poincare_distance_x1e10",
]


def round10(value: float) -> float:
    return float(round(float(value), 10))


def scaled_distance(value: float) -> int:
    return int(round(float(value) * DISTANCE_SCALE))


def distance_matrix(adjacency: np.ndarray) -> np.ndarray:
    node_count = int(adjacency.shape[0])
    distances = np.full((node_count, node_count), node_count + 1, dtype=np.int64)
    for source in range(node_count):
        distances[source, source] = 0
        queue: deque[int] = deque([source])
        while queue:
            node = queue.popleft()
            for neighbor in np.flatnonzero(adjacency[node]):
                neighbor = int(neighbor)
                if int(distances[source, neighbor]) <= int(distances[source, node]) + 1:
                    continue
                distances[source, neighbor] = int(distances[source, node]) + 1
                queue.append(neighbor)
    return distances


def connected_components(adjacency: np.ndarray, labels: list[int]) -> list[list[int]]:
    seen: set[int] = set()
    components: list[list[int]] = []
    for start in range(len(labels)):
        if start in seen:
            continue
        seen.add(start)
        queue: deque[int] = deque([start])
        component: list[int] = []
        while queue:
            node = queue.popleft()
            component.append(labels[node])
            for neighbor in np.flatnonzero(adjacency[node]):
                neighbor = int(neighbor)
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                queue.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda row: (len(row), row), reverse=True)


def gromov_delta_witness(distances: np.ndarray, labels: list[int]) -> dict[str, Any]:
    best_delta_twice = -1
    best_nodes: list[int] = []
    best_sums: list[int] = []
    for a, b, c, d in itertools.combinations(range(len(labels)), 4):
        local = distances[np.ix_([a, b, c, d], [a, b, c, d])]
        if int(np.max(local)) > len(labels):
            continue
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
            best_nodes = [labels[a], labels[b], labels[c], labels[d]]
            best_sums = sums
    return {
        "delta": round10(best_delta_twice / 2.0),
        "delta_twice": int(best_delta_twice),
        "witness_nodes": best_nodes,
        "witness_sums": best_sums,
    }


def graph_summary(adjacency: np.ndarray, labels: list[int]) -> dict[str, Any]:
    distances = distance_matrix(adjacency)
    finite = distances <= len(labels)
    components = connected_components(adjacency, labels)
    eccentricities = np.max(distances, axis=1)
    diameter = int(np.max(distances[finite]))
    radius = int(np.min(eccentricities))
    centers = [labels[index] for index, value in enumerate(eccentricities) if int(value) == radius]
    diameter_pairs = [
        [labels[left], labels[right]]
        for left in range(len(labels))
        for right in range(left + 1, len(labels))
        if int(distances[left, right]) == diameter
    ]
    unordered_distances = [
        int(distances[left, right])
        for left in range(len(labels))
        for right in range(left, len(labels))
        if int(distances[left, right]) <= len(labels)
    ]
    return {
        "node_count": len(labels),
        "edge_count": int(np.sum(adjacency) // 2),
        "component_count": len(components),
        "component_node_ids": components,
        "component_size_histogram": histogram([len(component) for component in components]),
        "diameter": diameter,
        "radius": radius,
        "center_node_ids": centers,
        "diameter_pair_count": len(diameter_pairs),
        "diameter_pairs": diameter_pairs,
        "distance_histogram": histogram(unordered_distances),
        "gromov_delta": gromov_delta_witness(distances, labels),
    }


def build_payloads() -> dict[str, Any]:
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_complex = load_json(REWRITE_COMPLEX_JSON)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    interval_report = load_json(INTERVAL_SHEAF_REPORT)
    interval_sheaf = load_json(INTERVAL_SHEAF_JSON)
    interval_certificate = load_json(INTERVAL_SHEAF_CERTIFICATE)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    interval_tables = np.load(INTERVAL_SHEAF_TABLES, allow_pickle=False)

    original_adjacency = np.asarray(rewrite_tables["adjacency"], dtype=np.int8)
    original_distances = np.asarray(rewrite_tables["graph_distances"], dtype=np.int64)
    node_poincare_distances = np.asarray(
        rewrite_tables["node_poincare_distances"], dtype=np.float64
    )
    interval_table = np.asarray(interval_tables["interval_table"], dtype=np.int64)
    interval_membership = np.asarray(interval_tables["interval_membership"], dtype=np.int8)
    nodes = rewrite_complex["nodes"]
    edges = rewrite_complex["edges"]

    full_high_intervals = [
        row for row in interval_sheaf["intervals"] if int(row["full_high_preserved"]) == 1
    ]
    full_high_node_ids = sorted(
        node["node_id"]
        for node in nodes
        if int(node["sector_coverage_count"]) == 6
        and int(node["signature_union_count"]) >= HIGH_SIGNATURE_THRESHOLD
    )
    interval_core_node_ids = sorted(
        {
            int(node_id)
            for row in full_high_intervals
            for node_id in row["interval_node_ids"]
        }
    )
    endpoint_node_ids = sorted(
        {
            int(row["source_node_id"])
            for row in full_high_intervals
        }
        | {
            int(row["target_node_id"])
            for row in full_high_intervals
        }
    )
    core_node_ids = full_high_node_ids
    core_node_set = set(core_node_ids)
    core_index = {node_id: index for index, node_id in enumerate(core_node_ids)}

    core_adjacency = np.zeros((len(core_node_ids), len(core_node_ids)), dtype=np.int8)
    core_edge_rows: list[dict[str, Any]] = []
    core_edge_table_rows: list[list[int]] = []
    boundary_edge_rows: list[dict[str, Any]] = []
    boundary_edge_table_rows: list[list[int]] = []
    frontier_node_set: set[int] = set()

    for edge in edges:
        source = int(edge["source_node_id"])
        target = int(edge["target_node_id"])
        source_in_core = source in core_node_set
        target_in_core = target in core_node_set
        if source_in_core and target_in_core:
            local_source = core_index[source]
            local_target = core_index[target]
            core_adjacency[local_source, local_target] = 1
            core_adjacency[local_target, local_source] = 1
            row = {
                "core_edge_id": len(core_edge_rows),
                "source_node_id": source,
                "target_node_id": target,
                "source_core_node_id": local_source,
                "target_core_node_id": local_target,
                "source_word": edge["source_word"],
                "target_word": edge["target_word"],
                "edge_sector_union_count": int(edge["edge_sector_union_count"]),
                "source_signature_union_count": int(edge["source_signature_union_count"]),
                "target_signature_union_count": int(edge["target_signature_union_count"]),
                "signature_union_delta_abs": int(edge["signature_union_delta_abs"]),
                "poincare_barycenter_distance": edge["poincare_barycenter_distance"],
                "poincare_barycenter_distance_x1e10": scaled_distance(
                    edge["poincare_barycenter_distance"]
                ),
            }
            core_edge_rows.append(row)
            core_edge_table_rows.append([int(row[column]) for column in CORE_EDGE_COLUMNS])
        elif source_in_core or target_in_core:
            core_node = source if source_in_core else target
            frontier_node = target if source_in_core else source
            frontier_node_set.add(frontier_node)

    frontier_node_ids = sorted(frontier_node_set)
    frontier_index = {node_id: index for index, node_id in enumerate(frontier_node_ids)}
    boundary_band_node_ids = core_node_ids + frontier_node_ids
    boundary_band_index = {node_id: index for index, node_id in enumerate(boundary_band_node_ids)}
    cut_graph_adjacency = np.zeros(
        (len(boundary_band_node_ids), len(boundary_band_node_ids)),
        dtype=np.int8,
    )
    boundary_band_adjacency = np.zeros_like(cut_graph_adjacency)

    for edge in edges:
        source = int(edge["source_node_id"])
        target = int(edge["target_node_id"])
        source_in_core = source in core_node_set
        target_in_core = target in core_node_set
        if source in boundary_band_index and target in boundary_band_index:
            left = boundary_band_index[source]
            right = boundary_band_index[target]
            boundary_band_adjacency[left, right] = 1
            boundary_band_adjacency[right, left] = 1
        if not (source_in_core ^ target_in_core):
            continue
        core_node = source if source_in_core else target
        frontier_node = target if source_in_core else source
        cut_left = boundary_band_index[core_node]
        cut_right = boundary_band_index[frontier_node]
        cut_graph_adjacency[cut_left, cut_right] = 1
        cut_graph_adjacency[cut_right, cut_left] = 1
        row = {
            "boundary_edge_id": len(boundary_edge_rows),
            "core_node_id": core_node,
            "frontier_node_id": frontier_node,
            "core_local_node_id": core_index[core_node],
            "frontier_local_node_id": frontier_index[frontier_node],
            "core_word": nodes[core_node]["canonical_word"],
            "frontier_word": nodes[frontier_node]["canonical_word"],
            "core_signature_union_count": int(nodes[core_node]["signature_union_count"]),
            "frontier_signature_union_count": int(nodes[frontier_node]["signature_union_count"]),
            "frontier_sector_coverage_count": int(nodes[frontier_node]["sector_coverage_count"]),
            "poincare_barycenter_distance": round10(node_poincare_distances[core_node, frontier_node]),
            "poincare_barycenter_distance_x1e10": scaled_distance(
                node_poincare_distances[core_node, frontier_node]
            ),
        }
        boundary_edge_rows.append(row)
        boundary_edge_table_rows.append([int(row[column]) for column in BOUNDARY_EDGE_COLUMNS])

    core_distances = distance_matrix(core_adjacency)
    cut_graph_distances = distance_matrix(cut_graph_adjacency)
    boundary_band_distances = distance_matrix(boundary_band_adjacency)

    interval_cover_counts = {node_id: 0 for node_id in core_node_ids}
    core_interval_rows: list[dict[str, Any]] = []
    core_interval_table_rows: list[list[int]] = []
    core_interval_incidence = np.zeros((len(full_high_intervals), len(core_node_ids)), dtype=np.int8)
    for local_id, row in enumerate(full_high_intervals):
        interval_nodes = [int(node_id) for node_id in row["interval_node_ids"]]
        for node_id in interval_nodes:
            interval_cover_counts[node_id] += 1
            core_interval_incidence[local_id, core_index[node_id]] = 1
        interval_row = {
            "core_interval_id": local_id,
            "source_node_id": int(row["source_node_id"]),
            "target_node_id": int(row["target_node_id"]),
            "source_word": row["source_word"],
            "target_word": row["target_word"],
            "graph_distance": int(row["graph_distance"]),
            "interval_node_count": int(row["interval_node_count"]),
            "interval_node_ids": interval_nodes,
            "shortest_path_count": int(row["shortest_path_count"]),
            "min_signature_union_count": int(row["min_signature_union_count"]),
            "endpoint_poincare_distance": row["endpoint_poincare_distance"],
            "endpoint_poincare_distance_x1e10": int(row["endpoint_poincare_distance_x1e10"]),
        }
        core_interval_rows.append(interval_row)
        core_interval_table_rows.append(
            [int(interval_row[column]) for column in PRESERVED_INTERVAL_COLUMNS]
        )

    core_node_rows: list[dict[str, Any]] = []
    core_node_table_rows: list[list[int]] = []
    boundary_degree_by_core = {
        node_id: int(
            np.sum(
                [
                    1
                    for neighbor in np.flatnonzero(original_adjacency[node_id])
                    if int(neighbor) not in core_node_set
                ]
            )
        )
        for node_id in core_node_ids
    }
    for local_id, node_id in enumerate(core_node_ids):
        source = nodes[node_id]
        row = {
            "core_node_id": local_id,
            "node_id": node_id,
            "canonical_word": source["canonical_word"],
            "symbol_counts": source["symbol_counts"],
            "symbol_0_count": int(source["symbol_0_count"]),
            "symbol_1_count": int(source["symbol_1_count"]),
            "symbol_2_count": int(source["symbol_2_count"]),
            "symbol_3_count": int(source["symbol_3_count"]),
            "symbol_4_count": int(source["symbol_4_count"]),
            "symbol_5_count": int(source["symbol_5_count"]),
            "sector_union_mask": int(source["sector_union_mask"]),
            "sector_coverage_count": int(source["sector_coverage_count"]),
            "signature_union_count": int(source["signature_union_count"]),
            "tensor_path_support_sum": int(source["tensor_path_support_sum"]),
            "tensor_path_coefficient_mass_sum": int(source["tensor_path_coefficient_mass_sum"]),
            "core_internal_degree": int(np.sum(core_adjacency[local_id])),
            "boundary_degree": boundary_degree_by_core[node_id],
            "full_high_interval_cover_count": interval_cover_counts[node_id],
            "is_boundary_node": int(boundary_degree_by_core[node_id] > 0),
        }
        core_node_rows.append(row)
        core_node_table_rows.append([int(row[column]) for column in CORE_NODE_COLUMNS])

    complement_node_ids = [node_id for node_id in range(len(nodes)) if node_id not in core_node_set]
    complement_index = {node_id: index for index, node_id in enumerate(complement_node_ids)}
    complement_adjacency = np.zeros((len(complement_node_ids), len(complement_node_ids)), dtype=np.int8)
    for source in complement_node_ids:
        for target in np.flatnonzero(original_adjacency[source]):
            target = int(target)
            if target not in complement_index:
                continue
            complement_adjacency[complement_index[source], complement_index[target]] = 1
    complement_components = connected_components(complement_adjacency, complement_node_ids)
    exterior_distance_records = []
    for node_id in complement_node_ids:
        min_distance = min(int(original_distances[node_id, core_node]) for core_node in core_node_ids)
        exterior_distance_records.append(
            {
                "node_id": node_id,
                "canonical_word": nodes[node_id]["canonical_word"],
                "distance_to_core": min_distance,
                "sector_coverage_count": int(nodes[node_id]["sector_coverage_count"]),
                "signature_union_count": int(nodes[node_id]["signature_union_count"]),
            }
        )
    exterior_distance_two_nodes = [
        row["node_id"] for row in exterior_distance_records if row["distance_to_core"] == 2
    ]

    core_pair_count = len(core_node_ids) * (len(core_node_ids) + 1) // 2
    core_endpoint_interval_rows = [
        row
        for row in interval_sheaf["intervals"]
        if int(row["source_node_id"]) in core_node_set and int(row["target_node_id"]) in core_node_set
    ]
    geodesically_preserved_core_pairs = [
        row for row in core_endpoint_interval_rows if set(row["interval_node_ids"]).issubset(core_node_set)
    ]
    escaping_core_pairs = [
        {
            "source_node_id": int(row["source_node_id"]),
            "target_node_id": int(row["target_node_id"]),
            "graph_distance": int(row["graph_distance"]),
            "escaping_node_ids": [
                int(node_id) for node_id in row["interval_node_ids"] if int(node_id) not in core_node_set
            ],
        }
        for row in core_endpoint_interval_rows
        if not set(row["interval_node_ids"]).issubset(core_node_set)
    ]

    isometric_pair_count = 0
    max_core_metric_distortion = 0
    for left, source in enumerate(core_node_ids):
        for right, target in enumerate(core_node_ids[left:], start=left):
            distortion = int(core_distances[left, right] - original_distances[source, target])
            max_core_metric_distortion = max(max_core_metric_distortion, distortion)
            if distortion == 0:
                isometric_pair_count += 1

    core_summary = graph_summary(core_adjacency, core_node_ids)
    cut_graph_summary = graph_summary(cut_graph_adjacency, boundary_band_node_ids)
    boundary_band_summary = graph_summary(boundary_band_adjacency, boundary_band_node_ids)
    core_poincare_diameter = max(
        (
            (
                round10(node_poincare_distances[source, target]),
                source,
                target,
                int(original_distances[source, target]),
            )
            for source, target in itertools.combinations(core_node_ids, 2)
        ),
        key=lambda row: (row[0], row[3], row[1], row[2]),
    )

    preserved_core = {
        "schema": "c985.d20_preserved_core_subcomplex@1",
        "object": "d20",
        "source_rewrite_complex_certificate": rewrite_report.get("certificate_sha256"),
        "source_interval_sheaf_certificate": interval_report.get("certificate_sha256"),
        "construction_rule": {
            "core_selector": (
                "nodes with full six-sector coverage and signature-union count at least "
                f"{HIGH_SIGNATURE_THRESHOLD}"
            ),
            "interval_collapse": "union of the 46 full-sector plus high-signature geodesic intervals",
            "core_subcomplex": "rewrite-complex subgraph induced by the selected core nodes",
            "finite_boundary": "core nodes and exterior frontier nodes incident to a core-complement edge",
            "boundary_band": "original rewrite-complex subgraph induced by core nodes plus the exterior frontier",
        },
        "core_nodes": core_node_rows,
        "core_edges": core_edge_rows,
        "full_high_interval_cover": core_interval_rows,
        "boundary_edges": boundary_edge_rows,
        "boundary": {
            "core_boundary_node_ids": [
                row["node_id"] for row in core_node_rows if row["is_boundary_node"] == 1
            ],
            "frontier_node_ids": frontier_node_ids,
            "boundary_band_node_ids": boundary_band_node_ids,
            "exterior_distance_two_node_ids": exterior_distance_two_nodes,
            "cut_graph_summary": cut_graph_summary,
            "boundary_band_summary": boundary_band_summary,
            "complement_component_count": len(complement_components),
            "complement_component_node_ids": complement_components,
            "exterior_distance_to_core_histogram": histogram(
                [row["distance_to_core"] for row in exterior_distance_records]
            ),
            "exterior_distance_records": exterior_distance_records,
        },
        "summary": {
            "high_signature_threshold": HIGH_SIGNATURE_THRESHOLD,
            "core_node_count": len(core_node_ids),
            "core_node_ids": core_node_ids,
            "full_high_interval_count": len(full_high_intervals),
            "core_edge_count": len(core_edge_rows),
            "core_component_count": core_summary["component_count"],
            "core_graph_diameter": core_summary["diameter"],
            "core_graph_radius": core_summary["radius"],
            "core_center_node_ids": core_summary["center_node_ids"],
            "core_gromov_delta": core_summary["gromov_delta"]["delta"],
            "core_gromov_delta_twice": core_summary["gromov_delta"]["delta_twice"],
            "core_gromov_delta_witness_nodes": core_summary["gromov_delta"]["witness_nodes"],
            "core_distance_histogram": core_summary["distance_histogram"],
            "core_internal_degree_histogram": histogram(
                [row["core_internal_degree"] for row in core_node_rows]
            ),
            "core_boundary_degree_histogram": histogram(
                [row["boundary_degree"] for row in core_node_rows]
            ),
            "core_interval_cover_count_histogram": histogram(
                [row["full_high_interval_cover_count"] for row in core_node_rows]
            ),
            "core_pair_count": core_pair_count,
            "core_pair_isometric_count": isometric_pair_count,
            "max_core_metric_distortion": max_core_metric_distortion,
            "geodesically_preserved_core_pair_count": len(geodesically_preserved_core_pairs),
            "escaping_core_pair_count": len(escaping_core_pairs),
            "escaping_core_pairs": escaping_core_pairs,
            "core_poincare_diameter_pair": {
                "source_node_id": int(core_poincare_diameter[1]),
                "target_node_id": int(core_poincare_diameter[2]),
                "graph_distance": int(core_poincare_diameter[3]),
                "endpoint_poincare_distance": core_poincare_diameter[0],
            },
            "boundary_core_node_count": int(
                sum(row["is_boundary_node"] for row in core_node_rows)
            ),
            "frontier_node_count": len(frontier_node_ids),
            "boundary_edge_count": len(boundary_edge_rows),
            "boundary_band_node_count": len(boundary_band_node_ids),
            "cut_graph_diameter": cut_graph_summary["diameter"],
            "cut_graph_gromov_delta": cut_graph_summary["gromov_delta"]["delta"],
            "cut_graph_gromov_delta_twice": cut_graph_summary["gromov_delta"]["delta_twice"],
            "boundary_band_edge_count": boundary_band_summary["edge_count"],
            "boundary_band_diameter": boundary_band_summary["diameter"],
            "boundary_band_gromov_delta": boundary_band_summary["gromov_delta"]["delta"],
            "boundary_band_gromov_delta_twice": boundary_band_summary["gromov_delta"]["delta_twice"],
            "complement_node_count": len(complement_node_ids),
            "complement_component_count": len(complement_components),
            "exterior_distance_two_node_ids": exterior_distance_two_nodes,
        },
    }

    core_node_table = np.asarray(core_node_table_rows, dtype=np.int64)
    core_edge_table = np.asarray(core_edge_table_rows, dtype=np.int64)
    boundary_edge_table = np.asarray(boundary_edge_table_rows, dtype=np.int64)
    core_interval_table = np.asarray(core_interval_table_rows, dtype=np.int64)
    core_nodes_array = np.asarray(core_node_ids, dtype=np.int64)
    frontier_nodes_array = np.asarray(frontier_node_ids, dtype=np.int64)
    boundary_band_nodes_array = np.asarray(boundary_band_node_ids, dtype=np.int64)

    checks = {
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "interval_sheaf_report_certified": interval_report.get("status")
        == "C985_D20_GEODESIC_INTERVAL_SHEAF_CERTIFIED",
        "interval_sheaf_certificate_certified": interval_certificate.get("status")
        == "C985_D20_GEODESIC_INTERVAL_SHEAF_CERTIFIED",
        "high_signature_threshold_matches_interval_sheaf": interval_report.get("witness", {}).get(
            "high_signature_threshold"
        )
        == HIGH_SIGNATURE_THRESHOLD,
        "full_high_interval_count_is_46": len(full_high_intervals) == 46,
        "core_node_count_is_12": len(core_node_ids) == 12,
        "full_high_nodes_equal_interval_union": full_high_node_ids == interval_core_node_ids,
        "full_high_endpoints_equal_core_nodes": endpoint_node_ids == core_node_ids,
        "core_node_table_shape_is_12_by_17": tuple(core_node_table.shape)
        == (12, len(CORE_NODE_COLUMNS)),
        "core_edge_count_is_31": len(core_edge_rows) == 31,
        "core_edge_table_shape_is_31_by_10": tuple(core_edge_table.shape)
        == (31, len(CORE_EDGE_COLUMNS)),
        "core_adjacency_shape_is_12_by_12": tuple(core_adjacency.shape) == (12, 12),
        "core_graph_connected": core_summary["component_count"] == 1,
        "core_graph_diameter_is_3": core_summary["diameter"] == 3,
        "core_graph_radius_is_2": core_summary["radius"] == 2,
        "core_centers_are_19_34_42_44": core_summary["center_node_ids"]
        == [19, 34, 42, 44],
        "core_gromov_delta_is_1": core_summary["gromov_delta"]["delta_twice"] == 2,
        "core_delta_witness_is_10_13_32_41": core_summary["gromov_delta"]["witness_nodes"]
        == [10, 13, 32, 41],
        "core_distance_histogram_matches": core_summary["distance_histogram"]
        == [
            {"value": 0, "count": 12},
            {"value": 1, "count": 31},
            {"value": 2, "count": 26},
            {"value": 3, "count": 9},
        ],
        "core_induced_metric_is_isometric_for_all_78_core_pairs": isometric_pair_count == 78
        and max_core_metric_distortion == 0,
        "geodesically_preserved_core_pair_count_is_46": len(geodesically_preserved_core_pairs)
        == 46,
        "escaping_core_pair_count_is_32": len(escaping_core_pairs) == 32,
        "core_boundary_node_count_is_12": preserved_core["summary"]["boundary_core_node_count"]
        == 12,
        "core_has_no_interior_nodes": all(row["is_boundary_node"] == 1 for row in core_node_rows),
        "frontier_node_count_is_40": len(frontier_node_ids) == 40,
        "boundary_edge_count_is_108": len(boundary_edge_rows) == 108,
        "boundary_edge_table_shape_is_108_by_9": tuple(boundary_edge_table.shape)
        == (108, len(BOUNDARY_EDGE_COLUMNS)),
        "complement_node_count_is_44": len(complement_node_ids) == 44,
        "complement_connected": len(complement_components) == 1,
        "exterior_distance_two_nodes_are_0_21_46_55": exterior_distance_two_nodes
        == [0, 21, 46, 55],
        "cut_graph_connected": cut_graph_summary["component_count"] == 1,
        "cut_graph_node_count_is_52": cut_graph_summary["node_count"] == 52,
        "cut_graph_edge_count_is_108": cut_graph_summary["edge_count"] == 108,
        "cut_graph_diameter_is_6": cut_graph_summary["diameter"] == 6,
        "cut_graph_gromov_delta_is_2": cut_graph_summary["gromov_delta"]["delta_twice"] == 4,
        "boundary_band_connected": boundary_band_summary["component_count"] == 1,
        "boundary_band_node_count_is_52": boundary_band_summary["node_count"] == 52,
        "boundary_band_edge_count_is_295": boundary_band_summary["edge_count"] == 295,
        "boundary_band_diameter_is_3": boundary_band_summary["diameter"] == 3,
        "boundary_band_gromov_delta_is_1": boundary_band_summary["gromov_delta"][
            "delta_twice"
        ]
        == 2,
        "core_poincare_diameter_pair_is_10_44": [
            preserved_core["summary"]["core_poincare_diameter_pair"]["source_node_id"],
            preserved_core["summary"]["core_poincare_diameter_pair"]["target_node_id"],
        ]
        == [10, 44],
        "core_poincare_diameter_distance_is_0_3697551314": preserved_core["summary"][
            "core_poincare_diameter_pair"
        ]["endpoint_poincare_distance"]
        == 0.3697551314,
        "core_interval_incidence_shape_is_46_by_12": tuple(core_interval_incidence.shape)
        == (46, 12),
        "core_interval_table_shape_is_46_by_8": tuple(core_interval_table.shape)
        == (46, len(PRESERVED_INTERVAL_COLUMNS)),
        "core_interval_incidence_counts_match": bool(
            np.all(np.sum(core_interval_incidence, axis=1) == core_interval_table[:, 4])
        ),
    }

    witness = {
        "high_signature_threshold": HIGH_SIGNATURE_THRESHOLD,
        "full_high_interval_count": len(full_high_intervals),
        "core_node_count": len(core_node_ids),
        "core_node_ids": core_node_ids,
        "core_edge_count": len(core_edge_rows),
        "core_component_count": core_summary["component_count"],
        "core_graph_diameter": core_summary["diameter"],
        "core_graph_radius": core_summary["radius"],
        "core_center_node_ids": core_summary["center_node_ids"],
        "core_gromov_delta": core_summary["gromov_delta"]["delta"],
        "core_gromov_delta_twice": core_summary["gromov_delta"]["delta_twice"],
        "core_gromov_delta_witness_nodes": core_summary["gromov_delta"]["witness_nodes"],
        "core_distance_histogram": core_summary["distance_histogram"],
        "core_internal_degree_histogram": preserved_core["summary"][
            "core_internal_degree_histogram"
        ],
        "core_boundary_degree_histogram": preserved_core["summary"][
            "core_boundary_degree_histogram"
        ],
        "core_interval_cover_count_histogram": preserved_core["summary"][
            "core_interval_cover_count_histogram"
        ],
        "core_pair_count": core_pair_count,
        "core_pair_isometric_count": isometric_pair_count,
        "geodesically_preserved_core_pair_count": len(geodesically_preserved_core_pairs),
        "escaping_core_pair_count": len(escaping_core_pairs),
        "core_poincare_diameter_pair": preserved_core["summary"]["core_poincare_diameter_pair"],
        "boundary_core_node_count": preserved_core["summary"]["boundary_core_node_count"],
        "frontier_node_count": len(frontier_node_ids),
        "frontier_node_ids": frontier_node_ids,
        "boundary_edge_count": len(boundary_edge_rows),
        "boundary_band_node_count": len(boundary_band_node_ids),
        "cut_graph_diameter": cut_graph_summary["diameter"],
        "cut_graph_gromov_delta": cut_graph_summary["gromov_delta"]["delta"],
        "cut_graph_gromov_delta_twice": cut_graph_summary["gromov_delta"]["delta_twice"],
        "cut_graph_delta_witness_nodes": cut_graph_summary["gromov_delta"]["witness_nodes"],
        "boundary_band_edge_count": boundary_band_summary["edge_count"],
        "boundary_band_diameter": boundary_band_summary["diameter"],
        "boundary_band_gromov_delta": boundary_band_summary["gromov_delta"]["delta"],
        "boundary_band_gromov_delta_twice": boundary_band_summary["gromov_delta"][
            "delta_twice"
        ],
        "boundary_band_delta_witness_nodes": boundary_band_summary["gromov_delta"][
            "witness_nodes"
        ],
        "complement_node_count": len(complement_node_ids),
        "complement_component_count": len(complement_components),
        "exterior_distance_two_node_ids": exterior_distance_two_nodes,
        "core_node_table_sha256": sha_array(core_node_table),
        "core_edge_table_sha256": sha_array(core_edge_table),
        "boundary_edge_table_sha256": sha_array(boundary_edge_table),
        "core_interval_table_sha256": sha_array(core_interval_table),
        "core_interval_incidence_sha256": sha_array(core_interval_incidence),
        "core_adjacency_sha256": sha_array(core_adjacency),
        "core_distances_sha256": sha_array(core_distances),
        "cut_graph_adjacency_sha256": sha_array(cut_graph_adjacency),
        "cut_graph_distances_sha256": sha_array(cut_graph_distances),
        "boundary_band_adjacency_sha256": sha_array(boundary_band_adjacency),
        "boundary_band_distances_sha256": sha_array(boundary_band_distances),
        "source_interval_table_sha256": sha_array(interval_table),
        "source_interval_membership_sha256": sha_array(interval_membership),
        "source_original_distances_sha256": sha_array(original_distances),
    }

    certificate = {
        "schema": "c985.d20_preserved_core_subcomplex_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_PRESERVED_CORE_SUBCOMPLEX_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 46 full-high interval stalks collapse to exactly 12 full-sector high-signature core nodes",
            "the induced preserved core is connected, isometric inside the 56-node rewrite metric, and has exact Gromov delta 1",
            "all 12 core nodes lie on the finite boundary of the core inside the rewrite complex",
            "the core-complement cut graph is connected with exact delta 2",
            "the 52-node boundary band is connected with exact delta 1",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_preserved_core_subcomplex@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The 46 geodesic intervals preserving full six-sector coverage and high "
            "relation-signature support collapse to a connected 12-node preserved "
            "core subcomplex whose internal metric and finite boundary are exactly "
            "certified inside the 56-node d20 rewrite complex."
        ),
        "stage_protocol": {
            "draft": "select the full-sector high-signature core from the certified interval sheaf",
            "witness": "materialize the induced core graph, full-high interval cover, core-complement cut, and boundary band",
            "coherence": "check connected components, graph distances, isometry, interval convexity, and Gromov-delta witnesses",
            "closure": "certify the preserved-core subcomplex and its finite hyperbolic boundary band",
            "emit": "emit core JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex": input_entry(REWRITE_COMPLEX_JSON),
            "rewrite_complex_tables": input_entry(REWRITE_COMPLEX_TABLES),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "interval_sheaf_report": input_entry(
                INTERVAL_SHEAF_REPORT,
                {
                    "status": interval_report.get("status"),
                    "certificate_sha256": interval_report.get("certificate_sha256"),
                },
            ),
            "interval_sheaf": input_entry(INTERVAL_SHEAF_JSON),
            "interval_sheaf_tables": input_entry(INTERVAL_SHEAF_TABLES),
            "interval_sheaf_certificate": input_entry(INTERVAL_SHEAF_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "preserved_core_subcomplex": relpath(OUT_DIR / "preserved_core_subcomplex.json"),
            "preserved_core_nodes_csv": relpath(OUT_DIR / "preserved_core_nodes.csv"),
            "preserved_core_edges_csv": relpath(OUT_DIR / "preserved_core_edges.csv"),
            "preserved_core_boundary_edges_csv": relpath(
                OUT_DIR / "preserved_core_boundary_edges.csv"
            ),
            "preserved_core_intervals_csv": relpath(OUT_DIR / "preserved_core_intervals.csv"),
            "preserved_core_tables": relpath(OUT_DIR / "preserved_core_tables.npz"),
            "preserved_core_certificate": relpath(OUT_DIR / "preserved_core_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the exact 12-node preserved core selected by full-sector coverage and signature count >= 155",
                "the 31-edge induced core graph and its connected component structure",
                "exact core graph distances, radius, diameter, centers, and Gromov-delta witness",
                "which core endpoint pairs have geodesic intervals staying inside the preserved core",
                "the finite core-complement boundary and 52-node boundary band inside the rewrite complex",
            ],
            "does_not_certify_because_not_required": [
                "an infinite visual boundary or asymptotic Gromov boundary",
                "arbitrary-length symbolic rewrite confluence",
                "new C985 associator or pentagon data beyond the existing certificate",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Turn the 12-node preserved core into a chamber system: orient its 31 "
            "core edges by signature and Poincare flow, then certify directed "
            "cycles, sources/sinks, and whether the boundary band retracts onto "
            "a smaller hyperbolic spine."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_preserved_core_subcomplex_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified rewrite-complex and geodesic interval-sheaf artifacts",
            "derive the full-sector high-signature core and compare it with the full-high interval union",
            "materialize induced core, cut graph, boundary band, and interval incidence tables",
            "check connected components, exact graph metrics, finite-boundary facts, and Gromov-delta witnesses",
            "check source hashes and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "preserved_core_subcomplex": preserved_core,
        "preserved_core_nodes_csv": csv_text(CORE_NODE_COLUMNS, core_node_rows),
        "preserved_core_edges_csv": csv_text(CORE_EDGE_COLUMNS, core_edge_rows),
        "preserved_core_boundary_edges_csv": csv_text(BOUNDARY_EDGE_COLUMNS, boundary_edge_rows),
        "preserved_core_intervals_csv": csv_text(PRESERVED_INTERVAL_COLUMNS, core_interval_rows),
        "core_node_table": core_node_table,
        "core_edge_table": core_edge_table,
        "boundary_edge_table": boundary_edge_table,
        "core_interval_table": core_interval_table,
        "core_interval_incidence": core_interval_incidence,
        "core_nodes": core_nodes_array,
        "frontier_nodes": frontier_nodes_array,
        "boundary_band_nodes": boundary_band_nodes_array,
        "core_adjacency": core_adjacency,
        "core_distances": core_distances,
        "cut_graph_adjacency": cut_graph_adjacency,
        "cut_graph_distances": cut_graph_distances,
        "boundary_band_adjacency": boundary_band_adjacency,
        "boundary_band_distances": boundary_band_distances,
        "preserved_core_certificate": certificate,
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
    write_json(OUT_DIR / "preserved_core_subcomplex.json", payloads["preserved_core_subcomplex"])
    (OUT_DIR / "preserved_core_nodes.csv").write_text(
        payloads["preserved_core_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "preserved_core_edges.csv").write_text(
        payloads["preserved_core_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "preserved_core_boundary_edges.csv").write_text(
        payloads["preserved_core_boundary_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "preserved_core_intervals.csv").write_text(
        payloads["preserved_core_intervals_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "preserved_core_tables.npz",
        core_node_table=payloads["core_node_table"],
        core_edge_table=payloads["core_edge_table"],
        boundary_edge_table=payloads["boundary_edge_table"],
        core_interval_table=payloads["core_interval_table"],
        core_interval_incidence=payloads["core_interval_incidence"],
        core_nodes=payloads["core_nodes"],
        frontier_nodes=payloads["frontier_nodes"],
        boundary_band_nodes=payloads["boundary_band_nodes"],
        core_adjacency=payloads["core_adjacency"],
        core_distances=payloads["core_distances"],
        cut_graph_adjacency=payloads["cut_graph_adjacency"],
        cut_graph_distances=payloads["cut_graph_distances"],
        boundary_band_adjacency=payloads["boundary_band_adjacency"],
        boundary_band_distances=payloads["boundary_band_distances"],
    )
    write_json(OUT_DIR / "preserved_core_certificate.json", payloads["preserved_core_certificate"])
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
                "core_node_count": witness["core_node_count"],
                "core_edge_count": witness["core_edge_count"],
                "core_gromov_delta": witness["core_gromov_delta"],
                "frontier_node_count": witness["frontier_node_count"],
                "boundary_edge_count": witness["boundary_edge_count"],
                "boundary_band_gromov_delta": witness["boundary_band_gromov_delta"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
