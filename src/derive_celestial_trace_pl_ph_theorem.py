from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "celestial_trace_pl_ph"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
EDGE_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
FLAT_TRIANGULAR_SECTORS = 6


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_label(label: str) -> tuple[str, ...]:
    body = label.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError(f"bad D20 label: {label!r}")
    parts = tuple(part.strip() for part in body[1:-1].split(",") if part.strip())
    order = {name: i for i, name in enumerate(H6_LABELS)}
    return tuple(sorted(parts, key=order.__getitem__))


def label_text(parts: tuple[str, ...]) -> str:
    return "{" + ",".join(parts) + "}"


def load_d20_graph() -> tuple[dict[int, tuple[str, ...]], list[dict[str, Any]], dict[int, set[int]]]:
    vertices: dict[int, tuple[str, ...]] = {}
    edges: list[dict[str, Any]] = []
    adjacency: dict[int, set[int]] = defaultdict(set)
    with EDGE_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            u = int(row["u"])
            v = int(row["v"])
            u_label = parse_label(row["u_label"])
            v_label = parse_label(row["v_label"])
            if u in vertices and vertices[u] != u_label:
                raise ValueError(f"inconsistent label for vertex {u}")
            if v in vertices and vertices[v] != v_label:
                raise ValueError(f"inconsistent label for vertex {v}")
            vertices[u] = u_label
            vertices[v] = v_label
            edge = {
                "edge_id": int(row["edge_id"]),
                "u": u,
                "v": v,
                "u_label": label_text(u_label),
                "v_label": label_text(v_label),
                "shared_duad": row["shared_duad"],
                "swapped_pair": row["swapped_pair"],
                "interface_weight": int(row["interface_weight"]),
            }
            edges.append(edge)
            adjacency[u].add(v)
            adjacency[v].add(u)
    return vertices, edges, adjacency


def is_connected(vertices: dict[int, tuple[str, ...]], adjacency: dict[int, set[int]]) -> bool:
    if not vertices:
        return False
    start = next(iter(vertices))
    seen = {start}
    q: deque[int] = deque([start])
    while q:
        u = q.popleft()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return seen == set(vertices)


def canonical_cycle(path: list[int]) -> tuple[int, ...]:
    n = len(path)
    candidates: list[tuple[int, ...]] = []
    for seq in (path, list(reversed(path))):
        for i in range(n):
            candidates.append(tuple(seq[i:] + seq[:i]))
    return min(candidates)


def pentagonal_cycles(vertices: dict[int, tuple[str, ...]], adjacency: dict[int, set[int]]) -> list[tuple[int, ...]]:
    cycles: set[tuple[int, ...]] = set()

    def walk(start: int, current: int, path: list[int]) -> None:
        if len(path) == 5:
            if start in adjacency[current]:
                cycles.add(canonical_cycle(path))
            return
        for nxt in adjacency[current]:
            if nxt in path:
                continue
            walk(start, nxt, path + [nxt])

    for start in sorted(vertices):
        walk(start, start, [start])
    return sorted(cycles)


def cycle_edges(cycle: tuple[int, ...]) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for i, u in enumerate(cycle):
        v = cycle[(i + 1) % len(cycle)]
        out.add(tuple(sorted((u, v))))
    return out


def fraction_obj(value: Fraction) -> dict[str, int | str]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "as_fraction": f"{value.numerator}/{value.denominator}",
    }


def build_theorem() -> dict[str, Any]:
    vertices, edges, adjacency = load_d20_graph()
    edge_set = {tuple(sorted((edge["u"], edge["v"]))) for edge in edges}
    degrees = {v: len(adjacency[v]) for v in sorted(vertices)}
    expected_triples = {tuple(H6_LABELS[i] for i in combo) for combo in combinations(range(6), 3)}
    graph_connected = is_connected(vertices, adjacency)

    faces = pentagonal_cycles(vertices, adjacency)
    face_edges = {i: cycle_edges(face) for i, face in enumerate(faces)}
    edge_face_ids: dict[tuple[int, int], list[int]] = defaultdict(list)
    vertex_face_ids: dict[int, list[int]] = defaultdict(list)
    for face_id, face in enumerate(faces):
        for edge in face_edges[face_id]:
            edge_face_ids[edge].append(face_id)
        for vertex in face:
            vertex_face_ids[vertex].append(face_id)

    dual_edges = {
        tuple(sorted(face_ids)): edge
        for edge, face_ids in edge_face_ids.items()
        if len(face_ids) == 2
    }
    dual_faces = {
        vertex: tuple(sorted(face_ids))
        for vertex, face_ids in vertex_face_ids.items()
    }
    dual_valences = Counter()
    for a, b in dual_edges:
        dual_valences[a] += 1
        dual_valences[b] += 1

    local_defects = []
    total_index = Fraction(0, 1)
    for face_id, face in enumerate(faces):
        valence = dual_valences[face_id]
        defect = Fraction(FLAT_TRIANGULAR_SECTORS - valence, FLAT_TRIANGULAR_SECTORS)
        total_index += defect
        local_defects.append(
            {
                "dual_vertex_id": face_id,
                "primal_pentagon_vertices": list(face),
                "primal_pentagon_labels": [label_text(vertices[v]) for v in face],
                "incident_dual_faces": valence,
                "flat_reference_sectors": FLAT_TRIANGULAR_SECTORS,
                "missing_sector_count": FLAT_TRIANGULAR_SECTORS - valence,
                "index": fraction_obj(defect),
            }
        )

    primal_chi = len(vertices) - len(edge_set) + len(faces)
    dual_chi = len(faces) - len(dual_edges) + len(dual_faces)
    checks = {
        "edge_table_exists": EDGE_CSV.exists(),
        "d20_state_count_is_20": len(vertices) == 20,
        "d20_states_are_all_lambda3_h6": set(vertices.values()) == expected_triples,
        "legal_edge_count_is_30": len(edge_set) == 30,
        "no_duplicate_edges": len(edge_set) == len(edges),
        "graph_is_connected": graph_connected,
        "graph_is_3_regular": set(degrees.values()) == {3},
        "pentagonal_dual_vertex_count_is_12": len(faces) == 12,
        "each_primal_edge_has_two_pentagonal_sides": all(len(edge_face_ids[edge]) == 2 for edge in edge_set),
        "each_d20_state_has_three_dual_vertices": all(len(ids) == 3 for ids in vertex_face_ids.values()),
        "dual_edge_count_is_30": len(dual_edges) == 30,
        "dual_face_count_is_20": len(dual_faces) == 20,
        "dual_vertices_are_valence_5": set(dual_valences.values()) == {5},
        "primal_euler_characteristic_is_2": primal_chi == 2,
        "dual_euler_characteristic_is_2": dual_chi == 2,
        "total_pl_index_is_2": total_index == Fraction(2, 1),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_CELESTIAL_TRACE_PL_POINCARE_HOPF_CERTIFIED"
        if all_checks_pass
        else "D20_CELESTIAL_TRACE_PL_POINCARE_HOPF_NEEDS_REVIEW"
    )
    turn_field = [
        {
            "d20_state_id": vertex,
            "d20_state": label_text(vertices[vertex]),
            "dual_triangle_vertices": list(dual_faces[vertex]),
            "local_rule": "the D20 angular state is the oriented PL triangle dual to the three pentagonal return vertices incident at that state",
        }
        for vertex in sorted(dual_faces)
    ]
    report = {
        "schema": "d20.theorem.celestial_trace_pl_poincare_hopf.v1",
        "status": status,
        "object": "d20",
        "claim": (
            "The D20 boundary graph determines a finite PL celestial screen whose "
            "dual icosahedral surface has total Poincare-Hopf defect 2."
        ),
        "inputs": {
            "hcycle_edge_table": {
                "path": rel(EDGE_CSV),
                "sha256": sha_file(EDGE_CSV),
            },
            "six_channel_boundary": H6_LABELS,
            "public_boundary": "D20 = Lambda^3 H6",
        },
        "derived": {
            "primal_d20_graph": {
                "vertices": len(vertices),
                "edges": len(edge_set),
                "degree_multiset": sorted(degrees.values()),
                "connected": graph_connected,
                "euler_characteristic_with_pentagonal_faces": primal_chi,
            },
            "pentagonal_dual_vertices": [
                {
                    "dual_vertex_id": face_id,
                    "cycle_vertices": list(face),
                    "cycle_labels": [label_text(vertices[v]) for v in face],
                }
                for face_id, face in enumerate(faces)
            ],
            "dual_icosahedral_surface": {
                "vertices": len(faces),
                "edges": len(dual_edges),
                "faces": len(dual_faces),
                "euler_characteristic": dual_chi,
                "face_source": "each dual triangular face is one D20 angular state",
            },
            "turn_field_on_d20_angular_states": turn_field,
            "local_poincare_hopf_defects": local_defects,
            "total_pl_index": fraction_obj(total_index),
        },
        "checks": checks,
        "theorem": {
            "statement": (
                "For the certified D20 H-cycle boundary graph, the PL dual surface "
                "has twelve valence-five vertices. Relative to the six-sector flat "
                "triangular tangent fan, each vertex contributes index 1/6, so the "
                "total finite tangent defect is 12*(1/6)=2=chi(S^2)."
            ),
            "hairy_ball_reading": (
                "Any continuum celestial recovery from this finite angular skeleton "
                "must carry a global tangent-field residue: a zero, pole, vortex, "
                "patch transition, curvature charge, or hidden-sector correction."
            ),
            "not_claimed": [
                "a smooth continuum S^2 has been constructed",
                "BMS flux balance is already certified",
                "the A985 residual term vanishes globally",
            ],
        },
        "next_highest_yield_item": (
            "Promote this PL defect ledger into a finite flux-balance theorem by "
            "typing each closed D20 return as Flux_D20(gamma)+Res_A985(gamma) and "
            "certifying the coherence condition under which Res_A985(gamma)=0."
        ),
        "all_checks_pass": all_checks_pass,
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.v1",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.celestial_trace_pl_poincare_hopf_manifest.v1",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "recover the 20 Lambda^3 H6 public states from the H-cycle edge table",
            "verify the 30-edge 3-regular connected D20 transition graph",
            "derive the twelve pentagonal cycles that form the dual vertices",
            "dualize to the 12-30-20 icosahedral PL surface",
            "sum the twelve valence-five missing-sector indices to total defect 2",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
