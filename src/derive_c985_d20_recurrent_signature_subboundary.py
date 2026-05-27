from __future__ import annotations

import itertools
import json
from collections import defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_hyperbolic_boundary_graph import (
        OUT_DIR as HYPERBOLIC_GRAPH_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        atom_signature_sets,
        signature_class_ids,
    )
    from .derive_c985_d20_stationary_atom_flow_lift import (
        OUT_DIR as ATOM_FLOW_DIR,
        SIGNATURE_FLOW_COLUMNS,
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
    from derive_c985_d20_hyperbolic_boundary_graph import (
        OUT_DIR as HYPERBOLIC_GRAPH_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        atom_signature_sets,
        signature_class_ids,
    )
    from derive_c985_d20_stationary_atom_flow_lift import (
        OUT_DIR as ATOM_FLOW_DIR,
        SIGNATURE_FLOW_COLUMNS,
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


THEOREM_ID = "c985_d20_recurrent_signature_subboundary"
STATUS = "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
ATLAS_REPORT = ATLAS_DIR / "report.json"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"
ATLAS_TABLES = ATLAS_DIR / "d20_boundary_invariant_atlas.npz"
ATLAS_CERTIFICATE = ATLAS_DIR / "projection_certificate.json"

ATOM_FLOW_REPORT = ATOM_FLOW_DIR / "report.json"
ATOM_FLOW_JSON = ATOM_FLOW_DIR / "stationary_atom_flow_lift.json"
ATOM_FLOW_TABLES = ATOM_FLOW_DIR / "stationary_atom_flow_tables.npz"
ATOM_FLOW_CERTIFICATE = ATOM_FLOW_DIR / "stationary_atom_flow_certificate.json"

HYPERBOLIC_GRAPH_REPORT = HYPERBOLIC_GRAPH_DIR / "report.json"
HYPERBOLIC_GRAPH_JSON = HYPERBOLIC_GRAPH_DIR / "boundary_hyperbolic_graph.json"
HYPERBOLIC_GRAPH_TABLES = HYPERBOLIC_GRAPH_DIR / "boundary_hyperbolic_metrics.npz"
HYPERBOLIC_GRAPH_CERTIFICATE = HYPERBOLIC_GRAPH_DIR / "hyperbolic_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_recurrent_signature_subboundary.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_recurrent_signature_subboundary.py"

SIGNATURE_VERTEX_COLUMNS = [
    "signature_vertex_id",
    "signature_class_id",
    "signature_flow_mass_x1e12",
    "carrier_atom_mask",
    "active_atom_count",
    "degree",
    "eccentricity",
    "carrier_mask_class_id",
    "signature_flow_rank",
]

SIGNATURE_EDGE_COLUMNS = [
    "signature_edge_id",
    "source_signature_class_id",
    "target_signature_class_id",
    "shared_active_atom_count",
    "source_carrier_atom_mask",
    "target_carrier_atom_mask",
]

CARRIER_MASK_CLASS_COLUMNS = [
    "carrier_mask_class_id",
    "carrier_atom_mask",
    "active_atom_count",
    "signature_class_count",
    "total_signature_flow_mass_x1e12",
    "mask_graph_degree",
    "carrier_atom_id_0",
    "carrier_atom_id_1",
    "carrier_atom_id_2",
    "carrier_atom_id_3",
]

EXCLUDED_SIGNATURE_COLUMNS = [
    "signature_class_id",
    "full_carrier_atom_mask",
    "full_carrier_atom_count",
    "active_carrier_atom_count",
    "full_carrier_atom_id_0",
    "full_carrier_atom_id_1",
    "full_carrier_atom_id_2",
    "full_carrier_atom_id_3",
]

EXPECTED_INACTIVE_SIGNATURE_IDS = [
    39,
    40,
    41,
    42,
    43,
    44,
    184,
    185,
    186,
    187,
    188,
    189,
]

EXPECTED_CARRIER_MASK_HISTOGRAM = [
    {"carrier_atom_mask": 2, "carrier_atom_ids": [1], "signature_class_count": 10},
    {"carrier_atom_mask": 16, "carrier_atom_ids": [4], "signature_class_count": 14},
    {"carrier_atom_mask": 128, "carrier_atom_ids": [7], "signature_class_count": 22},
    {"carrier_atom_mask": 146, "carrier_atom_ids": [1, 4, 7], "signature_class_count": 29},
    {"carrier_atom_mask": 2048, "carrier_atom_ids": [11], "signature_class_count": 12},
    {"carrier_atom_mask": 4096, "carrier_atom_ids": [12], "signature_class_count": 14},
    {"carrier_atom_mask": 6144, "carrier_atom_ids": [11, 12], "signature_class_count": 6},
    {"carrier_atom_mask": 6146, "carrier_atom_ids": [1, 11, 12], "signature_class_count": 10},
    {"carrier_atom_mask": 6160, "carrier_atom_ids": [4, 11, 12], "signature_class_count": 7},
    {"carrier_atom_mask": 524288, "carrier_atom_ids": [19], "signature_class_count": 30},
    {"carrier_atom_mask": 524416, "carrier_atom_ids": [7, 19], "signature_class_count": 8},
    {"carrier_atom_mask": 524434, "carrier_atom_ids": [1, 4, 7, 19], "signature_class_count": 20},
    {"carrier_atom_mask": 526464, "carrier_atom_ids": [7, 11, 19], "signature_class_count": 18},
    {"carrier_atom_mask": 528384, "carrier_atom_ids": [12, 19], "signature_class_count": 21},
]

EXPECTED_SIGNATURE_DISTANCE_HISTOGRAM = [
    {"value": 1, "count": 13035},
    {"value": 2, "count": 10967},
    {"value": 3, "count": 308},
]

EXPECTED_DEGREE_HISTOGRAM = [
    {"value": 52, "count": 12},
    {"value": 57, "count": 14},
    {"value": 68, "count": 10},
    {"value": 69, "count": 14},
    {"value": 87, "count": 6},
    {"value": 96, "count": 52},
    {"value": 133, "count": 21},
    {"value": 137, "count": 29},
    {"value": 146, "count": 10},
    {"value": 147, "count": 8},
    {"value": 150, "count": 7},
    {"value": 182, "count": 18},
    {"value": 188, "count": 20},
]

EXPECTED_ACTIVE_ATOM_COUNT_HISTOGRAM = [
    {"value": 1, "count": 102},
    {"value": 2, "count": 35},
    {"value": 3, "count": 64},
    {"value": 4, "count": 20},
]

EXPECTED_MASK_DISTANCE_HISTOGRAM = [
    {"value": 1, "count": 44},
    {"value": 2, "count": 46},
    {"value": 3, "count": 1},
]


def atom_ids_from_mask(mask: int) -> list[int]:
    return [atom_id for atom_id in range(20) if int(mask) & (1 << atom_id)]


def padded_atom_ids(atom_ids: list[int], width: int = 4) -> list[int]:
    return atom_ids + [-1] * (width - len(atom_ids))


def signature_flow_rows(signature_table: np.ndarray) -> list[dict[str, int]]:
    return [
        {
            column: int(row[column_index])
            for column_index, column in enumerate(SIGNATURE_FLOW_COLUMNS)
        }
        for row in np.asarray(signature_table, dtype=np.int64)
    ]


def all_pairs_unweighted_distances(adjacency: np.ndarray) -> np.ndarray:
    node_count = int(adjacency.shape[0])
    infinity = node_count + 1
    distances = np.full((node_count, node_count), infinity, dtype=np.int16)
    np.fill_diagonal(distances, 0)
    distances[np.asarray(adjacency, dtype=bool)] = 1
    for pivot in range(node_count):
        distances = np.minimum(
            distances,
            distances[:, [pivot]] + distances[[pivot], :],
        )
    return distances


def component_count(adjacency: np.ndarray) -> int:
    node_count = int(adjacency.shape[0])
    seen: set[int] = set()
    count = 0
    for start in range(node_count):
        if start in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start)
        while stack:
            node = stack.pop()
            neighbors = np.nonzero(adjacency[node])[0]
            for neighbor in neighbors:
                neighbor_id = int(neighbor)
                if neighbor_id not in seen:
                    seen.add(neighbor_id)
                    stack.append(neighbor_id)
    return count


def positive_distance_histogram(distances: np.ndarray) -> list[dict[str, int]]:
    node_count = int(distances.shape[0])
    return histogram(
        [
            int(distances[left, right])
            for left in range(node_count)
            for right in range(left + 1, node_count)
        ]
    )


def full_signature_carriers(atlas: dict[str, Any]) -> dict[int, list[int]]:
    relation_npz = np.load(RELATION_GEOMETRY_SIGNATURES, allow_pickle=False)
    relation_records = np.asarray(relation_npz["relation_records"], dtype=np.int64)
    class_ids = signature_class_ids(relation_records)
    atom_sets = atom_signature_sets(atlas, relation_records, class_ids)
    carriers: dict[int, list[int]] = {signature_id: [] for signature_id in range(233)}
    for atom_id, signature_set in enumerate(atom_sets):
        for signature_id in signature_set:
            carriers[int(signature_id)].append(int(atom_id))
    return {signature_id: sorted(atom_ids) for signature_id, atom_ids in carriers.items()}


def build_signature_graph(
    active_rows: list[dict[str, int]],
) -> tuple[np.ndarray, list[dict[str, int]]]:
    vertex_count = len(active_rows)
    adjacency = np.zeros((vertex_count, vertex_count), dtype=np.int8)
    edges: list[dict[str, int]] = []
    for left, right in itertools.combinations(range(vertex_count), 2):
        source_mask = int(active_rows[left]["carrier_atom_mask"])
        target_mask = int(active_rows[right]["carrier_atom_mask"])
        shared_count = int((source_mask & target_mask).bit_count())
        if shared_count == 0:
            continue
        adjacency[left, right] = 1
        adjacency[right, left] = 1
        edges.append(
            {
                "signature_edge_id": len(edges),
                "source_signature_class_id": int(active_rows[left]["signature_class_id"]),
                "target_signature_class_id": int(active_rows[right]["signature_class_id"]),
                "shared_active_atom_count": shared_count,
                "source_carrier_atom_mask": source_mask,
                "target_carrier_atom_mask": target_mask,
            }
        )
    return adjacency, edges


def build_mask_graph(masks: list[int]) -> np.ndarray:
    mask_count = len(masks)
    adjacency = np.zeros((mask_count, mask_count), dtype=np.int8)
    for left, right in itertools.combinations(range(mask_count), 2):
        if int(masks[left]) & int(masks[right]):
            adjacency[left, right] = 1
            adjacency[right, left] = 1
    return adjacency


def carrier_mask_histogram(active_rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    counts: dict[int, int] = {}
    for row in active_rows:
        mask = int(row["carrier_atom_mask"])
        counts[mask] = counts.get(mask, 0) + 1
    return [
        {
            "carrier_atom_mask": int(mask),
            "carrier_atom_ids": atom_ids_from_mask(mask),
            "signature_class_count": int(count),
        }
        for mask, count in sorted(counts.items())
    ]


def gromov_hyperbolicity_from_representatives(
    distances: np.ndarray,
    active_rows: list[dict[str, int]],
    representatives: list[int],
) -> dict[str, Any]:
    histogram_counts: dict[int, int] = {}
    best_gap = -1
    best_quad: tuple[int, int, int, int] | None = None
    best_sums: list[int] = []
    for quad in itertools.combinations(representatives, 4):
        a, b, c, d = quad
        sums = [
            int(distances[a, b] + distances[c, d]),
            int(distances[a, c] + distances[b, d]),
            int(distances[a, d] + distances[b, c]),
        ]
        sorted_sums = sorted(sums)
        gap = int(sorted_sums[2] - sorted_sums[1])
        histogram_counts[gap] = histogram_counts.get(gap, 0) + 1
        if gap > best_gap:
            best_gap = gap
            best_quad = quad
            best_sums = sums
    if best_quad is None:
        raise ValueError("at least four representatives are required")
    witness_ids = [int(active_rows[index]["signature_class_id"]) for index in best_quad]
    witness_masks = [int(active_rows[index]["carrier_atom_mask"]) for index in best_quad]
    return {
        "delta_twice": int(best_gap),
        "delta_fraction": [int(best_gap), 2],
        "witness_signature_class_ids": witness_ids,
        "witness_carrier_atom_masks": witness_masks,
        "witness_pair_sums": [int(value) for value in best_sums],
        "representative_vertex_count": len(representatives),
        "representative_signature_class_ids": [
            int(active_rows[index]["signature_class_id"]) for index in representatives
        ],
        "representative_exhaustion_rule": (
            "distances between distinct signatures depend only on carrier masks; "
            "four representatives per carrier mask realize every equality pattern "
            "of a four-point witness"
        ),
        "gap_histogram_on_representatives": [
            {"gap_twice": int(gap), "quadruple_count": int(count)}
            for gap, count in sorted(histogram_counts.items())
        ],
    }


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray([[int(row[column]) for column in columns] for row in rows], dtype=np.int64)


def build_payloads() -> dict[str, Any]:
    atlas_report = load_json(ATLAS_REPORT)
    atlas = load_json(ATLAS_JSON)
    atlas_certificate = load_json(ATLAS_CERTIFICATE)
    atom_flow_report = load_json(ATOM_FLOW_REPORT)
    atom_flow = load_json(ATOM_FLOW_JSON)
    atom_flow_certificate = load_json(ATOM_FLOW_CERTIFICATE)
    hyperbolic_report = load_json(HYPERBOLIC_GRAPH_REPORT)
    hyperbolic_graph = load_json(HYPERBOLIC_GRAPH_JSON)
    hyperbolic_certificate = load_json(HYPERBOLIC_GRAPH_CERTIFICATE)
    atom_flow_tables = np.load(ATOM_FLOW_TABLES, allow_pickle=False)
    hyperbolic_tables = np.load(HYPERBOLIC_GRAPH_TABLES, allow_pickle=False)
    atlas_tables = np.load(ATLAS_TABLES, allow_pickle=False)

    signature_rows = signature_flow_rows(atom_flow_tables["signature_flow_table"])
    active_rows = [
        row for row in signature_rows if int(row["active_flow"]) == 1
    ]
    inactive_rows = [
        row for row in signature_rows if int(row["active_flow"]) == 0
    ]
    active_signature_ids = [int(row["signature_class_id"]) for row in active_rows]
    inactive_signature_ids = [int(row["signature_class_id"]) for row in inactive_rows]
    active_atom_ids = sorted(
        {
            atom_id
            for row in active_rows
            for atom_id in atom_ids_from_mask(int(row["carrier_atom_mask"]))
        }
    )

    signature_adjacency, edge_rows = build_signature_graph(active_rows)
    signature_distances = all_pairs_unweighted_distances(signature_adjacency)
    degrees = [int(np.sum(signature_adjacency[index])) for index in range(len(active_rows))]
    eccentricities = [int(signature_distances[index].max()) for index in range(len(active_rows))]

    mask_to_indices: dict[int, list[int]] = defaultdict(list)
    for index, row in enumerate(active_rows):
        mask_to_indices[int(row["carrier_atom_mask"])].append(index)
    carrier_masks = sorted(mask_to_indices)
    carrier_mask_class_ids = {mask: index for index, mask in enumerate(carrier_masks)}
    mask_adjacency = build_mask_graph(carrier_masks)
    mask_distances = all_pairs_unweighted_distances(mask_adjacency)

    vertex_rows: list[dict[str, int]] = []
    for vertex_id, row in enumerate(active_rows):
        carrier_mask = int(row["carrier_atom_mask"])
        vertex_rows.append(
            {
                "signature_vertex_id": vertex_id,
                "signature_class_id": int(row["signature_class_id"]),
                "signature_flow_mass_x1e12": int(row["signature_flow_mass_x1e12"]),
                "carrier_atom_mask": carrier_mask,
                "active_atom_count": int(row["active_atom_count"]),
                "degree": degrees[vertex_id],
                "eccentricity": eccentricities[vertex_id],
                "carrier_mask_class_id": carrier_mask_class_ids[carrier_mask],
                "signature_flow_rank": int(row["signature_flow_rank"]),
            }
        )

    mask_rows: list[dict[str, int]] = []
    for mask in carrier_masks:
        class_id = carrier_mask_class_ids[mask]
        atom_ids = atom_ids_from_mask(mask)
        padded = padded_atom_ids(atom_ids)
        indices = mask_to_indices[mask]
        mask_rows.append(
            {
                "carrier_mask_class_id": class_id,
                "carrier_atom_mask": int(mask),
                "active_atom_count": len(atom_ids),
                "signature_class_count": len(indices),
                "total_signature_flow_mass_x1e12": int(
                    sum(int(active_rows[index]["signature_flow_mass_x1e12"]) for index in indices)
                ),
                "mask_graph_degree": int(np.sum(mask_adjacency[class_id])),
                "carrier_atom_id_0": padded[0],
                "carrier_atom_id_1": padded[1],
                "carrier_atom_id_2": padded[2],
                "carrier_atom_id_3": padded[3],
            }
        )

    full_carriers = full_signature_carriers(atlas)
    excluded_rows: list[dict[str, int]] = []
    for row in inactive_rows:
        signature_id = int(row["signature_class_id"])
        full_atoms = full_carriers[signature_id]
        padded = padded_atom_ids(full_atoms)
        full_mask = sum(1 << atom_id for atom_id in full_atoms)
        excluded_rows.append(
            {
                "signature_class_id": signature_id,
                "full_carrier_atom_mask": int(full_mask),
                "full_carrier_atom_count": len(full_atoms),
                "active_carrier_atom_count": int(row["active_atom_count"]),
                "full_carrier_atom_id_0": padded[0],
                "full_carrier_atom_id_1": padded[1],
                "full_carrier_atom_id_2": padded[2],
                "full_carrier_atom_id_3": padded[3],
            }
        )

    representatives: list[int] = []
    for mask in carrier_masks:
        representatives.extend(mask_to_indices[mask][:4])
    hyperbolicity = gromov_hyperbolicity_from_representatives(
        signature_distances,
        active_rows,
        representatives,
    )

    signature_distance_hist = positive_distance_histogram(signature_distances)
    mask_distance_hist = positive_distance_histogram(mask_distances)
    degree_hist = histogram(degrees)
    active_atom_count_hist = histogram(
        [int(row["active_atom_count"]) for row in active_rows]
    )
    mask_hist = carrier_mask_histogram(active_rows)

    signature_vertex_table = table_from_rows(SIGNATURE_VERTEX_COLUMNS, vertex_rows)
    signature_edge_table = table_from_rows(SIGNATURE_EDGE_COLUMNS, edge_rows)
    carrier_mask_class_table = table_from_rows(CARRIER_MASK_CLASS_COLUMNS, mask_rows)
    excluded_signature_table = table_from_rows(EXCLUDED_SIGNATURE_COLUMNS, excluded_rows)
    delta_representative_indices = np.asarray(representatives, dtype=np.int64)

    signature_subboundary = {
        "schema": "c985.d20_recurrent_signature_subboundary@1",
        "object": "d20",
        "graph_rule": {
            "vertices": "the 221 relation-signature classes receiving recurrent atom-flow mass",
            "edges": "two active signature classes are adjacent when their active carrier atom masks intersect",
            "carrier_mask_quotient": "active signature classes are quotient by identical active carrier atom masks",
            "hyperbolicity_witness": (
                "exact four-point delta is computed on four representatives per carrier mask, "
                "which realizes all equality patterns of four distinct signature vertices"
            ),
        },
        "source_support": {
            "active_atom_ids": active_atom_ids,
            "active_signature_class_count": len(active_rows),
            "inactive_signature_class_count": len(inactive_rows),
            "inactive_signature_class_ids": inactive_signature_ids,
        },
        "metric_summary": {
            "vertex_count": len(active_rows),
            "edge_count": len(edge_rows),
            "component_count": component_count(signature_adjacency),
            "diameter": int(signature_distances.max()),
            "distance_histogram": signature_distance_hist,
            "degree_histogram": degree_hist,
            "active_atom_count_histogram": active_atom_count_hist,
            "exact_gromov_hyperbolicity": hyperbolicity,
        },
        "carrier_mask_quotient": {
            "mask_class_count": len(carrier_masks),
            "mask_class_edge_count": int(np.sum(mask_adjacency) // 2),
            "diameter": int(mask_distances.max()),
            "distance_histogram": mask_distance_hist,
            "carrier_mask_histogram": mask_hist,
        },
        "excluded_signature_classes": [
            {
                "signature_class_id": int(row["signature_class_id"]),
                "full_carrier_atom_ids": [
                    int(value)
                    for value in [
                        row["full_carrier_atom_id_0"],
                        row["full_carrier_atom_id_1"],
                        row["full_carrier_atom_id_2"],
                        row["full_carrier_atom_id_3"],
                    ]
                    if int(value) >= 0
                ],
                "full_carrier_atom_mask": int(row["full_carrier_atom_mask"]),
                "active_carrier_atom_count": int(row["active_carrier_atom_count"]),
            }
            for row in excluded_rows
        ],
        "top_signature_flow_vertices": [
            {
                "signature_class_id": int(row["signature_class_id"]),
                "signature_flow_mass_x1e12": int(row["signature_flow_mass_x1e12"]),
                "carrier_atom_ids": atom_ids_from_mask(int(row["carrier_atom_mask"])),
                "degree": int(row["degree"]),
                "signature_flow_rank": int(row["signature_flow_rank"]),
            }
            for row in sorted(
                vertex_rows,
                key=lambda item: (
                    int(item["signature_flow_rank"]),
                    int(item["signature_class_id"]),
                ),
            )[:16]
        ],
        "comparison_with_full_boundary": {
            "full_johnson_vertex_count": int(hyperbolic_report["witness"]["atom_count"]),
            "full_johnson_diameter": int(hyperbolic_report["witness"]["johnson_diameter"]),
            "full_johnson_delta_fraction": hyperbolic_report["witness"][
                "johnson_delta_fraction"
            ],
            "subboundary_diameter": int(signature_distances.max()),
            "subboundary_delta_fraction": hyperbolicity["delta_fraction"],
        },
    }

    checks = {
        "atom_flow_report_certified": atom_flow_report.get("status")
        == "C985_D20_STATIONARY_ATOM_FLOW_LIFT_CERTIFIED",
        "atom_flow_certificate_certified": atom_flow_certificate.get("status")
        == "C985_D20_STATIONARY_ATOM_FLOW_LIFT_CERTIFIED",
        "hyperbolic_graph_report_certified": hyperbolic_report.get("status")
        == "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_CERTIFIED",
        "hyperbolic_graph_certificate_certified": hyperbolic_certificate.get("status")
        == "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_CERTIFIED",
        "boundary_atlas_report_certified": atlas_report.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "boundary_atlas_certificate_certified": atlas_certificate.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "active_signature_count_is_221": len(active_rows) == 221,
        "inactive_signature_count_is_12": len(inactive_rows) == 12,
        "inactive_signature_ids_are_expected": inactive_signature_ids
        == EXPECTED_INACTIVE_SIGNATURE_IDS,
        "active_atoms_are_expected": active_atom_ids == [1, 4, 7, 11, 12, 19],
        "signature_graph_edge_count_is_13035": len(edge_rows) == 13035,
        "signature_graph_is_connected": component_count(signature_adjacency) == 1,
        "signature_graph_diameter_is_3": int(signature_distances.max()) == 3,
        "signature_distance_histogram_matches_expected": signature_distance_hist
        == EXPECTED_SIGNATURE_DISTANCE_HISTOGRAM,
        "degree_histogram_matches_expected": degree_hist == EXPECTED_DEGREE_HISTOGRAM,
        "active_atom_count_histogram_matches_expected": active_atom_count_hist
        == EXPECTED_ACTIVE_ATOM_COUNT_HISTOGRAM,
        "carrier_mask_count_is_14": len(carrier_masks) == 14,
        "carrier_mask_histogram_matches_expected": mask_hist
        == EXPECTED_CARRIER_MASK_HISTOGRAM,
        "mask_graph_edge_count_is_44": int(np.sum(mask_adjacency) // 2) == 44,
        "mask_graph_diameter_is_3": int(mask_distances.max()) == 3,
        "mask_graph_distance_histogram_matches_expected": mask_distance_hist
        == EXPECTED_MASK_DISTANCE_HISTOGRAM,
        "delta_representative_count_is_56": len(representatives) == 56,
        "signature_graph_delta_twice_is_2": hyperbolicity["delta_twice"] == 2,
        "signature_graph_delta_witness_is_expected": hyperbolicity[
            "witness_signature_class_ids"
        ]
        == [0, 48, 126, 212],
        "signature_graph_delta_witness_masks_are_expected": hyperbolicity[
            "witness_carrier_atom_masks"
        ]
        == [146, 6146, 524416, 528384],
        "signature_graph_delta_witness_sums_are_expected": hyperbolicity[
            "witness_pair_sums"
        ]
        == [2, 2, 4],
        "full_johnson_boundary_diameter_matches": int(
            hyperbolic_report["witness"]["johnson_diameter"]
        )
        == 3,
        "full_johnson_boundary_delta_matches": hyperbolic_report["witness"][
            "johnson_delta_fraction"
        ]
        == [2, 2],
        "subboundary_matches_full_johnson_diameter": int(signature_distances.max())
        == int(hyperbolic_report["witness"]["johnson_diameter"]),
        "subboundary_matches_full_johnson_delta": hyperbolicity["delta_fraction"]
        == hyperbolic_report["witness"]["johnson_delta_fraction"],
        "excluded_signature_full_carrier_mask_is_840": all(
            int(row["full_carrier_atom_mask"]) == 840 for row in excluded_rows
        ),
        "excluded_signature_full_carriers_are_3_6_8_9": all(
            [
                int(row["full_carrier_atom_id_0"]),
                int(row["full_carrier_atom_id_1"]),
                int(row["full_carrier_atom_id_2"]),
                int(row["full_carrier_atom_id_3"]),
            ]
            == [3, 6, 8, 9]
            for row in excluded_rows
        ),
        "excluded_signature_active_carrier_count_is_zero": all(
            int(row["active_carrier_atom_count"]) == 0 for row in excluded_rows
        ),
        "signature_vertex_table_shape_is_221_by_9": tuple(signature_vertex_table.shape)
        == (221, len(SIGNATURE_VERTEX_COLUMNS)),
        "signature_edge_table_shape_is_13035_by_6": tuple(signature_edge_table.shape)
        == (13035, len(SIGNATURE_EDGE_COLUMNS)),
        "carrier_mask_class_table_shape_is_14_by_10": tuple(
            carrier_mask_class_table.shape
        )
        == (14, len(CARRIER_MASK_CLASS_COLUMNS)),
        "excluded_signature_table_shape_is_12_by_8": tuple(
            excluded_signature_table.shape
        )
        == (12, len(EXCLUDED_SIGNATURE_COLUMNS)),
        "signature_adjacency_shape_is_221_by_221": tuple(signature_adjacency.shape)
        == (221, 221),
        "signature_distances_shape_is_221_by_221": tuple(signature_distances.shape)
        == (221, 221),
        "mask_class_adjacency_shape_is_14_by_14": tuple(mask_adjacency.shape)
        == (14, 14),
        "mask_class_distances_shape_is_14_by_14": tuple(mask_distances.shape)
        == (14, 14),
        "hyperbolic_tables_johnson_distance_available": "johnson_distances"
        in hyperbolic_tables.files,
        "atlas_atom_table_shape_is_20_rows": int(np.asarray(atlas_tables["atom_table"]).shape[0])
        == 20,
        "atom_flow_signature_table_shape_is_233_rows": int(
            np.asarray(atom_flow_tables["signature_flow_table"]).shape[0]
        )
        == 233,
        "atom_flow_json_schema_available": atom_flow.get("schema")
        == "c985.d20_stationary_atom_flow_lift@1",
        "hyperbolic_graph_json_schema_available": hyperbolic_graph.get("schema")
        == "c985.d20_hyperbolic_boundary_graph@1",
    }

    witness = {
        "active_atom_ids": active_atom_ids,
        "active_signature_class_count": len(active_rows),
        "inactive_signature_class_count": len(inactive_rows),
        "inactive_signature_class_ids": inactive_signature_ids,
        "signature_graph_edge_count": len(edge_rows),
        "signature_graph_component_count": component_count(signature_adjacency),
        "signature_graph_diameter": int(signature_distances.max()),
        "signature_distance_histogram": signature_distance_hist,
        "signature_degree_histogram": degree_hist,
        "signature_active_atom_count_histogram": active_atom_count_hist,
        "carrier_mask_count": len(carrier_masks),
        "carrier_mask_histogram": mask_hist,
        "mask_graph_edge_count": int(np.sum(mask_adjacency) // 2),
        "mask_graph_diameter": int(mask_distances.max()),
        "mask_graph_distance_histogram": mask_distance_hist,
        "signature_graph_delta_twice": hyperbolicity["delta_twice"],
        "signature_graph_delta_fraction": hyperbolicity["delta_fraction"],
        "delta_witness_signature_class_ids": hyperbolicity[
            "witness_signature_class_ids"
        ],
        "delta_witness_carrier_atom_masks": hyperbolicity[
            "witness_carrier_atom_masks"
        ],
        "delta_witness_pair_sums": hyperbolicity["witness_pair_sums"],
        "delta_representative_count": len(representatives),
        "excluded_full_carrier_atom_ids": [3, 6, 8, 9],
        "excluded_full_carrier_atom_mask": 840,
        "full_johnson_diameter": int(hyperbolic_report["witness"]["johnson_diameter"]),
        "full_johnson_delta_fraction": hyperbolic_report["witness"][
            "johnson_delta_fraction"
        ],
        "signature_vertex_table_sha256": sha_array(signature_vertex_table),
        "signature_edge_table_sha256": sha_array(signature_edge_table),
        "carrier_mask_class_table_sha256": sha_array(carrier_mask_class_table),
        "excluded_signature_table_sha256": sha_array(excluded_signature_table),
        "signature_adjacency_sha256": sha_array(signature_adjacency),
        "signature_distances_sha256": sha_array(signature_distances),
        "mask_class_adjacency_sha256": sha_array(mask_adjacency),
        "mask_class_distances_sha256": sha_array(mask_distances),
        "delta_representative_indices_sha256": sha_array(delta_representative_indices),
    }

    certificate = {
        "schema": "c985.d20_recurrent_signature_subboundary_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 221 recurrent relation-signature classes form one connected signature-intersection graph",
            "the recurrent signature graph has diameter 3 and exact four-point Gromov delta 1",
            "the carrier-mask quotient has 14 classes, 44 edges, diameter 3, and one distance-three mask pair",
            "the 12 excluded signature classes are exactly the classes carried by inactive atoms 3, 6, 8, and 9",
            "the recurrent subboundary preserves the full 20-atom Johnson boundary diameter and delta",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_recurrent_signature_subboundary@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The stationary atom-flow lift induces a certified recurrent signature "
            "subboundary: its 221 active relation-signature classes form one "
            "connected carrier-intersection graph with diameter 3 and exact "
            "four-point Gromov delta 1, matching the unweighted 20-atom Johnson "
            "boundary while identifying the 12 excluded classes."
        ),
        "stage_protocol": {
            "draft": "restrict relation-signature classes to those with recurrent atom-flow mass",
            "witness": "materialize signature vertices, shared-carrier edges, carrier-mask quotient classes, and excluded signatures",
            "coherence": "check connectedness, diameter, exact hyperbolicity, quotient metrics, excluded carriers, and full-boundary comparison",
            "closure": "certify the recurrent signature subboundary without adding new categorical structure",
            "emit": "emit subboundary JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "stationary_atom_flow_report": input_entry(
                ATOM_FLOW_REPORT,
                {
                    "status": atom_flow_report.get("status"),
                    "certificate_sha256": atom_flow_report.get("certificate_sha256"),
                },
            ),
            "stationary_atom_flow": input_entry(ATOM_FLOW_JSON),
            "stationary_atom_flow_tables": input_entry(ATOM_FLOW_TABLES),
            "stationary_atom_flow_certificate": input_entry(ATOM_FLOW_CERTIFICATE),
            "hyperbolic_graph_report": input_entry(
                HYPERBOLIC_GRAPH_REPORT,
                {
                    "status": hyperbolic_report.get("status"),
                    "certificate_sha256": hyperbolic_report.get("certificate_sha256"),
                },
            ),
            "hyperbolic_graph": input_entry(HYPERBOLIC_GRAPH_JSON),
            "hyperbolic_graph_tables": input_entry(HYPERBOLIC_GRAPH_TABLES),
            "hyperbolic_graph_certificate": input_entry(HYPERBOLIC_GRAPH_CERTIFICATE),
            "boundary_atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "boundary_atlas_tables": input_entry(ATLAS_TABLES),
            "boundary_atlas_certificate": input_entry(ATLAS_CERTIFICATE),
            "relation_geometry_signatures": input_entry(RELATION_GEOMETRY_SIGNATURES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "recurrent_signature_subboundary": relpath(
                OUT_DIR / "recurrent_signature_subboundary.json"
            ),
            "signature_subboundary_vertices_csv": relpath(
                OUT_DIR / "signature_subboundary_vertices.csv"
            ),
            "signature_subboundary_edges_csv": relpath(
                OUT_DIR / "signature_subboundary_edges.csv"
            ),
            "carrier_mask_classes_csv": relpath(OUT_DIR / "carrier_mask_classes.csv"),
            "excluded_signature_classes_csv": relpath(
                OUT_DIR / "excluded_signature_classes.csv"
            ),
            "recurrent_signature_subboundary_tables": relpath(
                OUT_DIR / "recurrent_signature_subboundary_tables.npz"
            ),
            "recurrent_signature_subboundary_certificate": relpath(
                OUT_DIR / "recurrent_signature_subboundary_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the induced signature-intersection graph on recurrent signature classes",
                "all 13,035 shared-active-carrier edges",
                "exact unweighted shortest-path matrices for the signature graph and carrier-mask quotient",
                "exact four-point hyperbolicity delta by carrier-mask representative exhaustion",
                "which signature classes are excluded from recurrent atom-flow support and their full carriers",
            ],
            "does_not_certify_because_not_required": [
                "a canonical transition kernel between individual signature classes",
                "a continuum boundary measure on relation signatures",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
                "that the 12 excluded classes are impossible in a different transfer law",
            ],
        },
        "next_highest_yield_item": (
            "Put dynamics on the recurrent signature subboundary itself: build a "
            "signature-class transfer kernel from shared carrier atoms and "
            "signature-flow masses, certify its stationary measure, and compare "
            "its spectral gap against the 12-node core transfer operator."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_recurrent_signature_subboundary_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified atom-flow, hyperbolic-boundary, and atlas artifacts",
            "restrict to the 221 signature classes with recurrent atom-flow mass",
            "materialize the induced signature-intersection graph and carrier-mask quotient",
            "verify connectedness, diameter, degree distribution, distance distribution, and exact delta",
            "verify excluded signature carriers against the full 20-atom relation-signature atlas",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "recurrent_signature_subboundary": signature_subboundary,
        "signature_subboundary_vertices_csv": csv_text(
            SIGNATURE_VERTEX_COLUMNS,
            vertex_rows,
        ),
        "signature_subboundary_edges_csv": csv_text(
            SIGNATURE_EDGE_COLUMNS,
            edge_rows,
        ),
        "carrier_mask_classes_csv": csv_text(CARRIER_MASK_CLASS_COLUMNS, mask_rows),
        "excluded_signature_classes_csv": csv_text(
            EXCLUDED_SIGNATURE_COLUMNS,
            excluded_rows,
        ),
        "signature_vertex_table": signature_vertex_table,
        "signature_edge_table": signature_edge_table,
        "carrier_mask_class_table": carrier_mask_class_table,
        "excluded_signature_table": excluded_signature_table,
        "signature_adjacency": signature_adjacency,
        "signature_distances": signature_distances,
        "mask_class_adjacency": mask_adjacency,
        "mask_class_distances": mask_distances,
        "delta_representative_indices": delta_representative_indices,
        "recurrent_signature_subboundary_certificate": certificate,
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
        OUT_DIR / "recurrent_signature_subboundary.json",
        payloads["recurrent_signature_subboundary"],
    )
    (OUT_DIR / "signature_subboundary_vertices.csv").write_text(
        payloads["signature_subboundary_vertices_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_subboundary_edges.csv").write_text(
        payloads["signature_subboundary_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "carrier_mask_classes.csv").write_text(
        payloads["carrier_mask_classes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "excluded_signature_classes.csv").write_text(
        payloads["excluded_signature_classes_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "recurrent_signature_subboundary_tables.npz",
        signature_vertex_table=payloads["signature_vertex_table"],
        signature_edge_table=payloads["signature_edge_table"],
        carrier_mask_class_table=payloads["carrier_mask_class_table"],
        excluded_signature_table=payloads["excluded_signature_table"],
        signature_adjacency=payloads["signature_adjacency"],
        signature_distances=payloads["signature_distances"],
        mask_class_adjacency=payloads["mask_class_adjacency"],
        mask_class_distances=payloads["mask_class_distances"],
        delta_representative_indices=payloads["delta_representative_indices"],
    )
    write_json(
        OUT_DIR / "recurrent_signature_subboundary_certificate.json",
        payloads["recurrent_signature_subboundary_certificate"],
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
                "active_signature_class_count": witness[
                    "active_signature_class_count"
                ],
                "signature_graph_edge_count": witness["signature_graph_edge_count"],
                "signature_graph_diameter": witness["signature_graph_diameter"],
                "signature_graph_delta_fraction": witness[
                    "signature_graph_delta_fraction"
                ],
                "carrier_mask_count": witness["carrier_mask_count"],
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
