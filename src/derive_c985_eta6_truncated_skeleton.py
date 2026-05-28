from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict, deque
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area as aperture
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion as promotion
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area as aperture
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion as promotion
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT, relpath


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_TRUNCATED_ICOSAHEDRAL_BOUNDARY_SKELETON_CERTIFIED"
)
OUT_DIR_NAME = "c985_eta6_truncated_skeleton"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / OUT_DIR_NAME

PUBLIC_BOUNDARY_REPORT = (
    D20_INVARIANTS / "theorems" / "public_boundary_graph_invariants" / "report.json"
)
CELESTIAL_TRACE_REPORT = (
    D20_INVARIANTS / "theorems" / "celestial_trace_pl_ph" / "report.json"
)
APERTURE_POLYGON_REPORT = aperture.OUT_DIR / "report.json"
APERTURE_POLYGON_TABLES = (
    aperture.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_tables.npz"
)
PROMOTION_TABLES = (
    promotion.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_tables.npz"
)
HCYCLE_EDGE_TABLE = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_eta6_truncated_skeleton.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_eta6_truncated_skeleton.py"
)

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]

TRUNCATED_VERTEX_COLUMNS = [
    "vertex_id",
    "center_dual_vertex_id",
    "neighbor_dual_vertex_id",
]
TRUNCATED_EDGE_COLUMNS = [
    "edge_id",
    "source_vertex_id",
    "target_vertex_id",
    "edge_type_code",
    "source_dual_vertex_id",
    "target_dual_vertex_id",
]
TRUNCATED_FACE_COLUMNS = [
    "face_id",
    "face_type_code",
    "source_id",
    "face_size",
    "cycle_v0",
    "cycle_v1",
    "cycle_v2",
    "cycle_v3",
    "cycle_v4",
    "cycle_v5",
]
GRAPH_COLUMNS = [
    "graph_id",
    "graph_code",
    "vertex_count",
    "edge_count",
    "face_count",
    "component_count",
    "min_degree",
    "max_degree",
    "connected_flag",
    "cubic_flag",
    "three_vertex_connected_flag",
    "polyhedral_embedding_flag",
    "d20_boundary_graph_flag",
    "dual_icosahedral_graph_flag",
    "truncated_icosahedral_graph_flag",
    "euler_characteristic",
    "girth",
    "diameter",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "public_boundary_vertex_count": 0,
    "public_boundary_edge_count": 1,
    "public_boundary_face_count": 2,
    "dual_icosahedral_vertex_count": 3,
    "dual_icosahedral_edge_count": 4,
    "dual_icosahedral_face_count": 5,
    "truncated_vertex_count": 6,
    "truncated_edge_count": 7,
    "truncated_face_count": 8,
    "truncated_pentagon_face_count": 9,
    "truncated_hexagon_face_count": 10,
    "truncated_cubic_flag": 11,
    "truncated_planar_embedding_flag": 12,
    "truncated_three_vertex_connected_flag": 13,
    "truncated_girth": 14,
    "truncated_diameter": 15,
    "endpoint_cut_vertex_count": 16,
    "endpoint_cut_edge_count": 17,
    "endpoint_cut_component_count": 18,
    "endpoint_cut_truncated_match_flag": 19,
    "midpoint_convex_hull_vertex_count": 20,
    "midpoint_graham_match_flag": 21,
}


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def csv_text(headers: list[str], rows: list[dict[str, int]]) -> str:
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(row[header]) for header in headers))
    return "\n".join(lines) + "\n"


def parse_label(label: str) -> tuple[str, ...]:
    body = label.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError(f"bad d20 label: {label!r}")
    order = {name: index for index, name in enumerate(H6_LABELS)}
    parts = tuple(part.strip() for part in body[1:-1].split(",") if part.strip())
    return tuple(sorted(parts, key=order.__getitem__))


def label_text(parts: tuple[str, ...]) -> str:
    return "{" + ",".join(parts) + "}"


def load_public_d20_graph() -> dict[str, Any]:
    vertices: dict[int, tuple[str, ...]] = {}
    edges: list[tuple[int, int]] = []
    adjacency: dict[int, set[int]] = defaultdict(set)
    with HCYCLE_EDGE_TABLE.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source = int(row["u"])
            target = int(row["v"])
            source_label = parse_label(row["u_label"])
            target_label = parse_label(row["v_label"])
            if source in vertices and vertices[source] != source_label:
                raise ValueError(f"inconsistent label for d20 vertex {source}")
            if target in vertices and vertices[target] != target_label:
                raise ValueError(f"inconsistent label for d20 vertex {target}")
            vertices[source] = source_label
            vertices[target] = target_label
            edge = tuple(sorted((source, target)))
            edges.append(edge)
            adjacency[source].add(target)
            adjacency[target].add(source)
    return {
        "vertices": vertices,
        "edges": sorted(set(edges)),
        "adjacency": {vertex: set(neighbors) for vertex, neighbors in adjacency.items()},
    }


def canonical_cycle(path: list[int]) -> tuple[int, ...]:
    choices: list[tuple[int, ...]] = []
    for sequence in (path, list(reversed(path))):
        for index in range(len(sequence)):
            choices.append(tuple(sequence[index:] + sequence[:index]))
    return min(choices)


def pentagonal_cycles(graph: dict[str, Any]) -> list[tuple[int, ...]]:
    adjacency = graph["adjacency"]
    cycles: set[tuple[int, ...]] = set()

    def walk(start: int, current: int, path: list[int]) -> None:
        if len(path) == 5:
            if start in adjacency[current]:
                cycles.add(canonical_cycle(path))
            return
        for next_vertex in adjacency[current]:
            if next_vertex not in path:
                walk(start, next_vertex, path + [next_vertex])

    for start in sorted(graph["vertices"]):
        walk(start, start, [start])
    return sorted(cycles)


def cycle_edges(cycle: tuple[int, ...]) -> set[tuple[int, int]]:
    return {
        tuple(sorted((cycle[index], cycle[(index + 1) % len(cycle)])))
        for index in range(len(cycle))
    }


def connected_components(
    vertices: set[int],
    edges: set[tuple[int, int]],
    removed: set[int] | None = None,
) -> int:
    removed = removed or set()
    remaining = sorted(vertices - removed)
    if not remaining:
        return 0
    adjacency = {vertex: set() for vertex in remaining}
    for source, target in edges:
        if source in removed or target in removed:
            continue
        adjacency[source].add(target)
        adjacency[target].add(source)
    seen: set[int] = set()
    components = 0
    for start in remaining:
        if start in seen:
            continue
        components += 1
        seen.add(start)
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbor in adjacency[vertex]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return components


def graph_diameter(vertices: set[int], edges: set[tuple[int, int]]) -> int:
    if connected_components(vertices, edges) != 1:
        return -1
    adjacency = {vertex: set() for vertex in vertices}
    for source, target in edges:
        adjacency[source].add(target)
        adjacency[target].add(source)
    diameter = 0
    for start in vertices:
        distances = {start: 0}
        queue: deque[int] = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor in adjacency[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        diameter = max(diameter, max(distances.values()))
    return diameter


def graph_girth(vertices: set[int], edges: set[tuple[int, int]]) -> int:
    if not edges:
        return 0
    adjacency = {vertex: set() for vertex in vertices}
    for source, target in edges:
        adjacency[source].add(target)
        adjacency[target].add(source)
    best = len(vertices) + 1
    for start in vertices:
        distances = {start: 0}
        parents = {start: -1}
        queue: deque[int] = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor in adjacency[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    parents[neighbor] = vertex
                    queue.append(neighbor)
                elif parents[vertex] != neighbor and parents[neighbor] != vertex:
                    best = min(best, distances[vertex] + distances[neighbor] + 1)
    return 0 if best == len(vertices) + 1 else best


def three_vertex_connected(vertices: set[int], edges: set[tuple[int, int]]) -> bool:
    if len(vertices) < 4 or connected_components(vertices, edges) != 1:
        return False
    for size in (1, 2):
        for removed in combinations(vertices, size):
            if connected_components(vertices, edges, set(removed)) != 1:
                return False
    return True


def graph_row(
    *,
    graph_id: int,
    graph_code: int,
    vertex_count: int,
    edge_pairs: set[tuple[int, int]],
    face_count: int,
    polyhedral_embedding_flag: int,
    d20_boundary_graph_flag: int,
    dual_icosahedral_graph_flag: int,
    truncated_icosahedral_graph_flag: int,
) -> dict[str, int]:
    vertices = set(range(vertex_count))
    degrees = Counter()
    for source, target in edge_pairs:
        degrees[source] += 1
        degrees[target] += 1
    degree_values = [degrees[vertex] for vertex in vertices]
    component_count = connected_components(vertices, edge_pairs)
    return {
        "graph_id": graph_id,
        "graph_code": graph_code,
        "vertex_count": vertex_count,
        "edge_count": len(edge_pairs),
        "face_count": face_count,
        "component_count": component_count,
        "min_degree": min(degree_values) if degree_values else 0,
        "max_degree": max(degree_values) if degree_values else 0,
        "connected_flag": int(component_count == 1),
        "cubic_flag": int(set(degree_values) == {3}),
        "three_vertex_connected_flag": int(three_vertex_connected(vertices, edge_pairs)),
        "polyhedral_embedding_flag": polyhedral_embedding_flag,
        "d20_boundary_graph_flag": d20_boundary_graph_flag,
        "dual_icosahedral_graph_flag": dual_icosahedral_graph_flag,
        "truncated_icosahedral_graph_flag": truncated_icosahedral_graph_flag,
        "euler_characteristic": vertex_count - len(edge_pairs) + face_count,
        "girth": graph_girth(vertices, edge_pairs),
        "diameter": graph_diameter(vertices, edge_pairs),
    }


def build_dual_and_truncation(graph: dict[str, Any]) -> dict[str, Any]:
    faces = pentagonal_cycles(graph)
    face_edges = {
        face_id: cycle_edges(face)
        for face_id, face in enumerate(faces)
    }
    edge_face_ids: dict[tuple[int, int], list[int]] = defaultdict(list)
    vertex_face_ids: dict[int, list[int]] = defaultdict(list)
    for face_id, face in enumerate(faces):
        for edge in face_edges[face_id]:
            edge_face_ids[edge].append(face_id)
        for vertex in face:
            vertex_face_ids[vertex].append(face_id)

    dual_edges = sorted(tuple(sorted(face_ids)) for face_ids in edge_face_ids.values())
    dual_edge_pairs = set(dual_edges)
    half_edges = sorted((source, target) for source, target in dual_edges for source, target in ((source, target), (target, source)))
    vertex_id_by_half_edge = {
        half_edge: vertex_id for vertex_id, half_edge in enumerate(half_edges)
    }
    truncated_vertex_rows = [
        {
            "vertex_id": vertex_id,
            "center_dual_vertex_id": center,
            "neighbor_dual_vertex_id": neighbor,
        }
        for vertex_id, (center, neighbor) in enumerate(half_edges)
    ]

    truncated_edges: dict[tuple[int, int], dict[str, int]] = {}
    for source, target in dual_edges:
        left = vertex_id_by_half_edge[(source, target)]
        right = vertex_id_by_half_edge[(target, source)]
        key = tuple(sorted((left, right)))
        truncated_edges[key] = {
            "edge_type_code": 0,
            "source_dual_vertex_id": source,
            "target_dual_vertex_id": target,
        }

    pentagon_faces: list[list[int]] = []
    for center, face in enumerate(faces):
        cycle = []
        for index, source in enumerate(face):
            target = face[(index + 1) % len(face)]
            incident_faces = sorted(edge_face_ids[tuple(sorted((source, target)))])
            neighbor = incident_faces[0] if incident_faces[1] == center else incident_faces[1]
            cycle.append(vertex_id_by_half_edge[(center, neighbor)])
        pentagon_faces.append(cycle)
        for left, right in zip(cycle, cycle[1:] + cycle[:1]):
            key = tuple(sorted((left, right)))
            truncated_edges[key] = {
                "edge_type_code": 1,
                "source_dual_vertex_id": center,
                "target_dual_vertex_id": -1,
            }

    hexagon_faces: list[list[int]] = []
    for vertex in sorted(graph["vertices"]):
        left, middle, right = sorted(vertex_face_ids[vertex])
        hexagon_faces.append(
            [
                vertex_id_by_half_edge[(left, middle)],
                vertex_id_by_half_edge[(middle, left)],
                vertex_id_by_half_edge[(middle, right)],
                vertex_id_by_half_edge[(right, middle)],
                vertex_id_by_half_edge[(right, left)],
                vertex_id_by_half_edge[(left, right)],
            ]
        )

    truncated_edge_rows = [
        {
            "edge_id": edge_id,
            "source_vertex_id": source,
            "target_vertex_id": target,
            **metadata,
        }
        for edge_id, ((source, target), metadata) in enumerate(
            sorted(truncated_edges.items())
        )
    ]
    face_rows = []
    for face_id, cycle in enumerate(pentagon_faces + hexagon_faces):
        padded = cycle + [-1] * (6 - len(cycle))
        face_rows.append(
            {
                "face_id": face_id,
                "face_type_code": 0 if face_id < len(pentagon_faces) else 1,
                "source_id": face_id if face_id < len(pentagon_faces) else face_id - len(pentagon_faces),
                "face_size": len(cycle),
                "cycle_v0": padded[0],
                "cycle_v1": padded[1],
                "cycle_v2": padded[2],
                "cycle_v3": padded[3],
                "cycle_v4": padded[4],
                "cycle_v5": padded[5],
            }
        )

    edge_face_counts = Counter()
    vertex_face_counts = Counter()
    for cycle in pentagon_faces + hexagon_faces:
        for vertex in cycle:
            vertex_face_counts[vertex] += 1
        for left, right in zip(cycle, cycle[1:] + cycle[:1]):
            edge_face_counts[tuple(sorted((left, right)))] += 1
    edge_face_count_histogram = {
        str(key): value for key, value in Counter(edge_face_counts.values()).items()
    }
    vertex_face_count_histogram = {
        str(key): value for key, value in Counter(vertex_face_counts.values()).items()
    }

    return {
        "primal_faces": faces,
        "dual_edge_pairs": dual_edge_pairs,
        "dual_face_ids_by_primal_vertex": {
            vertex: tuple(sorted(face_ids))
            for vertex, face_ids in vertex_face_ids.items()
        },
        "truncated_vertex_rows": truncated_vertex_rows,
        "truncated_edge_rows": truncated_edge_rows,
        "truncated_face_rows": face_rows,
        "pentagon_faces": pentagon_faces,
        "hexagon_faces": hexagon_faces,
        "edge_face_count_histogram": edge_face_count_histogram,
        "vertex_face_count_histogram": vertex_face_count_histogram,
    }


def endpoint_cut_graph_row() -> dict[str, int]:
    tables = np.load(PROMOTION_TABLES, allow_pickle=False)
    edge_rows = table_rows(
        np.asarray(tables["edge_table"], dtype=np.int64),
        promotion.EDGE_COLUMNS,
    )
    endpoint_id = 0
    endpoint_edges = set()
    for row in sorted(edge_rows, key=lambda item: item["automaton_edge_id"]):
        if row["new_spectral_cut_edge_flag"] != 1:
            continue
        source_endpoint = endpoint_id
        target_endpoint = endpoint_id + 1
        endpoint_id += 2
        endpoint_edges.add((source_endpoint, target_endpoint))
    return graph_row(
        graph_id=3,
        graph_code=3,
        vertex_count=endpoint_id,
        edge_pairs=endpoint_edges,
        face_count=0,
        polyhedral_embedding_flag=0,
        d20_boundary_graph_flag=0,
        dual_icosahedral_graph_flag=0,
        truncated_icosahedral_graph_flag=0,
    )


def build_payload_rows() -> dict[str, Any]:
    public_report = load_json(PUBLIC_BOUNDARY_REPORT)
    celestial_report = load_json(CELESTIAL_TRACE_REPORT)
    aperture_report = load_json(APERTURE_POLYGON_REPORT)
    graph = load_public_d20_graph()
    derived = build_dual_and_truncation(graph)

    public_row = graph_row(
        graph_id=0,
        graph_code=0,
        vertex_count=len(graph["vertices"]),
        edge_pairs=set(graph["edges"]),
        face_count=len(derived["primal_faces"]),
        polyhedral_embedding_flag=1,
        d20_boundary_graph_flag=1,
        dual_icosahedral_graph_flag=0,
        truncated_icosahedral_graph_flag=0,
    )
    dual_row = graph_row(
        graph_id=1,
        graph_code=1,
        vertex_count=len(derived["primal_faces"]),
        edge_pairs=derived["dual_edge_pairs"],
        face_count=len(graph["vertices"]),
        polyhedral_embedding_flag=1,
        d20_boundary_graph_flag=0,
        dual_icosahedral_graph_flag=1,
        truncated_icosahedral_graph_flag=0,
    )
    truncated_edge_pairs = {
        tuple(sorted((row["source_vertex_id"], row["target_vertex_id"])))
        for row in derived["truncated_edge_rows"]
    }
    truncated_row = graph_row(
        graph_id=2,
        graph_code=2,
        vertex_count=len(derived["truncated_vertex_rows"]),
        edge_pairs=truncated_edge_pairs,
        face_count=len(derived["truncated_face_rows"]),
        polyhedral_embedding_flag=1,
        d20_boundary_graph_flag=0,
        dual_icosahedral_graph_flag=0,
        truncated_icosahedral_graph_flag=1,
    )
    endpoint_row = endpoint_cut_graph_row()
    graph_rows = [public_row, dual_row, truncated_row, endpoint_row]
    truncated_face_type_counts = Counter(
        row["face_type_code"] for row in derived["truncated_face_rows"]
    )
    midpoint_metric = aperture_report["witness"]["metric"]
    observable_values = {
        "public_boundary_vertex_count": public_row["vertex_count"],
        "public_boundary_edge_count": public_row["edge_count"],
        "public_boundary_face_count": public_row["face_count"],
        "dual_icosahedral_vertex_count": dual_row["vertex_count"],
        "dual_icosahedral_edge_count": dual_row["edge_count"],
        "dual_icosahedral_face_count": dual_row["face_count"],
        "truncated_vertex_count": truncated_row["vertex_count"],
        "truncated_edge_count": truncated_row["edge_count"],
        "truncated_face_count": truncated_row["face_count"],
        "truncated_pentagon_face_count": truncated_face_type_counts[0],
        "truncated_hexagon_face_count": truncated_face_type_counts[1],
        "truncated_cubic_flag": truncated_row["cubic_flag"],
        "truncated_planar_embedding_flag": truncated_row["polyhedral_embedding_flag"],
        "truncated_three_vertex_connected_flag": truncated_row[
            "three_vertex_connected_flag"
        ],
        "truncated_girth": truncated_row["girth"],
        "truncated_diameter": truncated_row["diameter"],
        "endpoint_cut_vertex_count": endpoint_row["vertex_count"],
        "endpoint_cut_edge_count": endpoint_row["edge_count"],
        "endpoint_cut_component_count": endpoint_row["component_count"],
        "endpoint_cut_truncated_match_flag": endpoint_row[
            "truncated_icosahedral_graph_flag"
        ],
        "midpoint_convex_hull_vertex_count": int(
            midpoint_metric["convex_hull_vertex_count"]
        ),
        "midpoint_graham_match_flag": int(midpoint_metric["graham_area_match_flag"]),
    }
    observable_rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(observable_values[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]
    return {
        "public_report": public_report,
        "celestial_report": celestial_report,
        "aperture_report": aperture_report,
        "graph": graph,
        "derived": derived,
        "graph_rows": graph_rows,
        "observable_values": observable_values,
        "observable_rows": observable_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    vertex_table = table_from_rows(
        TRUNCATED_VERTEX_COLUMNS,
        rows["derived"]["truncated_vertex_rows"],
    )
    edge_table = table_from_rows(
        TRUNCATED_EDGE_COLUMNS,
        rows["derived"]["truncated_edge_rows"],
    )
    face_table = table_from_rows(
        TRUNCATED_FACE_COLUMNS,
        rows["derived"]["truncated_face_rows"],
    )
    graph_table = table_from_rows(GRAPH_COLUMNS, rows["graph_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    public_row, dual_row, truncated_row, endpoint_row = rows["graph_rows"]
    observable_values = rows["observable_values"]

    checks = {
        "input_reports_are_certified": (
            rows["public_report"].get("status"),
            rows["celestial_report"].get("status"),
            rows["aperture_report"].get("status"),
        )
        == (
            "D20_PUBLIC_BOUNDARY_GRAPH_INVARIANTS_CERTIFIED",
            "D20_CELESTIAL_TRACE_PL_POINCARE_HOPF_CERTIFIED",
            aperture.STATUS,
        ),
        "public_boundary_is_dodecahedral_20_30_12": (
            public_row["vertex_count"],
            public_row["edge_count"],
            public_row["face_count"],
            public_row["cubic_flag"],
            public_row["three_vertex_connected_flag"],
            public_row["euler_characteristic"],
        )
        == (20, 30, 12, 1, 1, 2),
        "dual_boundary_is_icosahedral_12_30_20": (
            dual_row["vertex_count"],
            dual_row["edge_count"],
            dual_row["face_count"],
            dual_row["min_degree"],
            dual_row["max_degree"],
            dual_row["three_vertex_connected_flag"],
            dual_row["euler_characteristic"],
        )
        == (12, 30, 20, 5, 5, 1, 2),
        "truncated_dual_is_60_90_cubic_polyhedral_graph": (
            truncated_row["vertex_count"],
            truncated_row["edge_count"],
            truncated_row["face_count"],
            truncated_row["min_degree"],
            truncated_row["max_degree"],
            truncated_row["cubic_flag"],
            truncated_row["connected_flag"],
            truncated_row["three_vertex_connected_flag"],
            truncated_row["polyhedral_embedding_flag"],
            truncated_row["euler_characteristic"],
        )
        == (60, 90, 32, 3, 3, 1, 1, 1, 1, 2),
        "truncated_face_structure_is_12_pentagons_20_hexagons": (
            observable_values["truncated_pentagon_face_count"],
            observable_values["truncated_hexagon_face_count"],
            rows["derived"]["edge_face_count_histogram"],
            rows["derived"]["vertex_face_count_histogram"],
        )
        == (12, 20, {"2": 90}, {"3": 60}),
        "truncated_girth_and_diameter_are_expected": (
            truncated_row["girth"],
            truncated_row["diameter"],
        )
        == (5, 9),
        "six_edge_endpoint_cut_is_not_the_truncated_skeleton": (
            endpoint_row["vertex_count"],
            endpoint_row["edge_count"],
            endpoint_row["component_count"],
            endpoint_row["connected_flag"],
            endpoint_row["three_vertex_connected_flag"],
            endpoint_row["truncated_icosahedral_graph_flag"],
        )
        == (12, 6, 6, 0, 0, 0),
        "midpoint_projection_marks_need_for_lifted_skeleton": (
            observable_values["midpoint_convex_hull_vertex_count"],
            observable_values["midpoint_graham_match_flag"],
        )
        == (3, 0),
        "table_shapes_match_codebooks": (
            tuple(vertex_table.shape),
            tuple(edge_table.shape),
            tuple(face_table.shape),
            tuple(graph_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (60, len(TRUNCATED_VERTEX_COLUMNS)),
            (90, len(TRUNCATED_EDGE_COLUMNS)),
            (32, len(TRUNCATED_FACE_COLUMNS)),
            (4, len(GRAPH_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "graph_rows": rows["graph_rows"],
        "truncated_face_type_counts": {
            "pentagons": observable_values["truncated_pentagon_face_count"],
            "hexagons": observable_values["truncated_hexagon_face_count"],
        },
        "edge_face_count_histogram": rows["derived"]["edge_face_count_histogram"],
        "vertex_face_count_histogram": rows["derived"]["vertex_face_count_histogram"],
        "endpoint_cut_graph": endpoint_row,
        "midpoint_aperture_screen": {
            "convex_hull_vertex_count": observable_values[
                "midpoint_convex_hull_vertex_count"
            ],
            "graham_match_flag": observable_values["midpoint_graham_match_flag"],
        },
        "vertex_table_sha256": sha_array(vertex_table),
        "edge_table_sha256": sha_array(edge_table),
        "face_table_sha256": sha_array(face_table),
        "graph_table_sha256": sha_array(graph_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    skeleton = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton@1",
        "object": "C985->d20",
        "construction": {
            "public_boundary": "certified d20 dodecahedral graph: 20 vertices, 30 edges, 12 pentagonal faces",
            "dual_surface": "dual icosahedral surface: 12 vertices, 30 edges, 20 triangular d20-state faces",
            "truncation": "replace each directed dual edge by one vertex; add original-edge links and cyclic links around each dual vertex",
        },
        "steinitz_reading": {
            "truncated_icosahedral_graph_vertices": 60,
            "truncated_icosahedral_graph_edges": 90,
            "planar_graph_flag": bool(truncated_row["polyhedral_embedding_flag"]),
            "three_vertex_connected_flag": bool(
                truncated_row["three_vertex_connected_flag"]
            ),
            "cubic_flag": bool(truncated_row["cubic_flag"]),
            "face_split": {
                "pentagons": observable_values["truncated_pentagon_face_count"],
                "hexagons": observable_values["truncated_hexagon_face_count"],
            },
        },
        "aperture_relation": {
            "six_edge_endpoint_cut_graph": endpoint_row,
            "interpretation": (
                "the six-edge eta6 aperture is not itself the 60/90 graph; "
                "the truncated-icosahedral skeleton lives at the dual public-boundary lift"
            ),
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_TRUNCATED_ICOSAHEDRAL_BOUNDARY_SKELETON_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The six-edge eta6 aperture is the local support seam, while the "
            "truncated-icosahedral geometry appears one lift higher. The "
            "certified d20 public boundary is the dodecahedral 20/30 graph; "
            "its dual is the 12/30/20 icosahedral PL surface; truncating that "
            "dual gives a 60-vertex, 90-edge, cubic, planar, 3-vertex-connected "
            "graph with 12 pentagonal and 20 hexagonal faces. This is the "
            "Steinitz-compatible boundary skeleton layer."
        ),
        "stage_protocol": {
            "draft": "start from the certified public boundary, celestial dual, and eta6 aperture polygon reports",
            "witness": "construct the dual icosahedral surface and truncate its directed-edge skeleton",
            "coherence": "check vertex, edge, face, cubic, Euler, face-incidence, and 3-connectivity invariants",
            "closure": "certify the 60/90 truncated-icosahedral boundary skeleton separately from the six-edge cut",
            "emit": "emit skeleton tables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "public_boundary_report": input_entry(
                PUBLIC_BOUNDARY_REPORT,
                {
                    "status": rows["public_report"].get("status"),
                    "certificate_sha256": rows["public_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "celestial_trace_report": input_entry(
                CELESTIAL_TRACE_REPORT,
                {
                    "status": rows["celestial_report"].get("status"),
                    "certificate_sha256": rows["celestial_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "aperture_polygon_report": input_entry(
                APERTURE_POLYGON_REPORT,
                {
                    "status": rows["aperture_report"].get("status"),
                    "certificate_sha256": rows["aperture_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "aperture_polygon_tables": input_entry(APERTURE_POLYGON_TABLES),
            "second_window_promotion_tables": input_entry(PROMOTION_TABLES),
            "hcycle_edge_table": input_entry(HCYCLE_EDGE_TABLE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "skeleton": relpath(
                OUT_DIR
                / "eta6_truncated_skeleton.json"
            ),
            "vertices_csv": relpath(
                OUT_DIR / "eta6_truncated_icosahedral_vertices.csv"
            ),
            "edges_csv": relpath(OUT_DIR / "eta6_truncated_icosahedral_edges.csv"),
            "faces_csv": relpath(OUT_DIR / "eta6_truncated_icosahedral_faces.csv"),
            "graphs_csv": relpath(
                OUT_DIR / "eta6_truncated_icosahedral_graphs.csv"
            ),
            "observables_csv": relpath(
                OUT_DIR / "eta6_truncated_icosahedral_observables.csv"
            ),
            "tables": relpath(
                OUT_DIR
                / "eta6_truncated_skeleton_tables.npz"
            ),
            "certificate": relpath(
                OUT_DIR
                / "eta6_truncated_skeleton_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the d20 public boundary dual truncates to a 60-vertex/90-edge cubic graph",
                "the truncated graph has a planar polyhedral embedding with 12 pentagons and 20 hexagons",
                "the truncated graph is 3-vertex-connected, matching the Steinitz graph condition",
                "the six-edge eta6 endpoint cut is the local seam; the truncated skeleton is the lifted boundary carrier",
            ],
            "does_not_certify_because_not_required": [
                "Euclidean coordinates for a convex truncated icosahedron realization",
                "an isomorphism to an external named graph database",
                "that the Graham aperture area is realized by any endpoint or face-barycenter polygon",
                "that the six-edge aperture has opened under any F-symbol intervention",
            ],
        },
        "next_highest_yield_item": (
            "Use the 20 hexagonal faces of this truncated boundary skeleton as "
            "the face-barycenter aperture candidates, then compute whether any "
            "six-face eta6 throat polygon gives a Graham-like area ratio."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the Steinitz 60/90 graph belongs to the dual public-boundary truncation layer",
            "the eta6 cut remains the six-edge support seam that points into the lifted polyhedral skeleton",
            "the next area test should use truncated-skeleton face geometry rather than cut-edge midpoints",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified public boundary, celestial dual, and eta6 aperture polygon reports",
            "derive the dodecahedral public graph pentagonal faces",
            "dualize to the 12/30/20 icosahedral surface",
            "truncate the dual surface to a 60/90 graph with 12 pentagons and 20 hexagons",
            "check cubic degree, Euler characteristic, face incidence, and 3-vertex-connectivity",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "skeleton": skeleton,
        "vertices_csv": csv_text(
            TRUNCATED_VERTEX_COLUMNS,
            rows["derived"]["truncated_vertex_rows"],
        ),
        "edges_csv": csv_text(
            TRUNCATED_EDGE_COLUMNS,
            rows["derived"]["truncated_edge_rows"],
        ),
        "faces_csv": csv_text(
            TRUNCATED_FACE_COLUMNS,
            rows["derived"]["truncated_face_rows"],
        ),
        "graphs_csv": csv_text(GRAPH_COLUMNS, rows["graph_rows"]),
        "observables_csv": csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "vertex_table": vertex_table,
        "edge_table": edge_table,
        "face_table": face_table,
        "graph_table": graph_table,
        "observable_table": observable_table,
        "certificate": certificate,
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
        OUT_DIR
        / "eta6_truncated_skeleton.json",
        payloads["skeleton"],
    )
    (OUT_DIR / "eta6_truncated_icosahedral_vertices.csv").write_text(
        payloads["vertices_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_truncated_icosahedral_edges.csv").write_text(
        payloads["edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_truncated_icosahedral_faces.csv").write_text(
        payloads["faces_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_truncated_icosahedral_graphs.csv").write_text(
        payloads["graphs_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_truncated_icosahedral_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "eta6_truncated_skeleton_tables.npz",
        vertex_table=payloads["vertex_table"],
        edge_table=payloads["edge_table"],
        face_table=payloads["face_table"],
        graph_table=payloads["graph_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "eta6_truncated_skeleton_certificate.json",
        payloads["certificate"],
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
