from __future__ import annotations

import itertools
import json
from collections import deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_preserved_core_subcomplex import (
        HIGH_SIGNATURE_THRESHOLD,
        PRESERVED_INTERVAL_COLUMNS,
        connected_components,
        distance_matrix,
        graph_summary,
        round10,
        scaled_distance,
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
    from derive_c985_d20_preserved_core_subcomplex import (
        HIGH_SIGNATURE_THRESHOLD,
        PRESERVED_INTERVAL_COLUMNS,
        connected_components,
        distance_matrix,
        graph_summary,
        round10,
        scaled_distance,
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


THEOREM_ID = "c985_d20_chamber_spine"
STATUS = "C985_D20_CHAMBER_SPINE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REWRITE_COMPLEX_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_rewrite_complex_hyperbolicity"
PRESERVED_CORE_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_preserved_core_subcomplex"

REWRITE_COMPLEX_REPORT = REWRITE_COMPLEX_DIR / "report.json"
REWRITE_COMPLEX_JSON = REWRITE_COMPLEX_DIR / "rewrite_complex.json"
REWRITE_COMPLEX_TABLES = REWRITE_COMPLEX_DIR / "rewrite_complex_tables.npz"
REWRITE_COMPLEX_CERTIFICATE = REWRITE_COMPLEX_DIR / "rewrite_complex_certificate.json"
PRESERVED_CORE_REPORT = PRESERVED_CORE_DIR / "report.json"
PRESERVED_CORE_JSON = PRESERVED_CORE_DIR / "preserved_core_subcomplex.json"
PRESERVED_CORE_TABLES = PRESERVED_CORE_DIR / "preserved_core_tables.npz"
PRESERVED_CORE_CERTIFICATE = PRESERVED_CORE_DIR / "preserved_core_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_chamber_spine.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_chamber_spine.py"

ORIENTATION_REASON_CODES = {
    "signature_ascent": 0,
    "poincare_inward_tie": 1,
    "node_id_tie": 2,
}
POINCARE_FLOW_CODES = {
    "inward": -1,
    "flat": 0,
    "outward": 1,
}

ORIENTED_EDGE_COLUMNS = [
    "oriented_edge_id",
    "source_node_id",
    "target_node_id",
    "source_signature_union_count",
    "target_signature_union_count",
    "source_radius_x1e10",
    "target_radius_x1e10",
    "signature_delta",
    "radius_delta_x1e10",
    "orientation_reason_code",
    "poincare_flow_code",
]

TRANSITIVE_REDUCTION_COLUMNS = [
    "reduction_edge_id",
    "source_node_id",
    "target_node_id",
    "source_signature_union_count",
    "target_signature_union_count",
    "signature_delta",
]

MAXIMAL_CHAMBER_COLUMNS = [
    "chamber_id",
    "chamber_size",
    "chamber_dimension",
    "node_id_0",
    "node_id_1",
    "node_id_2",
    "node_id_3",
    "node_id_4",
    "node_id_5",
    "source_node_id",
    "sink_node_id",
    "min_signature_union_count",
    "max_signature_union_count",
    "directed_edge_count",
]

FOLD_COLUMNS = [
    "fold_id",
    "removed_node_id",
    "dominator_node_id",
    "active_node_count_before",
    "removed_signature_union_count",
    "dominator_signature_union_count",
    "removed_is_core",
    "dominator_is_core",
]

RETRACTION_COLUMNS = [
    "boundary_band_node_id",
    "image_node_id",
    "node_is_spine",
    "node_is_core",
    "image_is_core",
]


def node_radius_x1e10(node: dict[str, Any]) -> int:
    return scaled_distance(node["poincare_barycenter"]["radius"])


def node_potential(node: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(node["signature_union_count"]),
        -node_radius_x1e10(node),
        int(node["node_id"]),
    )


def orientation_reason(source: dict[str, Any], target: dict[str, Any]) -> str:
    if int(source["signature_union_count"]) != int(target["signature_union_count"]):
        return "signature_ascent"
    if node_radius_x1e10(source) != node_radius_x1e10(target):
        return "poincare_inward_tie"
    return "node_id_tie"


def poincare_flow(source: dict[str, Any], target: dict[str, Any]) -> str:
    source_radius = node_radius_x1e10(source)
    target_radius = node_radius_x1e10(target)
    if target_radius < source_radius:
        return "inward"
    if target_radius > source_radius:
        return "outward"
    return "flat"


def build_oriented_edges(
    core_edges: list[dict[str, Any]],
    node_by_id: dict[int, dict[str, Any]],
    core_node_ids: list[int],
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    core_index = {node_id: index for index, node_id in enumerate(core_node_ids)}
    directed_adjacency = np.zeros((len(core_node_ids), len(core_node_ids)), dtype=np.int8)
    oriented_rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for edge in core_edges:
        left = int(edge["source_node_id"])
        right = int(edge["target_node_id"])
        source_id, target_id = (
            (left, right)
            if node_potential(node_by_id[left]) < node_potential(node_by_id[right])
            else (right, left)
        )
        source = node_by_id[source_id]
        target = node_by_id[target_id]
        reason = orientation_reason(source, target)
        flow = poincare_flow(source, target)
        row = {
            "oriented_edge_id": len(oriented_rows),
            "source_node_id": source_id,
            "target_node_id": target_id,
            "source_word": source["canonical_word"],
            "target_word": target["canonical_word"],
            "source_signature_union_count": int(source["signature_union_count"]),
            "target_signature_union_count": int(target["signature_union_count"]),
            "source_radius": source["poincare_barycenter"]["radius"],
            "target_radius": target["poincare_barycenter"]["radius"],
            "source_radius_x1e10": node_radius_x1e10(source),
            "target_radius_x1e10": node_radius_x1e10(target),
            "signature_delta": int(target["signature_union_count"])
            - int(source["signature_union_count"]),
            "radius_delta_x1e10": node_radius_x1e10(target) - node_radius_x1e10(source),
            "orientation_reason": reason,
            "orientation_reason_code": ORIENTATION_REASON_CODES[reason],
            "poincare_flow": flow,
            "poincare_flow_code": POINCARE_FLOW_CODES[flow],
        }
        oriented_rows.append(row)
        table_rows.append([int(row[column]) for column in ORIENTED_EDGE_COLUMNS])
        directed_adjacency[core_index[source_id], core_index[target_id]] = 1
    return (
        oriented_rows,
        np.asarray(table_rows, dtype=np.int64),
        directed_adjacency,
    )


def topological_order(directed_adjacency: np.ndarray, labels: list[int]) -> list[int]:
    potentials = {node_id: node_id for node_id in labels}
    indegrees = np.asarray(directed_adjacency.sum(axis=0), dtype=np.int64)
    queue = sorted(
        [index for index, value in enumerate(indegrees) if int(value) == 0],
        key=lambda index: potentials[labels[index]],
    )
    order: list[int] = []
    while queue:
        index = queue.pop(0)
        order.append(labels[index])
        for neighbor in np.flatnonzero(directed_adjacency[index]):
            neighbor = int(neighbor)
            indegrees[neighbor] -= 1
            if int(indegrees[neighbor]) == 0:
                queue.append(neighbor)
                queue.sort(key=lambda item: potentials[labels[item]])
    return order


def potential_order(core_node_ids: list[int], node_by_id: dict[int, dict[str, Any]]) -> list[int]:
    return sorted(core_node_ids, key=lambda node_id: node_potential(node_by_id[node_id]))


def transitive_reduction(
    directed_adjacency: np.ndarray,
    labels: list[int],
    node_by_id: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    reduction = np.zeros_like(directed_adjacency)
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for source in range(len(labels)):
        for target in np.flatnonzero(directed_adjacency[source]):
            target = int(target)
            seen: set[int] = set()
            queue: deque[int] = deque(
                int(neighbor)
                for neighbor in np.flatnonzero(directed_adjacency[source])
                if int(neighbor) != target
            )
            found = False
            while queue:
                node = queue.popleft()
                if node == target:
                    found = True
                    break
                if node in seen:
                    continue
                seen.add(node)
                queue.extend(int(neighbor) for neighbor in np.flatnonzero(directed_adjacency[node]))
            if found:
                continue
            reduction[source, target] = 1
            source_node = node_by_id[labels[source]]
            target_node = node_by_id[labels[target]]
            row = {
                "reduction_edge_id": len(rows),
                "source_node_id": labels[source],
                "target_node_id": labels[target],
                "source_signature_union_count": int(source_node["signature_union_count"]),
                "target_signature_union_count": int(target_node["signature_union_count"]),
                "signature_delta": int(target_node["signature_union_count"])
                - int(source_node["signature_union_count"]),
            }
            rows.append(row)
            table_rows.append([int(row[column]) for column in TRANSITIVE_REDUCTION_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64), reduction


def directed_path_summary(
    directed_adjacency: np.ndarray,
    labels: list[int],
) -> dict[str, Any]:
    adjacency = {
        labels[index]: [labels[int(neighbor)] for neighbor in np.flatnonzero(directed_adjacency[index])]
        for index in range(len(labels))
    }
    indegree = {
        labels[index]: int(directed_adjacency[:, index].sum())
        for index in range(len(labels))
    }
    outdegree = {
        labels[index]: int(directed_adjacency[index, :].sum())
        for index in range(len(labels))
    }
    sources = [node_id for node_id in labels if indegree[node_id] == 0]
    sinks = [node_id for node_id in labels if outdegree[node_id] == 0]

    all_paths: list[list[int]] = []
    source_sink_paths: list[list[int]] = []

    def visit(path: list[int]) -> None:
        all_paths.append(path)
        if path[-1] in sinks and path[0] in sources:
            source_sink_paths.append(path)
        for neighbor in adjacency[path[-1]]:
            visit([*path, neighbor])

    for node_id in labels:
        visit([node_id])

    longest = max(source_sink_paths, key=lambda path: (len(path), path))
    return {
        "source_node_ids": sources,
        "sink_node_ids": sinks,
        "indegree_histogram": histogram(list(indegree.values())),
        "outdegree_histogram": histogram(list(outdegree.values())),
        "all_directed_path_count": len(all_paths),
        "nontrivial_directed_path_count": sum(1 for path in all_paths if len(path) > 1),
        "all_directed_path_length_histogram": histogram([len(path) - 1 for path in all_paths]),
        "source_sink_path_count": len(source_sink_paths),
        "source_sink_path_length_histogram": histogram(
            [len(path) - 1 for path in source_sink_paths]
        ),
        "longest_source_sink_path_length": len(longest) - 1,
        "longest_source_sink_path": longest,
    }


def clique_rows(
    core_adjacency: np.ndarray,
    directed_adjacency: np.ndarray,
    core_node_ids: list[int],
    node_by_id: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, Any]]:
    all_cliques: list[tuple[int, ...]] = []
    maximal: list[tuple[int, ...]] = []
    for size in range(1, len(core_node_ids) + 1):
        for combo in itertools.combinations(core_node_ids, size):
            indices = [core_node_ids.index(node_id) for node_id in combo]
            if not all(
                bool(core_adjacency[left, right])
                for left, right in itertools.combinations(indices, 2)
            ):
                continue
            all_cliques.append(combo)
            if not any(set(combo) < set(row) for row in maximal):
                maximal = [row for row in maximal if not set(row) < set(combo)]
                maximal.append(combo)

    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for chamber_id, clique in enumerate(sorted(maximal, key=lambda row: (len(row), row))):
        ordered = sorted(clique, key=lambda node_id: node_potential(node_by_id[node_id]))
        signatures = [int(node_by_id[node_id]["signature_union_count"]) for node_id in clique]
        padded = [*clique, *([-1] * (6 - len(clique)))]
        directed_edge_count = 0
        for left, right in itertools.combinations(clique, 2):
            left_index = core_node_ids.index(left)
            right_index = core_node_ids.index(right)
            if directed_adjacency[left_index, right_index] or directed_adjacency[right_index, left_index]:
                directed_edge_count += 1
        row = {
            "chamber_id": chamber_id,
            "chamber_size": len(clique),
            "chamber_dimension": len(clique) - 1,
            "node_ids": list(clique),
            "node_id_0": int(padded[0]),
            "node_id_1": int(padded[1]),
            "node_id_2": int(padded[2]),
            "node_id_3": int(padded[3]),
            "node_id_4": int(padded[4]),
            "node_id_5": int(padded[5]),
            "source_node_id": ordered[0],
            "sink_node_id": ordered[-1],
            "min_signature_union_count": min(signatures),
            "max_signature_union_count": max(signatures),
            "directed_edge_count": directed_edge_count,
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in MAXIMAL_CHAMBER_COLUMNS])

    clique_size_hist = histogram([len(row) for row in all_cliques])
    maximal_size_hist = histogram([len(row) for row in maximal])
    euler_characteristic = sum(
        ((-1) ** (entry["value"] - 1)) * entry["count"] for entry in clique_size_hist
    )
    triangle_count = sum(1 for row in all_cliques if len(row) == 3)
    cyclic_triangle_count = 0
    for clique in all_cliques:
        if len(clique) != 3:
            continue
        indegrees = {node_id: 0 for node_id in clique}
        outdegrees = {node_id: 0 for node_id in clique}
        for left, right in itertools.combinations(clique, 2):
            left_index = core_node_ids.index(left)
            right_index = core_node_ids.index(right)
            if directed_adjacency[left_index, right_index]:
                outdegrees[left] += 1
                indegrees[right] += 1
            elif directed_adjacency[right_index, left_index]:
                outdegrees[right] += 1
                indegrees[left] += 1
        if all(indegrees[node] == 1 and outdegrees[node] == 1 for node in clique):
            cyclic_triangle_count += 1

    summary = {
        "clique_size_histogram": clique_size_hist,
        "maximal_chamber_count": len(maximal),
        "maximal_chamber_size_histogram": maximal_size_hist,
        "triangle_count": triangle_count,
        "cyclic_directed_triangle_count": cyclic_triangle_count,
        "transitive_directed_triangle_count": triangle_count - cyclic_triangle_count,
        "clique_complex_euler_characteristic": euler_characteristic,
        "largest_chamber_node_ids": max((list(row) for row in maximal), key=lambda row: (len(row), row)),
    }
    return rows, np.asarray(table_rows, dtype=np.int64), summary


def closed_neighbors(
    active: list[int],
    adjacency: np.ndarray,
    index: dict[int, int],
    node_id: int,
) -> set[int]:
    return {
        node_id,
        *[neighbor for neighbor in active if bool(adjacency[index[node_id], index[neighbor]])],
    }


def fold_dominated_vertices(
    node_ids: list[int],
    adjacency: np.ndarray,
    node_by_id: dict[int, dict[str, Any]],
    core_node_ids: list[int],
    preserve: set[int] | None = None,
) -> tuple[list[int], list[dict[str, Any]]]:
    active = list(node_ids)
    index = {node_id: local_id for local_id, node_id in enumerate(node_ids)}
    core_set = set(core_node_ids)
    preserve = preserve or set()
    steps: list[dict[str, Any]] = []
    while True:
        folded = False
        for node_id in list(active):
            if node_id in preserve:
                continue
            node_neighbors = closed_neighbors(active, adjacency, index, node_id)
            dominators = [
                candidate
                for candidate in active
                if candidate != node_id
                and node_neighbors <= closed_neighbors(active, adjacency, index, candidate)
            ]
            if not dominators:
                continue
            dominator = sorted(
                dominators,
                key=lambda candidate: (
                    candidate not in core_set,
                    -int(node_by_id[candidate]["signature_union_count"]),
                    candidate,
                ),
            )[0]
            steps.append(
                {
                    "fold_id": len(steps),
                    "removed_node_id": node_id,
                    "dominator_node_id": dominator,
                    "active_node_count_before": len(active),
                    "removed_signature_union_count": int(
                        node_by_id[node_id]["signature_union_count"]
                    ),
                    "dominator_signature_union_count": int(
                        node_by_id[dominator]["signature_union_count"]
                    ),
                    "removed_is_core": int(node_id in core_set),
                    "dominator_is_core": int(dominator in core_set),
                }
            )
            active.remove(node_id)
            folded = True
            break
        if not folded:
            return active, steps


def residual_dominated_pairs(
    node_ids: list[int],
    adjacency: np.ndarray,
    original_index: dict[int, int],
) -> list[list[int]]:
    active_index = {node_id: position for position, node_id in enumerate(node_ids)}
    induced = np.zeros((len(node_ids), len(node_ids)), dtype=np.int8)
    for left, source in enumerate(node_ids):
        for right, target in enumerate(node_ids):
            if bool(adjacency[original_index[source], original_index[target]]):
                induced[left, right] = 1
    pairs: list[list[int]] = []
    for node_id in node_ids:
        node_neighbors = closed_neighbors(node_ids, induced, active_index, node_id)
        for candidate in node_ids:
            if candidate == node_id:
                continue
            if node_neighbors <= closed_neighbors(node_ids, induced, active_index, candidate):
                pairs.append([node_id, candidate])
                break
    return pairs


def retraction_map(
    band_node_ids: list[int],
    fold_steps: list[dict[str, Any]],
) -> dict[int, int]:
    mapping = {node_id: node_id for node_id in band_node_ids}
    for step in fold_steps:
        mapping[int(step["removed_node_id"])] = int(step["dominator_node_id"])
    for node_id in list(mapping):
        image = mapping[node_id]
        seen: set[int] = set()
        while mapping.get(image, image) != image:
            if image in seen:
                raise AssertionError("cycle in retraction fold map")
            seen.add(image)
            image = mapping[image]
        mapping[node_id] = image
    return mapping


def retraction_failures(
    node_ids: list[int],
    adjacency: np.ndarray,
    mapping: dict[int, int],
) -> list[list[int]]:
    index = {node_id: local_id for local_id, node_id in enumerate(node_ids)}
    failures: list[list[int]] = []
    for left, source in enumerate(node_ids):
        for right in range(left + 1, len(node_ids)):
            target = node_ids[right]
            if not bool(adjacency[left, right]):
                continue
            image_source = mapping[source]
            image_target = mapping[target]
            if image_source == image_target:
                continue
            if not bool(adjacency[index[image_source], index[image_target]]):
                failures.append([source, target, image_source, image_target])
    return failures


def core_retraction_obstructions(
    band_node_ids: list[int],
    boundary_band_adjacency: np.ndarray,
    core_node_ids: list[int],
) -> list[dict[str, Any]]:
    index = {node_id: local_id for local_id, node_id in enumerate(band_node_ids)}
    core_index = {node_id: local_id for local_id, node_id in enumerate(core_node_ids)}
    core_adjacency = np.zeros((len(core_node_ids), len(core_node_ids)), dtype=np.int8)
    for left, source in enumerate(core_node_ids):
        for right, target in enumerate(core_node_ids):
            core_adjacency[left, right] = int(boundary_band_adjacency[index[source], index[target]])
    obstructions: list[dict[str, Any]] = []
    for node_id in band_node_ids:
        if node_id in core_index:
            continue
        core_neighbors = [
            core_node
            for core_node in core_node_ids
            if bool(boundary_band_adjacency[index[node_id], index[core_node]])
        ]
        allowed = [
            candidate
            for candidate in core_node_ids
            if all(
                candidate == neighbor
                or bool(core_adjacency[core_index[candidate], core_index[neighbor]])
                for neighbor in core_neighbors
            )
        ]
        if not allowed:
            obstructions.append(
                {
                    "frontier_node_id": node_id,
                    "core_neighbor_ids": core_neighbors,
                }
            )
    return obstructions


def induced_adjacency(node_ids: list[int], source_adjacency: np.ndarray, source_index: dict[int, int]) -> np.ndarray:
    adjacency = np.zeros((len(node_ids), len(node_ids)), dtype=np.int8)
    for left, source in enumerate(node_ids):
        for right, target in enumerate(node_ids):
            adjacency[left, right] = int(source_adjacency[source_index[source], source_index[target]])
    return adjacency


def build_payloads() -> dict[str, Any]:
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_complex = load_json(REWRITE_COMPLEX_JSON)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    preserved_report = load_json(PRESERVED_CORE_REPORT)
    preserved_core = load_json(PRESERVED_CORE_JSON)
    preserved_certificate = load_json(PRESERVED_CORE_CERTIFICATE)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    preserved_tables = np.load(PRESERVED_CORE_TABLES, allow_pickle=False)

    nodes = rewrite_complex["nodes"]
    node_by_id = {int(node["node_id"]): node for node in nodes}
    core_node_ids = [int(node_id) for node_id in preserved_core["summary"]["core_node_ids"]]
    boundary_band_node_ids = [
        int(node_id) for node_id in preserved_core["boundary"]["boundary_band_node_ids"]
    ]
    core_edges = preserved_core["core_edges"]
    full_graph_node_ids = [int(node["node_id"]) for node in nodes]
    full_graph_adjacency = np.asarray(rewrite_tables["adjacency"], dtype=np.int8)
    core_adjacency = np.asarray(preserved_tables["core_adjacency"], dtype=np.int8)
    boundary_band_adjacency = np.asarray(
        preserved_tables["boundary_band_adjacency"], dtype=np.int8
    )

    oriented_edges, oriented_edge_table, directed_adjacency = build_oriented_edges(
        core_edges,
        node_by_id,
        core_node_ids,
    )
    potential_topological_order = potential_order(core_node_ids, node_by_id)
    kahn_topological_order = topological_order(directed_adjacency, core_node_ids)
    is_acyclic = len(kahn_topological_order) == len(core_node_ids)
    reduction_edges, reduction_edge_table, reduction_adjacency = transitive_reduction(
        directed_adjacency,
        core_node_ids,
        node_by_id,
    )
    path_summary = directed_path_summary(directed_adjacency, core_node_ids)
    chamber_rows, chamber_table, chamber_summary = clique_rows(
        core_adjacency,
        directed_adjacency,
        core_node_ids,
        node_by_id,
    )

    core_spine_node_ids, fold_steps = fold_dominated_vertices(
        boundary_band_node_ids,
        boundary_band_adjacency,
        node_by_id,
        core_node_ids,
        preserve=set(core_node_ids),
    )
    fold_table = np.asarray(
        [[int(row[column]) for column in FOLD_COLUMNS] for row in fold_steps],
        dtype=np.int64,
    )
    band_index = {node_id: local_id for local_id, node_id in enumerate(boundary_band_node_ids)}
    spine_adjacency = induced_adjacency(
        core_spine_node_ids,
        boundary_band_adjacency,
        band_index,
    )
    spine_distances = distance_matrix(spine_adjacency)
    spine_summary = graph_summary(spine_adjacency, core_spine_node_ids)
    residual_pairs = residual_dominated_pairs(
        core_spine_node_ids,
        boundary_band_adjacency,
        band_index,
    )
    fold_retraction = retraction_map(boundary_band_node_ids, fold_steps)
    fold_failures = retraction_failures(
        boundary_band_node_ids,
        boundary_band_adjacency,
        fold_retraction,
    )
    retraction_rows = [
        {
            "boundary_band_node_id": node_id,
            "image_node_id": fold_retraction[node_id],
            "node_is_spine": int(node_id in set(core_spine_node_ids)),
            "node_is_core": int(node_id in set(core_node_ids)),
            "image_is_core": int(fold_retraction[node_id] in set(core_node_ids)),
        }
        for node_id in boundary_band_node_ids
    ]
    retraction_table = np.asarray(
        [[int(row[column]) for column in RETRACTION_COLUMNS] for row in retraction_rows],
        dtype=np.int64,
    )

    full_spine_node_ids, full_fold_steps = fold_dominated_vertices(
        full_graph_node_ids,
        full_graph_adjacency,
        node_by_id,
        core_node_ids,
    )
    full_fold_table = np.asarray(
        [[int(row[column]) for column in FOLD_COLUMNS] for row in full_fold_steps],
        dtype=np.int64,
    )

    core_obstructions = core_retraction_obstructions(
        boundary_band_node_ids,
        boundary_band_adjacency,
        core_node_ids,
    )
    chamber_node_potential_table = np.asarray(
        [
            [
                int(node_id),
                int(node_by_id[node_id]["signature_union_count"]),
                node_radius_x1e10(node_by_id[node_id]),
                int(directed_adjacency[:, core_node_ids.index(node_id)].sum()),
                int(directed_adjacency[core_node_ids.index(node_id), :].sum()),
                potential_topological_order.index(node_id),
            ]
            for node_id in core_node_ids
        ],
        dtype=np.int64,
    )

    orientation_reason_hist = histogram(
        [int(row["orientation_reason_code"]) for row in oriented_edges]
    )
    poincare_flow_hist = histogram([int(row["poincare_flow_code"]) for row in oriented_edges])

    chamber_spine = {
        "schema": "c985.d20_chamber_spine@1",
        "object": "d20",
        "source_rewrite_complex_certificate": rewrite_report.get("certificate_sha256"),
        "source_preserved_core_certificate": preserved_report.get("certificate_sha256"),
        "orientation_rule": {
            "primary": "orient each preserved-core edge toward larger signature-union count",
            "secondary": "when signatures tie, orient inward toward smaller Poincare barycenter radius",
            "tertiary": "when both tie, orient by increasing node id",
            "potential": "(signature_union_count, -radius_x1e10, node_id)",
        },
        "oriented_edges": oriented_edges,
        "transitive_reduction_edges": reduction_edges,
        "maximal_chambers": chamber_rows,
        "boundary_band_folds": fold_steps,
        "full_rewrite_complex_folds": full_fold_steps,
        "spine_retraction": retraction_rows,
        "core_retraction_obstructions": core_obstructions,
        "summary": {
            "core_node_count": len(core_node_ids),
            "core_edge_count": len(core_edges),
            "oriented_edge_count": len(oriented_edges),
            "orientation_reason_codebook": ORIENTATION_REASON_CODES,
            "poincare_flow_codebook": POINCARE_FLOW_CODES,
            "orientation_reason_histogram": orientation_reason_hist,
            "poincare_flow_histogram": poincare_flow_hist,
            "directed_acyclic": is_acyclic,
            "directed_cycle_count": 0 if is_acyclic else None,
            "potential_topological_order": potential_topological_order,
            "kahn_topological_order": kahn_topological_order,
            "transitive_reduction_edge_count": len(reduction_edges),
            "path_summary": path_summary,
            "undirected_cycle_rank": len(core_edges) - len(core_node_ids) + 1,
            "chamber_summary": chamber_summary,
            "boundary_band_node_count": len(boundary_band_node_ids),
            "boundary_band_fold_count": len(fold_steps),
            "spine_node_count": len(core_spine_node_ids),
            "spine_node_ids": core_spine_node_ids,
            "spine_edge_count": spine_summary["edge_count"],
            "spine_diameter": spine_summary["diameter"],
            "spine_gromov_delta": spine_summary["gromov_delta"]["delta"],
            "spine_gromov_delta_twice": spine_summary["gromov_delta"]["delta_twice"],
            "spine_gromov_delta_witness_nodes": spine_summary["gromov_delta"]["witness_nodes"],
            "spine_degree_histogram": histogram(
                [int(row) for row in np.sum(spine_adjacency, axis=1)]
            ),
            "residual_dominated_pair_count": len(residual_pairs),
            "residual_dominated_pairs": residual_pairs,
            "fold_retraction_failure_count": len(fold_failures),
            "fold_retraction_failures": fold_failures,
            "core_retraction_obstruction_count": len(core_obstructions),
            "core_retraction_obstruction_node_ids": [
                row["frontier_node_id"] for row in core_obstructions
            ],
            "full_rewrite_complex_fold_count": len(full_fold_steps),
            "full_rewrite_complex_spine_node_count": len(full_spine_node_ids),
            "full_rewrite_complex_spine_matches_boundary_spine": sorted(full_spine_node_ids)
            == sorted(core_spine_node_ids),
        },
    }

    checks = {
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "preserved_core_report_certified": preserved_report.get("status")
        == "C985_D20_PRESERVED_CORE_SUBCOMPLEX_CERTIFIED",
        "preserved_core_certificate_certified": preserved_certificate.get("status")
        == "C985_D20_PRESERVED_CORE_SUBCOMPLEX_CERTIFIED",
        "high_signature_threshold_matches_preserved_core": preserved_report.get("witness", {}).get(
            "high_signature_threshold"
        )
        == HIGH_SIGNATURE_THRESHOLD,
        "core_node_count_is_12": len(core_node_ids) == 12,
        "core_edge_count_is_31": len(core_edges) == 31,
        "oriented_edge_count_is_31": len(oriented_edges) == 31,
        "oriented_edge_table_shape_is_31_by_11": tuple(oriented_edge_table.shape)
        == (31, len(ORIENTED_EDGE_COLUMNS)),
        "directed_adjacency_shape_is_12_by_12": tuple(directed_adjacency.shape) == (12, 12),
        "orientation_reason_histogram_is_30_signature_1_poincare": orientation_reason_hist
        == [
            {"value": 0, "count": 30},
            {"value": 1, "count": 1},
        ],
        "poincare_flow_histogram_is_23_inward_8_outward": poincare_flow_hist
        == [
            {"value": -1, "count": 23},
            {"value": 1, "count": 8},
        ],
        "directed_orientation_is_acyclic": is_acyclic is True,
        "directed_cycle_count_is_zero": chamber_spine["summary"]["directed_cycle_count"] == 0,
        "sources_are_10_43": path_summary["source_node_ids"] == [10, 43],
        "sink_is_44": path_summary["sink_node_ids"] == [44],
        "source_sink_path_count_is_42": path_summary["source_sink_path_count"] == 42,
        "all_directed_path_count_is_176": path_summary["all_directed_path_count"] == 176,
        "longest_source_sink_path_is_43_38_13_41_28_34_44": path_summary[
            "longest_source_sink_path"
        ]
        == [43, 38, 13, 41, 28, 34, 44],
        "transitive_reduction_edge_count_is_15": len(reduction_edges) == 15,
        "transitive_reduction_table_shape_is_15_by_6": tuple(reduction_edge_table.shape)
        == (15, len(TRANSITIVE_REDUCTION_COLUMNS)),
        "maximal_chamber_count_is_10": chamber_summary["maximal_chamber_count"] == 10,
        "maximal_chamber_size_histogram_is_9_triangles_1_six": chamber_summary[
            "maximal_chamber_size_histogram"
        ]
        == [
            {"value": 3, "count": 9},
            {"value": 6, "count": 1},
        ],
        "triangle_count_is_29": chamber_summary["triangle_count"] == 29,
        "cyclic_directed_triangle_count_is_zero": chamber_summary[
            "cyclic_directed_triangle_count"
        ]
        == 0,
        "clique_complex_euler_characteristic_is_zero": chamber_summary[
            "clique_complex_euler_characteristic"
        ]
        == 0,
        "largest_chamber_is_13_28_38_41_43_44": chamber_summary["largest_chamber_node_ids"]
        == [13, 28, 38, 41, 43, 44],
        "undirected_cycle_rank_is_20": chamber_spine["summary"]["undirected_cycle_rank"] == 20,
        "boundary_band_node_count_is_52": len(boundary_band_node_ids) == 52,
        "boundary_band_fold_count_is_2": len(fold_steps) == 2,
        "boundary_band_fold_steps_are_36_to_38_and_52_to_43": [
            [int(row["removed_node_id"]), int(row["dominator_node_id"])] for row in fold_steps
        ]
        == [[36, 38], [52, 43]],
        "fold_table_shape_is_2_by_8": tuple(fold_table.shape) == (2, len(FOLD_COLUMNS)),
        "spine_node_count_is_50": len(core_spine_node_ids) == 50,
        "spine_edge_count_is_285": spine_summary["edge_count"] == 285,
        "spine_diameter_is_3": spine_summary["diameter"] == 3,
        "spine_gromov_delta_is_1": spine_summary["gromov_delta"]["delta_twice"] == 2,
        "spine_degree_histogram_is_30_nine_20_fifteen": chamber_spine["summary"][
            "spine_degree_histogram"
        ]
        == [
            {"value": 9, "count": 30},
            {"value": 15, "count": 20},
        ],
        "spine_has_no_residual_dominated_pairs": len(residual_pairs) == 0,
        "fold_retraction_has_no_graph_failures": len(fold_failures) == 0,
        "retraction_table_shape_is_52_by_5": tuple(retraction_table.shape)
        == (52, len(RETRACTION_COLUMNS)),
        "core_retraction_obstruction_count_is_9": len(core_obstructions) == 9,
        "core_retraction_obstruction_nodes_are_expected": [
            row["frontier_node_id"] for row in core_obstructions
        ]
        == [7, 9, 12, 14, 16, 27, 29, 31, 50],
        "full_rewrite_complex_fold_count_is_6": len(full_fold_steps) == 6,
        "full_rewrite_complex_spine_matches_boundary_spine": sorted(full_spine_node_ids)
        == sorted(core_spine_node_ids),
    }

    witness = {
        "core_node_count": len(core_node_ids),
        "core_edge_count": len(core_edges),
        "oriented_edge_count": len(oriented_edges),
        "orientation_reason_histogram": orientation_reason_hist,
        "poincare_flow_histogram": poincare_flow_hist,
        "directed_acyclic": is_acyclic,
        "directed_cycle_count": chamber_spine["summary"]["directed_cycle_count"],
        "potential_topological_order": potential_topological_order,
        "source_node_ids": path_summary["source_node_ids"],
        "sink_node_ids": path_summary["sink_node_ids"],
        "source_sink_path_count": path_summary["source_sink_path_count"],
        "source_sink_path_length_histogram": path_summary[
            "source_sink_path_length_histogram"
        ],
        "all_directed_path_count": path_summary["all_directed_path_count"],
        "all_directed_path_length_histogram": path_summary[
            "all_directed_path_length_histogram"
        ],
        "longest_source_sink_path_length": path_summary["longest_source_sink_path_length"],
        "longest_source_sink_path": path_summary["longest_source_sink_path"],
        "transitive_reduction_edge_count": len(reduction_edges),
        "undirected_cycle_rank": chamber_spine["summary"]["undirected_cycle_rank"],
        "maximal_chamber_count": chamber_summary["maximal_chamber_count"],
        "maximal_chamber_size_histogram": chamber_summary[
            "maximal_chamber_size_histogram"
        ],
        "triangle_count": chamber_summary["triangle_count"],
        "cyclic_directed_triangle_count": chamber_summary["cyclic_directed_triangle_count"],
        "clique_complex_euler_characteristic": chamber_summary[
            "clique_complex_euler_characteristic"
        ],
        "largest_chamber_node_ids": chamber_summary["largest_chamber_node_ids"],
        "boundary_band_node_count": len(boundary_band_node_ids),
        "boundary_band_fold_count": len(fold_steps),
        "boundary_band_fold_steps": [
            [int(row["removed_node_id"]), int(row["dominator_node_id"])] for row in fold_steps
        ],
        "spine_node_count": len(core_spine_node_ids),
        "spine_node_ids": core_spine_node_ids,
        "spine_edge_count": spine_summary["edge_count"],
        "spine_diameter": spine_summary["diameter"],
        "spine_gromov_delta": spine_summary["gromov_delta"]["delta"],
        "spine_gromov_delta_twice": spine_summary["gromov_delta"]["delta_twice"],
        "spine_gromov_delta_witness_nodes": spine_summary["gromov_delta"]["witness_nodes"],
        "spine_degree_histogram": chamber_spine["summary"]["spine_degree_histogram"],
        "fold_retraction_failure_count": len(fold_failures),
        "residual_dominated_pair_count": len(residual_pairs),
        "core_retraction_obstruction_count": len(core_obstructions),
        "core_retraction_obstruction_node_ids": [
            row["frontier_node_id"] for row in core_obstructions
        ],
        "full_rewrite_complex_fold_count": len(full_fold_steps),
        "full_rewrite_complex_spine_matches_boundary_spine": sorted(full_spine_node_ids)
        == sorted(core_spine_node_ids),
        "chamber_node_potential_table_sha256": sha_array(chamber_node_potential_table),
        "oriented_edge_table_sha256": sha_array(oriented_edge_table),
        "directed_adjacency_sha256": sha_array(directed_adjacency),
        "transitive_reduction_table_sha256": sha_array(reduction_edge_table),
        "transitive_reduction_adjacency_sha256": sha_array(reduction_adjacency),
        "maximal_chamber_table_sha256": sha_array(chamber_table),
        "fold_table_sha256": sha_array(fold_table),
        "full_fold_table_sha256": sha_array(full_fold_table),
        "retraction_table_sha256": sha_array(retraction_table),
        "spine_adjacency_sha256": sha_array(spine_adjacency),
        "spine_distances_sha256": sha_array(spine_distances),
    }

    certificate = {
        "schema": "c985.d20_chamber_spine_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_CHAMBER_SPINE_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 31 preserved-core edges have a deterministic signature/Poincare orientation",
            "the oriented core is acyclic with sources 10 and 43 and sink 44",
            "the undirected core has 10 maximal clique chambers and cycle rank 20",
            "the 52-node boundary band folds through two dominated vertices to a 50-node hyperbolic spine",
            "the boundary band does not retract directly onto the 12-node core under a graph retraction fixing the core",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_chamber_spine@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The preserved 12-node d20 core carries a deterministic acyclic "
            "signature/Poincare chamber orientation, and its 52-node finite "
            "boundary band folds to a certified 50-node hyperbolic spine while "
            "not retracting directly onto the 12-node core."
        ),
        "stage_protocol": {
            "draft": "orient the preserved-core graph by signature ascent and Poincare tie-flow",
            "witness": "materialize oriented edges, chamber cliques, directed paths, dominated folds, and spine retraction tables",
            "coherence": "check acyclicity, sources/sinks, chamber counts, path counts, fold dominance, retraction failures, and spine hyperbolicity",
            "closure": "certify the chamber orientation and finite boundary-band spine",
            "emit": "emit chamber-spine JSON/CSV/NPZ, certificate, report, verifier command, and next target",
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
            "preserved_core_report": input_entry(
                PRESERVED_CORE_REPORT,
                {
                    "status": preserved_report.get("status"),
                    "certificate_sha256": preserved_report.get("certificate_sha256"),
                },
            ),
            "preserved_core": input_entry(PRESERVED_CORE_JSON),
            "preserved_core_tables": input_entry(PRESERVED_CORE_TABLES),
            "preserved_core_certificate": input_entry(PRESERVED_CORE_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "chamber_spine": relpath(OUT_DIR / "chamber_spine.json"),
            "oriented_core_edges_csv": relpath(OUT_DIR / "oriented_core_edges.csv"),
            "transitive_reduction_edges_csv": relpath(OUT_DIR / "transitive_reduction_edges.csv"),
            "maximal_chambers_csv": relpath(OUT_DIR / "maximal_chambers.csv"),
            "spine_folds_csv": relpath(OUT_DIR / "spine_folds.csv"),
            "spine_retraction_csv": relpath(OUT_DIR / "spine_retraction.csv"),
            "chamber_spine_tables": relpath(OUT_DIR / "chamber_spine_tables.npz"),
            "chamber_spine_certificate": relpath(OUT_DIR / "chamber_spine_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "signature/Poincare orientation for all 31 preserved-core edges",
                "directed acyclicity, source/sink nodes, path counts, and transitive reduction",
                "maximal clique chambers and directed triangle behavior in the preserved core",
                "dominated-vertex fold of the 52-node boundary band to a 50-node spine",
                "spine diameter, exact Gromov-delta witness, and failure of direct core retraction",
            ],
            "does_not_certify_because_not_required": [
                "a continuous topological deformation retract",
                "an infinite visual boundary or asymptotic Gromov boundary",
                "arbitrary-length symbolic rewrite confluence",
                "new C985 associator or pentagon data beyond the existing certificate",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the acyclic chamber orientation as a Morse/Reeb quotient: "
            "certify the two source basins flowing to sink 44, the basin boundary "
            "inside the 50-node spine, and the induced interval category of "
            "directed source-sink paths."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_chamber_spine_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified rewrite-complex and preserved-core artifacts",
            "orient every preserved-core edge by the signature/Poincare potential",
            "check directed acyclicity, source/sink nodes, directed path counts, and maximal chamber cliques",
            "fold dominated boundary-band vertices and verify the graph retraction to the 50-node spine",
            "check source hashes and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "chamber_spine": chamber_spine,
        "oriented_core_edges_csv": csv_text(ORIENTED_EDGE_COLUMNS, oriented_edges),
        "transitive_reduction_edges_csv": csv_text(TRANSITIVE_REDUCTION_COLUMNS, reduction_edges),
        "maximal_chambers_csv": csv_text(MAXIMAL_CHAMBER_COLUMNS, chamber_rows),
        "spine_folds_csv": csv_text(FOLD_COLUMNS, fold_steps),
        "spine_retraction_csv": csv_text(RETRACTION_COLUMNS, retraction_rows),
        "chamber_node_potential_table": chamber_node_potential_table,
        "oriented_edge_table": oriented_edge_table,
        "directed_adjacency": directed_adjacency,
        "transitive_reduction_table": reduction_edge_table,
        "transitive_reduction_adjacency": reduction_adjacency,
        "maximal_chamber_table": chamber_table,
        "fold_table": fold_table,
        "full_fold_table": full_fold_table,
        "retraction_table": retraction_table,
        "spine_nodes": np.asarray(core_spine_node_ids, dtype=np.int64),
        "spine_adjacency": spine_adjacency,
        "spine_distances": spine_distances,
        "chamber_spine_certificate": certificate,
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
    write_json(OUT_DIR / "chamber_spine.json", payloads["chamber_spine"])
    (OUT_DIR / "oriented_core_edges.csv").write_text(
        payloads["oriented_core_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "transitive_reduction_edges.csv").write_text(
        payloads["transitive_reduction_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "maximal_chambers.csv").write_text(
        payloads["maximal_chambers_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "spine_folds.csv").write_text(payloads["spine_folds_csv"], encoding="utf-8")
    (OUT_DIR / "spine_retraction.csv").write_text(
        payloads["spine_retraction_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "chamber_spine_tables.npz",
        chamber_node_potential_table=payloads["chamber_node_potential_table"],
        oriented_edge_table=payloads["oriented_edge_table"],
        directed_adjacency=payloads["directed_adjacency"],
        transitive_reduction_table=payloads["transitive_reduction_table"],
        transitive_reduction_adjacency=payloads["transitive_reduction_adjacency"],
        maximal_chamber_table=payloads["maximal_chamber_table"],
        fold_table=payloads["fold_table"],
        full_fold_table=payloads["full_fold_table"],
        retraction_table=payloads["retraction_table"],
        spine_nodes=payloads["spine_nodes"],
        spine_adjacency=payloads["spine_adjacency"],
        spine_distances=payloads["spine_distances"],
    )
    write_json(OUT_DIR / "chamber_spine_certificate.json", payloads["chamber_spine_certificate"])
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
                "oriented_edge_count": witness["oriented_edge_count"],
                "source_node_ids": witness["source_node_ids"],
                "sink_node_ids": witness["sink_node_ids"],
                "maximal_chamber_count": witness["maximal_chamber_count"],
                "spine_node_count": witness["spine_node_count"],
                "spine_gromov_delta": witness["spine_gromov_delta"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
