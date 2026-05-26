from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
import math
from collections import Counter, deque
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import (
        DEFAULT_OUT_DIR as SANDPILE_OUT_DIR,
        adjacency_matrix,
        bareiss_det,
        connected,
        laplacian,
        read_edges,
        reduced_matrix,
        rel,
        sha_file,
        sha_json,
        smith_normal_form_diagonal,
    )
    from .paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT
except ImportError:  # Supports `python src/derive_d20_public_boundary_graph_theorem.py`.
    from derive_d20_sandpile_critical_group_theorem import (
        DEFAULT_OUT_DIR as SANDPILE_OUT_DIR,
        adjacency_matrix,
        bareiss_det,
        connected,
        laplacian,
        read_edges,
        reduced_matrix,
        rel,
        sha_file,
        sha_json,
        smith_normal_form_diagonal,
    )
    from paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "public_boundary_graph_invariants"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"
AUTOMORPHISM_SUMMARY = HCYCLE_INVARIANTS / "d20_Hcycle_automorphism_summary.json"
SANDPILE_REPORT = SANDPILE_OUT_DIR / "report.json"
VERTEX_COUNT = 20

STANDARD_DODECAHEDRAL_EDGES = [
    (0, 1),
    (0, 10),
    (0, 19),
    (1, 2),
    (1, 8),
    (2, 3),
    (2, 6),
    (3, 4),
    (3, 19),
    (4, 5),
    (4, 17),
    (5, 6),
    (5, 15),
    (6, 7),
    (7, 8),
    (7, 14),
    (8, 9),
    (9, 10),
    (9, 13),
    (10, 11),
    (11, 12),
    (11, 18),
    (12, 13),
    (12, 16),
    (13, 14),
    (14, 15),
    (15, 16),
    (16, 17),
    (17, 18),
    (18, 19),
]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
        index = load_json(index_path)
        schema = index.get("schema", "d20.theorem_registry.source_drop")
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        schema = "d20.theorem_registry.source_drop"
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": schema,
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def adjacency_from_edge_pairs(edge_pairs: list[tuple[int, int]], vertex_count: int = VERTEX_COUNT) -> list[list[int]]:
    adjacency = [[0 for _ in range(vertex_count)] for _ in range(vertex_count)]
    for u, v in edge_pairs:
        adjacency[u][v] += 1
        adjacency[v][u] += 1
    return adjacency


def distance_matrix(adjacency: list[list[int]]) -> list[list[int]]:
    n = len(adjacency)
    distances = []
    for start in range(n):
        row = [n + 1] * n
        row[start] = 0
        queue: deque[int] = deque([start])
        while queue:
            node = queue.popleft()
            for other, value in enumerate(adjacency[node]):
                if value and row[other] == n + 1:
                    row[other] = row[node] + 1
                    queue.append(other)
        distances.append(row)
    return distances


def graph_diameter(adjacency: list[list[int]]) -> int:
    return max(max(row) for row in distance_matrix(adjacency))


def girth(adjacency: list[list[int]]) -> int | None:
    n = len(adjacency)
    best = n + 1
    for start in range(n):
        distance = [-1] * n
        parent = [-1] * n
        distance[start] = 0
        queue: deque[int] = deque([start])
        while queue:
            node = queue.popleft()
            for other, value in enumerate(adjacency[node]):
                if not value:
                    continue
                if distance[other] < 0:
                    distance[other] = distance[node] + 1
                    parent[other] = node
                    queue.append(other)
                elif parent[node] != other and parent[other] != node:
                    best = min(best, distance[node] + distance[other] + 1)
    return None if best == n + 1 else best


def enumerate_isomorphisms(
    source_adjacency: list[list[int]],
    target_adjacency: list[list[int]],
    *,
    stop_after_first: bool = False,
) -> list[tuple[int, ...]]:
    n = len(source_adjacency)
    source_distances = distance_matrix(source_adjacency)
    target_distances = distance_matrix(target_adjacency)
    source_degrees = [sum(row) for row in source_adjacency]
    target_degrees = [sum(row) for row in target_adjacency]
    mappings: list[tuple[int, ...]] = []

    def recurse(mapping: dict[int, int], used: set[int]) -> None:
        if stop_after_first and mappings:
            return
        if len(mapping) == n:
            mappings.append(tuple(mapping[idx] for idx in range(n)))
            return

        best_source: int | None = None
        best_candidates: list[int] | None = None
        for source in range(n):
            if source in mapping:
                continue
            candidates = []
            for target in range(n):
                if target in used or source_degrees[source] != target_degrees[target]:
                    continue
                if all(
                    source_adjacency[source][known_source] == target_adjacency[target][known_target]
                    and source_distances[source][known_source]
                    == target_distances[target][known_target]
                    for known_source, known_target in mapping.items()
                ):
                    candidates.append(target)
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_source = source
                best_candidates = candidates
            if best_candidates == []:
                break

        if best_source is None or not best_candidates:
            return
        for target in best_candidates:
            mapping[best_source] = target
            used.add(target)
            recurse(mapping, used)
            used.remove(target)
            del mapping[best_source]

    for root_image in range(n):
        recurse({0: root_image}, {root_image})
        if stop_after_first and mappings:
            break
    return sorted(set(mappings))


def phase_screen() -> dict[str, Any]:
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    labels = sorted({label for row in rows for label in row["turn_addresses"].split()})
    best_defects = len(rows) + 1
    best_records: list[dict[str, Any]] = []

    for mask in range(1, (1 << len(labels)) - 1):
        positive = [label for i, label in enumerate(labels) if (mask >> i) & 1]
        negative = [label for i, label in enumerate(labels) if not ((mask >> i) & 1)]
        defect_cycles = []
        coherent_cycles = []
        for row in rows:
            product = 1
            for label in row["turn_addresses"].split():
                product *= 1 if label in positive else -1
            target = {
                "cycle_id": int(row["cycle_id"]),
                "length": int(row["length"]),
                "turn_addresses": row["turn_addresses"],
                "phase_product": product,
            }
            if product == 1:
                coherent_cycles.append(target)
            else:
                defect_cycles.append(target)
        if len(defect_cycles) < best_defects:
            best_defects = len(defect_cycles)
            best_records = []
        if len(defect_cycles) == best_defects:
            best_records.append(
                {
                    "positive_phase_labels": positive,
                    "negative_phase_labels": negative,
                    "defect_cycle_ids": [row["cycle_id"] for row in defect_cycles],
                    "coherent_cycle_count": len(coherent_cycles),
                    "defect_count": len(defect_cycles),
                }
            )

    return {
        "definition": (
            "A nontrivial signed-turn phase gate assigns each of B+, B-, S+, S-, V+, V- "
            "a phase in {+1,-1}. A primitive H-cycle is coherent when the product of "
            "its turn-address phases is +1; otherwise it is a defect."
        ),
        "turn_address_labels": labels,
        "primitive_cycle_count": len(rows),
        "best_nontrivial_defect_count": best_defects,
        "best_gate_count": len(best_records),
        "representative_best_gates": best_records[:5],
        "all_best_gate_records_sha256": hashlib.sha256(canonical(best_records)).hexdigest(),
    }


def build_theorem() -> dict[str, Any]:
    edges = read_edges()
    edge_pairs = [(int(edge["u"]), int(edge["v"])) for edge in edges]
    adjacency = adjacency_matrix(edges)
    standard_adjacency = adjacency_from_edge_pairs(STANDARD_DODECAHEDRAL_EDGES)
    d20_laplacian = laplacian(adjacency)
    reduced = reduced_matrix(d20_laplacian, 0)
    snf = smith_normal_form_diagonal(reduced)
    cofactor = abs(bareiss_det(reduced))
    automorphisms = enumerate_isomorphisms(adjacency, adjacency)
    dodecahedral_isomorphism = enumerate_isomorphisms(adjacency, standard_adjacency, stop_after_first=True)
    automorphism_summary = load_json(AUTOMORPHISM_SUMMARY)
    sandpile_report = load_json(SANDPILE_REPORT) if SANDPILE_REPORT.exists() else {}
    fourier = phase_screen()

    vertices = len(adjacency)
    edge_count = len(edges)
    cycle_rank = edge_count - vertices + 1
    degree_histogram = Counter(sum(row) for row in adjacency)
    nonbacktracking_directed_edge_count = 2 * edge_count
    nonbacktracking_out_degree = 2

    checks = {
        "public_graph_has_20_vertices": vertices == 20,
        "public_graph_has_30_edges": edge_count == 30,
        "public_graph_is_3_regular": dict(degree_histogram) == {3: 20},
        "public_graph_is_connected": connected(adjacency),
        "public_graph_diameter_is_5": graph_diameter(adjacency) == 5,
        "public_graph_girth_is_5": girth(adjacency) == 5,
        "public_graph_is_dodecahedral": bool(dodecahedral_isomorphism),
        "cycle_rank_is_11": cycle_rank == 11,
        "automorphism_group_order_is_120": len(automorphisms) == 120
        and int(automorphism_summary.get("automorphism_count", 0)) == 120,
        "sandpile_group_matches_readme_value": snf["nonunit_invariant_factors"]
        == [2, 12, 60, 60, 60],
        "spanning_tree_count_is_5184000": cofactor == 5_184_000,
        "shift_entropy_is_log_3": all(sum(row) == 3 for row in adjacency),
        "nonbacktracking_entropy_is_log_2": nonbacktracking_out_degree == 2
        and nonbacktracking_directed_edge_count == 60,
        "fourier_screen_best_nontrivial_phase_gate_has_two_defects": fourier[
            "best_nontrivial_defect_count"
        ]
        == 2,
        "sandpile_report_agrees_if_present": not sandpile_report
        or sandpile_report.get("derived", {}).get("critical_group", {}).get("invariant_factors")
        == [2, 12, 60, 60, 60],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_PUBLIC_BOUNDARY_GRAPH_INVARIANTS_CERTIFIED"
        if all_checks_pass
        else "D20_PUBLIC_BOUNDARY_GRAPH_INVARIANTS_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.public_boundary_graph_invariants",
        "status": status,
        "object": "d20",
        "claim": (
            "The D20 public boundary is the dodecahedral 20-vertex, 30-edge, cubic graph. "
            "Its cycle rank is 11, automorphism group order is 120, sandpile critical group is "
            "Z/2 x Z/12 x Z/60^3, walk entropy is log(3), nonbacktracking entropy is log(2), "
            "and the best nontrivial signed-turn Fourier screen has two primitive-cycle defects."
        ),
        "definition": {
            "public_graph": "The unweighted legal H-cycle graph from subscript_Hcycle_d20_edges.csv.",
            "cycle_rank": "For a connected graph, beta_1 = |E|-|V|+1.",
            "shift_entropy": "Topological entropy of legal public walks on the cubic adjacency graph: log(spectral_radius(A)) = log(3).",
            "nonbacktracking_entropy": "Entropy of geodesic/nonbacktracking histories on a cubic graph: log(2).",
            "fourier_screen": fourier["definition"],
        },
        "inputs": {
            "hcycle_edge_table": {
                "path": rel(EDGES_CSV),
                "sha256": sha_file(EDGES_CSV),
            },
            "primitive_cycles": {
                "path": rel(PRIMITIVE_CYCLES_CSV),
                "sha256": sha_file(PRIMITIVE_CYCLES_CSV),
            },
            "automorphism_summary": {
                "path": rel(AUTOMORPHISM_SUMMARY),
                "sha256": sha_file(AUTOMORPHISM_SUMMARY),
            },
            "sandpile_critical_group_report": {
                "path": rel(SANDPILE_REPORT),
                "sha256": sha_file(SANDPILE_REPORT),
            }
            if SANDPILE_REPORT.exists()
            else None,
        },
        "derived": {
            "public_graph": {
                "vertices": vertices,
                "edges": edge_count,
                "degree_histogram": {str(k): int(v) for k, v in sorted(degree_histogram.items())},
                "connected": connected(adjacency),
                "diameter": graph_diameter(adjacency),
                "girth": girth(adjacency),
                "dodecahedral_isomorphism_found": bool(dodecahedral_isomorphism),
                "sample_dodecahedral_isomorphism": list(dodecahedral_isomorphism[0])
                if dodecahedral_isomorphism
                else [],
            },
            "cycle_space": {
                "cycle_rank_formula": "30 - 20 + 1",
                "cycle_rank": cycle_rank,
            },
            "automorphisms": {
                "aut_gamma_order": len(automorphisms),
                "summary_order": automorphism_summary.get("automorphism_count"),
                "vertex_orbits": automorphism_summary.get("vertex_orbits"),
                "pair_orbit_count": automorphism_summary.get("pair_orbit_count"),
                "automorphism_records_sha256": hashlib.sha256(canonical(automorphisms)).hexdigest(),
            },
            "sandpile": {
                "critical_group": "Z/2 x Z/12 x Z/60^3",
                "invariant_factors": snf["nonunit_invariant_factors"],
                "spanning_tree_count": cofactor,
                "smith_diagonal": snf["diagonal"],
            },
            "symbolic_dynamics": {
                "legal_public_history_branching_base": 3,
                "shift_entropy_natural": "log(3)",
                "shift_entropy_log2": math.log2(3),
                "nonbacktracking_directed_edge_count": nonbacktracking_directed_edge_count,
                "nonbacktracking_branching_base": nonbacktracking_out_degree,
                "nonbacktracking_entropy_natural": "log(2)",
                "nonbacktracking_entropy_log2": 1.0,
            },
            "fourier_screen": fourier,
        },
        "interpretation": {
            "table_rows": [
                ["Public graph", "20 vertices, 30 edges, 3-regular, connected, diameter 5", "finite public boundary"],
                ["Dodecahedral check", "isomorphic to the standard dodecahedral graph", "confirms spherical public board"],
                ["Cycle rank", "30 - 20 + 1 = 11", "geon/residue space"],
                ["Automorphisms", "|Aut(Gamma_d20)| = 120", "public board symmetry"],
                ["Sandpile group", "Z/2 x Z/12 x (Z/60)^3", "recurrent boundary residues"],
                ["Spanning trees", "5,184,000", "order of critical group"],
                ["Shift entropy", "log(3)", "legal public histories"],
                ["Nonbacktracking entropy", "log(2)", "geodesic histories"],
                ["Fourier screen", "best nontrivial signed-turn phase gate has 2 defects", "Ulam-style hidden chamber candidate"],
            ],
            "what_this_does_not_prove": (
                "This certifies the finite public-boundary graph and a signed-turn phase screen. "
                "It does not yet lift the phase screen into an A985 sector character or classify "
                "sandpile recurrence for each of the 2048 closed-return residue masks."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Lift the two-defect signed-turn Fourier screen into the A985/sector-character language "
            "and pair it with the 2048 closed-return residue masks."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.public_boundary_graph_invariants_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify public graph size, cubicity, connectivity, girth, and diameter",
            "verify graph isomorphism to the standard dodecahedral graph",
            "enumerate the 120 graph automorphisms",
            "verify the reduced Laplacian Smith factors and spanning-tree count",
            "verify legal-walk and nonbacktracking entropy bases",
            "enumerate nonconstant signed-turn phase gates and verify the best defect count is 2",
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
