from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_chamber_spine import (
        OUT_DIR as CHAMBER_SPINE_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
    )
    from .derive_c985_d20_preserved_core_subcomplex import distance_matrix, graph_summary
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
    from derive_c985_d20_chamber_spine import (
        OUT_DIR as CHAMBER_SPINE_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
    )
    from derive_c985_d20_preserved_core_subcomplex import distance_matrix, graph_summary
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


THEOREM_ID = "c985_d20_morse_reeb_quotient"
STATUS = "C985_D20_MORSE_REEB_QUOTIENT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CHAMBER_SPINE_REPORT = CHAMBER_SPINE_DIR / "report.json"
CHAMBER_SPINE_JSON = CHAMBER_SPINE_DIR / "chamber_spine.json"
CHAMBER_SPINE_TABLES = CHAMBER_SPINE_DIR / "chamber_spine_tables.npz"
CHAMBER_SPINE_CERTIFICATE = CHAMBER_SPINE_DIR / "chamber_spine_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_morse_reeb_quotient.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_morse_reeb_quotient.py"

BASIN_BOUNDARY_CODE = 0
BASIN_10_CODE = 10
BASIN_43_CODE = 43
MORSE_SOURCES = [10, 43]
MORSE_SINK = 44
MAX_DIRECTED_PATH_NODE_COUNT = 7
MAX_DIRECTED_INTERVAL_NODE_COUNT = 9

CORE_BASIN_COLUMNS = [
    "node_id",
    "reachable_from_10",
    "reachable_from_43",
    "basin_code",
    "directed_indegree",
    "directed_outdegree",
    "path_count_from_10",
    "path_count_from_43",
    "path_count_to_sink",
]

SPINE_BASIN_COLUMNS = [
    "spine_node_id",
    "basin_code",
    "distance_to_10_lobe",
    "distance_to_43_lobe",
    "distance_to_overlap",
    "node_is_core",
    "node_is_core_overlap",
    "node_is_retraction_obstruction",
    "signature_union_count",
]

DIRECTED_PATH_COLUMNS = [
    "morphism_id",
    "source_node_id",
    "target_node_id",
    "path_length",
    "source_is_morse_source",
    "target_is_sink",
    "source_sink_path",
    "node_id_0",
    "node_id_1",
    "node_id_2",
    "node_id_3",
    "node_id_4",
    "node_id_5",
    "node_id_6",
    "min_signature_union_count",
    "max_signature_union_count",
]

DIRECTED_INTERVAL_COLUMNS = [
    "interval_id",
    "source_node_id",
    "target_node_id",
    "interval_node_count",
    "morphism_count",
    "min_path_length",
    "max_path_length",
    "source_sink_interval",
    "interval_node_id_0",
    "interval_node_id_1",
    "interval_node_id_2",
    "interval_node_id_3",
    "interval_node_id_4",
    "interval_node_id_5",
    "interval_node_id_6",
    "interval_node_id_7",
    "interval_node_id_8",
]

DIRECTED_COMPOSITION_COLUMNS = [
    "composition_id",
    "left_morphism_id",
    "right_morphism_id",
    "composite_morphism_id",
    "source_node_id",
    "via_node_id",
    "target_node_id",
    "left_path_length",
    "right_path_length",
    "composite_path_length",
]


def induced_adjacency(
    node_ids: list[int],
    adjacency: np.ndarray,
    full_index: dict[int, int],
) -> np.ndarray:
    induced = np.zeros((len(node_ids), len(node_ids)), dtype=np.int8)
    for row, source in enumerate(node_ids):
        for column, target in enumerate(node_ids):
            if bool(adjacency[full_index[source], full_index[target]]):
                induced[row, column] = 1
    return induced


def directed_adjacency_map(adjacency: np.ndarray, labels: list[int]) -> dict[int, list[int]]:
    return {
        labels[index]: [labels[int(neighbor)] for neighbor in np.flatnonzero(adjacency[index])]
        for index in range(len(labels))
    }


def reachable_from(
    adjacency_by_node: dict[int, list[int]],
    source: int,
) -> set[int]:
    seen: set[int] = set()
    stack = [source]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(reversed(adjacency_by_node[node]))
    return seen


def enumerate_directed_paths(
    adjacency: np.ndarray,
    labels: list[int],
    node_by_id: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray]:
    adjacency_by_node = directed_adjacency_map(adjacency, labels)
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []

    def visit(path: list[int]) -> None:
        signatures = [int(node_by_id[node_id]["signature_union_count"]) for node_id in path]
        padded_path = [*path, *([-1] * (MAX_DIRECTED_PATH_NODE_COUNT - len(path)))]
        row = {
            "morphism_id": len(rows),
            "source_node_id": path[0],
            "target_node_id": path[-1],
            "path_length": len(path) - 1,
            "source_is_morse_source": int(path[0] in MORSE_SOURCES),
            "target_is_sink": int(path[-1] == MORSE_SINK),
            "source_sink_path": int(path[0] in MORSE_SOURCES and path[-1] == MORSE_SINK),
            "node_ids": path,
            "node_id_0": int(padded_path[0]),
            "node_id_1": int(padded_path[1]),
            "node_id_2": int(padded_path[2]),
            "node_id_3": int(padded_path[3]),
            "node_id_4": int(padded_path[4]),
            "node_id_5": int(padded_path[5]),
            "node_id_6": int(padded_path[6]),
            "min_signature_union_count": min(signatures),
            "max_signature_union_count": max(signatures),
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in DIRECTED_PATH_COLUMNS])
        for neighbor in adjacency_by_node[path[-1]]:
            visit([*path, neighbor])

    for node_id in labels:
        visit([node_id])
    return rows, np.asarray(table_rows, dtype=np.int64)


def build_directed_intervals(
    morphism_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray]:
    by_pair: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in morphism_rows:
        by_pair[(int(row["source_node_id"]), int(row["target_node_id"]))].append(row)

    interval_rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for interval_id, (source, target) in enumerate(sorted(by_pair)):
        paths = sorted(by_pair[(source, target)], key=lambda row: int(row["morphism_id"]))
        interval_nodes = sorted({int(node_id) for path in paths for node_id in path["node_ids"]})
        path_lengths = [int(path["path_length"]) for path in paths]
        padded_nodes = [
            *interval_nodes,
            *([-1] * (MAX_DIRECTED_INTERVAL_NODE_COUNT - len(interval_nodes))),
        ]
        row = {
            "interval_id": interval_id,
            "source_node_id": source,
            "target_node_id": target,
            "interval_node_count": len(interval_nodes),
            "morphism_count": len(paths),
            "min_path_length": min(path_lengths),
            "max_path_length": max(path_lengths),
            "source_sink_interval": int(source in MORSE_SOURCES and target == MORSE_SINK),
            "interval_node_ids": interval_nodes,
            "morphism_ids": [int(path["morphism_id"]) for path in paths],
            "interval_node_id_0": int(padded_nodes[0]),
            "interval_node_id_1": int(padded_nodes[1]),
            "interval_node_id_2": int(padded_nodes[2]),
            "interval_node_id_3": int(padded_nodes[3]),
            "interval_node_id_4": int(padded_nodes[4]),
            "interval_node_id_5": int(padded_nodes[5]),
            "interval_node_id_6": int(padded_nodes[6]),
            "interval_node_id_7": int(padded_nodes[7]),
            "interval_node_id_8": int(padded_nodes[8]),
        }
        interval_rows.append(row)
        table_rows.append([int(row[column]) for column in DIRECTED_INTERVAL_COLUMNS])
    return interval_rows, np.asarray(table_rows, dtype=np.int64)


def build_compositions(
    morphism_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, Any]]:
    path_to_id = {tuple(int(node_id) for node_id in row["node_ids"]): int(row["morphism_id"]) for row in morphism_rows}
    by_source: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in morphism_rows:
        by_source[int(row["source_node_id"])].append(row)

    composition_id_by_pair: dict[tuple[int, int], int] = {}
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for left in morphism_rows:
        right_candidates = by_source[int(left["target_node_id"])]
        for right in right_candidates:
            composite_path = [*left["node_ids"], *right["node_ids"][1:]]
            composite_id = path_to_id[tuple(int(node_id) for node_id in composite_path)]
            row = {
                "composition_id": len(rows),
                "left_morphism_id": int(left["morphism_id"]),
                "right_morphism_id": int(right["morphism_id"]),
                "composite_morphism_id": composite_id,
                "source_node_id": int(left["source_node_id"]),
                "via_node_id": int(left["target_node_id"]),
                "target_node_id": int(right["target_node_id"]),
                "left_path_length": int(left["path_length"]),
                "right_path_length": int(right["path_length"]),
                "composite_path_length": len(composite_path) - 1,
            }
            composition_id_by_pair[
                (int(left["morphism_id"]), int(right["morphism_id"]))
            ] = composite_id
            rows.append(row)
            table_rows.append([int(row[column]) for column in DIRECTED_COMPOSITION_COLUMNS])

    identity_ids = {
        int(row["source_node_id"]): int(row["morphism_id"])
        for row in morphism_rows
        if int(row["path_length"]) == 0
    }
    left_identity_failures = []
    right_identity_failures = []
    for row in morphism_rows:
        morphism_id = int(row["morphism_id"])
        source = int(row["source_node_id"])
        target = int(row["target_node_id"])
        if composition_id_by_pair[(identity_ids[source], morphism_id)] != morphism_id:
            left_identity_failures.append(morphism_id)
        if composition_id_by_pair[(morphism_id, identity_ids[target])] != morphism_id:
            right_identity_failures.append(morphism_id)

    associativity_triple_count = 0
    associativity_failures: list[list[int]] = []
    for left in morphism_rows:
        for middle in by_source[int(left["target_node_id"])]:
            left_middle_id = composition_id_by_pair[
                (int(left["morphism_id"]), int(middle["morphism_id"]))
            ]
            for right in by_source[int(middle["target_node_id"])]:
                associativity_triple_count += 1
                middle_right_id = composition_id_by_pair[
                    (int(middle["morphism_id"]), int(right["morphism_id"]))
                ]
                first = composition_id_by_pair[(left_middle_id, int(right["morphism_id"]))]
                second = composition_id_by_pair[(int(left["morphism_id"]), middle_right_id)]
                if first != second:
                    associativity_failures.append(
                        [
                            int(left["morphism_id"]),
                            int(middle["morphism_id"]),
                            int(right["morphism_id"]),
                        ]
                    )

    summary = {
        "identity_morphism_ids_by_node": {
            str(node_id): identity_ids[node_id] for node_id in sorted(identity_ids)
        },
        "composition_pair_count": len(rows),
        "associativity_triple_count": associativity_triple_count,
        "associativity_failure_count": len(associativity_failures),
        "associativity_failures": associativity_failures,
        "left_identity_failure_count": len(left_identity_failures),
        "right_identity_failure_count": len(right_identity_failures),
        "left_identity_failures": left_identity_failures,
        "right_identity_failures": right_identity_failures,
    }
    return rows, np.asarray(table_rows, dtype=np.int64), summary


def path_counts_by_pair(morphism_rows: list[dict[str, Any]]) -> Counter[tuple[int, int]]:
    counts: Counter[tuple[int, int]] = Counter()
    for row in morphism_rows:
        counts[(int(row["source_node_id"]), int(row["target_node_id"]))] += 1
    return counts


def basin_label_name(code: int) -> str:
    if code == BASIN_10_CODE:
        return "10"
    if code == BASIN_43_CODE:
        return "43"
    return "boundary"


def basin_label_rank(label: str) -> int:
    return {"10": 0, "43": 1, "boundary": 2}[label]


def build_core_basin_rows(
    labels: list[int],
    directed_adjacency: np.ndarray,
    source_reachability: dict[int, set[int]],
    morphism_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, list[int]]]:
    pair_counts = path_counts_by_pair(morphism_rows)
    reach_10 = source_reachability[10]
    reach_43 = source_reachability[43]
    exclusive_10 = sorted(reach_10 - reach_43)
    exclusive_43 = sorted(reach_43 - reach_10)
    overlap = sorted(reach_10 & reach_43)

    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for local_id, node_id in enumerate(labels):
        if node_id in exclusive_10:
            basin_code = BASIN_10_CODE
        elif node_id in exclusive_43:
            basin_code = BASIN_43_CODE
        else:
            basin_code = BASIN_BOUNDARY_CODE
        row = {
            "node_id": node_id,
            "reachable_from_10": int(node_id in reach_10),
            "reachable_from_43": int(node_id in reach_43),
            "basin_code": basin_code,
            "directed_indegree": int(np.sum(directed_adjacency[:, local_id])),
            "directed_outdegree": int(np.sum(directed_adjacency[local_id, :])),
            "path_count_from_10": pair_counts[(10, node_id)],
            "path_count_from_43": pair_counts[(43, node_id)],
            "path_count_to_sink": pair_counts[(node_id, MORSE_SINK)],
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in CORE_BASIN_COLUMNS])

    regions = {
        "exclusive_10": exclusive_10,
        "exclusive_43": exclusive_43,
        "overlap": overlap,
    }
    return rows, np.asarray(table_rows, dtype=np.int64), regions


def build_spine_basin_rows(
    spine_node_ids: list[int],
    spine_adjacency: np.ndarray,
    core_regions: dict[str, list[int]],
    overlap_core_nodes: list[int],
    obstruction_nodes: list[int],
    node_by_id: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, Any]]:
    spine_index = {node_id: index for index, node_id in enumerate(spine_node_ids)}
    spine_distances = distance_matrix(spine_adjacency)
    core_node_set = set(
        core_regions["exclusive_10"] + core_regions["exclusive_43"] + overlap_core_nodes
    )
    overlap_set = set(overlap_core_nodes)
    obstruction_set = set(obstruction_nodes)

    def min_distance(node_id: int, targets: list[int]) -> int:
        source_index = spine_index[node_id]
        return min(int(spine_distances[source_index, spine_index[target]]) for target in targets)

    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for node_id in spine_node_ids:
        distance_to_10 = min_distance(node_id, core_regions["exclusive_10"])
        distance_to_43 = min_distance(node_id, core_regions["exclusive_43"])
        distance_to_overlap = min_distance(node_id, overlap_core_nodes)
        if distance_to_10 < distance_to_43:
            basin_code = BASIN_10_CODE
        elif distance_to_43 < distance_to_10:
            basin_code = BASIN_43_CODE
        else:
            basin_code = BASIN_BOUNDARY_CODE
        row = {
            "spine_node_id": node_id,
            "basin_code": basin_code,
            "distance_to_10_lobe": distance_to_10,
            "distance_to_43_lobe": distance_to_43,
            "distance_to_overlap": distance_to_overlap,
            "node_is_core": int(node_id in core_node_set),
            "node_is_core_overlap": int(node_id in overlap_set),
            "node_is_retraction_obstruction": int(node_id in obstruction_set),
            "signature_union_count": int(node_by_id[node_id]["signature_union_count"]),
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in SPINE_BASIN_COLUMNS])

    basin_nodes = {
        "10": [int(row["spine_node_id"]) for row in rows if int(row["basin_code"]) == 10],
        "43": [int(row["spine_node_id"]) for row in rows if int(row["basin_code"]) == 43],
        "boundary": [
            int(row["spine_node_id"]) for row in rows if int(row["basin_code"]) == 0
        ],
    }
    basin_summaries: dict[str, dict[str, Any]] = {}
    basin_adjacencies: dict[str, np.ndarray] = {}
    for name, node_ids in basin_nodes.items():
        adjacency = induced_adjacency(node_ids, spine_adjacency, spine_index)
        basin_adjacencies[name] = adjacency
        basin_summaries[name] = graph_summary(adjacency, node_ids)

    edge_label_counts: Counter[tuple[str, str]] = Counter()
    label_by_node = {
        int(row["spine_node_id"]): basin_label_name(int(row["basin_code"])) for row in rows
    }
    for left in range(len(spine_node_ids)):
        for right in range(left + 1, len(spine_node_ids)):
            if not bool(spine_adjacency[left, right]):
                continue
            labels = sorted(
                [label_by_node[spine_node_ids[left]], label_by_node[spine_node_ids[right]]],
                key=basin_label_rank,
            )
            edge_label_counts[(labels[0], labels[1])] += 1
    edge_label_count_rows = [
        {
            "left_basin": left,
            "right_basin": right,
            "edge_count": int(count),
        }
        for (left, right), count in sorted(
            edge_label_counts.items(),
            key=lambda item: (-int(item[1]), basin_label_rank(item[0][0]), basin_label_rank(item[0][1])),
        )
    ]

    summary = {
        "basin_nodes": basin_nodes,
        "basin_summaries": basin_summaries,
        "edge_label_counts": edge_label_count_rows,
        "basin_label_vector": np.asarray([int(row["basin_code"]) for row in rows], dtype=np.int64),
        "region_10_nodes": np.asarray(basin_nodes["10"], dtype=np.int64),
        "region_43_nodes": np.asarray(basin_nodes["43"], dtype=np.int64),
        "boundary_nodes": np.asarray(basin_nodes["boundary"], dtype=np.int64),
        "region_10_adjacency": basin_adjacencies["10"],
        "region_43_adjacency": basin_adjacencies["43"],
        "boundary_adjacency": basin_adjacencies["boundary"],
    }
    return rows, np.asarray(table_rows, dtype=np.int64), summary


def source_reachability_matrix(
    source_reachability: dict[int, set[int]],
    labels: list[int],
) -> np.ndarray:
    return np.asarray(
        [
            [int(node_id in source_reachability[source]) for node_id in labels]
            for source in MORSE_SOURCES
        ],
        dtype=np.int8,
    )


def build_payloads() -> dict[str, Any]:
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_complex = load_json(REWRITE_COMPLEX_JSON)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    chamber_report = load_json(CHAMBER_SPINE_REPORT)
    chamber_spine = load_json(CHAMBER_SPINE_JSON)
    chamber_certificate = load_json(CHAMBER_SPINE_CERTIFICATE)
    chamber_tables = np.load(CHAMBER_SPINE_TABLES, allow_pickle=False)

    node_by_id = {int(node["node_id"]): node for node in rewrite_complex["nodes"]}
    core_node_ids = [
        int(node_id)
        for node_id in chamber_report["witness"]["potential_topological_order"]
    ]
    core_node_ids = sorted(core_node_ids)
    directed_adjacency = np.asarray(chamber_tables["directed_adjacency"], dtype=np.int8)
    spine_node_ids = [int(node_id) for node_id in np.asarray(chamber_tables["spine_nodes"])]
    spine_adjacency = np.asarray(chamber_tables["spine_adjacency"], dtype=np.int8)
    adjacency_by_node = directed_adjacency_map(directed_adjacency, core_node_ids)

    source_reach = {source: reachable_from(adjacency_by_node, source) for source in MORSE_SOURCES}
    source_matrix = source_reachability_matrix(source_reach, core_node_ids)

    morphism_rows, directed_path_table = enumerate_directed_paths(
        directed_adjacency,
        core_node_ids,
        node_by_id,
    )
    interval_rows, directed_interval_table = build_directed_intervals(morphism_rows)
    composition_rows, directed_composition_table, composition_summary = build_compositions(
        morphism_rows
    )
    core_basin_rows, core_basin_table, core_regions = build_core_basin_rows(
        core_node_ids,
        directed_adjacency,
        source_reach,
        morphism_rows,
    )
    obstruction_nodes = [
        int(node_id)
        for node_id in chamber_report["witness"]["core_retraction_obstruction_node_ids"]
    ]
    spine_basin_rows, spine_basin_table, spine_summary = build_spine_basin_rows(
        spine_node_ids,
        spine_adjacency,
        core_regions,
        core_regions["overlap"],
        obstruction_nodes,
        node_by_id,
    )

    source_sink_paths = [row for row in morphism_rows if int(row["source_sink_path"]) == 1]
    source_sink_counts = [
        {
            "source_node_id": source,
            "path_count": sum(1 for row in source_sink_paths if int(row["source_node_id"]) == source),
            "path_length_histogram": histogram(
                [
                    int(row["path_length"])
                    for row in source_sink_paths
                    if int(row["source_node_id"]) == source
                ]
            ),
        }
        for source in MORSE_SOURCES
    ]
    source_label_sets = [
        tuple(source for source in MORSE_SOURCES if node_id in source_reach[source])
        for node_id in core_node_ids
    ]
    source_label_histogram = [
        {
            "source_node_ids": list(label_set),
            "count": count,
            "node_ids": [
                node_id
                for node_id, source_label_set in zip(core_node_ids, source_label_sets)
                if source_label_set == label_set
            ],
        }
        for label_set, count in sorted(
            Counter(source_label_sets).items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]
    max_path_interval = max(
        interval_rows,
        key=lambda row: (int(row["morphism_count"]), int(row["interval_node_count"]), row["source_node_id"], row["target_node_id"]),
    )

    morse_reeb = {
        "schema": "c985.d20_morse_reeb_quotient@1",
        "object": "d20",
        "source_chamber_spine_certificate": chamber_report.get("certificate_sha256"),
        "quotient_rule": {
            "finite_flow": "use the certified acyclic chamber orientation as a finite gradient flow",
            "morse_sources": MORSE_SOURCES,
            "sink": MORSE_SINK,
            "core_basins": "classify core nodes by reachability from the two Morse sources",
            "spine_basins": "classify spine nodes by nearest distance to the exclusive source lobes; ties form the basin boundary",
            "path_category": "directed paths are morphisms; concatenation is composition",
        },
        "core_basin_nodes": core_basin_rows,
        "spine_basin_nodes": spine_basin_rows,
        "directed_intervals": interval_rows,
        "summary": {
            "core_node_ids": core_node_ids,
            "directed_edge_count": int(np.sum(directed_adjacency)),
            "source_node_ids": MORSE_SOURCES,
            "sink_node_ids": [MORSE_SINK],
            "source_reachability": {
                str(source): sorted(int(node_id) for node_id in source_reach[source])
                for source in MORSE_SOURCES
            },
            "source_reachability_histogram": source_label_histogram,
            "exclusive_10_lobe_node_ids": core_regions["exclusive_10"],
            "exclusive_43_lobe_node_ids": core_regions["exclusive_43"],
            "overlap_rejoin_node_ids": core_regions["overlap"],
            "directed_path_morphism_count": len(morphism_rows),
            "nonidentity_morphism_count": sum(
                1 for row in morphism_rows if int(row["path_length"]) > 0
            ),
            "directed_interval_count": len(interval_rows),
            "reachable_nonidentity_pair_count": sum(
                1 for row in interval_rows if int(row["min_path_length"]) > 0
            ),
            "directed_path_length_histogram": histogram(
                [int(row["path_length"]) for row in morphism_rows]
            ),
            "source_sink_path_count": len(source_sink_paths),
            "source_sink_path_counts": source_sink_counts,
            "source_sink_path_length_histogram": histogram(
                [int(row["path_length"]) for row in source_sink_paths]
            ),
            "directed_interval_path_count_histogram": histogram(
                [int(row["morphism_count"]) for row in interval_rows]
            ),
            "directed_interval_node_count_histogram": histogram(
                [int(row["interval_node_count"]) for row in interval_rows]
            ),
            "max_path_interval": {
                "source_node_id": int(max_path_interval["source_node_id"]),
                "target_node_id": int(max_path_interval["target_node_id"]),
                "interval_node_count": int(max_path_interval["interval_node_count"]),
                "morphism_count": int(max_path_interval["morphism_count"]),
                "interval_node_ids": max_path_interval["interval_node_ids"],
            },
            "source_sink_intervals": [
                {
                    "source_node_id": int(row["source_node_id"]),
                    "target_node_id": int(row["target_node_id"]),
                    "interval_node_count": int(row["interval_node_count"]),
                    "morphism_count": int(row["morphism_count"]),
                    "interval_node_ids": row["interval_node_ids"],
                }
                for row in interval_rows
                if int(row["source_sink_interval"]) == 1
            ],
            "composition_pair_count": composition_summary["composition_pair_count"],
            "associativity_triple_count": composition_summary["associativity_triple_count"],
            "associativity_failure_count": composition_summary["associativity_failure_count"],
            "left_identity_failure_count": composition_summary["left_identity_failure_count"],
            "right_identity_failure_count": composition_summary["right_identity_failure_count"],
            "identity_morphism_ids_by_node": composition_summary[
                "identity_morphism_ids_by_node"
            ],
            "spine_node_count": len(spine_node_ids),
            "spine_basin_node_counts": {
                name: len(node_ids)
                for name, node_ids in spine_summary["basin_nodes"].items()
            },
            "spine_basin_nodes": spine_summary["basin_nodes"],
            "spine_basin_summaries": spine_summary["basin_summaries"],
            "spine_edge_label_counts": spine_summary["edge_label_counts"],
            "boundary_contains_core_retraction_obstructions": set(obstruction_nodes)
            <= set(spine_summary["basin_nodes"]["boundary"]),
            "core_retraction_obstruction_node_ids": obstruction_nodes,
        },
    }

    checks = {
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "chamber_spine_report_certified": chamber_report.get("status")
        == "C985_D20_CHAMBER_SPINE_CERTIFIED",
        "chamber_spine_certificate_certified": chamber_certificate.get("status")
        == "C985_D20_CHAMBER_SPINE_CERTIFIED",
        "core_node_count_is_12": len(core_node_ids) == 12,
        "directed_edge_count_is_31": int(np.sum(directed_adjacency)) == 31,
        "sources_are_10_43": chamber_report.get("witness", {}).get("source_node_ids")
        == MORSE_SOURCES,
        "sink_is_44": chamber_report.get("witness", {}).get("sink_node_ids") == [MORSE_SINK],
        "source_10_reach_count_is_7": len(source_reach[10]) == 7,
        "source_43_reach_count_is_9": len(source_reach[43]) == 9,
        "exclusive_10_lobe_is_10_17_32": core_regions["exclusive_10"] == [10, 17, 32],
        "exclusive_43_lobe_is_13_28_38_41_43": core_regions["exclusive_43"]
        == [13, 28, 38, 41, 43],
        "overlap_rejoin_is_19_34_42_44": core_regions["overlap"] == [19, 34, 42, 44],
        "source_reachability_matrix_shape_is_2_by_12": tuple(source_matrix.shape) == (2, 12),
        "source_sink_path_count_is_42": len(source_sink_paths) == 42,
        "source_sink_path_counts_are_10_and_32": [
            row["path_count"] for row in source_sink_counts
        ]
        == [10, 32],
        "directed_morphism_count_is_176": len(morphism_rows) == 176,
        "nonidentity_morphism_count_is_164": morse_reeb["summary"][
            "nonidentity_morphism_count"
        ]
        == 164,
        "directed_interval_count_is_57": len(interval_rows) == 57,
        "reachable_nonidentity_pair_count_is_45": morse_reeb["summary"][
            "reachable_nonidentity_pair_count"
        ]
        == 45,
        "directed_path_length_histogram_matches": morse_reeb["summary"][
            "directed_path_length_histogram"
        ]
        == [
            {"value": 0, "count": 12},
            {"value": 1, "count": 31},
            {"value": 2, "count": 49},
            {"value": 3, "count": 48},
            {"value": 4, "count": 27},
            {"value": 5, "count": 8},
            {"value": 6, "count": 1},
        ],
        "source_sink_path_length_histogram_matches": morse_reeb["summary"][
            "source_sink_path_length_histogram"
        ]
        == [
            {"value": 1, "count": 1},
            {"value": 2, "count": 6},
            {"value": 3, "count": 14},
            {"value": 4, "count": 14},
            {"value": 5, "count": 6},
            {"value": 6, "count": 1},
        ],
        "directed_interval_path_count_histogram_matches": morse_reeb["summary"][
            "directed_interval_path_count_histogram"
        ]
        == [
            {"value": 1, "count": 30},
            {"value": 2, "count": 12},
            {"value": 3, "count": 2},
            {"value": 4, "count": 4},
            {"value": 5, "count": 3},
            {"value": 8, "count": 1},
            {"value": 9, "count": 1},
            {"value": 10, "count": 2},
            {"value": 16, "count": 1},
            {"value": 32, "count": 1},
        ],
        "directed_interval_node_count_histogram_matches": morse_reeb["summary"][
            "directed_interval_node_count_histogram"
        ]
        == [
            {"value": 1, "count": 12},
            {"value": 2, "count": 15},
            {"value": 3, "count": 11},
            {"value": 4, "count": 7},
            {"value": 5, "count": 5},
            {"value": 6, "count": 2},
            {"value": 7, "count": 3},
            {"value": 8, "count": 1},
            {"value": 9, "count": 1},
        ],
        "max_path_interval_is_43_to_44_with_32_paths": morse_reeb["summary"][
            "max_path_interval"
        ]
        == {
            "source_node_id": 43,
            "target_node_id": 44,
            "interval_node_count": 9,
            "morphism_count": 32,
            "interval_node_ids": [13, 19, 28, 34, 38, 41, 42, 43, 44],
        },
        "composition_pair_count_is_603": composition_summary["composition_pair_count"] == 603,
        "associativity_triple_count_is_1480": composition_summary[
            "associativity_triple_count"
        ]
        == 1480,
        "associativity_has_zero_failures": composition_summary[
            "associativity_failure_count"
        ]
        == 0,
        "identity_has_zero_failures": composition_summary["left_identity_failure_count"] == 0
        and composition_summary["right_identity_failure_count"] == 0,
        "core_basin_table_shape_is_12_by_9": tuple(core_basin_table.shape)
        == (12, len(CORE_BASIN_COLUMNS)),
        "spine_basin_table_shape_is_50_by_9": tuple(spine_basin_table.shape)
        == (50, len(SPINE_BASIN_COLUMNS)),
        "directed_path_table_shape_is_176_by_16": tuple(directed_path_table.shape)
        == (176, len(DIRECTED_PATH_COLUMNS)),
        "directed_interval_table_shape_is_57_by_17": tuple(directed_interval_table.shape)
        == (57, len(DIRECTED_INTERVAL_COLUMNS)),
        "directed_composition_table_shape_is_603_by_10": tuple(
            directed_composition_table.shape
        )
        == (603, len(DIRECTED_COMPOSITION_COLUMNS)),
        "spine_basin_counts_are_16_20_14": morse_reeb["summary"][
            "spine_basin_node_counts"
        ]
        == {"10": 16, "43": 20, "boundary": 14},
        "boundary_nodes_are_expected": spine_summary["basin_nodes"]["boundary"]
        == [19, 34, 42, 7, 9, 12, 14, 16, 27, 29, 31, 45, 50, 54],
        "boundary_contains_all_core_retraction_obstructions": set(obstruction_nodes)
        <= set(spine_summary["basin_nodes"]["boundary"]),
        "region_10_connected_edges_diameter_delta": spine_summary["basin_summaries"]["10"][
            "component_count"
        ]
        == 1
        and spine_summary["basin_summaries"]["10"]["edge_count"] == 48
        and spine_summary["basin_summaries"]["10"]["diameter"] == 3
        and spine_summary["basin_summaries"]["10"]["gromov_delta"]["delta_twice"] == 2,
        "region_43_connected_edges_diameter_delta": spine_summary["basin_summaries"]["43"][
            "component_count"
        ]
        == 1
        and spine_summary["basin_summaries"]["43"]["edge_count"] == 58
        and spine_summary["basin_summaries"]["43"]["diameter"] == 3
        and spine_summary["basin_summaries"]["43"]["gromov_delta"]["delta_twice"] == 2,
        "boundary_connected_edges_diameter_delta": spine_summary["basin_summaries"][
            "boundary"
        ]["component_count"]
        == 1
        and spine_summary["basin_summaries"]["boundary"]["edge_count"] == 37
        and spine_summary["basin_summaries"]["boundary"]["diameter"] == 3
        and spine_summary["basin_summaries"]["boundary"]["gromov_delta"]["delta_twice"] == 2,
        "spine_edge_label_counts_match": spine_summary["edge_label_counts"]
        == [
            {"left_basin": "43", "right_basin": "boundary", "edge_count": 70},
            {"left_basin": "43", "right_basin": "43", "edge_count": 58},
            {"left_basin": "10", "right_basin": "boundary", "edge_count": 54},
            {"left_basin": "10", "right_basin": "10", "edge_count": 48},
            {"left_basin": "boundary", "right_basin": "boundary", "edge_count": 37},
            {"left_basin": "10", "right_basin": "43", "edge_count": 18},
        ],
    }

    witness = {
        "core_node_count": len(core_node_ids),
        "directed_edge_count": int(np.sum(directed_adjacency)),
        "source_node_ids": MORSE_SOURCES,
        "sink_node_ids": [MORSE_SINK],
        "source_10_reach_node_ids": sorted(source_reach[10]),
        "source_43_reach_node_ids": sorted(source_reach[43]),
        "exclusive_10_lobe_node_ids": core_regions["exclusive_10"],
        "exclusive_43_lobe_node_ids": core_regions["exclusive_43"],
        "overlap_rejoin_node_ids": core_regions["overlap"],
        "source_reachability_histogram": source_label_histogram,
        "directed_path_morphism_count": len(morphism_rows),
        "nonidentity_morphism_count": morse_reeb["summary"]["nonidentity_morphism_count"],
        "directed_interval_count": len(interval_rows),
        "reachable_nonidentity_pair_count": morse_reeb["summary"][
            "reachable_nonidentity_pair_count"
        ],
        "directed_path_length_histogram": morse_reeb["summary"][
            "directed_path_length_histogram"
        ],
        "source_sink_path_count": len(source_sink_paths),
        "source_sink_path_counts": source_sink_counts,
        "source_sink_path_length_histogram": morse_reeb["summary"][
            "source_sink_path_length_histogram"
        ],
        "directed_interval_path_count_histogram": morse_reeb["summary"][
            "directed_interval_path_count_histogram"
        ],
        "directed_interval_node_count_histogram": morse_reeb["summary"][
            "directed_interval_node_count_histogram"
        ],
        "max_path_interval": morse_reeb["summary"]["max_path_interval"],
        "source_sink_intervals": morse_reeb["summary"]["source_sink_intervals"],
        "composition_pair_count": composition_summary["composition_pair_count"],
        "associativity_triple_count": composition_summary["associativity_triple_count"],
        "associativity_failure_count": composition_summary["associativity_failure_count"],
        "left_identity_failure_count": composition_summary["left_identity_failure_count"],
        "right_identity_failure_count": composition_summary["right_identity_failure_count"],
        "spine_node_count": len(spine_node_ids),
        "spine_basin_node_counts": morse_reeb["summary"]["spine_basin_node_counts"],
        "spine_region_10_node_ids": spine_summary["basin_nodes"]["10"],
        "spine_region_43_node_ids": spine_summary["basin_nodes"]["43"],
        "spine_boundary_node_ids": spine_summary["basin_nodes"]["boundary"],
        "spine_region_10_edge_count": spine_summary["basin_summaries"]["10"]["edge_count"],
        "spine_region_43_edge_count": spine_summary["basin_summaries"]["43"]["edge_count"],
        "spine_boundary_edge_count": spine_summary["basin_summaries"]["boundary"][
            "edge_count"
        ],
        "spine_region_10_diameter": spine_summary["basin_summaries"]["10"]["diameter"],
        "spine_region_43_diameter": spine_summary["basin_summaries"]["43"]["diameter"],
        "spine_boundary_diameter": spine_summary["basin_summaries"]["boundary"][
            "diameter"
        ],
        "spine_region_10_gromov_delta_twice": spine_summary["basin_summaries"]["10"][
            "gromov_delta"
        ]["delta_twice"],
        "spine_region_43_gromov_delta_twice": spine_summary["basin_summaries"]["43"][
            "gromov_delta"
        ]["delta_twice"],
        "spine_boundary_gromov_delta_twice": spine_summary["basin_summaries"][
            "boundary"
        ]["gromov_delta"]["delta_twice"],
        "spine_edge_label_counts": spine_summary["edge_label_counts"],
        "core_retraction_obstruction_node_ids": obstruction_nodes,
        "boundary_contains_core_retraction_obstructions": morse_reeb["summary"][
            "boundary_contains_core_retraction_obstructions"
        ],
        "core_basin_table_sha256": sha_array(core_basin_table),
        "spine_basin_table_sha256": sha_array(spine_basin_table),
        "directed_path_table_sha256": sha_array(directed_path_table),
        "directed_interval_table_sha256": sha_array(directed_interval_table),
        "directed_composition_table_sha256": sha_array(directed_composition_table),
        "source_reachability_matrix_sha256": sha_array(source_matrix),
        "basin_label_vector_sha256": sha_array(spine_summary["basin_label_vector"]),
        "region_10_adjacency_sha256": sha_array(spine_summary["region_10_adjacency"]),
        "region_43_adjacency_sha256": sha_array(spine_summary["region_43_adjacency"]),
        "boundary_adjacency_sha256": sha_array(spine_summary["boundary_adjacency"]),
    }

    certificate = {
        "schema": "c985.d20_morse_reeb_quotient_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_MORSE_REEB_QUOTIENT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the acyclic chamber orientation defines a finite two-source flow into sink 44",
            "the source reachability quotient has two exclusive lobes and a four-node overlap/rejoin set",
            "all directed paths form a finite category with 12 objects, 176 morphisms, and associative concatenation",
            "the 50-node chamber spine splits into two connected basins separated by a connected 14-node boundary",
            "the basin boundary contains every direct obstruction to retracting the boundary band onto the 12-node core",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_morse_reeb_quotient@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified acyclic d20 chamber orientation induces a finite "
            "Morse/Reeb quotient with two source basins flowing to sink 44, "
            "an associative directed-path category, and a connected hyperbolic "
            "basin boundary inside the 50-node spine."
        ),
        "stage_protocol": {
            "draft": "treat the chamber orientation as a finite gradient flow with Morse sources 10 and 43",
            "witness": "materialize source reachability, core basins, spine basins, directed intervals, and path compositions",
            "coherence": "check basin counts, source-sink paths, interval morphisms, associativity, identity laws, and basin-boundary hyperbolicity",
            "closure": "certify the Morse/Reeb quotient and its finite directed-path category",
            "emit": "emit Morse/Reeb JSON/CSV/NPZ, certificate, report, verifier command, and next target",
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
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "chamber_spine_report": input_entry(
                CHAMBER_SPINE_REPORT,
                {
                    "status": chamber_report.get("status"),
                    "certificate_sha256": chamber_report.get("certificate_sha256"),
                },
            ),
            "chamber_spine": input_entry(CHAMBER_SPINE_JSON),
            "chamber_spine_tables": input_entry(CHAMBER_SPINE_TABLES),
            "chamber_spine_certificate": input_entry(CHAMBER_SPINE_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "morse_reeb_quotient": relpath(OUT_DIR / "morse_reeb_quotient.json"),
            "core_basin_nodes_csv": relpath(OUT_DIR / "core_basin_nodes.csv"),
            "spine_basin_nodes_csv": relpath(OUT_DIR / "spine_basin_nodes.csv"),
            "directed_interval_paths_csv": relpath(OUT_DIR / "directed_interval_paths.csv"),
            "directed_intervals_csv": relpath(OUT_DIR / "directed_intervals.csv"),
            "directed_compositions_csv": relpath(OUT_DIR / "directed_compositions.csv"),
            "morse_reeb_tables": relpath(OUT_DIR / "morse_reeb_tables.npz"),
            "morse_reeb_certificate": relpath(OUT_DIR / "morse_reeb_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the two source reachability basins and four-node overlap/rejoin set in the directed core",
                "the complete finite category of directed paths, including identity and associativity checks",
                "all 57 reachable directed intervals and the 42 source-sink path morphisms",
                "the shortest-distance basin split of the 50-node spine into two connected regions and a connected boundary",
                "that the basin boundary contains the nine direct core-retraction obstruction nodes",
            ],
            "does_not_certify_because_not_required": [
                "a smooth Morse function or continuous Reeb graph",
                "an infinite visual boundary or asymptotic Gromov boundary",
                "probabilistic transition weights on source-sink paths",
                "stationary or recurrent flow measures",
                "new C985 associator or pentagon data beyond the existing certificate",
            ],
        },
        "next_highest_yield_item": (
            "Promote the Morse/Reeb quotient into a boundary transfer operator: "
            "assign transition weights from the 42 source-sink morphisms, certify "
            "its stationary/recurrent support, and compare the resulting "
            "hyperbolic flow measure against the Poincare barycenter geometry."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_morse_reeb_quotient_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified rewrite-complex and chamber-spine artifacts",
            "derive source reachability, exclusive lobes, and overlap/rejoin nodes",
            "enumerate every directed path, interval, and composable path pair",
            "check category identity and associativity laws by finite exhaustive composition",
            "classify the 50-node spine into two source basins and a connected basin boundary",
            "check source hashes and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "morse_reeb_quotient": morse_reeb,
        "core_basin_nodes_csv": csv_text(CORE_BASIN_COLUMNS, core_basin_rows),
        "spine_basin_nodes_csv": csv_text(SPINE_BASIN_COLUMNS, spine_basin_rows),
        "directed_interval_paths_csv": csv_text(DIRECTED_PATH_COLUMNS, morphism_rows),
        "directed_intervals_csv": csv_text(DIRECTED_INTERVAL_COLUMNS, interval_rows),
        "directed_compositions_csv": csv_text(DIRECTED_COMPOSITION_COLUMNS, composition_rows),
        "core_basin_table": core_basin_table,
        "spine_basin_table": spine_basin_table,
        "directed_path_table": directed_path_table,
        "directed_interval_table": directed_interval_table,
        "directed_composition_table": directed_composition_table,
        "source_reachability_matrix": source_matrix,
        "basin_label_vector": spine_summary["basin_label_vector"],
        "region_10_nodes": spine_summary["region_10_nodes"],
        "region_43_nodes": spine_summary["region_43_nodes"],
        "boundary_nodes": spine_summary["boundary_nodes"],
        "region_10_adjacency": spine_summary["region_10_adjacency"],
        "region_43_adjacency": spine_summary["region_43_adjacency"],
        "boundary_adjacency": spine_summary["boundary_adjacency"],
        "morse_reeb_certificate": certificate,
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
    write_json(OUT_DIR / "morse_reeb_quotient.json", payloads["morse_reeb_quotient"])
    (OUT_DIR / "core_basin_nodes.csv").write_text(
        payloads["core_basin_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "spine_basin_nodes.csv").write_text(
        payloads["spine_basin_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "directed_interval_paths.csv").write_text(
        payloads["directed_interval_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "directed_intervals.csv").write_text(
        payloads["directed_intervals_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "directed_compositions.csv").write_text(
        payloads["directed_compositions_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "morse_reeb_tables.npz",
        core_basin_table=payloads["core_basin_table"],
        spine_basin_table=payloads["spine_basin_table"],
        directed_path_table=payloads["directed_path_table"],
        directed_interval_table=payloads["directed_interval_table"],
        directed_composition_table=payloads["directed_composition_table"],
        source_reachability_matrix=payloads["source_reachability_matrix"],
        basin_label_vector=payloads["basin_label_vector"],
        region_10_nodes=payloads["region_10_nodes"],
        region_43_nodes=payloads["region_43_nodes"],
        boundary_nodes=payloads["boundary_nodes"],
        region_10_adjacency=payloads["region_10_adjacency"],
        region_43_adjacency=payloads["region_43_adjacency"],
        boundary_adjacency=payloads["boundary_adjacency"],
    )
    write_json(OUT_DIR / "morse_reeb_certificate.json", payloads["morse_reeb_certificate"])
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
                "directed_path_morphism_count": witness["directed_path_morphism_count"],
                "directed_interval_count": witness["directed_interval_count"],
                "composition_pair_count": witness["composition_pair_count"],
                "spine_basin_node_counts": witness["spine_basin_node_counts"],
                "spine_boundary_node_ids": witness["spine_boundary_node_ids"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
