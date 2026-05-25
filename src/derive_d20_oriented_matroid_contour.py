from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any

try:
    from src.derive_d20_public_boundary_graph_theorem import enumerate_isomorphisms
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_public_boundary_graph_theorem import enumerate_isomorphisms
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_oriented_matroid_contour"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_JSON = ROOT / "d20.json"
D20_FINITE_CONTOUR = (
    D20_INVARIANTS / "theorems" / "d20_finite_contour_integration" / "report.json"
)
PUBLIC_BOUNDARY_GRAPH = (
    D20_INVARIANTS / "theorems" / "public_boundary_graph_invariants" / "report.json"
)
SECTOR33_HEIGHT_TRANSPORT = (
    D20_INVARIANTS / "theorems" / "sector33_height_coherent_transport" / "report.json"
)
SECTOR33_UNIQUE_PUBLIC_ZERO = (
    D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support" / "report.json"
)
HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER = (
    D20_INVARIANTS / "theorems" / "hidden_split_augmented_ledger_stabilizer" / "report.json"
)
SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient"
    / "report.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


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
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_signed_vector(vector: list[int]) -> list[int]:
    for value in vector:
        if value:
            return vector if value > 0 else [-entry for entry in vector]
    return vector


def same_up_to_global_sign(left: list[int], right: list[int]) -> bool:
    return left == right or left == [-value for value in right]


def rank_rational(matrix: list[list[int]]) -> int:
    from fractions import Fraction

    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    row_count = len(work)
    col_count = len(work[0])
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if work[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][col]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    work[row][idx] - factor * work[rank][idx] for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def edge_table(d20: dict[str, Any]) -> list[dict[str, Any]]:
    rows = d20["game_theory"]["tables"]["subscript_Hcycle_d20_edges.csv"]["rows"]
    return sorted(rows, key=lambda row: int(row["edge_id"]))


def base_edges(edge_rows: list[dict[str, Any]]) -> dict[int, tuple[int, int]]:
    return {
        int(row["edge_id"]): (int(row["u"]), int(row["v"]))
        for row in sorted(edge_rows, key=lambda item: int(item["edge_id"]))
    }


def adjacency(base: dict[int, tuple[int, int]], vertex_count: int) -> list[list[tuple[int, int]]]:
    graph: list[list[tuple[int, int]]] = [[] for _ in range(vertex_count)]
    for edge_id, (u, v) in base.items():
        graph[u].append((v, edge_id))
        graph[v].append((u, edge_id))
    for row in graph:
        row.sort()
    return graph


def adjacency_matrix(base: dict[int, tuple[int, int]], vertex_count: int) -> list[list[int]]:
    matrix = [[0 for _ in range(vertex_count)] for _ in range(vertex_count)]
    for u, v in base.values():
        matrix[u][v] += 1
        matrix[v][u] += 1
    return matrix


def incidence_matrix(base: dict[int, tuple[int, int]], vertex_count: int) -> list[list[int]]:
    edge_count = len(base)
    matrix = [[0 for _ in range(edge_count)] for _ in range(vertex_count)]
    for edge_id, (u, v) in base.items():
        matrix[u][edge_id] = -1
        matrix[v][edge_id] = 1
    return matrix


def signed_vector_from_closed_walk(
    vertices: list[int],
    edge_ids: list[int],
    base: dict[int, tuple[int, int]],
) -> list[int]:
    vector = [0 for _ in range(len(base))]
    for start, stop, edge_id in zip(vertices[:-1], vertices[1:], edge_ids):
        u, v = base[edge_id]
        if (start, stop) == (u, v):
            vector[edge_id] = 1
        elif (start, stop) == (v, u):
            vector[edge_id] = -1
        else:
            raise ValueError(f"edge {edge_id} is not incident to {start}->{stop}")
    return vector


def signed_vector_from_sparse(rows: list[list[int]], edge_count: int) -> list[int]:
    vector = [0 for _ in range(edge_count)]
    for edge_id, sign in rows:
        vector[int(edge_id)] = int(sign)
    return vector


def signed_support(vector: list[int]) -> list[list[int]]:
    return [[edge_id, value] for edge_id, value in enumerate(vector) if value]


def enumerate_signed_circuits(
    base: dict[int, tuple[int, int]],
    vertex_count: int,
) -> list[dict[str, Any]]:
    graph = adjacency(base, vertex_count)
    edge_count = len(base)
    circuits: dict[frozenset[int], dict[str, Any]] = {}

    for start in range(vertex_count):

        def dfs(current: int, path_vertices: list[int], path_edges: list[int]) -> None:
            for neighbor, edge_id in graph[current]:
                if neighbor == start and len(path_edges) >= 2:
                    edge_ids = path_edges + [edge_id]
                    support = frozenset(edge_ids)
                    if support in circuits:
                        continue
                    vertices = path_vertices + [start]
                    vector = normalize_signed_vector(
                        signed_vector_from_closed_walk(vertices, edge_ids, base)
                    )
                    circuits[support] = {
                        "length": len(edge_ids),
                        "support": sorted(support),
                        "signed_support": signed_support(vector),
                    }
                elif neighbor > start and neighbor not in path_vertices:
                    dfs(neighbor, path_vertices + [neighbor], path_edges + [edge_id])

        dfs(start, [start], [])

    return sorted(circuits.values(), key=lambda row: (row["length"], row["support"]))


def connected_subset(mask: int, graph: list[list[tuple[int, int]]]) -> bool:
    if mask == 0:
        return False
    start = (mask & -mask).bit_length() - 1
    seen_mask = 0
    stack = [start]
    while stack:
        node = stack.pop()
        if (seen_mask >> node) & 1:
            continue
        seen_mask |= 1 << node
        for neighbor, _edge_id in graph[node]:
            if ((mask >> neighbor) & 1) and not ((seen_mask >> neighbor) & 1):
                stack.append(neighbor)
    return seen_mask == mask


def enumerate_signed_cocircuits(
    base: dict[int, tuple[int, int]],
    vertex_count: int,
) -> list[dict[str, Any]]:
    graph = adjacency(base, vertex_count)
    full = (1 << vertex_count) - 1
    cocircuits = []
    for mask in range(1, full):
        if not (mask & 1):
            continue
        complement = full ^ mask
        if not connected_subset(mask, graph) or not connected_subset(complement, graph):
            continue
        vector = [0 for _ in range(len(base))]
        support = []
        for edge_id, (u, v) in base.items():
            u_in = (mask >> u) & 1
            v_in = (mask >> v) & 1
            if u_in == v_in:
                continue
            support.append(edge_id)
            vector[edge_id] = 1 if u_in and not v_in else -1
        vector = normalize_signed_vector(vector)
        cocircuits.append(
            {
                "size": len(support),
                "support": sorted(support),
                "signed_support": signed_support(vector),
            }
        )
    return sorted(cocircuits, key=lambda row: (row["size"], row["support"]))


def is_acyclic_orientation(
    signs: dict[int, int],
    base: dict[int, tuple[int, int]],
    vertex_count: int,
) -> bool:
    outgoing = [[] for _ in range(vertex_count)]
    indegree = [0 for _ in range(vertex_count)]
    for edge_id, sign in signs.items():
        u, v = base[edge_id]
        start, stop = (u, v) if sign > 0 else (v, u)
        outgoing[start].append(stop)
        indegree[stop] += 1
    queue: deque[int] = deque([idx for idx, degree in enumerate(indegree) if degree == 0])
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for neighbor in outgoing[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    return seen == vertex_count


def tope_extension_from_partial(
    partial: dict[int, int],
    base: dict[int, tuple[int, int]],
    vertex_count: int,
) -> dict[str, Any]:
    outgoing = [[] for _ in range(vertex_count)]
    indegree = [0 for _ in range(vertex_count)]
    for edge_id, sign in partial.items():
        u, v = base[edge_id]
        start, stop = (u, v) if sign > 0 else (v, u)
        outgoing[start].append(stop)
        indegree[stop] += 1

    queue: list[int] = [idx for idx, degree in enumerate(indegree) if degree == 0]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for neighbor in sorted(outgoing[node]):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
                queue.sort()
    if len(order) != vertex_count:
        return {"extends": False, "reason": "partial orientation has a directed cycle"}

    position = {vertex: idx for idx, vertex in enumerate(order)}
    signs = {}
    for edge_id, (u, v) in base.items():
        signs[edge_id] = 1 if position[u] < position[v] else -1
    matches_partial = all(signs[edge_id] == sign for edge_id, sign in partial.items())
    complete_acyclic = is_acyclic_orientation(signs, base, vertex_count)
    return {
        "extends": matches_partial and complete_acyclic,
        "topological_order": order,
        "signed_tope": signed_support([signs[idx] for idx in range(len(base))]),
        "complete_orientation_is_acyclic": complete_acyclic,
        "matches_partial_signs": matches_partial,
    }


def edge_action_for_automorphism(
    permutation: tuple[int, ...],
    base: dict[int, tuple[int, int]],
) -> tuple[list[int], list[int]]:
    edge_by_pair = {frozenset(pair): edge_id for edge_id, pair in base.items()}
    image_edges = []
    orientation_signs = []
    for edge_id in range(len(base)):
        u, v = base[edge_id]
        image_u = permutation[u]
        image_v = permutation[v]
        image_edge = edge_by_pair[frozenset((image_u, image_v))]
        base_u, base_v = base[image_edge]
        image_edges.append(image_edge)
        orientation_signs.append(1 if (image_u, image_v) == (base_u, base_v) else -1)
    return image_edges, orientation_signs


def transform_partial_signs(
    partial: dict[int, int],
    edge_permutation: list[int],
    orientation_signs: list[int],
) -> dict[int, int]:
    return {
        edge_permutation[edge_id]: sign * orientation_signs[edge_id]
        for edge_id, sign in sorted(partial.items())
    }


def stabilizer_ids(
    partial: dict[int, int],
    edge_actions: list[tuple[list[int], list[int]]],
    *,
    support_only: bool = False,
    up_to_global_sign: bool = False,
) -> list[int]:
    target_support = set(partial)
    target = dict(sorted(partial.items()))
    target_negated = {edge_id: -sign for edge_id, sign in target.items()}
    ids = []
    for automorphism_id, (edge_permutation, orientation_signs) in enumerate(edge_actions):
        image = transform_partial_signs(partial, edge_permutation, orientation_signs)
        if support_only and set(image) == target_support:
            ids.append(automorphism_id)
        elif image == target or (up_to_global_sign and image == target_negated):
            ids.append(automorphism_id)
    return ids


def vector_dot_sparse_height(sparse_rows: list[list[int]], heights: dict[int, int]) -> int:
    return sum(int(sign) * heights[int(edge_id)] for edge_id, sign in sparse_rows)


def build_theorem() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    finite_contour = load_json(D20_FINITE_CONTOUR)
    public_boundary = load_json(PUBLIC_BOUNDARY_GRAPH)
    sector33_height = load_json(SECTOR33_HEIGHT_TRANSPORT)
    sector33_unique = load_json(SECTOR33_UNIQUE_PUBLIC_ZERO)
    hidden_stabilizer = load_json(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER)
    label_relaxed = load_json(SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT)

    edge_rows = edge_table(d20)
    base = base_edges(edge_rows)
    vertex_count = 20
    edge_count = len(base)
    incidence = incidence_matrix(base, vertex_count)
    rank = rank_rational(incidence)
    corank = edge_count - rank

    circuits = enumerate_signed_circuits(base, vertex_count)
    cocircuits = enumerate_signed_cocircuits(base, vertex_count)
    circuit_supports = {tuple(row["support"]) for row in circuits}
    cocircuit_supports = {tuple(row["support"]) for row in cocircuits}

    active = sector33_height["derived"]["active_circuit"]
    gamma8_active_positive = {int(edge_id): int(sign) for edge_id, sign in active["active_matrix_row"]}
    gamma8_signed_circuit = {int(edge_id): int(sign) for edge_id, sign in active["signed_circuit_row"]}
    gamma8_support = sorted(gamma8_active_positive)
    gamma8_signed_vector = signed_vector_from_sparse(active["signed_circuit_row"], edge_count)
    normalized_gamma8_signed_vector = normalize_signed_vector(list(gamma8_signed_vector))
    gamma8_circuit_record = next(row for row in circuits if row["support"] == gamma8_support)
    gamma8_circuit_vector = [0 for _ in range(edge_count)]
    for edge_id, sign in gamma8_circuit_record["signed_support"]:
        gamma8_circuit_vector[int(edge_id)] = int(sign)

    weights = {int(row["edge_id"]): int(row["interface_weight"]) for row in edge_rows}
    active_height_sum = sum(weights[edge_id] for edge_id in gamma8_support)
    signed_height_sum = vector_dot_sparse_height(active["signed_circuit_row"], weights)
    active_tope = tope_extension_from_partial(gamma8_active_positive, base, vertex_count)

    graph_matrix = adjacency_matrix(base, vertex_count)
    automorphisms = enumerate_isomorphisms(graph_matrix, graph_matrix)
    edge_actions = [edge_action_for_automorphism(permutation, base) for permutation in automorphisms]
    active_positive_stabilizer = stabilizer_ids(gamma8_active_positive, edge_actions)
    active_support_stabilizer = stabilizer_ids(
        gamma8_active_positive, edge_actions, support_only=True
    )
    cyclic_signed_stabilizer = stabilizer_ids(gamma8_signed_circuit, edge_actions)
    cyclic_signed_unoriented_stabilizer = stabilizer_ids(
        gamma8_signed_circuit, edge_actions, up_to_global_sign=True
    )

    circuit_histogram = {
        str(key): int(value)
        for key, value in sorted(Counter(row["length"] for row in circuits).items())
    }
    cocircuit_histogram = {
        str(key): int(value)
        for key, value in sorted(Counter(row["size"] for row in cocircuits).items())
    }
    active_complement = sorted(set(range(edge_count)) - set(gamma8_support))

    contour_summary = {
        "oriented_matroid": "M_contour = OM(partial_D20), the graphic oriented matroid of the directed D20 incidence matrix",
        "ground_set": "directed public D20 boundary edges",
        "vertex_count": vertex_count,
        "edge_count": edge_count,
        "rank": rank,
        "corank_cycle_rank": corank,
        "signed_circuit_count": len(circuits),
        "signed_circuit_length_histogram": circuit_histogram,
        "signed_cocircuit_count": len(cocircuits),
        "signed_cocircuit_size_histogram": cocircuit_histogram,
        "signed_circuits_sha256": sha_json(circuits),
        "signed_cocircuits_sha256": sha_json(cocircuits),
        "primitive_h_cycle_basis_count": finite_contour["derived"]["contour_summary"][
            "primitive_cycle_count"
        ],
        "primitive_h_cycle_basis_rank": finite_contour["derived"]["contour_summary"][
            "primitive_cycle_rank_over_F2"
        ],
    }

    gamma8_summary = {
        "basis_coordinate": 8,
        "support": gamma8_support,
        "active_positive_row": sorted([[edge_id, sign] for edge_id, sign in gamma8_active_positive.items()]),
        "cyclic_signed_circuit_row": sorted(
            [[edge_id, sign] for edge_id, sign in gamma8_signed_circuit.items()]
        ),
        "support_is_signed_circuit": tuple(gamma8_support) in circuit_supports,
        "support_is_signed_cocircuit": tuple(gamma8_support) in cocircuit_supports,
        "support_is_hyperplane_zero_set": tuple(active_complement) in cocircuit_supports,
        "reported_signed_circuit_matches_graphic_circuit_up_to_global_sign": same_up_to_global_sign(
            normalized_gamma8_signed_vector, gamma8_circuit_vector
        ),
        "active_positive_partial_orientation_is_acyclic": is_acyclic_orientation(
            gamma8_active_positive, base, vertex_count
        ),
        "cyclic_signed_circuit_partial_orientation_is_acyclic": is_acyclic_orientation(
            gamma8_signed_circuit, base, vertex_count
        ),
        "active_positive_extends_to_acyclic_tope": active_tope["extends"],
        "active_positive_tope_witness": active_tope,
        "height_dot_active_positive_row": active_height_sum,
        "height_dot_reported_signed_circuit_row": signed_height_sum,
        "reported_height_action": int(active["height_dot_active_row"]),
        "height_action_matches_active_positive_row": active_height_sum
        == int(active["height_dot_active_row"]),
        "overclaim_guard": (
            "The cyclic signed circuit row is a circuit, not a tope; the all-positive "
            "active height row is the sign pattern that extends to an acyclic tope."
        ),
    }

    pure_symmetry = {
        "public_graph_automorphism_order": len(automorphisms),
        "public_boundary_report_automorphism_order": public_boundary["derived"]["automorphisms"][
            "aut_gamma_order"
        ],
        "active_positive_signed_row_stabilizer_ids": active_positive_stabilizer,
        "active_positive_signed_row_stabilizer_order": len(active_positive_stabilizer),
        "active_support_only_stabilizer_order": len(active_support_stabilizer),
        "active_support_only_stabilizer_ids": active_support_stabilizer,
        "cyclic_signed_circuit_stabilizer_order": len(cyclic_signed_stabilizer),
        "cyclic_signed_circuit_stabilizer_ids": cyclic_signed_stabilizer,
        "cyclic_signed_circuit_unoriented_stabilizer_order": len(
            cyclic_signed_unoriented_stabilizer
        ),
        "cyclic_signed_circuit_unoriented_stabilizer_ids": cyclic_signed_unoriented_stabilizer,
        "pure_contour_relaxation_is_c2": len(active_support_stabilizer) == 2
        or len(cyclic_signed_unoriented_stabilizer) == 2,
    }

    augmented_symmetry = {
        "hidden_split_stabilizer_order": hidden_stabilizer["derived"]["candidate_group"][
            "hidden_split_stabilizer_order"
        ],
        "full_augmented_ledger_stabilizer_order": hidden_stabilizer["derived"][
            "candidate_group"
        ]["full_augmented_ledger_stabilizer_order"],
        "label_relaxed_hidden_split_c2_has_543_kernel_target_orbits": label_relaxed[
            "checks"
        ]["hidden_split_c2_quotient_has_543_kernel_target_orbits"],
        "full_public_action_requires_forgetting_gamma8_source_anchor": label_relaxed[
            "checks"
        ]["full_public_quotient_requires_forgetting_source_anchor"],
        "interpretation": (
            "The certified C2 belongs to the augmented hidden-split/label-relaxed "
            "ledger, not to the pure graphic contour matroid relaxation."
        ),
    }

    sector33_summary = {
        "sector33_public_zero_is_certified": sector33_unique.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED",
        "sector33_height_transport_is_certified": sector33_height.get("status")
        == "D20_SECTOR33_HEIGHT_COHERENT_TRANSPORT_CERTIFIED",
        "profile_public_zero_sectors": sector33_unique["derived"]["profile_public_zero_sectors"],
        "current_contour_ground_set": "30 public boundary edges",
        "sector33_is_ground_set_element_of_m_contour": False,
        "sector33_active_support_reading": (
            "sector 33 is attached to the gamma8 circuit support by the height transport report"
        ),
        "active_support_is_circuit_not_cocircuit": gamma8_summary["support_is_signed_circuit"]
        and not gamma8_summary["support_is_signed_cocircuit"],
        "active_support_is_not_hyperplane_zero_set": not gamma8_summary[
            "support_is_hyperplane_zero_set"
        ],
        "blocked_extension": (
            "To test sector 33 as a cocircuit or hyperplane, the contour matroid needs "
            "an explicit single-element or decorated extension whose ground set includes "
            "the sector idempotent/coefficient, not only public boundary edges."
        ),
    }

    os_summary = {
        "generator_count": edge_count,
        "circuit_boundary_relation_count": len(circuits),
        "gamma8_circuit_relation_support": gamma8_support,
        "presentation_status": (
            "Orlik-Solomon presentation skeleton identified for the graphic matroid; "
            "graded Betti numbers and Tutte polynomial are not computed in this certificate."
        ),
    }

    blocked_or_deferred = {
        "sector33_cocircuit_or_hyperplane_in_m_contour": "blocked_missing_sector33_ground_set_extension",
        "pure_contour_gamma8_relaxation_c2": "not_supported_by_pure_contour_matroid",
        "tutte_polynomial": "deferred_to_deletion_contraction_or_specialized_graph_polynomial_pass",
        "full_covector_and_tope_enumeration": "deferred; this certificate gives counts/hashes for circuits/cocircuits and a gamma8 tope witness",
        "orlik_solomon_betti_numbers": "deferred_until_tutte_polynomial_or_no-broken-circuit_basis_pass",
    }

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "finite_contour_input_is_certified": finite_contour.get("status")
        == "D20_FINITE_CONTOUR_INTEGRATION_TEST_PASS"
        and finite_contour.get("all_checks_pass") is True,
        "public_boundary_input_is_certified": public_boundary.get("status")
        == "D20_PUBLIC_BOUNDARY_GRAPH_INVARIANTS_CERTIFIED"
        and public_boundary.get("all_checks_pass") is True,
        "sector33_inputs_are_certified": sector33_summary["sector33_public_zero_is_certified"]
        and sector33_summary["sector33_height_transport_is_certified"],
        "augmented_symmetry_inputs_are_certified": hidden_stabilizer.get("all_checks_pass")
        is True
        and label_relaxed.get("all_checks_pass") is True,
        "graphic_oriented_matroid_has_expected_rank": contour_summary["rank"] == 19
        and contour_summary["corank_cycle_rank"] == 11,
        "signed_circuit_count_matches_recomputation": contour_summary[
            "signed_circuit_count"
        ]
        == 1168,
        "signed_cocircuit_count_matches_recomputation": contour_summary[
            "signed_cocircuit_count"
        ]
        == 12878,
        "gamma8_support_is_circuit": gamma8_summary["support_is_signed_circuit"],
        "gamma8_reported_signed_row_matches_graphic_circuit": gamma8_summary[
            "reported_signed_circuit_matches_graphic_circuit_up_to_global_sign"
        ],
        "gamma8_active_positive_row_extends_to_acyclic_tope": gamma8_summary[
            "active_positive_extends_to_acyclic_tope"
        ],
        "gamma8_cyclic_signed_circuit_is_not_misclassified_as_tope": gamma8_summary[
            "cyclic_signed_circuit_partial_orientation_is_acyclic"
        ]
        is False,
        "gamma8_active_positive_signed_stabilizer_is_identity": pure_symmetry[
            "active_positive_signed_row_stabilizer_order"
        ]
        == 1
        and pure_symmetry["active_positive_signed_row_stabilizer_ids"] == [0],
        "public_source_forgotten_automorphism_order_is_120": pure_symmetry[
            "public_graph_automorphism_order"
        ]
        == 120
        and pure_symmetry["public_boundary_report_automorphism_order"] == 120,
        "pure_contour_relaxation_is_not_c2_overclaim": pure_symmetry[
            "pure_contour_relaxation_is_c2"
        ]
        is False
        and pure_symmetry["active_support_only_stabilizer_order"] == 10
        and pure_symmetry["cyclic_signed_circuit_stabilizer_order"] == 5,
        "sector33_is_not_overclaimed_as_pure_contour_cocircuit": sector33_summary[
            "active_support_is_circuit_not_cocircuit"
        ]
        and sector33_summary["active_support_is_not_hyperplane_zero_set"],
        "augmented_hidden_split_c2_is_cross_linked": augmented_symmetry[
            "hidden_split_stabilizer_order"
        ]
        == 2
        and augmented_symmetry["full_augmented_ledger_stabilizer_order"] == 1,
    }

    report = {
        "schema": "d20.theorem.d20_oriented_matroid_contour",
        "status": "D20_ORIENTED_MATROID_CONTOUR_CERTIFIED",
        "object": "D20",
        "definition": {
            "m_contour": (
                "the graphic oriented matroid of the directed D20 boundary incidence "
                "matrix partial_D20, with ground set the 30 public boundary edges"
            ),
            "signed_circuit": (
                "a signed simple cycle of the directed public boundary graph, normalized "
                "up to global sign"
            ),
            "signed_cocircuit": (
                "a signed bond/minimal cut of the public boundary graph, normalized "
                "up to global sign"
            ),
            "tope_witness": (
                "an acyclic full orientation extending a partial edge-sign assignment"
            ),
        },
        "claim": (
            "The D20 finite contour system has a classical graphic oriented-matroid "
            "spine. Its signed circuits are the 1168 simple cycles and its signed "
            "cocircuits are the 12878 bonds of the public dodecahedral boundary. The "
            "gamma8 active height row is a signed circuit support that extends to an "
            "acyclic tope and has trivial signed stabilizer in Aut(M_contour). The full "
            "public source-forgotten automorphism group has order 120. The pure contour "
            "matroid does not by itself certify sector 33 as a cocircuit/hyperplane or "
            "produce the hidden C2 relaxation; those require the existing augmented "
            "sector/ledger structure."
        ),
        "inputs": {
            "d20_json": input_record(D20_JSON),
            "d20_finite_contour_integration_report": input_record(D20_FINITE_CONTOUR),
            "public_boundary_graph_report": input_record(PUBLIC_BOUNDARY_GRAPH),
            "sector33_height_coherent_transport_report": input_record(
                SECTOR33_HEIGHT_TRANSPORT
            ),
            "sector33_unique_public_zero_support_report": input_record(
                SECTOR33_UNIQUE_PUBLIC_ZERO
            ),
            "hidden_split_augmented_ledger_stabilizer_report": input_record(
                HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER
            ),
            "sourced_balance_label_relaxed_orbit_quotient_report": input_record(
                SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT
            ),
        },
        "derived": {
            "contour_oriented_matroid_summary": contour_summary,
            "gamma8_tests": gamma8_summary,
            "pure_contour_symmetry_tests": pure_symmetry,
            "augmented_symmetry_cross_link": augmented_symmetry,
            "sector33_tests": sector33_summary,
            "orlik_solomon_summary": os_summary,
            "blocked_or_deferred": blocked_or_deferred,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "classical_terms_confirmed": {
                "boundary_contour": "signed circuit",
                "height_certificate": "positive active circuit row with acyclic tope extension",
                "public_120_symmetry": "Aut(M_contour) after forgetting source/ledger decorations",
                "gamma8_choice_operator": "acyclic active-row tope selector with trivial signed stabilizer",
            },
            "classical_terms_not_yet_confirmed": {
                "sector33_as_cocircuit_or_hyperplane": blocked_or_deferred[
                    "sector33_cocircuit_or_hyperplane_in_m_contour"
                ],
                "c2_after_forgetting_as_pure_matroid_stabilizer": blocked_or_deferred[
                    "pure_contour_gamma8_relaxation_c2"
                ],
                "tutte_and_full_os_package": "deferred",
            },
            "overclaim_guard": (
                "This is an oriented-matroid certificate for the D20 public contour "
                "incidence system. It is not a proof of P != NP, not M-theory, and not "
                "yet a sector-33 single-element extension theorem."
            ),
        },
        "next_highest_yield_item": (
            "Build the decorated/single-element extension M_contour + e33 so sector 33 "
            "can be tested as an actual cocircuit or hyperplane, then compute the "
            "Tutte/Orlik-Solomon invariants for that extended matroid."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_oriented_matroid_contour_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "construct the graphic oriented matroid of the D20 contour incidence matrix",
            "certify signed circuit/cocircuit counts and gamma8 tope/stabilizer tests",
            "separate pure contour-matroid facts from augmented sector/ledger facts",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
