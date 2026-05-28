from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter
from typing import Any

import numpy as np

try:
    from . import derive_eta6_hit2 as hit2
    from . import derive_eta6_repl as repl
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_eta6_hit2 as hit2
    import derive_eta6_repl as repl
    from paths import D20_INVARIANTS, ROOT


pair = repl.pair

THEOREM_ID = "eta6_p2"
STATUS = "ETA6_P2_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REPL_REPORT = repl.OUT_DIR / "report.json"
HIT2_REPORT = hit2.OUT_DIR / "report.json"
REPL_VERTS = repl.OUT_DIR / "verts.csv"
REPL_FACES = repl.OUT_DIR / "faces.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p2.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p2.py"

HULL_EPS = 1.0e-8
REMOVED_OLD_LOCAL = [42, 40, 49, 48, 52, 53]
HIT_OLD_LOCAL = [41, 50, 51]
HIT_ORIGINAL = [41, 52, 55]

VERTEX_COLUMNS = [
    "vertex_id",
    "old_local_vertex_id",
    "original_vertex_id",
    "x_x1e12",
    "y_x1e12",
    "z_x1e12",
]
EDGE_COLUMNS = ["edge_id", "source_vertex_id", "target_vertex_id"]
FACE_COLUMNS = [
    "face_id",
    "old_face_id",
    "kind_code",
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
SAMPLE_COLUMNS = repl.SAMPLE_COLUMNS
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
    "degree_three_vertex_count": 12,
    "degree_five_vertex_count": 13,
    "cubic_carrier_flag": 14,
    "central_face_id": 15,
    "source_exact_face_count": 16,
    "source_shrunk_face_count": 17,
    "fused_face_count": 18,
    "cap_face_count": 19,
    "support_row_count": 20,
    "support_positive_row_count": 21,
    "support_zero_row_count": 22,
    "min_support_slack_x1e12": 23,
    "max_support_slack_x1e12": 24,
    "positive_support_cone_flag": 25,
    "collinear_triple_count": 26,
    "minimal_c4_count": 27,
    "minimal_c5_count": 28,
    "minimal_affine_circuit_count": 29,
    "circuit_census_gap_flag": 30,
    "signed_row_count": 31,
    "zero_pairing_count": 32,
    "positive_pairing_count": 33,
    "min_positive_pairing": 34,
    "max_positive_pairing_bit_length": 35,
    "strict_height_orientation_flag": 36,
    "eta6_identity_transfer_ready_flag": 37,
    "valence_change_flag": 38,
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


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def read_csv_ints(path) -> list[dict[str, int]]:
    import csv

    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def sequence_hash(values: list[tuple[int, ...]]) -> str:
    digest = hashlib.sha256()
    for row in values:
        digest.update((",".join(str(value) for value in row) + "\n").encode("ascii"))
    return digest.hexdigest()


def hull_face_sets(
    points: dict[int, np.ndarray],
    vertices: list[int],
) -> list[tuple[int, ...]]:
    face_sets: set[tuple[int, ...]] = set()
    for left, middle, right in itertools.combinations(vertices, 3):
        a = points[left]
        b = points[middle]
        c = points[right]
        normal = np.cross(b - a, c - a)
        if float(np.linalg.norm(normal)) < 1.0e-10:
            continue
        signed = np.asarray(
            [float(np.dot(points[vertex] - a, normal)) for vertex in vertices],
            dtype=np.float64,
        )
        if bool(np.all(signed >= -HULL_EPS)) or bool(np.all(signed <= HULL_EPS)):
            coplanar = tuple(
                sorted(
                    vertex
                    for vertex, distance in zip(vertices, signed)
                    if abs(float(distance)) <= HULL_EPS
                )
            )
            if len(coplanar) >= 3:
                face_sets.add(coplanar)

    maximal: list[tuple[int, ...]] = []
    for face in sorted(face_sets, key=lambda row: (len(row), row), reverse=True):
        face_set = set(face)
        if not any(face_set < set(existing) for existing in maximal):
            maximal.append(face)
    return sorted(maximal)


def ordered_face(
    face: tuple[int, ...],
    points: dict[int, np.ndarray],
    old_to_new: dict[int, int],
) -> list[int]:
    vertices = list(face)
    face_points = np.asarray([points[vertex] for vertex in vertices], dtype=np.float64)
    center = np.mean(face_points, axis=0)
    normal = np.zeros(3, dtype=np.float64)
    for left, middle, right in itertools.combinations(range(len(vertices)), 3):
        normal = np.cross(
            face_points[middle] - face_points[left],
            face_points[right] - face_points[left],
        )
        if float(np.linalg.norm(normal)) > 1.0e-10:
            break
    normal = normal / float(np.linalg.norm(normal))
    axis_u = face_points[0] - center
    axis_u = axis_u / float(np.linalg.norm(axis_u))
    axis_v = np.cross(normal, axis_u)
    angles = [
        (
            math.atan2(
                float(np.dot(point - center, axis_v)),
                float(np.dot(point - center, axis_u)),
            ),
            vertex,
        )
        for point, vertex in zip(face_points, vertices)
    ]
    ordered = [vertex for _, vertex in sorted(angles)]
    rotation = min(range(len(ordered)), key=lambda index: old_to_new[ordered[index]])
    return ordered[rotation:] + ordered[:rotation]


def face_cycle(row: dict[str, int]) -> list[int]:
    return [row[f"cycle_v{index}"] for index in range(row["face_size"])]


def build_patch_rows() -> dict[str, Any]:
    old_vertex_rows = read_csv_ints(REPL_VERTS)
    old_face_rows = read_csv_ints(REPL_FACES)
    removed = set(REMOVED_OLD_LOCAL)
    old_points = {
        row["vertex_id"]: np.asarray(
            [row["x_x1e12"], row["y_x1e12"], row["z_x1e12"]],
            dtype=np.float64,
        )
        / float(repl.ext.SCALE)
        for row in old_vertex_rows
    }
    original_by_old = {
        row["vertex_id"]: row["original_vertex_id"]
        for row in old_vertex_rows
    }
    kept_old = [
        row["vertex_id"]
        for row in old_vertex_rows
        if row["vertex_id"] not in removed
    ]
    old_to_new = {old_id: new_id for new_id, old_id in enumerate(kept_old)}
    new_to_old = {new_id: old_id for old_id, new_id in old_to_new.items()}
    vertex_rows = []
    coords = {}
    for new_id, old_id in enumerate(kept_old):
        point = old_points[old_id]
        vertex_rows.append(
            {
                "vertex_id": new_id,
                "old_local_vertex_id": old_id,
                "original_vertex_id": original_by_old[old_id],
                "x_x1e12": repl.ext.scaled(point[0]),
                "y_x1e12": repl.ext.scaled(point[1]),
                "z_x1e12": repl.ext.scaled(point[2]),
            }
        )
        coords[new_id] = point

    old_face_by_shrunk = {}
    old_face_by_exact = {}
    for face in old_face_rows:
        old_cycle = face_cycle(face)
        old_face_by_exact[tuple(sorted(old_cycle))] = face
        shrunk = tuple(sorted(vertex for vertex in old_cycle if vertex not in removed))
        if len(shrunk) >= 3:
            old_face_by_shrunk[shrunk] = face

    hit_set = tuple(sorted(HIT_OLD_LOCAL))
    face_rows = []
    old_cycles = []
    for old_face in hull_face_sets(old_points, kept_old):
        old_cycle = ordered_face(old_face, old_points, old_to_new)
        old_set = tuple(sorted(old_cycle))
        old_cycles.append(old_set)
        if old_set == hit_set:
            old_face_id = 31
            source_id = next(face["source_id"] for face in old_face_rows if face["face_id"] == 31)
            kind_code = 3
        elif old_set in old_face_by_exact:
            source = old_face_by_exact[old_set]
            old_face_id = source["face_id"]
            source_id = source["source_id"]
            kind_code = 0
        elif old_set in old_face_by_shrunk:
            source = old_face_by_shrunk[old_set]
            old_face_id = source["face_id"]
            source_id = source["source_id"]
            kind_code = 1
        else:
            old_face_id = -1
            source_id = -1
            kind_code = 2
        new_cycle = [old_to_new[vertex] for vertex in old_cycle]
        padded = new_cycle + [-1] * (6 - len(new_cycle))
        face_rows.append(
            {
                "face_id": len(face_rows),
                "old_face_id": old_face_id,
                "kind_code": kind_code,
                "source_id": source_id,
                "face_type_code": len(new_cycle),
                "face_size": len(new_cycle),
                "cycle_v0": padded[0],
                "cycle_v1": padded[1],
                "cycle_v2": padded[2],
                "cycle_v3": padded[3],
                "cycle_v4": padded[4],
                "cycle_v5": padded[5],
            }
        )

    edge_rows = repl.edge_rows_from_faces(face_rows)
    support_rows = repl.build_support_rows(face_rows, coords)
    circuit_stats = repl.replacement_circuit_stats(vertex_rows)
    edge_counter = Counter()
    for face in face_rows:
        cycle = face_cycle(face)
        for left, right in zip(cycle, cycle[1:] + cycle[:1]):
            edge_counter[tuple(sorted((left, right)))] += 1
    degrees = Counter()
    for edge in edge_rows:
        degrees[edge["source_vertex_id"]] += 1
        degrees[edge["target_vertex_id"]] += 1
    face_sizes = Counter(row["face_size"] for row in face_rows)
    kind_counts = Counter(row["kind_code"] for row in face_rows)
    slacks = [row["slack_x1e12"] for row in support_rows]
    central_face_id = next(
        row["face_id"]
        for row in face_rows
        if set(new_to_old[row[f"cycle_v{index}"]] for index in range(row["face_size"]))
        == set(HIT_OLD_LOCAL)
    )
    high_degree_originals = [
        original_by_old[new_to_old[vertex_id]]
        for vertex_id, degree in sorted(degrees.items())
        if degree == 5
    ]
    obs_values = {
        "vertex_count": len(vertex_rows),
        "removed_vertex_count": len(removed),
        "edge_count": len(edge_rows),
        "face_count": len(face_rows),
        "triangle_face_count": face_sizes[3],
        "quadrilateral_face_count": face_sizes[4],
        "pentagon_face_count": face_sizes[5],
        "hexagon_face_count": face_sizes[6],
        "euler_characteristic": len(vertex_rows) - len(edge_rows) + len(face_rows),
        "connected_flag": int(
            repl.components(
                len(vertex_rows),
                {
                    (row["source_vertex_id"], row["target_vertex_id"])
                    for row in edge_rows
                },
            )
            == 1
        ),
        "three_vertex_connected_flag": int(
            repl.three_vertex_connected(
                len(vertex_rows),
                {
                    (row["source_vertex_id"], row["target_vertex_id"])
                    for row in edge_rows
                },
            )
        ),
        "edge_two_face_incidence_flag": int(set(edge_counter.values()) == {2}),
        "degree_three_vertex_count": sum(degree == 3 for degree in degrees.values()),
        "degree_five_vertex_count": sum(degree == 5 for degree in degrees.values()),
        "cubic_carrier_flag": int(all(degree == 3 for degree in degrees.values())),
        "central_face_id": central_face_id,
        "source_exact_face_count": kind_counts[0],
        "source_shrunk_face_count": kind_counts[1],
        "fused_face_count": kind_counts[2],
        "cap_face_count": kind_counts[3],
        "support_row_count": len(support_rows),
        "support_positive_row_count": sum(value > 0 for value in slacks),
        "support_zero_row_count": sum(value == 0 for value in slacks),
        "min_support_slack_x1e12": min(slacks),
        "max_support_slack_x1e12": max(slacks),
        "positive_support_cone_flag": int(all(value > 0 for value in slacks)),
        "collinear_triple_count": circuit_stats["collinear_count"],
        "minimal_c4_count": len(circuit_stats["c4_rows"]),
        "minimal_c5_count": circuit_stats["c5_count"],
        "minimal_affine_circuit_count": (
            len(circuit_stats["c4_rows"]) + circuit_stats["c5_count"]
        ),
        "circuit_census_gap_flag": int(
            circuit_stats["collinear_count"] == 0
            and circuit_stats["min_non_c4_det_abs"] > 1e-3
        ),
        "signed_row_count": circuit_stats["row_count"],
        "zero_pairing_count": circuit_stats["zero_count"],
        "positive_pairing_count": circuit_stats["positive_count"],
        "min_positive_pairing": circuit_stats["min_positive"],
        "max_positive_pairing_bit_length": circuit_stats["max_positive"].bit_length(),
        "strict_height_orientation_flag": int(circuit_stats["zero_count"] == 0),
        "eta6_identity_transfer_ready_flag": int(
            len(face_rows) == 32 and all(degree == 3 for degree in degrees.values())
        ),
        "valence_change_flag": int(high_degree_originals == HIT_ORIGINAL),
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
        "removed_old_local": REMOVED_OLD_LOCAL,
        "hit_old_local": HIT_OLD_LOCAL,
        "hit_original": HIT_ORIGINAL,
        "high_degree_originals": high_degree_originals,
        "hull_face_sets_sha256": sequence_hash(old_cycles),
    }


def build_payload_rows() -> dict[str, Any]:
    return {
        "repl_report": load_json(REPL_REPORT),
        "hit2_report": load_json(HIT2_REPORT),
        "patch": build_patch_rows(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    patch = rows["patch"]
    vertex_table = table_from_rows(VERTEX_COLUMNS, patch["vertex_rows"])
    edge_table = table_from_rows(EDGE_COLUMNS, patch["edge_rows"])
    face_table = table_from_rows(FACE_COLUMNS, patch["face_rows"])
    support_table = table_from_rows(SUPP_COLUMNS, patch["support_rows"])
    c4_table = table_from_rows(C4_COLUMNS, patch["circuit_stats"]["c4_rows"])
    sample_table = table_from_rows(SAMPLE_COLUMNS, patch["circuit_stats"]["samples"])
    obs_table = table_from_rows(OBS_COLUMNS, patch["obs_rows"])
    obs = patch["obs_values"]
    checks = {
        "input_certificates_available": (
            rows["repl_report"].get("all_checks_pass") is True
            and rows["hit2_report"].get("all_checks_pass") is True
        ),
        "convex_hull_patch_counts_match_second_hit": (
            obs["vertex_count"],
            obs["removed_vertex_count"],
            obs["edge_count"],
            obs["face_count"],
            obs["triangle_face_count"],
            obs["quadrilateral_face_count"],
            obs["pentagon_face_count"],
            obs["hexagon_face_count"],
            obs["euler_characteristic"],
            obs["central_face_id"],
        )
        == (48, 6, 75, 29, 1, 3, 15, 10, 2, 27),
        "patch_graph_is_polyhedral_but_not_cubic": (
            obs["connected_flag"],
            obs["three_vertex_connected_flag"],
            obs["edge_two_face_incidence_flag"],
            obs["degree_three_vertex_count"],
            obs["degree_five_vertex_count"],
            obs["cubic_carrier_flag"],
            patch["high_degree_originals"],
        )
        == (1, 1, 1, 45, 3, 0, HIT_ORIGINAL),
        "patch_face_sources_show_multi_face_fusion": (
            obs["source_exact_face_count"],
            obs["source_shrunk_face_count"],
            obs["fused_face_count"],
            obs["cap_face_count"],
            obs["eta6_identity_transfer_ready_flag"],
            obs["valence_change_flag"],
            patch["hull_face_sets_sha256"],
        )
        == (
            19,
            6,
            3,
            1,
            0,
            1,
            "d48c8dc86f78e6e1f7872fcdf48f0f7ed44c4e04d9b02315ae9259c65db4196b",
        ),
        "patch_support_cone_is_positive": (
            obs["support_row_count"],
            obs["support_positive_row_count"],
            obs["support_zero_row_count"],
            obs["min_support_slack_x1e12"],
            obs["max_support_slack_x1e12"],
            obs["positive_support_cone_flag"],
        )
        == (1_242, 1_242, 0, 147_018_786_278, 3_103_251_249_022, 1),
        "patch_affine_circuit_census_has_gap": (
            obs["collinear_triple_count"],
            obs["minimal_c4_count"],
            obs["minimal_c5_count"],
            obs["minimal_affine_circuit_count"],
            obs["circuit_census_gap_flag"],
            patch["circuit_stats"]["c4_hash"],
        )
        == (
            0,
            4_626,
            1_518_732,
            1_523_358,
            1,
            "909e0b8e20e0d924dd267787687d55e1953b5340fd83ace128ccbabd2fc68693",
        ),
        "patch_height_orientation_is_strict": (
            obs["signed_row_count"],
            obs["zero_pairing_count"],
            obs["positive_pairing_count"],
            obs["min_positive_pairing"],
            obs["max_positive_pairing_bit_length"],
            obs["strict_height_orientation_flag"],
            patch["circuit_stats"]["row_stream_sha256"],
            patch["circuit_stats"]["support_stream_sha256"],
        )
        == (
            1_523_358,
            0,
            1_523_358,
            146,
            140,
            1,
            "282b0ae02d1ccd34bca5e8f2f84b9fdc8bfb913108d7a10a2ab6a2e450116f50",
            "ce39fd237012c2a5ef57d0cb33b7aa556064878383b082ae625fdb02ebcbaf8e",
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
            (48, len(VERTEX_COLUMNS)),
            (75, len(EDGE_COLUMNS)),
            (29, len(FACE_COLUMNS)),
            (1_242, len(SUPP_COLUMNS)),
            (4_626, len(C4_COLUMNS)),
            (repl.SAMPLE_LIMIT, len(SAMPLE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "removed_old_local_vertices": patch["removed_old_local"],
        "hit_old_local_vertices": patch["hit_old_local"],
        "hit_original_vertices": patch["hit_original"],
        "high_degree_original_vertices": patch["high_degree_originals"],
        "hull_face_sets_sha256": patch["hull_face_sets_sha256"],
        "support": {
            "support_rows": obs["support_row_count"],
            "min_slack_x1e12": obs["min_support_slack_x1e12"],
            "max_slack_x1e12": obs["max_support_slack_x1e12"],
        },
        "circuits": {
            "minimal_c4_count": obs["minimal_c4_count"],
            "minimal_c5_count": obs["minimal_c5_count"],
            "row_stream_sha256": patch["circuit_stats"]["row_stream_sha256"],
            "support_stream_sha256": patch["circuit_stats"]["support_stream_sha256"],
            "min_positive_pairing": obs["min_positive_pairing"],
        },
        "eta6_transfer_boundary": (
            "The previous identity transfer expects a 32-face cubic carrier. "
            "This patch has 29 faces and three degree-5 hit vertices, so eta6 "
            "transfer must be reformulated before claiming preservation."
        ),
        "observable_table_sha256": pair.parent.sha_array(obs_table),
        "vertex_table_sha256": pair.parent.sha_array(vertex_table),
        "edge_table_sha256": pair.parent.sha_array(edge_table),
        "face_table_sha256": pair.parent.sha_array(face_table),
        "support_table_sha256": pair.parent.sha_array(support_table),
        "c4_table_sha256": pair.parent.sha_array(c4_table),
        "sample_table_sha256": pair.parent.sha_array(sample_table),
    }
    p2 = {
        "schema": "eta6.p2@1",
        "object": "eta6",
        "construction": {
            "patch": "convex hull after deleting the six second-hit face-31 vertices",
            "classification": "support-positive valence-change patch",
            "reading": (
                "the three-edge collapse has a valid convex multi-face patch, "
                "but the carrier leaves the old cubic/32-face transfer regime"
            ),
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p2.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P2_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The second-hit three-edge collapse has a concrete convex hull "
            "patch: delete the six old face-31 vertices and keep the three hit "
            "vertices as a central triangle. The resulting carrier has 48 "
            "vertices, 75 edges, 29 faces, Euler characteristic 2, "
            "3-vertex-connected graph incidence, all 1,242 support rows "
            "strictly positive, and all 1,523,358 minimal affine circuit rows "
            "strictly oriented with minimum deterministic margin 146. The "
            "patch is not cubic: the three hit vertices have degree 5, so the "
            "previous 32-face identity eta6 transfer is no longer applicable "
            "without a new transfer law."
        ),
        "stage_protocol": {
            "draft": "start from eta6_repl and eta6_hit2",
            "witness": "delete the second-hit face-31 cycle and compute the convex hull of the remaining vertices",
            "coherence": "check graph incidence, support positivity, circuit census, and row orientation",
            "closure": "certify the multi-face patch as support-positive and record the eta6 transfer boundary",
            "emit": "emit compact p2 artifacts, verifier command, and next seam",
        },
        "inputs": {
            "repl_report": pair.parent.input_entry(
                REPL_REPORT,
                {
                    "status": rows["repl_report"].get("status"),
                    "certificate_sha256": rows["repl_report"].get("certificate_sha256"),
                },
            ),
            "hit2_report": pair.parent.input_entry(
                HIT2_REPORT,
                {
                    "status": rows["hit2_report"].get("status"),
                    "certificate_sha256": rows["hit2_report"].get("certificate_sha256"),
                },
            ),
            "repl_verts": pair.parent.input_entry(REPL_VERTS),
            "repl_faces": pair.parent.input_entry(REPL_FACES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p2": pair.parent.relpath(OUT_DIR / "p2.json"),
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
                "a concrete convex multi-face patch for the second-hit collapse",
                "positive support cone for the patched carrier",
                "minimal affine circuit census and strict deterministic row orientation",
                "the old cubic/32-face eta6 transfer rule is not applicable to this valence-changed patch",
            ],
            "does_not_certify_because_not_required": [
                "eta6 preservation through a new non-cubic transfer law",
                "C985 associator data on the patched carrier",
                "global automaton closure after repeated patches",
            ],
        },
        "next_highest_yield_item": (
            "Define the eta6 transfer law for the non-cubic 48/75/29 patch, "
            "or prove that the degree-5 triangle is a genuine transfer obstruction."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p2.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p2.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")
    return {
        "p2": p2,
        "verts_csv": csv_text(VERTEX_COLUMNS, patch["vertex_rows"]),
        "edges_csv": csv_text(EDGE_COLUMNS, patch["edge_rows"]),
        "faces_csv": csv_text(FACE_COLUMNS, patch["face_rows"]),
        "supp_csv": csv_text(SUPP_COLUMNS, patch["support_rows"]),
        "c4_csv": csv_text(C4_COLUMNS, patch["circuit_stats"]["c4_rows"]),
        "samp_csv": csv_text(SAMPLE_COLUMNS, patch["circuit_stats"]["samples"]),
        "obs_csv": pair.csv_text(OBS_COLUMNS, patch["obs_rows"]),
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
    index_path = repl.ext.nonholonomic.preservation.INDEX_PATH
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
    pair.parent.write_json(OUT_DIR / "p2.json", payloads["p2"])
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
