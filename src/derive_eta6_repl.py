from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_eta6_truncated_skeleton as skeleton
    from . import derive_eta6_aext as aext
    from . import derive_eta6_ext_cone as ext
    from . import derive_eta6_srows as srows
    from . import derive_eta6_surg as surg
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_eta6_truncated_skeleton as skeleton
    import derive_eta6_aext as aext
    import derive_eta6_ext_cone as ext
    import derive_eta6_srows as srows
    import derive_eta6_surg as surg
    from paths import D20_INVARIANTS, ROOT


pair = ext.pair

THEOREM_ID = "eta6_repl"
STATUS = "ETA6_REPL_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SURG_REPORT = surg.OUT_DIR / "report.json"
TRUNCATED_REPORT = skeleton.OUT_DIR / "report.json"
TRUNCATED_TABLES = skeleton.OUT_DIR / "eta6_truncated_skeleton_tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_repl.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_repl.py"

REMOVED_ORIGINAL_VERTICES = [43, 53, 54, 59, 57, 44]
CAP_ORIGINAL_VERTICES = [42, 40, 51, 50, 56, 58]

VERTEX_COLUMNS = [
    "vertex_id",
    "original_vertex_id",
    "x_x1e12",
    "y_x1e12",
    "z_x1e12",
]
EDGE_COLUMNS = ["edge_id", "source_vertex_id", "target_vertex_id"]
FACE_COLUMNS = [
    "face_id",
    "old_face_id",
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
SUPP_COLUMNS = [
    "support_row_id",
    "face_id",
    "vertex_id",
    "face_type_code",
    "face_size",
    "slack_x1e12",
    "positive_flag",
]
C4_COLUMNS = ["circuit_id", "v0", "v1", "v2", "v3"]
SAMPLE_COLUMNS = [
    "sample_id",
    "circuit_size",
    "v0",
    "v1",
    "v2",
    "v3",
    "v4",
    "pairing_value_bit_length",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "vertex_count": 0,
    "removed_vertex_count": 1,
    "edge_count": 2,
    "face_count": 3,
    "triangle_face_count": 4,
    "quadrilateral_face_count": 5,
    "pentagon_face_count": 6,
    "hexagon_face_count": 7,
    "euler_characteristic": 8,
    "connected_flag": 9,
    "three_vertex_connected_flag": 10,
    "edge_two_face_incidence_flag": 11,
    "support_row_count": 12,
    "support_positive_row_count": 13,
    "support_zero_row_count": 14,
    "min_support_slack_x1e12": 15,
    "max_support_slack_x1e12": 16,
    "positive_support_cone_flag": 17,
    "collinear_triple_count": 18,
    "minimal_c4_count": 19,
    "minimal_c5_count": 20,
    "minimal_affine_circuit_count": 21,
    "max_c4_det_abs_x1e15": 22,
    "min_non_c4_det_abs_x1e12": 23,
    "circuit_census_gap_flag": 24,
    "signed_row_count": 25,
    "zero_pairing_count": 26,
    "positive_pairing_count": 27,
    "min_positive_pairing": 28,
    "max_positive_pairing_bit_length": 29,
    "strict_height_orientation_flag": 30,
}
SAMPLE_LIMIT = 16


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


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def face_cycle(row: dict[str, int]) -> list[int]:
    return [row[f"cycle_v{index}"] for index in range(row["face_size"])]


def replacement_faces(
    old_faces: list[dict[str, int]],
    original_to_local: dict[int, int],
) -> list[dict[str, int]]:
    removed = set(REMOVED_ORIGINAL_VERTICES)
    cap = [original_to_local[vertex] for vertex in CAP_ORIGINAL_VERTICES]
    rows = []
    for old in old_faces:
        old_cycle = face_cycle(old)
        if old["face_id"] == 31:
            cycle = cap
            face_type = 6
        elif removed & set(old_cycle):
            cycle = [
                original_to_local[vertex]
                for vertex in old_cycle
                if vertex not in removed
            ]
            face_type = len(cycle)
        else:
            cycle = [original_to_local[vertex] for vertex in old_cycle]
            face_type = old["face_size"]
        padded = cycle + [-1] * (6 - len(cycle))
        rows.append(
            {
                "face_id": len(rows),
                "old_face_id": old["face_id"],
                "face_type_code": face_type,
                "source_id": old["source_id"],
                "face_size": len(cycle),
                "cycle_v0": padded[0],
                "cycle_v1": padded[1],
                "cycle_v2": padded[2],
                "cycle_v3": padded[3],
                "cycle_v4": padded[4],
                "cycle_v5": padded[5],
            }
        )
    return rows


def edge_rows_from_faces(face_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    edges = set()
    for face in face_rows:
        cycle = face_cycle(face)
        for left, right in zip(cycle, cycle[1:] + cycle[:1]):
            edges.add(tuple(sorted((left, right))))
    return [
        {"edge_id": edge_id, "source_vertex_id": left, "target_vertex_id": right}
        for edge_id, (left, right) in enumerate(sorted(edges))
    ]


def components(vertex_count: int, edges: set[tuple[int, int]], removed: set[int] | None = None) -> int:
    removed = removed or set()
    vertices = [vertex for vertex in range(vertex_count) if vertex not in removed]
    if not vertices:
        return 0
    adjacency = {vertex: set() for vertex in vertices}
    for left, right in edges:
        if left in removed or right in removed:
            continue
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[int] = set()
    count = 0
    for start in vertices:
        if start in seen:
            continue
        count += 1
        seen.add(start)
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbor in adjacency[vertex]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return count


def three_vertex_connected(vertex_count: int, edges: set[tuple[int, int]]) -> bool:
    if components(vertex_count, edges) != 1:
        return False
    vertices = range(vertex_count)
    for size in (1, 2):
        for removed in combinations(vertices, size):
            if components(vertex_count, edges, set(removed)) != 1:
                return False
    return True


def build_support_rows(
    face_rows: list[dict[str, int]],
    coords: dict[int, np.ndarray],
) -> list[dict[str, int]]:
    origin = np.mean(np.asarray(list(coords.values())), axis=0)
    rows = []
    for face in face_rows:
        cycle = face_cycle(face)
        cycle_set = set(cycle)
        normal, offset = ext.oriented_face_support(cycle, coords, origin)
        for vertex_id in sorted(coords):
            if vertex_id in cycle_set:
                continue
            slack = offset - float(np.dot(normal, coords[vertex_id]))
            slack_x1e12 = ext.scaled(slack)
            rows.append(
                {
                    "support_row_id": len(rows),
                    "face_id": face["face_id"],
                    "vertex_id": vertex_id,
                    "face_type_code": face["face_type_code"],
                    "face_size": face["face_size"],
                    "slack_x1e12": slack_x1e12,
                    "positive_flag": int(slack_x1e12 > 0),
                }
            )
    return rows


def circuit_key(vertices: tuple[int, ...]) -> bytes:
    return (",".join(str(vertex_id) for vertex_id in vertices) + "\n").encode("ascii")


def det4_abs(matrix: np.ndarray, vertices: tuple[int, int, int, int]) -> float:
    return abs(float(np.linalg.det(matrix[list(vertices)])))


def triple_area(points: np.ndarray, vertices: tuple[int, int, int]) -> float:
    left, middle, right = points[list(vertices)]
    return float(np.linalg.norm(np.cross(middle - left, right - left)))


def sample_row(
    sample_id: int,
    support: tuple[int, ...],
    pairing_value: int,
) -> dict[str, int]:
    padded = list(support) + [-1] * (5 - len(support))
    return {
        "sample_id": sample_id,
        "circuit_size": len(support),
        "v0": padded[0],
        "v1": padded[1],
        "v2": padded[2],
        "v3": padded[3],
        "v4": padded[4],
        "pairing_value_bit_length": pairing_value.bit_length(),
    }


def replacement_circuit_stats(vertex_rows: list[dict[str, int]]) -> dict[str, Any]:
    coords = [
        (
            ext.SCALE,
            row["x_x1e12"],
            row["y_x1e12"],
            row["z_x1e12"],
        )
        for row in vertex_rows
    ]
    points = np.asarray(
        [[row["x_x1e12"], row["y_x1e12"], row["z_x1e12"]] for row in vertex_rows],
        dtype=np.float64,
    ) / float(ext.SCALE)
    homogeneous = np.column_stack([np.ones(len(points)), points])

    collinear_count = 0
    min_non_collinear_area = float("inf")
    for triple in combinations(range(len(points)), 3):
        area = triple_area(points, triple)
        if area < aext.COLLINEAR_EPS:
            collinear_count += 1
        else:
            min_non_collinear_area = min(min_non_collinear_area, area)

    c4_rows = []
    c4_set: set[tuple[int, int, int, int]] = set()
    c4_hash = hashlib.sha256()
    max_c4_det_abs = 0.0
    min_non_c4_det_abs = float("inf")
    for quad in combinations(range(len(points)), 4):
        det_abs = det4_abs(homogeneous, quad)
        if det_abs < aext.C4_ZERO_EPS:
            c4_set.add(quad)
            c4_hash.update(circuit_key(quad))
            c4_rows.append(
                {
                    "circuit_id": len(c4_rows),
                    "v0": quad[0],
                    "v1": quad[1],
                    "v2": quad[2],
                    "v3": quad[3],
                }
            )
            max_c4_det_abs = max(max_c4_det_abs, det_abs)
        else:
            min_non_c4_det_abs = min(min_non_c4_det_abs, det_abs)

    heights = srows.height_vector(len(coords))
    row_hash = hashlib.sha256()
    support_hash = hashlib.sha256()
    row_count = 0
    c5_count = 0
    zero_count = 0
    positive_count = 0
    min_positive: int | None = None
    max_positive = 0
    samples = []

    def emit(support: tuple[int, ...], coefficients: list[int]) -> None:
        nonlocal row_count
        nonlocal zero_count
        nonlocal positive_count
        nonlocal min_positive
        nonlocal max_positive
        pairing = sum(
            coefficient * heights[vertex_id]
            for coefficient, vertex_id in zip(coefficients, support)
        )
        if pairing < 0:
            coefficients = [-coefficient for coefficient in coefficients]
            pairing = -pairing
        if pairing == 0:
            zero_count += 1
        else:
            positive_count += 1
            min_positive = pairing if min_positive is None else min(min_positive, pairing)
            max_positive = max(max_positive, pairing)
        row_hash.update(srows.row_bytes(support, coefficients, pairing))
        support_hash.update(srows.support_bytes(support))
        if len(samples) < SAMPLE_LIMIT:
            samples.append(sample_row(row_count, support, pairing))
        row_count += 1

    for row in c4_rows:
        support = (row["v0"], row["v1"], row["v2"], row["v3"])
        emit(support, srows.coefs4([coords[index] for index in support]))

    for support in combinations(range(len(coords)), 5):
        if any(tuple(quad) in c4_set for quad in combinations(support, 4)):
            continue
        emit(support, srows.coefs5([coords[index] for index in support]))
        c5_count += 1

    if min_positive is None:
        min_positive = 0

    return {
        "collinear_count": collinear_count,
        "min_non_collinear_area": min_non_collinear_area,
        "c4_rows": c4_rows,
        "c4_hash": c4_hash.hexdigest(),
        "c5_count": c5_count,
        "max_c4_det_abs": max_c4_det_abs,
        "min_non_c4_det_abs": min_non_c4_det_abs,
        "row_count": row_count,
        "zero_count": zero_count,
        "positive_count": positive_count,
        "min_positive": min_positive,
        "max_positive": max_positive,
        "row_stream_sha256": row_hash.hexdigest(),
        "support_stream_sha256": support_hash.hexdigest(),
        "samples": samples,
    }


def build_replacement_rows() -> dict[str, Any]:
    tables = np.load(TRUNCATED_TABLES, allow_pickle=False)
    old_vertex_rows = table_rows(
        np.asarray(tables["vertex_table"], dtype=np.int64),
        skeleton.TRUNCATED_VERTEX_COLUMNS,
    )
    old_face_rows = table_rows(
        np.asarray(tables["face_table"], dtype=np.int64),
        skeleton.TRUNCATED_FACE_COLUMNS,
    )
    old_coords = ext.build_truncated_coordinates(old_vertex_rows)
    kept_originals = [
        vertex_id
        for vertex_id in sorted(old_coords)
        if vertex_id not in set(REMOVED_ORIGINAL_VERTICES)
    ]
    original_to_local = {
        original_id: local_id for local_id, original_id in enumerate(kept_originals)
    }
    vertex_rows = []
    coords = {}
    for local_id, original_id in enumerate(kept_originals):
        coord = old_coords[original_id]
        vertex_rows.append(
            {
                "vertex_id": local_id,
                "original_vertex_id": original_id,
                "x_x1e12": ext.scaled(coord[0]),
                "y_x1e12": ext.scaled(coord[1]),
                "z_x1e12": ext.scaled(coord[2]),
            }
        )
        coords[local_id] = coord
    face_rows = replacement_faces(old_face_rows, original_to_local)
    edge_rows = edge_rows_from_faces(face_rows)
    support_rows = build_support_rows(face_rows, coords)
    circuit_stats = replacement_circuit_stats(vertex_rows)

    edge_counter = Counter()
    for face in face_rows:
        cycle = face_cycle(face)
        for left, right in zip(cycle, cycle[1:] + cycle[:1]):
            edge_counter[tuple(sorted((left, right)))] += 1
    edges = {
        (row["source_vertex_id"], row["target_vertex_id"])
        for row in edge_rows
    }
    slack_values = [row["slack_x1e12"] for row in support_rows]
    face_sizes = Counter(row["face_size"] for row in face_rows)
    obs_values = {
        "vertex_count": len(vertex_rows),
        "removed_vertex_count": len(REMOVED_ORIGINAL_VERTICES),
        "edge_count": len(edge_rows),
        "face_count": len(face_rows),
        "triangle_face_count": face_sizes[3],
        "quadrilateral_face_count": face_sizes[4],
        "pentagon_face_count": face_sizes[5],
        "hexagon_face_count": face_sizes[6],
        "euler_characteristic": len(vertex_rows) - len(edge_rows) + len(face_rows),
        "connected_flag": int(components(len(vertex_rows), edges) == 1),
        "three_vertex_connected_flag": int(three_vertex_connected(len(vertex_rows), edges)),
        "edge_two_face_incidence_flag": int(set(edge_counter.values()) == {2}),
        "support_row_count": len(support_rows),
        "support_positive_row_count": sum(value > 0 for value in slack_values),
        "support_zero_row_count": sum(value == 0 for value in slack_values),
        "min_support_slack_x1e12": min(slack_values),
        "max_support_slack_x1e12": max(slack_values),
        "positive_support_cone_flag": int(all(value > 0 for value in slack_values)),
        "collinear_triple_count": circuit_stats["collinear_count"],
        "minimal_c4_count": len(circuit_stats["c4_rows"]),
        "minimal_c5_count": circuit_stats["c5_count"],
        "minimal_affine_circuit_count": (
            len(circuit_stats["c4_rows"]) + circuit_stats["c5_count"]
        ),
        "max_c4_det_abs_x1e15": int(round(circuit_stats["max_c4_det_abs"] * 1e15)),
        "min_non_c4_det_abs_x1e12": int(
            round(circuit_stats["min_non_c4_det_abs"] * 1e12)
        ),
        "circuit_census_gap_flag": int(
            circuit_stats["max_c4_det_abs"] < aext.C4_ZERO_EPS
            and circuit_stats["min_non_c4_det_abs"] > 1e-3
            and circuit_stats["collinear_count"] == 0
        ),
        "signed_row_count": circuit_stats["row_count"],
        "zero_pairing_count": circuit_stats["zero_count"],
        "positive_pairing_count": circuit_stats["positive_count"],
        "min_positive_pairing": circuit_stats["min_positive"],
        "max_positive_pairing_bit_length": circuit_stats["max_positive"].bit_length(),
        "strict_height_orientation_flag": int(circuit_stats["zero_count"] == 0),
    }
    obs_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value": int(obs_values[name]),
            "scale_code": 0,
        }
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "vertex_rows": vertex_rows,
        "edge_rows": edge_rows,
        "face_rows": face_rows,
        "support_rows": support_rows,
        "circuit_stats": circuit_stats,
        "obs_values": obs_values,
        "obs_rows": obs_rows,
    }


def build_payload_rows() -> dict[str, Any]:
    return {
        "surg_report": load_json(SURG_REPORT),
        "truncated_report": load_json(TRUNCATED_REPORT),
        "repl": build_replacement_rows(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    repl = rows["repl"]
    vertex_table = table_from_rows(VERTEX_COLUMNS, repl["vertex_rows"])
    edge_table = table_from_rows(EDGE_COLUMNS, repl["edge_rows"])
    face_table = table_from_rows(FACE_COLUMNS, repl["face_rows"])
    support_table = table_from_rows(SUPP_COLUMNS, repl["support_rows"])
    c4_table = table_from_rows(C4_COLUMNS, repl["circuit_stats"]["c4_rows"])
    sample_table = table_from_rows(SAMPLE_COLUMNS, repl["circuit_stats"]["samples"])
    obs_table = table_from_rows(OBS_COLUMNS, repl["obs_rows"])
    obs = repl["obs_values"]
    checks = {
        "input_certificates_available": (
            rows["surg_report"].get("all_checks_pass") is True
            and rows["truncated_report"].get("all_checks_pass") is True
        ),
        "replacement_cell_counts_match_first_cut": (
            obs["vertex_count"],
            obs["removed_vertex_count"],
            obs["edge_count"],
            obs["face_count"],
            obs["triangle_face_count"],
            obs["quadrilateral_face_count"],
            obs["pentagon_face_count"],
            obs["hexagon_face_count"],
            obs["euler_characteristic"],
        )
        == (54, 6, 84, 32, 3, 3, 9, 17, 2),
        "replacement_graph_is_polyhedral_candidate": (
            obs["connected_flag"],
            obs["three_vertex_connected_flag"],
            obs["edge_two_face_incidence_flag"],
        )
        == (1, 1, 1),
        "replacement_support_cone_is_positive": (
            obs["support_row_count"],
            obs["support_positive_row_count"],
            obs["support_zero_row_count"],
            obs["min_support_slack_x1e12"],
            obs["max_support_slack_x1e12"],
            obs["positive_support_cone_flag"],
        )
        == (1_560, 1_560, 0, 237_881_393_182, 3_103_251_249_022, 1),
        "replacement_affine_circuit_census_has_gap": (
            obs["collinear_triple_count"],
            obs["minimal_c4_count"],
            obs["minimal_c5_count"],
            obs["minimal_affine_circuit_count"],
            obs["max_c4_det_abs_x1e15"],
            obs["min_non_c4_det_abs_x1e12"],
            obs["circuit_census_gap_flag"],
            repl["circuit_stats"]["c4_hash"],
        )
        == (
            0,
            7_095,
            2_824_272,
            2_831_367,
            5_705,
            34_973_033_701,
            1,
            "a4d6c4e2363ef745b7b0c658be080c907c74391de821af8bca06efd8b7c69c98",
        ),
        "replacement_height_orientation_is_strict": (
            obs["signed_row_count"],
            obs["zero_pairing_count"],
            obs["positive_pairing_count"],
            obs["min_positive_pairing"],
            obs["max_positive_pairing_bit_length"],
            obs["strict_height_orientation_flag"],
            repl["circuit_stats"]["row_stream_sha256"],
            repl["circuit_stats"]["support_stream_sha256"],
        )
        == (
            2_831_367,
            0,
            2_831_367,
            146,
            141,
            1,
            "58a495540af510f0ef52e8d730ffbf58d42c07725971dff463364f67d79e118c",
            "99e478f0cc956ef367eca0ddf24d9b2ea22612ccc0a9ef1b4c4e250a4a5c9477",
        ),
        "table_shapes_match_codebooks": (
            tuple(vertex_table.shape),
            tuple(edge_table.shape),
            tuple(face_table.shape),
            tuple(support_table.shape),
            tuple(c4_table.shape),
            tuple(sample_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (54, len(VERTEX_COLUMNS)),
            (84, len(EDGE_COLUMNS)),
            (32, len(FACE_COLUMNS)),
            (1_560, len(SUPP_COLUMNS)),
            (7_095, len(C4_COLUMNS)),
            (SAMPLE_LIMIT, len(SAMPLE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "removed_original_vertices": REMOVED_ORIGINAL_VERTICES,
        "cap_original_vertices": CAP_ORIGINAL_VERTICES,
        "support": {
            "support_rows": obs["support_row_count"],
            "min_slack_x1e12": obs["min_support_slack_x1e12"],
            "max_slack_x1e12": obs["max_support_slack_x1e12"],
        },
        "circuits": {
            "minimal_c4_count": obs["minimal_c4_count"],
            "minimal_c5_count": obs["minimal_c5_count"],
            "row_stream_sha256": repl["circuit_stats"]["row_stream_sha256"],
            "support_stream_sha256": repl["circuit_stats"]["support_stream_sha256"],
            "min_positive_pairing": obs["min_positive_pairing"],
        },
        "observable_table_sha256": pair.parent.sha_array(obs_table),
        "vertex_table_sha256": pair.parent.sha_array(vertex_table),
        "edge_table_sha256": pair.parent.sha_array(edge_table),
        "face_table_sha256": pair.parent.sha_array(face_table),
        "support_table_sha256": pair.parent.sha_array(support_table),
        "c4_table_sha256": pair.parent.sha_array(c4_table),
        "sample_table_sha256": pair.parent.sha_array(sample_table),
    }
    repl_json = {
        "schema": "eta6.repl@1",
        "object": "eta6",
        "construction": {
            "replacement": "remove the old face-31 hex vertices and cap with the six first-hit vertices",
            "cap_original_vertices": CAP_ORIGINAL_VERTICES,
            "reading": "the first-cut replacement carrier has a positive support cone and strict affine-circuit orientation",
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.repl.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_REPL_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The first face-31 cut has an explicit replacement cell complex: "
            "remove the six old face vertices, shrink the six neighboring faces, "
            "and cap with the six first-hit vertices. The patched carrier has "
            "54 vertices, 84 edges, 32 faces, Euler characteristic 2, a "
            "3-vertex-connected graph, 1,560 strictly positive support rows, "
            "and 2,831,367 minimal affine circuit rows with strict deterministic "
            "height orientation."
        ),
        "stage_protocol": {
            "draft": "start from eta6_surg and the truncated skeleton",
            "witness": "construct the face-31 replacement cap and shrunken adjacent faces",
            "coherence": "check graph incidence, support positivity, circuit census, and signed row orientation",
            "closure": "certify the replacement carrier as support-positive with strict affine-circuit orientation",
            "emit": "emit short repl artifacts, hashes, verifier command, and next target",
        },
        "inputs": {
            "surg_report": pair.parent.input_entry(
                SURG_REPORT,
                {
                    "status": rows["surg_report"].get("status"),
                    "certificate_sha256": rows["surg_report"].get("certificate_sha256"),
                },
            ),
            "truncated_report": pair.parent.input_entry(
                TRUNCATED_REPORT,
                {
                    "status": rows["truncated_report"].get("status"),
                    "certificate_sha256": rows["truncated_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "truncated_tables": pair.parent.input_entry(TRUNCATED_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "repl": pair.parent.relpath(OUT_DIR / "repl.json"),
            "verts_csv": pair.parent.relpath(OUT_DIR / "verts.csv"),
            "edges_csv": pair.parent.relpath(OUT_DIR / "edges.csv"),
            "faces_csv": pair.parent.relpath(OUT_DIR / "faces.csv"),
            "supp_csv": pair.parent.relpath(OUT_DIR / "supp.csv"),
            "c4_csv": pair.parent.relpath(OUT_DIR / "c4.csv"),
            "samp_csv": pair.parent.relpath(OUT_DIR / "samp.csv"),
            "obs_csv": pair.parent.relpath(OUT_DIR / "obs.csv"),
            "tables": pair.parent.relpath(OUT_DIR / "tables.npz"),
            "certificate": pair.parent.relpath(OUT_DIR / "cert.json"),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a concrete replacement cell complex for the face-31 first cut",
                "positive support cone for that replacement carrier",
                "minimal affine circuit census for the replacement coordinates",
                "strict deterministic height orientation of all replacement circuit rows",
            ],
            "does_not_certify_because_not_required": [
                "C985 associator data on the replacement carrier",
                "global automaton closure after repeated surgeries",
                "opening or killing eta6",
            ],
        },
        "next_highest_yield_item": (
            "Compare eta6 support/holonomy before and after the face-31 replacement "
            "to decide whether the cut preserves, transforms, or kills the seam class."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.repl.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.repl.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")
    return {
        "repl": repl_json,
        "verts_csv": csv_text(VERTEX_COLUMNS, repl["vertex_rows"]),
        "edges_csv": csv_text(EDGE_COLUMNS, repl["edge_rows"]),
        "faces_csv": csv_text(FACE_COLUMNS, repl["face_rows"]),
        "supp_csv": csv_text(SUPP_COLUMNS, repl["support_rows"]),
        "c4_csv": csv_text(C4_COLUMNS, repl["circuit_stats"]["c4_rows"]),
        "samp_csv": csv_text(SAMPLE_COLUMNS, repl["circuit_stats"]["samples"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, repl["obs_rows"]),
        "vertex_table": vertex_table,
        "edge_table": edge_table,
        "face_table": face_table,
        "support_table": support_table,
        "c4_table": c4_table,
        "sample_table": sample_table,
        "obs_table": obs_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    index_path = ext.nonholonomic.preservation.INDEX_PATH
    if index_path.exists():
        index_payload = load_json(index_path)
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
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
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
    updated["registry_sha256"] = pair.parent.self_hash(updated, "registry_sha256")
    pair.parent.write_json(index_path, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(OUT_DIR / "repl.json", payloads["repl"])
    (OUT_DIR / "verts.csv").write_text(payloads["verts_csv"], encoding="utf-8")
    (OUT_DIR / "edges.csv").write_text(payloads["edges_csv"], encoding="utf-8")
    (OUT_DIR / "faces.csv").write_text(payloads["faces_csv"], encoding="utf-8")
    (OUT_DIR / "supp.csv").write_text(payloads["supp_csv"], encoding="utf-8")
    (OUT_DIR / "c4.csv").write_text(payloads["c4_csv"], encoding="utf-8")
    (OUT_DIR / "samp.csv").write_text(payloads["samp_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        vertex_table=payloads["vertex_table"],
        edge_table=payloads["edge_table"],
        face_table=payloads["face_table"],
        support_table=payloads["support_table"],
        c4_table=payloads["c4_table"],
        sample_table=payloads["sample_table"],
        observable_table=payloads["obs_table"],
    )
    pair.parent.write_json(OUT_DIR / "cert.json", payloads["cert"])
    pair.parent.write_json(OUT_DIR / "report.json", payloads["report"])
    pair.parent.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": pair.parent.relpath(OUT_DIR / "report.json"),
                "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
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
