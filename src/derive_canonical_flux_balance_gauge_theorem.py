from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
from typing import Any

from src.derive_finite_flux_balance_theorem import d20_charge, parse_label, sub_charge
from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "canonical_flux_balance_gauge"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_flux_balance" / "report.json"
)
HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT = (
    D20_INVARIANTS / "theorems" / "hidden_split_augmented_ledger_stabilizer" / "report.json"
)
EDGE_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"

PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")
VERTEX_COUNT = 20
EDGE_COUNT = 30


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
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_edges() -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    with EDGE_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            edges.append(
                {
                    "edge_id": int(row["edge_id"]),
                    "u": int(row["u"]),
                    "v": int(row["v"]),
                    "u_label": row["u_label"],
                    "v_label": row["v_label"],
                    "shared_duad": row["shared_duad"],
                    "swapped_pair": row["swapped_pair"],
                    "interface_weight": int(row["interface_weight"]),
                    "selector_duad_index": int(row["selector_duad_index"]),
                    "selector_choice": int(row["selector_choice"]),
                }
            )
    return sorted(edges, key=lambda item: item["edge_id"])


def vertex_labels(edges: list[dict[str, Any]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for edge in edges:
        labels.setdefault(edge["u"], edge["u_label"])
        labels.setdefault(edge["v"], edge["v_label"])
    return labels


def vertex_charges(labels: dict[int, str]) -> dict[int, dict[str, int]]:
    return {
        vertex: d20_charge(parse_label(label))
        for vertex, label in labels.items()
    }


def charge_tuple(charge: dict[str, int]) -> tuple[int, int, int, int]:
    return tuple(int(charge[component]) for component in PUBLIC_COMPONENTS)


def charge_dict(values: tuple[int, int, int, int]) -> dict[str, int]:
    return {component: int(value) for component, value in zip(PUBLIC_COMPONENTS, values)}


def add_charge_tuple(
    left: tuple[int, int, int, int],
    right: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    return tuple(left[idx] + right[idx] for idx in range(len(PUBLIC_COMPONENTS)))  # type: ignore[return-value]


def sub_charge_tuple(
    left: tuple[int, int, int, int],
    right: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    return tuple(left[idx] - right[idx] for idx in range(len(PUBLIC_COMPONENTS)))  # type: ignore[return-value]


def rank_over_q(rows: list[list[int]]) -> int:
    matrix = [[Fraction(value) for value in row] for row in rows if any(row)]
    if not matrix:
        return 0
    rank = 0
    row_count = len(matrix)
    column_count = len(matrix[0])
    for col in range(column_count):
        pivot = next((idx for idx in range(rank, row_count) if matrix[idx][col] != 0), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for idx in range(row_count):
            if idx == rank or matrix[idx][col] == 0:
                continue
            factor = matrix[idx][col]
            matrix[idx] = [
                matrix[idx][inner] - factor * matrix[rank][inner]
                for inner in range(column_count)
            ]
        rank += 1
        if rank == row_count:
            break
    return rank


def canonical_oriented_edges(
    edges: list[dict[str, Any]],
    charges: dict[int, dict[str, int]],
) -> list[dict[str, Any]]:
    oriented = []
    for edge in edges:
        endpoints = sorted(
            [edge["u"], edge["v"]],
            key=lambda vertex: charge_tuple(charges[vertex]),
        )
        source, target = endpoints
        source_charge = charge_tuple(charges[source])
        target_charge = charge_tuple(charges[target])
        oriented.append(
            {
                "edge_id": edge["edge_id"],
                "source": source,
                "target": target,
                "source_charge": charge_dict(source_charge),
                "target_charge": charge_dict(target_charge),
                "flux": charge_dict(sub_charge_tuple(target_charge, source_charge)),
                "interface_weight": edge["interface_weight"],
                "selector_duad_index": edge["selector_duad_index"],
                "selector_choice": edge["selector_choice"],
            }
        )
    return sorted(oriented, key=lambda item: item["edge_id"])


def incidence_rows(oriented_edges: list[dict[str, Any]]) -> list[list[int]]:
    rows = []
    for edge in oriented_edges:
        row = [0] * VERTEX_COUNT
        row[edge["source"]] = -1
        row[edge["target"]] = 1
        rows.append(row)
    return rows


def canonical_edge_marker(edge: dict[str, Any]) -> tuple[Any, ...]:
    return (
        tuple(edge["source_charge"][component] for component in PUBLIC_COMPONENTS),
        tuple(edge["target_charge"][component] for component in PUBLIC_COMPONENTS),
        edge["interface_weight"],
        edge["selector_duad_index"],
        edge["selector_choice"],
        tuple(edge["flux"][component] for component in PUBLIC_COMPONENTS),
    )


def recover_potential_from_flux(
    root: int,
    root_charge: tuple[int, int, int, int],
    oriented_edges: list[dict[str, Any]],
) -> tuple[dict[int, tuple[int, int, int, int]], list[dict[str, Any]]]:
    adjacency: dict[int, list[dict[str, Any]]] = {vertex: [] for vertex in range(VERTEX_COUNT)}
    for edge in oriented_edges:
        adjacency[edge["source"]].append(edge)
        adjacency[edge["target"]].append(edge)

    potentials: dict[int, tuple[int, int, int, int]] = {root: root_charge}
    queue = deque([root])
    inconsistencies: list[dict[str, Any]] = []
    while queue:
        vertex = queue.popleft()
        current = potentials[vertex]
        for edge in adjacency[vertex]:
            source = edge["source"]
            target = edge["target"]
            flux = tuple(edge["flux"][component] for component in PUBLIC_COMPONENTS)
            if vertex == source:
                neighbor = target
                expected = add_charge_tuple(current, flux)
            else:
                neighbor = source
                expected = sub_charge_tuple(current, flux)
            if neighbor not in potentials:
                potentials[neighbor] = expected
                queue.append(neighbor)
            elif potentials[neighbor] != expected:
                inconsistencies.append(
                    {
                        "edge_id": edge["edge_id"],
                        "known_vertex": vertex,
                        "neighbor": neighbor,
                        "expected": charge_dict(expected),
                        "actual": charge_dict(potentials[neighbor]),
                    }
                )
    return potentials, inconsistencies


def build_theorem() -> dict[str, Any]:
    finite_flux = load_json(FINITE_FLUX_BALANCE_REPORT)
    ledger_stabilizer = load_json(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT)
    edges = load_edges()
    labels = vertex_labels(edges)
    charges = vertex_charges(labels)
    charge_tuples = {vertex: charge_tuple(charge) for vertex, charge in charges.items()}
    oriented_edges = canonical_oriented_edges(edges, charges)

    charge_histogram = Counter(charge_tuples.values())
    unique_charge_vertices = [
        vertex for vertex, value in charge_tuples.items() if charge_histogram[value] == 1
    ]
    canonical_vertex_order = sorted(charge_tuples, key=lambda vertex: charge_tuples[vertex])
    canonical_root = canonical_vertex_order[0]
    root_charge = charge_tuples[canonical_root]

    edge_marker_histogram = Counter(canonical_edge_marker(edge) for edge in oriented_edges)
    uniquely_marked_edges = [
        edge["edge_id"]
        for edge in oriented_edges
        if edge_marker_histogram[canonical_edge_marker(edge)] == 1
    ]
    root_edge = min(oriented_edges, key=canonical_edge_marker)

    incidence = incidence_rows(oriented_edges)
    incidence_rank = rank_over_q(incidence)
    rooted_rank = rank_over_q(incidence + [[1 if vertex == canonical_root else 0 for vertex in range(VERTEX_COUNT)]])
    scalar_potential_gauge_dimension = VERTEX_COUNT - incidence_rank
    scalar_rooted_gauge_dimension = VERTEX_COUNT - rooted_rank
    four_component_gauge_dimension = len(PUBLIC_COMPONENTS) * scalar_potential_gauge_dimension
    four_component_rooted_gauge_dimension = len(PUBLIC_COMPONENTS) * scalar_rooted_gauge_dimension

    recovered, inconsistencies = recover_potential_from_flux(
        canonical_root,
        root_charge,
        oriented_edges,
    )
    recovered_matches_public_charges = {
        vertex: recovered.get(vertex) == charge_tuples[vertex]
        for vertex in range(VERTEX_COUNT)
    }
    root_zero_potential = {
        str(vertex): charge_dict(sub_charge_tuple(charge_tuples[vertex], root_charge))
        for vertex in sorted(charge_tuples)
    }

    ledger_candidate_group = ledger_stabilizer["derived"]["candidate_group"]
    checks = {
        "finite_exact_flux_balance_is_certified": finite_flux.get("status")
        == "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED"
        and finite_flux.get("all_checks_pass") is True,
        "augmented_ledger_stabilizer_is_certified": ledger_stabilizer.get("status")
        == "D20_HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_CERTIFIED"
        and ledger_stabilizer.get("all_checks_pass") is True,
        "graph_has_20_vertices_and_30_edges": len(labels) == VERTEX_COUNT
        and len(oriented_edges) == EDGE_COUNT,
        "public_charges_uniquely_mark_all_vertices": len(unique_charge_vertices) == VERTEX_COUNT,
        "canonical_root_is_unique": canonical_root == 0
        and charge_histogram[root_charge] == 1,
        "canonical_edge_markers_are_unique": len(uniquely_marked_edges) == EDGE_COUNT,
        "canonical_edge_orientation_has_no_charge_ties": all(
            edge["source_charge"] != edge["target_charge"] for edge in oriented_edges
        ),
        "incidence_rank_is_connected_graph_rank_19": incidence_rank == VERTEX_COUNT - 1,
        "rooted_incidence_rank_is_full_20": rooted_rank == VERTEX_COUNT,
        "unrooted_four_component_flux_potential_gauge_dimension_is_4": (
            four_component_gauge_dimension == len(PUBLIC_COMPONENTS)
        ),
        "rooted_four_component_flux_potential_gauge_dimension_is_0": (
            four_component_rooted_gauge_dimension == 0
        ),
        "canonical_rooted_flux_reconstruction_is_path_independent": inconsistencies == [],
        "canonical_rooted_flux_reconstruction_matches_public_charges": all(
            recovered_matches_public_charges.values()
        ),
        "augmented_ledger_has_no_residual_public_graph_symmetry": (
            int(ledger_candidate_group["full_augmented_ledger_stabilizer_order"]) == 1
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_CANONICAL_FLUX_BALANCE_GAUGE_CERTIFIED"
        if all_checks_pass
        else "D20_CANONICAL_FLUX_BALANCE_GAUGE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.canonical_flux_balance_gauge",
        "status": status,
        "object": "d20",
        "claim": (
            "The certified augmented D20 ledger defines a canonical finite boundary marking and a unique "
            "root-fixed exact flux-balance gauge. Public charge tuples uniquely mark all 20 D20 vertices; "
            "canonical charge-order orientation gives an incidence matrix of rank 19, and adding the "
            "canonical root makes the rank 20. Therefore the four-component exact boundary charge potential "
            "has only the expected four additive constants before rooting and no residual gauge freedom after "
            "rooting. The augmented ledger has no remaining graph-symmetry gauge."
        ),
        "definition": {
            "canonical_root": (
                "The unique D20 state with lexicographically minimal public charge tuple (M,J,P,Phi)."
            ),
            "canonical_edge_orientation": (
                "Each edge is oriented from the endpoint with smaller public charge tuple to the endpoint "
                "with larger public charge tuple."
            ),
            "root_fixed_flux_gauge": (
                "The exact boundary flux equation Flux(u,v)=Q(v)-Q(u), with Q at the canonical root fixed."
            ),
        },
        "inputs": {
            "finite_flux_balance_report": {
                "path": rel(FINITE_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_FLUX_BALANCE_REPORT),
            },
            "hidden_split_augmented_ledger_stabilizer_report": {
                "path": rel(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT),
                "sha256": sha_file(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT),
            },
            "hcycle_edge_table": {"path": rel(EDGE_CSV), "sha256": sha_file(EDGE_CSV)},
        },
        "derived": {
            "canonical_marking": {
                "canonical_root_vertex": canonical_root,
                "canonical_root_label": labels[canonical_root],
                "canonical_root_charge": charge_dict(root_charge),
                "canonical_vertex_order_by_public_charge": canonical_vertex_order,
                "unique_public_charge_vertex_count": len(unique_charge_vertices),
                "canonical_root_edge": {
                    "edge_id": root_edge["edge_id"],
                    "source": root_edge["source"],
                    "target": root_edge["target"],
                    "flux": root_edge["flux"],
                    "interface_weight": root_edge["interface_weight"],
                    "selector_duad_index": root_edge["selector_duad_index"],
                    "selector_choice": root_edge["selector_choice"],
                },
                "unique_canonical_edge_marker_count": len(uniquely_marked_edges),
                "canonical_oriented_edges_sha256": sha_json(oriented_edges),
            },
            "exact_flux_gauge": {
                "incidence_rank_over_q": incidence_rank,
                "rooted_incidence_rank_over_q": rooted_rank,
                "scalar_unrooted_gauge_dimension": scalar_potential_gauge_dimension,
                "scalar_rooted_gauge_dimension": scalar_rooted_gauge_dimension,
                "four_component_unrooted_gauge_dimension": four_component_gauge_dimension,
                "four_component_rooted_gauge_dimension": four_component_rooted_gauge_dimension,
                "root_fixed_reconstruction_inconsistencies": inconsistencies,
                "root_fixed_reconstruction_matches_public_charges": recovered_matches_public_charges,
                "root_zero_potential": root_zero_potential,
                "root_zero_potential_sha256": sha_json(root_zero_potential),
            },
            "residual_symmetry_gauge": {
                "hidden_split_stabilizer_order": ledger_candidate_group[
                    "hidden_split_stabilizer_order"
                ],
                "full_augmented_ledger_stabilizer_order": ledger_candidate_group[
                    "full_augmented_ledger_stabilizer_order"
                ],
                "full_augmented_ledger_preserving_automorphism_ids": ledger_candidate_group[
                    "full_augmented_ledger_preserving_automorphism_ids"
                ],
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the finite boundary screen has a canonical ledger-derived root and orientation",
                "exact public D20 flux has the standard connected-graph additive gauge before rooting",
                "fixing the canonical root removes that gauge completely",
                "the augmented ledger contributes no additional residual graph-symmetry gauge",
            ],
            "what_this_does_not_prove": (
                "This is a finite exact-flux gauge theorem. It does not prove a continuum BMS gauge choice or "
                "materialize the full Drinfeld idempotent coordinate matrix."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Push the canonical flux-balance gauge through the certified boundary-to-Loop_297 lift and test "
            "whether the cycle-8 Pi_33 obstruction remains canonical without materializing the full Drinfeld "
            "idempotent matrix."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.canonical_flux_balance_gauge_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify exact finite flux balance and augmented-ledger stabilizer inputs are certified",
            "verify public charges uniquely mark all 20 D20 vertices",
            "verify canonical charge-order edge orientation has no ties",
            "verify incidence rank 19 and rooted incidence rank 20",
            "verify root-fixed exact flux reconstruction is path-independent and matches public charges",
            "verify the full augmented ledger has no residual graph-symmetry gauge",
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
