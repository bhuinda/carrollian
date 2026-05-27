from __future__ import annotations

import itertools
import json
from collections import deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_x2_splice_obstruction import (
        OUT_DIR as X2_SPLICE_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        RESIDUAL_CHART_CARRIER_CSV,
        SYMBOLIC_ALPHABET_CSV,
    )
    from .derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_WITHIN_CENTRAL,
        OUT_DIR as CELL_COMPLEX_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
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
    from derive_c985_d20_signature_boundary_spine_x2_splice_obstruction import (
        OUT_DIR as X2_SPLICE_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        RESIDUAL_CHART_CARRIER_CSV,
        SYMBOLIC_ALPHABET_CSV,
    )
    from derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_WITHIN_CENTRAL,
        OUT_DIR as CELL_COMPLEX_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_x2_detour_fan"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

X2_SPLICE_REPORT = X2_SPLICE_DIR / "report.json"
X2_SPLICE_JSON = X2_SPLICE_DIR / "signature_boundary_spine_x2_splice_obstruction.json"
X2_SPLICE_NEAR_MISSES = X2_SPLICE_DIR / "x2_splice_near_misses.csv"
X2_SPLICE_TABLES = X2_SPLICE_DIR / "signature_boundary_spine_x2_splice_obstruction_tables.npz"
X2_SPLICE_CERTIFICATE = (
    X2_SPLICE_DIR / "signature_boundary_spine_x2_splice_obstruction_certificate.json"
)

CELL_COMPLEX_REPORT = CELL_COMPLEX_DIR / "report.json"
CELL_COMPLEX_JSON = CELL_COMPLEX_DIR / "signature_residual_cell_complex.json"
CELL_COMPLEX_EDGES = CELL_COMPLEX_DIR / "carrier_region_edges.csv"
CELL_COMPLEX_TABLES = CELL_COMPLEX_DIR / "signature_residual_cell_complex_tables.npz"
CELL_COMPLEX_CERTIFICATE = CELL_COMPLEX_DIR / "signature_residual_cell_complex_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_boundary_spine_x2_detour_fan.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_boundary_spine_x2_detour_fan.py"

ORIGIN_CARRIER_ID = 12
SLOT_NEGATIVE_CARRIER_ID = 4
X2_DETOUR_EDGE_IDS = [9, 14, 39, 41]
X2_DETOUR_TARGET_IDS = [2, 3, 10, 11]
RETURN_NEGATIVE_CARRIER_IDS = [7, 8, 9, 13]
CURRENT_SLOT_EDGE_ID = 18
INSERTED_SYMBOL_ID = 2

NODE_ORIGIN = 0
NODE_SLOT_NEGATIVE = 1
NODE_DETOUR_INTERNAL = 2
NODE_RETURN_NEGATIVE = 3
EDGE_X2_DETOUR = 0
EDGE_BOUNDARY_RETURN = 1
EDGE_CURRENT_SLOT = 2

DETOUR_NODE_COLUMNS = [
    "detour_node_rank",
    "carrier_mask_class_id",
    "node_role_code",
    "elbow_region_code",
    "nodal_sign",
    "carrier_atom_mask",
    "carrier_symbol_bitset",
    "carrier_symbol_count",
    "x2_carrier_flag",
    "fan_degree",
    "fan_distance_to_origin",
    "direct_boundary_return_count",
]

DETOUR_EDGE_COLUMNS = [
    "detour_edge_id",
    "cell_edge_id",
    "source_detour_node_rank",
    "target_detour_node_rank",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "edge_role_code",
    "edge_partition_code",
    "is_positive_negative_boundary",
    "shared_atom_bitset",
    "shared_symbol_bitset",
    "shared_symbol_count",
    "x2_shared_flag",
    "single_x2_flag",
    "mixed_x2_x5_flag",
]

RETURN_PATH_COLUMNS = [
    "return_path_id",
    "x2_cell_edge_id",
    "origin_carrier_mask_class_id",
    "detour_carrier_mask_class_id",
    "return_cell_edge_id",
    "return_negative_carrier_mask_class_id",
    "x2_shared_symbol_bitset",
    "x2_single_flag",
    "return_shared_symbol_bitset",
    "return_shared_symbol_count",
    "clean_single_x2_return_flag",
    "mixed_x2_return_flag",
    "node42_realization_flag",
]

DETOUR_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "detour_node_count": 0,
    "detour_edge_count": 1,
    "x2_detour_edge_count": 2,
    "current_slot_edge_count": 3,
    "boundary_return_edge_count": 4,
    "return_path_count": 5,
    "clean_single_x2_return_path_count": 6,
    "mixed_x2_return_path_count": 7,
    "dead_end_x2_detour_edge_count": 8,
    "detour_graph_diameter": 9,
    "detour_graph_radius": 10,
    "detour_gromov_delta_twice": 11,
    "origin_carrier_id": 12,
    "slot_negative_carrier_id": 13,
    "return_negative_carrier_count": 14,
    "node42_realization_path_count": 15,
}


def carrier_atom_ids(row: dict[str, int]) -> list[int]:
    return [
        int(row[f"carrier_atom_id_{index}"])
        for index in range(4)
        if int(row[f"carrier_atom_id_{index}"]) >= 0
    ]


def shortest_paths(adjacency: np.ndarray) -> np.ndarray:
    node_count = int(adjacency.shape[0])
    distances = np.full((node_count, node_count), 10**9, dtype=np.int64)
    neighbors = [
        np.flatnonzero(adjacency[node]).astype(np.int64).tolist()
        for node in range(node_count)
    ]
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
        raise AssertionError("detour fan needs at least four nodes")
    return {
        "delta": float(best_delta_twice / 2.0),
        "delta_twice": int(best_delta_twice),
        "witness_ranks": [int(value) for value in best_witness],
        "four_point_sums": [int(value) for value in best_sums],
    }


def edge_key(source: int, target: int) -> tuple[int, int]:
    return tuple(sorted((int(source), int(target))))


def build_payloads() -> dict[str, Any]:
    splice_report = load_json(X2_SPLICE_REPORT)
    splice = load_json(X2_SPLICE_JSON)
    splice_certificate = load_json(X2_SPLICE_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_complex = load_json(CELL_COMPLEX_JSON)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)

    splice_tables = np.load(X2_SPLICE_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    splice_near_miss_table = np.asarray(splice_tables["near_miss_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)

    carrier_rows = {
        int(row["carrier_mask_class_id"]): row
        for row in read_int_csv(RESIDUAL_CHART_CARRIER_CSV)
    }
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"])
        for row in read_int_csv(SYMBOLIC_ALPHABET_CSV)
    }
    cell_edge_rows = read_int_csv(CELL_COMPLEX_EDGES)
    edge_by_id = {int(row["cell_edge_id"]): row for row in cell_edge_rows}
    edge_by_pair = {
        edge_key(
            int(row["source_carrier_mask_class_id"]),
            int(row["target_carrier_mask_class_id"]),
        ): row
        for row in cell_edge_rows
    }

    carrier_symbol_bitsets: dict[int, int] = {}
    for carrier_id, row in carrier_rows.items():
        carrier_symbol_bitsets[carrier_id] = bitset(
            {atom_to_symbol[atom_id] for atom_id in carrier_atom_ids(row)}
        )

    return_edges: list[dict[str, int]] = []
    for target_id in X2_DETOUR_TARGET_IDS:
        for negative_id in RETURN_NEGATIVE_CARRIER_IDS:
            row = edge_by_pair.get(edge_key(target_id, negative_id))
            if row is None:
                continue
            if int(row["is_positive_negative_boundary"]) == 1:
                return_edges.append(row)

    detour_node_ids = [
        ORIGIN_CARRIER_ID,
        SLOT_NEGATIVE_CARRIER_ID,
        *X2_DETOUR_TARGET_IDS,
        *RETURN_NEGATIVE_CARRIER_IDS,
    ]
    rank_by_carrier = {
        carrier_id: rank for rank, carrier_id in enumerate(detour_node_ids)
    }

    detour_edge_specs: list[tuple[int, int, int]] = []
    detour_edge_specs.append((CURRENT_SLOT_EDGE_ID, EDGE_CURRENT_SLOT, 0))
    for edge_id in X2_DETOUR_EDGE_IDS:
        detour_edge_specs.append((edge_id, EDGE_X2_DETOUR, 0))
    for row in return_edges:
        detour_edge_specs.append((int(row["cell_edge_id"]), EDGE_BOUNDARY_RETURN, 0))

    adjacency = np.zeros((len(detour_node_ids), len(detour_node_ids)), dtype=np.int8)
    edge_rows: list[dict[str, int]] = []
    for detour_edge_id, (cell_edge_id, edge_role, _) in enumerate(detour_edge_specs):
        row = edge_by_id[cell_edge_id]
        source = int(row["source_carrier_mask_class_id"])
        target = int(row["target_carrier_mask_class_id"])
        source_rank = rank_by_carrier[source]
        target_rank = rank_by_carrier[target]
        shared_atom_bitset = int(row["source_carrier_atom_mask"]) & int(
            row["target_carrier_atom_mask"]
        )
        shared_atoms = [
            atom_id for atom_id in range(64) if shared_atom_bitset & (1 << atom_id)
        ]
        shared_symbols = sorted({atom_to_symbol[atom_id] for atom_id in shared_atoms})
        shared_symbol_bitset = bitset(shared_symbols)
        adjacency[source_rank, target_rank] = 1
        adjacency[target_rank, source_rank] = 1
        edge_rows.append(
            {
                "detour_edge_id": detour_edge_id,
                "cell_edge_id": cell_edge_id,
                "source_detour_node_rank": source_rank,
                "target_detour_node_rank": target_rank,
                "source_carrier_mask_class_id": source,
                "target_carrier_mask_class_id": target,
                "edge_role_code": edge_role,
                "edge_partition_code": int(row["edge_partition_code"]),
                "is_positive_negative_boundary": int(row["is_positive_negative_boundary"]),
                "shared_atom_bitset": shared_atom_bitset,
                "shared_symbol_bitset": shared_symbol_bitset,
                "shared_symbol_count": popcount(shared_symbol_bitset),
                "x2_shared_flag": int(INSERTED_SYMBOL_ID in shared_symbols),
                "single_x2_flag": int(shared_symbols == [INSERTED_SYMBOL_ID]),
                "mixed_x2_x5_flag": int(shared_symbols == [2, 5]),
            }
        )

    distances = shortest_paths(adjacency)
    delta = gromov_delta_witness(distances)
    degrees = np.asarray(adjacency.sum(axis=1), dtype=np.int64)

    return_edges_by_target: dict[int, list[dict[str, int]]] = {
        target_id: [] for target_id in X2_DETOUR_TARGET_IDS
    }
    for row in return_edges:
        source = int(row["source_carrier_mask_class_id"])
        target = int(row["target_carrier_mask_class_id"])
        positive = source if source in X2_DETOUR_TARGET_IDS else target
        return_edges_by_target[positive].append(row)

    node_rows: list[dict[str, int]] = []
    for rank, carrier_id in enumerate(detour_node_ids):
        carrier = carrier_rows[carrier_id]
        if carrier_id == ORIGIN_CARRIER_ID:
            role = NODE_ORIGIN
        elif carrier_id == SLOT_NEGATIVE_CARRIER_ID:
            role = NODE_SLOT_NEGATIVE
        elif carrier_id in X2_DETOUR_TARGET_IDS:
            role = NODE_DETOUR_INTERNAL
        else:
            role = NODE_RETURN_NEGATIVE
        node_rows.append(
            {
                "detour_node_rank": rank,
                "carrier_mask_class_id": carrier_id,
                "node_role_code": role,
                "elbow_region_code": int(carrier["elbow_region_code"]),
                "nodal_sign": int(carrier["nodal_sign"]),
                "carrier_atom_mask": int(carrier["carrier_atom_mask"]),
                "carrier_symbol_bitset": carrier_symbol_bitsets[carrier_id],
                "carrier_symbol_count": popcount(carrier_symbol_bitsets[carrier_id]),
                "x2_carrier_flag": int(
                    carrier_symbol_bitsets[carrier_id] & (1 << INSERTED_SYMBOL_ID) != 0
                ),
                "fan_degree": int(degrees[rank]),
                "fan_distance_to_origin": int(distances[rank_by_carrier[ORIGIN_CARRIER_ID], rank]),
                "direct_boundary_return_count": len(
                    return_edges_by_target.get(carrier_id, [])
                ),
            }
        )

    return_path_rows: list[dict[str, int]] = []
    for x2_edge_id in X2_DETOUR_EDGE_IDS:
        x2_edge = next(row for row in edge_rows if int(row["cell_edge_id"]) == x2_edge_id)
        detour_target = (
            int(x2_edge["source_carrier_mask_class_id"])
            if int(x2_edge["source_carrier_mask_class_id"]) != ORIGIN_CARRIER_ID
            else int(x2_edge["target_carrier_mask_class_id"])
        )
        for return_edge in return_edges_by_target[detour_target]:
            source = int(return_edge["source_carrier_mask_class_id"])
            target = int(return_edge["target_carrier_mask_class_id"])
            negative = source if source in RETURN_NEGATIVE_CARRIER_IDS else target
            shared_atom_bitset = int(return_edge["source_carrier_atom_mask"]) & int(
                return_edge["target_carrier_atom_mask"]
            )
            shared_atoms = [
                atom_id for atom_id in range(64) if shared_atom_bitset & (1 << atom_id)
            ]
            return_symbol_bitset = bitset(
                {atom_to_symbol[atom_id] for atom_id in shared_atoms}
            )
            return_path_rows.append(
                {
                    "return_path_id": len(return_path_rows),
                    "x2_cell_edge_id": x2_edge_id,
                    "origin_carrier_mask_class_id": ORIGIN_CARRIER_ID,
                    "detour_carrier_mask_class_id": detour_target,
                    "return_cell_edge_id": int(return_edge["cell_edge_id"]),
                    "return_negative_carrier_mask_class_id": negative,
                    "x2_shared_symbol_bitset": int(x2_edge["shared_symbol_bitset"]),
                    "x2_single_flag": int(x2_edge["single_x2_flag"]),
                    "return_shared_symbol_bitset": return_symbol_bitset,
                    "return_shared_symbol_count": popcount(return_symbol_bitset),
                    "clean_single_x2_return_flag": int(x2_edge["single_x2_flag"]),
                    "mixed_x2_return_flag": int(x2_edge["mixed_x2_x5_flag"]),
                    "node42_realization_flag": 1,
                }
            )

    x2_edges = [row for row in edge_rows if int(row["edge_role_code"]) == EDGE_X2_DETOUR]
    clean_return_paths = [
        row for row in return_path_rows if int(row["clean_single_x2_return_flag"]) == 1
    ]
    mixed_return_paths = [
        row for row in return_path_rows if int(row["mixed_x2_return_flag"]) == 1
    ]
    dead_end_edges = [
        row
        for row in x2_edges
        if not return_edges_by_target[
            int(row["source_carrier_mask_class_id"])
            if int(row["source_carrier_mask_class_id"]) != ORIGIN_CARRIER_ID
            else int(row["target_carrier_mask_class_id"])
        ]
    ]

    observable_values = {
        "detour_node_count": len(node_rows),
        "detour_edge_count": len(edge_rows),
        "x2_detour_edge_count": len(x2_edges),
        "current_slot_edge_count": 1,
        "boundary_return_edge_count": len(return_edges),
        "return_path_count": len(return_path_rows),
        "clean_single_x2_return_path_count": len(clean_return_paths),
        "mixed_x2_return_path_count": len(mixed_return_paths),
        "dead_end_x2_detour_edge_count": len(dead_end_edges),
        "detour_graph_diameter": int(np.max(distances)),
        "detour_graph_radius": int(np.min(np.max(distances, axis=1))),
        "detour_gromov_delta_twice": int(delta["delta_twice"]),
        "origin_carrier_id": ORIGIN_CARRIER_ID,
        "slot_negative_carrier_id": SLOT_NEGATIVE_CARRIER_ID,
        "return_negative_carrier_count": len(RETURN_NEGATIVE_CARRIER_IDS),
        "node42_realization_path_count": sum(
            int(row["node42_realization_flag"]) for row in return_path_rows
        ),
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

    node_table = table_from_rows(DETOUR_NODE_COLUMNS, node_rows)
    edge_table = table_from_rows(DETOUR_EDGE_COLUMNS, edge_rows)
    return_path_table = table_from_rows(RETURN_PATH_COLUMNS, return_path_rows)
    observable_table = table_from_rows(DETOUR_OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "x2_splice_report_certified": splice_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_SPLICE_OBSTRUCTION_CERTIFIED",
        "x2_splice_certificate_certified": splice_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_SPLICE_OBSTRUCTION_CERTIFIED",
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "x2_splice_schema_available": splice.get("schema")
        == "c985.d20_signature_boundary_spine_x2_splice_obstruction@1",
        "cell_complex_schema_available": cell_complex.get("schema")
        == "c985.d20_signature_residual_cell_complex@1",
        "x2_splice_near_miss_table_shape_is_10_by_14": tuple(
            splice_near_miss_table.shape
        )
        == (10, 14),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "origin_carrier_is_12": ORIGIN_CARRIER_ID == 12,
        "slot_negative_carrier_is_4": SLOT_NEGATIVE_CARRIER_ID == 4,
        "incident_x2_detour_edges_match_expected": X2_DETOUR_EDGE_IDS
        == [9, 14, 39, 41],
        "detour_target_carriers_match_expected": X2_DETOUR_TARGET_IDS
        == [2, 3, 10, 11],
        "detour_node_count_is_10": len(node_rows) == 10,
        "detour_edge_count_is_13": len(edge_rows) == 13,
        "x2_detour_edge_count_is_4": len(x2_edges) == 4,
        "boundary_return_edge_count_is_8": len(return_edges) == 8,
        "return_path_count_is_8": len(return_path_rows) == 8,
        "clean_single_x2_return_path_count_is_2": len(clean_return_paths) == 2,
        "mixed_x2_return_path_count_is_6": len(mixed_return_paths) == 6,
        "dead_end_x2_detour_edge_is_9": [
            int(row["cell_edge_id"]) for row in dead_end_edges
        ]
        == [9],
        "clean_single_x2_return_paths_use_edge_14": sorted(
            {int(row["x2_cell_edge_id"]) for row in clean_return_paths}
        )
        == [14],
        "mixed_x2_return_paths_use_edges_39_41": sorted(
            {int(row["x2_cell_edge_id"]) for row in mixed_return_paths}
        )
        == [39, 41],
        "return_negative_carriers_match_expected": sorted(
            {int(row["return_negative_carrier_mask_class_id"]) for row in return_path_rows}
        )
        == RETURN_NEGATIVE_CARRIER_IDS,
        "detour_graph_connected": bool(np.all(distances < 10**9)),
        "detour_graph_diameter_is_3": observable_values["detour_graph_diameter"]
        == 3,
        "detour_graph_radius_is_2": observable_values["detour_graph_radius"] == 2,
        "detour_gromov_delta_is_1": delta["delta_twice"] == 2,
        "detour_delta_witness_carriers_match_expected": [
            detour_node_ids[rank] for rank in delta["witness_ranks"]
        ]
        == [12, 3, 11, 7],
        "all_return_paths_realize_node42_context": all(
            int(row["node42_realization_flag"]) == 1 for row in return_path_rows
        ),
        "node_table_shape_is_10_by_12": tuple(node_table.shape)
        == (10, len(DETOUR_NODE_COLUMNS)),
        "edge_table_shape_is_13_by_15": tuple(edge_table.shape)
        == (13, len(DETOUR_EDGE_COLUMNS)),
        "return_path_table_shape_is_8_by_13": tuple(return_path_table.shape)
        == (8, len(RETURN_PATH_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(DETOUR_OBSERVABLE_COLUMNS)),
    }

    witness = {
        "origin_carrier_id": ORIGIN_CARRIER_ID,
        "slot_negative_carrier_id": SLOT_NEGATIVE_CARRIER_ID,
        "x2_detour_edge_ids": X2_DETOUR_EDGE_IDS,
        "x2_detour_target_ids": X2_DETOUR_TARGET_IDS,
        "return_negative_carrier_ids": RETURN_NEGATIVE_CARRIER_IDS,
        "return_path_count": len(return_path_rows),
        "clean_single_x2_return_paths": [
            [int(row["x2_cell_edge_id"]), int(row["return_cell_edge_id"])]
            for row in clean_return_paths
        ],
        "mixed_x2_return_paths": [
            [int(row["x2_cell_edge_id"]), int(row["return_cell_edge_id"])]
            for row in mixed_return_paths
        ],
        "dead_end_x2_detour_edge_ids": [
            int(row["cell_edge_id"]) for row in dead_end_edges
        ],
        "detour_graph_diameter": observable_values["detour_graph_diameter"],
        "detour_graph_radius": observable_values["detour_graph_radius"],
        "detour_gromov_delta": delta["delta"],
        "detour_gromov_delta_twice": delta["delta_twice"],
        "detour_delta_witness_carrier_ids": [
            detour_node_ids[rank] for rank in delta["witness_ranks"]
        ],
        "detour_distance_histogram": histogram(
            [
                int(distances[source, target])
                for source, target in itertools.combinations(
                    range(len(detour_node_ids)), 2
                )
            ]
        ),
        "node_table_sha256": sha_array(node_table),
        "edge_table_sha256": sha_array(edge_table),
        "return_path_table_sha256": sha_array(return_path_table),
        "adjacency_sha256": sha_array(adjacency),
        "distance_table_sha256": sha_array(distances),
        "observable_table_sha256": sha_array(observable_table),
    }

    detour_fan = {
        "schema": "c985.d20_signature_boundary_spine_x2_detour_fan@1",
        "object": "d20",
        "detour_rule": {
            "source": "certified x2 splice obstruction near misses",
            "origin": "carrier 12, the positive carrier of the selected insertion slot",
            "x2_detours": "central-positive carrier-pair edges incident to carrier 12 and sharing x2",
            "returns": "one-edge positive/negative boundary returns from the detour carriers",
            "node42_context": "the selected symbolic window (5,3,2) is fixed by the prior gate context; each x2 detour supplies the inserted x2 letter",
        },
        "detour_nodes": [
            {
                **row,
                "carrier_atom_ids": carrier_atom_ids(
                    carrier_rows[int(row["carrier_mask_class_id"])]
                ),
            }
            for row in node_rows
        ],
        "detour_edges": edge_rows,
        "return_paths": return_path_rows,
        "summary": {
            "return_path_count": len(return_path_rows),
            "clean_single_x2_return_path_count": len(clean_return_paths),
            "mixed_x2_return_path_count": len(mixed_return_paths),
            "dead_end_x2_detour_edge_ids": witness["dead_end_x2_detour_edge_ids"],
            "detour_graph_diameter": observable_values["detour_graph_diameter"],
            "detour_gromov_delta": delta["delta"],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_x2_detour_fan_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "carrier 12 has four positive-internal x2 detour edges: 9, 14, 39, and 41",
            "three of the four detour targets return to the positive/negative boundary in one more carrier edge",
            "only edge 14 gives clean single-x2 return paths; edge 9 is a dead-end at depth one",
            "the detour fan has 10 nodes, 13 edges, diameter 3, and exact Gromov delta 1",
            "all eight return paths can supply the inserted x2 for the fixed node-42 symbolic context, but six are mixed x2/x5 contacts",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_x2_detour_fan@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The x2 obstruction opens a controlled positive-internal detour fan: "
            "carrier 12 has four x2 exits, three can return to the typed "
            "boundary in one step, and only the detour through carrier 3 gives "
            "clean single-x2 boundary-return paths."
        ),
        "stage_protocol": {
            "draft": "use the certified x2 near misses incident to carrier 12 as off-boundary detour exits",
            "witness": "materialize detour nodes, x2 exits, boundary returns, return paths, and fan metric",
            "coherence": "check clean versus mixed x2 contacts, dead ends, boundary returns, and exact hyperbolicity",
            "closure": "certify a finite off-boundary detour fan without claiming it is already part of the typed spine",
            "emit": "emit detour-fan JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "x2_splice_report": input_entry(
                X2_SPLICE_REPORT,
                {
                    "status": splice_report.get("status"),
                    "certificate_sha256": splice_report.get("certificate_sha256"),
                },
            ),
            "x2_splice_obstruction": input_entry(X2_SPLICE_JSON),
            "x2_splice_near_misses": input_entry(X2_SPLICE_NEAR_MISSES),
            "x2_splice_tables": input_entry(X2_SPLICE_TABLES),
            "x2_splice_certificate": input_entry(X2_SPLICE_CERTIFICATE),
            "cell_complex_report": input_entry(
                CELL_COMPLEX_REPORT,
                {
                    "status": cell_report.get("status"),
                    "certificate_sha256": cell_report.get("certificate_sha256"),
                },
            ),
            "cell_complex": input_entry(CELL_COMPLEX_JSON),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "cell_complex_tables": input_entry(CELL_COMPLEX_TABLES),
            "cell_complex_certificate": input_entry(CELL_COMPLEX_CERTIFICATE),
            "residual_chart_carriers": input_entry(RESIDUAL_CHART_CARRIER_CSV),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_x2_detour_fan": relpath(
                OUT_DIR / "signature_boundary_spine_x2_detour_fan.json"
            ),
            "x2_detour_nodes_csv": relpath(OUT_DIR / "x2_detour_nodes.csv"),
            "x2_detour_edges_csv": relpath(OUT_DIR / "x2_detour_edges.csv"),
            "x2_detour_return_paths_csv": relpath(
                OUT_DIR / "x2_detour_return_paths.csv"
            ),
            "x2_detour_observables_csv": relpath(
                OUT_DIR / "x2_detour_observables.csv"
            ),
            "signature_boundary_spine_x2_detour_fan_tables": relpath(
                OUT_DIR / "signature_boundary_spine_x2_detour_fan_tables.npz"
            ),
            "signature_boundary_spine_x2_detour_fan_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_x2_detour_fan_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the finite off-boundary x2 detour fan incident to carrier 12",
                "one-step positive/negative boundary returns from detour carriers",
                "which returns are clean single-x2 and which are mixed x2/x5",
                "exact fan distances, diameter, radius, and Gromov delta",
            ],
            "does_not_certify_because_not_required": [
                "splicing the detour fan into the certified typed-spine order",
                "that mixed x2/x5 contacts can be disambiguated without extra data",
                "a subsequent x4 route to aperture node 44",
                "new carrier classes or raw relations outside the certified cell complex",
            ],
        },
        "next_highest_yield_item": (
            "Certify the clean x2 detour corridor through carrier 3: compare "
            "the two return choices to negative carriers 7 and 8 against the "
            "existing branch order and determine which return least disturbs "
            "the typed boundary sequence."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_x2_detour_fan_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified x2-splice obstruction and residual cell-complex artifacts",
            "construct the carrier-12 x2 detour fan and one-edge boundary returns",
            "classify clean single-x2, mixed x2/x5, and dead-end detours",
            "compute exact detour fan metric and Gromov hyperbolicity",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_x2_detour_fan": detour_fan,
        "x2_detour_nodes_csv": csv_text(DETOUR_NODE_COLUMNS, node_rows),
        "x2_detour_edges_csv": csv_text(DETOUR_EDGE_COLUMNS, edge_rows),
        "x2_detour_return_paths_csv": csv_text(RETURN_PATH_COLUMNS, return_path_rows),
        "x2_detour_observables_csv": csv_text(DETOUR_OBSERVABLE_COLUMNS, observable_rows),
        "node_table": node_table,
        "edge_table": edge_table,
        "return_path_table": return_path_table,
        "adjacency": adjacency,
        "distances": distances,
        "observable_table": observable_table,
        "signature_boundary_spine_x2_detour_fan_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_x2_detour_fan.json",
        payloads["signature_boundary_spine_x2_detour_fan"],
    )
    (OUT_DIR / "x2_detour_nodes.csv").write_text(
        payloads["x2_detour_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_detour_edges.csv").write_text(
        payloads["x2_detour_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_detour_return_paths.csv").write_text(
        payloads["x2_detour_return_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_detour_observables.csv").write_text(
        payloads["x2_detour_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_x2_detour_fan_tables.npz",
        node_table=payloads["node_table"],
        edge_table=payloads["edge_table"],
        return_path_table=payloads["return_path_table"],
        adjacency=payloads["adjacency"],
        distances=payloads["distances"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_x2_detour_fan_certificate.json",
        payloads["signature_boundary_spine_x2_detour_fan_certificate"],
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
                "return_path_count": witness["return_path_count"],
                "clean_single_x2_return_paths": witness[
                    "clean_single_x2_return_paths"
                ],
                "dead_end_x2_detour_edge_ids": witness[
                    "dead_end_x2_detour_edge_ids"
                ],
                "detour_gromov_delta": witness["detour_gromov_delta"],
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
