from __future__ import annotations

import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_eta6_truncated_skeleton as skeleton
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_eta6_truncated_skeleton as skeleton
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_HEX_FACE_BARYCENTER_GRAHAM_SCREEN_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TRUNCATED_SKELETON_REPORT = skeleton.OUT_DIR / "report.json"
TRUNCATED_SKELETON_TABLES = (
    skeleton.OUT_DIR
    / "eta6_truncated_skeleton_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen.py"
)

SCALE = 1_000_000_000_000
GRAHAM_AREA_X1E12 = 674_981_000_000
REGULAR_AREA_X1E12 = 649_519_000_000
GRAHAM_TOLERANCE_X1E12 = 5_000_000_000

CENTER_COLUMNS = [
    "face_source_id",
    "truncated_face_id",
    "x_x1e12",
    "y_x1e12",
    "z_x1e12",
]
EXTREMA_COLUMNS = [
    "screen_id",
    "screen_code",
    "candidate_rank",
    "face_0",
    "face_1",
    "face_2",
    "face_3",
    "face_4",
    "face_5",
    "ordered_0",
    "ordered_1",
    "ordered_2",
    "ordered_3",
    "ordered_4",
    "ordered_5",
    "area_x1e12",
    "area_over_regular_ratio_x1e12",
    "area_over_graham_ratio_x1e12",
    "regular_error_x1e12",
    "graham_error_x1e12",
    "pca_residual_x1e12",
    "projected_hull_vertex_count",
    "public_subgraph_edge_count",
    "connected_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "hex_face_center_count": 0,
    "candidate_count_all": 1,
    "candidate_count_connected": 2,
    "simple_public_six_cycle_count": 3,
    "graham_tolerance_x1e12": 4,
    "graham_area_x1e12": 5,
    "regular_area_x1e12": 6,
    "within_graham_tolerance_all_count": 7,
    "within_graham_tolerance_connected_count": 8,
    "closest_all_area_x1e12": 9,
    "closest_all_graham_error_x1e12": 10,
    "closest_all_connected_flag": 11,
    "closest_connected_area_x1e12": 12,
    "closest_connected_graham_error_x1e12": 13,
    "max_all_area_x1e12": 14,
    "max_connected_area_x1e12": 15,
}
SCREEN_CODES = {
    "closest_all": 0,
    "max_all": 1,
    "closest_connected": 2,
    "max_connected": 3,
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


def standard_icosahedron() -> dict[str, Any]:
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    coords = np.asarray(
        [
            (0.0, -1.0, -phi),
            (0.0, -1.0, phi),
            (0.0, 1.0, -phi),
            (0.0, 1.0, phi),
            (-1.0, -phi, 0.0),
            (-1.0, phi, 0.0),
            (1.0, -phi, 0.0),
            (1.0, phi, 0.0),
            (-phi, 0.0, -1.0),
            (phi, 0.0, -1.0),
            (-phi, 0.0, 1.0),
            (phi, 0.0, 1.0),
        ],
        dtype=np.float64,
    )
    distances = []
    for left, right in combinations(range(len(coords)), 2):
        distances.append(float(np.sum((coords[left] - coords[right]) ** 2)))
    edge_length_sq = min(value for value in distances if value > 0.0)
    edges = {
        (left, right)
        for left, right in combinations(range(len(coords)), 2)
        if abs(float(np.sum((coords[left] - coords[right]) ** 2)) - edge_length_sq)
        < 1e-9
    }
    adjacency = {vertex: set() for vertex in range(len(coords))}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    return {"coords": coords, "edges": edges, "adjacency": adjacency}


def dual_icosahedron_isomorphism(dual_edges: set[tuple[int, int]]) -> tuple[int, ...]:
    standard = standard_icosahedron()
    source_adjacency = {vertex: set() for vertex in range(12)}
    for left, right in dual_edges:
        source_adjacency[left].add(right)
        source_adjacency[right].add(left)
    target_adjacency = standard["adjacency"]
    mapping: dict[int, int] = {}
    used: set[int] = set()

    def compatible(source: int, target: int) -> bool:
        for mapped_source, mapped_target in mapping.items():
            if (mapped_source in source_adjacency[source]) != (
                mapped_target in target_adjacency[target]
            ):
                return False
        return True

    def search(source: int) -> tuple[int, ...] | None:
        if source == 12:
            return tuple(mapping[index] for index in range(12))
        for target in range(12):
            if target in used or not compatible(source, target):
                continue
            mapping[source] = target
            used.add(target)
            result = search(source + 1)
            if result is not None:
                return result
            used.remove(target)
            del mapping[source]
        return None

    result = search(0)
    if result is None:
        raise ValueError("dual graph is not isomorphic to the standard icosahedron")
    return result


def deterministic_pca_projection(points: np.ndarray) -> tuple[np.ndarray, int]:
    centered = points - np.mean(points, axis=0)
    scatter = centered.T @ centered
    eigenvalues, eigenvectors = np.linalg.eigh(scatter)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    basis = eigenvectors[:, :2].copy()
    for column in range(2):
        pivot = int(np.argmax(np.abs(basis[:, column])))
        if basis[pivot, column] < 0.0:
            basis[:, column] *= -1.0
    projection = centered @ basis
    positive = np.maximum(eigenvalues, 0.0)
    total = float(np.sum(positive))
    residual = 0 if total == 0.0 else int(round(float(positive[2] / total) * SCALE))
    return projection, residual


def ordered_polygon_area_x1e12(points: np.ndarray, face_ids: tuple[int, ...]) -> tuple[int, tuple[int, ...], int, int]:
    projected, residual = deterministic_pca_projection(points)
    center = np.mean(projected, axis=0)
    angles = np.arctan2(projected[:, 1] - center[1], projected[:, 0] - center[0])
    order = sorted(range(len(face_ids)), key=lambda index: (angles[index], face_ids[index]))
    ordered_points = projected[order]
    area_twice = 0.0
    for index in range(len(ordered_points)):
        x0, y0 = ordered_points[index]
        x1, y1 = ordered_points[(index + 1) % len(ordered_points)]
        area_twice += x0 * y1 - x1 * y0
    area = abs(area_twice) / 2.0
    diameter_sq = 0.0
    for left, right in combinations(range(len(projected)), 2):
        diameter_sq = max(
            diameter_sq,
            float(np.sum((projected[left] - projected[right]) ** 2)),
        )
    area_x1e12 = 0 if diameter_sq == 0.0 else int(round((area / diameter_sq) * SCALE))
    hull_count = convex_hull_vertex_count(projected)
    return area_x1e12, tuple(face_ids[index] for index in order), residual, hull_count


def convex_hull_vertex_count(points: np.ndarray) -> int:
    ordered = sorted((float(x), float(y)) for x, y in points)
    if len(ordered) <= 1:
        return len(ordered)

    def cross(origin, left, right) -> float:
        return (left[0] - origin[0]) * (right[1] - origin[1]) - (
            left[1] - origin[1]
        ) * (right[0] - origin[0])

    lower = []
    for point in ordered:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 1e-12:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(ordered):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 1e-12:
            upper.pop()
        upper.append(point)
    hull = lower[:-1] + upper[:-1]
    return len(hull)


def induced_edge_count(candidate: tuple[int, ...], public_edges: set[tuple[int, int]]) -> int:
    candidate_set = set(candidate)
    return sum(1 for left, right in public_edges if left in candidate_set and right in candidate_set)


def connected_candidate(candidate: tuple[int, ...], public_edges: set[tuple[int, int]]) -> bool:
    candidate_set = set(candidate)
    adjacency = {vertex: set() for vertex in candidate_set}
    for left, right in public_edges:
        if left in candidate_set and right in candidate_set:
            adjacency[left].add(right)
            adjacency[right].add(left)
    seen = {candidate[0]}
    stack = [candidate[0]]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return seen == candidate_set


def simple_cycle_count(
    vertices: list[int],
    adjacency: dict[int, set[int]],
    length: int,
) -> int:
    cycles: set[tuple[int, ...]] = set()

    def canonical(path: list[int]) -> tuple[int, ...]:
        options = []
        for sequence in (path, list(reversed(path))):
            for index in range(len(sequence)):
                options.append(tuple(sequence[index:] + sequence[:index]))
        return min(options)

    def walk(start: int, current: int, path: list[int]) -> None:
        if len(path) == length:
            if start in adjacency[current]:
                cycles.add(canonical(path))
            return
        for neighbor in sorted(adjacency[current]):
            if neighbor in path:
                continue
            walk(start, neighbor, path + [neighbor])

    for vertex in vertices:
        walk(vertex, vertex, [vertex])
    return len(cycles)


def candidate_row(
    candidate: tuple[int, ...],
    *,
    centers: dict[int, np.ndarray],
    public_edges: set[tuple[int, int]],
) -> dict[str, int]:
    points = np.asarray([centers[face_id] for face_id in candidate], dtype=np.float64)
    area_x1e12, ordered, residual, hull_count = ordered_polygon_area_x1e12(
        points,
        candidate,
    )
    connected_flag = int(connected_candidate(candidate, public_edges))
    subgraph_edge_count = induced_edge_count(candidate, public_edges)
    return {
        "face_0": candidate[0],
        "face_1": candidate[1],
        "face_2": candidate[2],
        "face_3": candidate[3],
        "face_4": candidate[4],
        "face_5": candidate[5],
        "ordered_0": ordered[0],
        "ordered_1": ordered[1],
        "ordered_2": ordered[2],
        "ordered_3": ordered[3],
        "ordered_4": ordered[4],
        "ordered_5": ordered[5],
        "area_x1e12": area_x1e12,
        "area_over_regular_ratio_x1e12": (area_x1e12 * SCALE)
        // REGULAR_AREA_X1E12,
        "area_over_graham_ratio_x1e12": (area_x1e12 * SCALE)
        // GRAHAM_AREA_X1E12,
        "regular_error_x1e12": abs(area_x1e12 - REGULAR_AREA_X1E12),
        "graham_error_x1e12": abs(area_x1e12 - GRAHAM_AREA_X1E12),
        "pca_residual_x1e12": residual,
        "projected_hull_vertex_count": hull_count,
        "public_subgraph_edge_count": subgraph_edge_count,
        "connected_flag": connected_flag,
    }


def ranked_screen_rows(
    centers: dict[int, np.ndarray],
    public_edges: set[tuple[int, int]],
) -> dict[str, Any]:
    all_count = 0
    connected_count = 0
    within_all_count = 0
    within_connected_count = 0
    closest_all = None
    max_all = None
    closest_connected = None
    max_connected = None
    for candidate in combinations(range(20), 6):
        all_count += 1
        row = candidate_row(candidate, centers=centers, public_edges=public_edges)
        if row["graham_error_x1e12"] <= GRAHAM_TOLERANCE_X1E12:
            within_all_count += 1
        if row["connected_flag"]:
            connected_count += 1
            if row["graham_error_x1e12"] <= GRAHAM_TOLERANCE_X1E12:
                within_connected_count += 1
        closest_key = (
            row["graham_error_x1e12"],
            tuple(row[f"face_{index}"] for index in range(6)),
        )
        max_key = (
            row["area_x1e12"],
            tuple(row[f"face_{index}"] for index in range(6)),
        )
        if closest_all is None or closest_key < closest_all[0]:
            closest_all = (closest_key, row)
        if max_all is None or max_key > max_all[0]:
            max_all = (max_key, row)
        if row["connected_flag"]:
            if closest_connected is None or closest_key < closest_connected[0]:
                closest_connected = (closest_key, row)
            if max_connected is None or max_key > max_connected[0]:
                max_connected = (max_key, row)
    extrema_seed_rows = [
        ("closest_all", closest_all[1]),
        ("max_all", max_all[1]),
        ("closest_connected", closest_connected[1]),
        ("max_connected", max_connected[1]),
    ]
    extrema_rows = []
    for screen_id, (name, row) in enumerate(extrema_seed_rows):
        extrema_rows.append(
            {
                "screen_id": screen_id,
                "screen_code": SCREEN_CODES[name],
                "candidate_rank": screen_id,
                **row,
            }
        )
    return {
        "candidate_count_all": all_count,
        "candidate_count_connected": connected_count,
        "within_graham_tolerance_all_count": within_all_count,
        "within_graham_tolerance_connected_count": within_connected_count,
        "extrema_rows": extrema_rows,
    }


def build_center_rows(
    vertex_rows: list[dict[str, int]],
    face_rows: list[dict[str, int]],
    dual_edges: set[tuple[int, int]],
) -> dict[str, Any]:
    standard = standard_icosahedron()
    iso = dual_icosahedron_isomorphism(dual_edges)
    dual_coords = {
        dual_id: standard["coords"][target_id]
        for dual_id, target_id in enumerate(iso)
    }
    truncated_coords = {}
    for row in vertex_rows:
        center = dual_coords[row["center_dual_vertex_id"]]
        neighbor = dual_coords[row["neighbor_dual_vertex_id"]]
        truncated_coords[row["vertex_id"]] = (2.0 * center + neighbor) / 3.0

    center_rows = []
    centers = {}
    for row in face_rows:
        if row["face_type_code"] != 1:
            continue
        cycle = [row[f"cycle_v{index}"] for index in range(6)]
        center = np.mean(
            np.asarray([truncated_coords[vertex_id] for vertex_id in cycle]),
            axis=0,
        )
        source_id = row["source_id"]
        centers[source_id] = center
        center_rows.append(
            {
                "face_source_id": source_id,
                "truncated_face_id": row["face_id"],
                "x_x1e12": int(round(float(center[0]) * SCALE)),
                "y_x1e12": int(round(float(center[1]) * SCALE)),
                "z_x1e12": int(round(float(center[2]) * SCALE)),
            }
        )
    return {
        "isomorphism": iso,
        "centers": centers,
        "center_rows": sorted(center_rows, key=lambda row: row["face_source_id"]),
    }


def build_payload_rows() -> dict[str, Any]:
    skeleton_report = load_json(TRUNCATED_SKELETON_REPORT)
    tables = np.load(TRUNCATED_SKELETON_TABLES, allow_pickle=False)
    vertex_rows = table_rows(
        np.asarray(tables["vertex_table"], dtype=np.int64),
        skeleton.TRUNCATED_VERTEX_COLUMNS,
    )
    face_rows = table_rows(
        np.asarray(tables["face_table"], dtype=np.int64),
        skeleton.TRUNCATED_FACE_COLUMNS,
    )
    public_graph = skeleton.load_public_d20_graph()
    derived = skeleton.build_dual_and_truncation(public_graph)
    center_data = build_center_rows(
        vertex_rows,
        face_rows,
        derived["dual_edge_pairs"],
    )
    public_edges = set(public_graph["edges"])
    screen = ranked_screen_rows(center_data["centers"], public_edges)
    public_six_cycle_count = simple_cycle_count(
        sorted(public_graph["vertices"]),
        public_graph["adjacency"],
        6,
    )
    extrema_by_code = {
        row["screen_code"]: row
        for row in screen["extrema_rows"]
    }
    closest_all = extrema_by_code[SCREEN_CODES["closest_all"]]
    closest_connected = extrema_by_code[SCREEN_CODES["closest_connected"]]
    max_all = extrema_by_code[SCREEN_CODES["max_all"]]
    max_connected = extrema_by_code[SCREEN_CODES["max_connected"]]
    observable_values = {
        "hex_face_center_count": len(center_data["center_rows"]),
        "candidate_count_all": screen["candidate_count_all"],
        "candidate_count_connected": screen["candidate_count_connected"],
        "simple_public_six_cycle_count": public_six_cycle_count,
        "graham_tolerance_x1e12": GRAHAM_TOLERANCE_X1E12,
        "graham_area_x1e12": GRAHAM_AREA_X1E12,
        "regular_area_x1e12": REGULAR_AREA_X1E12,
        "within_graham_tolerance_all_count": screen[
            "within_graham_tolerance_all_count"
        ],
        "within_graham_tolerance_connected_count": screen[
            "within_graham_tolerance_connected_count"
        ],
        "closest_all_area_x1e12": closest_all["area_x1e12"],
        "closest_all_graham_error_x1e12": closest_all["graham_error_x1e12"],
        "closest_all_connected_flag": closest_all["connected_flag"],
        "closest_connected_area_x1e12": closest_connected["area_x1e12"],
        "closest_connected_graham_error_x1e12": closest_connected[
            "graham_error_x1e12"
        ],
        "max_all_area_x1e12": max_all["area_x1e12"],
        "max_connected_area_x1e12": max_connected["area_x1e12"],
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
        "skeleton_report": skeleton_report,
        "public_graph": public_graph,
        "isomorphism": center_data["isomorphism"],
        "center_rows": center_data["center_rows"],
        "extrema_rows": screen["extrema_rows"],
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    center_table = table_from_rows(CENTER_COLUMNS, rows["center_rows"])
    extrema_table = table_from_rows(EXTREMA_COLUMNS, rows["extrema_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    extrema_by_code = {
        row["screen_code"]: row
        for row in rows["extrema_rows"]
    }
    closest_all = extrema_by_code[SCREEN_CODES["closest_all"]]
    closest_connected = extrema_by_code[SCREEN_CODES["closest_connected"]]
    max_all = extrema_by_code[SCREEN_CODES["max_all"]]
    max_connected = extrema_by_code[SCREEN_CODES["max_connected"]]

    checks = {
        "truncated_skeleton_report_certified": rows["skeleton_report"].get("status")
        == skeleton.STATUS,
        "dual_to_standard_icosahedron_isomorphism_found": len(
            rows["isomorphism"]
        )
        == 12
        and sorted(rows["isomorphism"]) == list(range(12)),
        "twenty_hex_face_barycenters_available": observable_values[
            "hex_face_center_count"
        ]
        == 20,
        "all_and_connected_six_face_candidate_counts_match": (
            observable_values["candidate_count_all"],
            observable_values["candidate_count_connected"],
        )
        == (38_760, 690),
        "public_boundary_has_no_simple_six_face_cycle": observable_values[
            "simple_public_six_cycle_count"
        ]
        == 0,
        "graham_tolerance_screen_is_negative": (
            observable_values["within_graham_tolerance_all_count"],
            observable_values["within_graham_tolerance_connected_count"],
        )
        == (0, 0),
        "closest_all_is_near_regular_but_not_connected": (
            closest_all["area_x1e12"],
            closest_all["regular_error_x1e12"],
            closest_all["graham_error_x1e12"],
            closest_all["connected_flag"],
        )
        == (654_459_905_217, 4_940_905_217, 20_521_094_783, 0),
        "connected_candidate_screen_stays_below_regular": (
            closest_connected["area_x1e12"],
            closest_connected["graham_error_x1e12"],
            closest_connected["connected_flag"],
            max_connected["area_x1e12"],
        )
        == (404_508_497_187, 270_472_502_813, 1, 404_508_497_187),
        "max_all_matches_closest_area_but_is_disconnected": (
            max_all["area_x1e12"],
            max_all["connected_flag"],
        )
        == (654_459_905_217, 0),
        "table_shapes_match_codebooks": (
            tuple(center_table.shape),
            tuple(extrema_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (20, len(CENTER_COLUMNS)),
            (4, len(EXTREMA_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "dual_to_standard_icosahedron_isomorphism": list(rows["isomorphism"]),
        "candidate_counts": {
            "all": observable_values["candidate_count_all"],
            "connected": observable_values["candidate_count_connected"],
            "simple_public_six_cycles": observable_values[
                "simple_public_six_cycle_count"
            ],
        },
        "graham_reference": {
            "graham_area_x1e12": GRAHAM_AREA_X1E12,
            "regular_area_x1e12": REGULAR_AREA_X1E12,
            "tolerance_x1e12": GRAHAM_TOLERANCE_X1E12,
        },
        "closest_all": closest_all,
        "max_all": max_all,
        "closest_connected": closest_connected,
        "max_connected": max_connected,
        "center_table_sha256": skeleton.sha_array(center_table),
        "extrema_table_sha256": skeleton.sha_array(extrema_table),
        "observable_table_sha256": skeleton.sha_array(observable_table),
    }

    screen = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen@1",
        "object": "C985->d20",
        "construction": {
            "carrier": "certified 60/90 truncated-icosahedral boundary skeleton",
            "coordinate_model": "standard icosahedron coordinates pulled back through a deterministic dual-graph isomorphism",
            "hex_face_point": "barycenter of each of the 20 truncated hexagonal faces",
            "six_face_shadow": "best-fit two-dimensional PCA projection of each six-face candidate",
            "normalization": "projected polygon area divided by projected squared diameter",
        },
        "reference": witness["graham_reference"],
        "extrema": {
            "closest_all": closest_all,
            "max_all": max_all,
            "closest_connected": closest_connected,
            "max_connected": max_connected,
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_HEX_FACE_BARYCENTER_GRAHAM_SCREEN_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The lifted 60/90 boundary carrier is real, but its canonical "
            "hex-face-barycenter PCA shadow does not realize the Graham "
            "biggest-little-hexagon throat. The closest all-subset shadow sits "
            "near the regular diameter-one hexagon baseline but is disconnected "
            "in the public d20 boundary. Connected six-face throat candidates "
            "remain far below both regular and Graham area levels. This rules "
            "out this face-barycenter PCA shadow as the Graham metric, not the "
            "deeper eta6 metric itself."
        ),
        "stage_protocol": {
            "draft": "start from the certified 60/90 truncated boundary skeleton",
            "witness": "assign standard icosahedral coordinates and compute 20 hex-face barycenters",
            "coherence": "screen all six-face subsets and connected six-face public-boundary candidates",
            "closure": "certify that this canonical face-barycenter PCA proxy has no Graham-tolerance hits",
            "emit": "emit center, extrema, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "truncated_skeleton_report": skeleton.input_entry(
                TRUNCATED_SKELETON_REPORT,
                {
                    "status": rows["skeleton_report"].get("status"),
                    "certificate_sha256": rows["skeleton_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "truncated_skeleton_tables": skeleton.input_entry(
                TRUNCATED_SKELETON_TABLES
            ),
            "hcycle_edge_table": skeleton.input_entry(skeleton.HCYCLE_EDGE_TABLE),
            "derive_script": skeleton.input_entry(DERIVE_SCRIPT),
            "validator": skeleton.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": skeleton.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "screen": skeleton.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen.json"
            ),
            "centers_csv": skeleton.relpath(
                OUT_DIR / "eta6_hex_face_barycenter_centers.csv"
            ),
            "extrema_csv": skeleton.relpath(
                OUT_DIR / "eta6_hex_face_barycenter_extrema.csv"
            ),
            "observables_csv": skeleton.relpath(
                OUT_DIR / "eta6_hex_face_barycenter_observables.csv"
            ),
            "tables": skeleton.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_tables.npz"
            ),
            "certificate": skeleton.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_certificate.json"
            ),
            "manifest": skeleton.relpath(OUT_DIR / "manifest.json"),
            "report": skeleton.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the 20 hexagonal faces of the lifted 60/90 skeleton have deterministic barycenter coordinates",
                "all 38,760 six-face barycenter PCA shadows have no Graham-tolerance area hit",
                "all 690 connected six-face candidates also have no Graham-tolerance area hit",
                "the best connected six-face PCA shadow remains well below the regular and Graham baselines",
            ],
            "does_not_certify_because_not_required": [
                "that Graham's hexagon is irrelevant to eta6",
                "an intrinsic spherical or graph-geodesic area metric on the truncated skeleton",
                "that an eta6-selected collar or F-symbol seam cannot realize a Graham-like throat",
                "that conductance relaxation has reached its asymptotic metric normal form",
            ],
        },
        "next_highest_yield_item": (
            "Replace PCA face-center shadows with an intrinsic truncated-skeleton "
            "metric: spherical/geodesic six-face area, eta6-selected face collars, "
            "or the actual F-symbol seam coordinates."
        ),
    }
    report["certificate_sha256"] = skeleton.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 60/90 skeleton is the correct lifted carrier for this screen",
            "the face-barycenter PCA proxy is not the Graham metric",
            "the next metric has to be intrinsic to the lifted skeleton or selected by eta6/F-symbol seam data",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified 60/90 truncated skeleton report and tables",
            "derive the public-boundary dual graph and deterministic icosahedral coordinate isomorphism",
            "compute the 20 truncated hex-face barycenters",
            "screen all six-face subsets and connected six-face public-boundary candidates",
            "check no candidate lies within the declared Graham area tolerance",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = skeleton.self_hash(manifest, "manifest_sha256")

    return {
        "screen": screen,
        "centers_csv": skeleton.csv_text(CENTER_COLUMNS, rows["center_rows"]),
        "extrema_csv": skeleton.csv_text(EXTREMA_COLUMNS, rows["extrema_rows"]),
        "observables_csv": skeleton.csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "center_table": center_table,
        "extrema_table": extrema_table,
        "observable_table": observable_table,
        "certificate": certificate,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if skeleton.INDEX_PATH.exists():
        index_payload = load_json(skeleton.INDEX_PATH)
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
            "manifest": skeleton.relpath(OUT_DIR / "manifest.json"),
            "report": skeleton.relpath(OUT_DIR / "report.json"),
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
    updated["registry_sha256"] = skeleton.self_hash(updated, "registry_sha256")
    skeleton.write_json(skeleton.INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    skeleton.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen.json",
        payloads["screen"],
    )
    (OUT_DIR / "eta6_hex_face_barycenter_centers.csv").write_text(
        payloads["centers_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_hex_face_barycenter_extrema.csv").write_text(
        payloads["extrema_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_hex_face_barycenter_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_tables.npz",
        center_table=payloads["center_table"],
        extrema_table=payloads["extrema_table"],
        observable_table=payloads["observable_table"],
    )
    skeleton.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_certificate.json",
        payloads["certificate"],
    )
    skeleton.write_json(OUT_DIR / "report.json", payloads["report"])
    skeleton.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": skeleton.relpath(OUT_DIR / "report.json"),
                "manifest": skeleton.relpath(OUT_DIR / "manifest.json"),
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
