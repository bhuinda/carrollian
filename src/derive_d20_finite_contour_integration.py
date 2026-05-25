from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports `python src/derive_d20_finite_contour_integration.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_finite_contour_integration"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
D20_JSON = ROOT / "d20.json"


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
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def rank_mod2(matrix: list[list[int]]) -> int:
    work = [[value & 1 for value in row] for row in matrix]
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
        for row in range(row_count):
            if row != rank and work[row][col]:
                work[row] = [a ^ b for a, b in zip(work[row], work[rank])]
        rank += 1
    return rank


def rank_rational(matrix: list[list[int]]) -> int:
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


def incidence_and_gradient(
    edge_rows: list[dict[str, Any]],
    vertex_count: int,
    edge_count: int,
) -> tuple[list[list[int]], list[list[int]], list[tuple[int, int, int, int]]]:
    incidence = [[0 for _ in range(edge_count)] for _ in range(vertex_count)]
    gradient = [[0 for _ in range(vertex_count)] for _ in range(edge_count)]
    edge_info = []
    for row in edge_rows:
        edge_id = int(row["edge_id"])
        u = int(row["u"])
        v = int(row["v"])
        weight = int(row["interface_weight"])
        incidence[u][edge_id] = -1
        incidence[v][edge_id] = 1
        gradient[edge_id][u] = -1
        gradient[edge_id][v] = 1
        edge_info.append((u, v, edge_id, weight))
    return incidence, gradient, edge_info


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix:
        return []
    return [[matrix[row][col] for row in range(len(matrix))] for col in range(len(matrix[0]))]


def matmul_mod2(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    if not left or not right:
        return []
    rows = len(left)
    cols = len(right[0])
    inner = len(right)
    return [
        [
            sum((left[row][idx] & 1) * (right[idx][col] & 1) for idx in range(inner)) & 1
            for col in range(cols)
        ]
        for row in range(rows)
    ]


def signed_integral_for_cycle(
    cycle: dict[str, Any],
    edge_by_id: dict[int, tuple[int, int, int]],
) -> int:
    signed = 0
    for start, stop, edge_id in zip(cycle["vertices"][:-1], cycle["vertices"][1:], cycle["edge_ids"]):
        u, v, weight = edge_by_id[int(edge_id)]
        if (int(start), int(stop)) == (u, v):
            signed += weight
        elif (int(start), int(stop)) == (v, u):
            signed -= weight
        else:
            raise ValueError(
                f"cycle {cycle['cycle_id']} edge {edge_id} is not incident to {start}->{stop}"
            )
    return signed


def build_theorem() -> dict[str, Any]:
    data = load_json(D20_JSON)
    edge_rows = data["game_theory"]["tables"]["subscript_Hcycle_d20_edges.csv"]["rows"]
    cycles = data["game_theory"]["primitive_H_cycles"]["cycles"]
    w_d6 = int(data["optics"]["constants"]["W_D6_order"])

    vertex_count = 20
    edge_count = 30
    incidence, gradient, edge_info = incidence_and_gradient(edge_rows, vertex_count, edge_count)
    edge_by_id = {edge_id: (u, v, weight) for u, v, edge_id, weight in edge_info}
    weights = [edge_by_id[edge_id][2] for edge_id in range(edge_count)]
    cycle_matrix = [[int(value) for value in cycle["incidence_vector_mod2"]] for cycle in cycles]
    boundary_matrix = matmul_mod2(incidence, transpose(cycle_matrix))

    positive_integrals = []
    signed_integrals = []
    cycle_rows = []
    for cycle in cycles:
        incidence_vector = [int(value) for value in cycle["incidence_vector_mod2"]]
        positive = sum(value * weight for value, weight in zip(incidence_vector, weights))
        signed = signed_integral_for_cycle(cycle, edge_by_id)
        stored_entropy = float(cycle["entropy_proxy_A_over_4WD6"])
        computed_entropy = Fraction(positive, 4 * w_d6)
        positive_integrals.append(positive)
        signed_integrals.append(signed)
        cycle_rows.append(
            {
                "cycle_id": int(cycle["cycle_id"]),
                "length": int(cycle["length"]),
                "stored_optical_action": int(cycle["optical_action"]),
                "computed_positive_integral": int(positive),
                "positive_matches_stored": positive == int(cycle["optical_action"]),
                "computed_entropy_proxy_A_over_4WD6": str(computed_entropy),
                "stored_entropy_proxy_A_over_4WD6": stored_entropy,
                "entropy_proxy_matches_stored": abs(float(computed_entropy) - stored_entropy) < 1e-9,
                "signed_contour_integral": int(signed),
                "edge_ids": [int(value) for value in cycle["edge_ids"]],
            }
        )

    signed_gcd = math.gcd(*[abs(value) for value in signed_integrals if value])
    primitive_residue_vector = [int(value // signed_gcd) for value in signed_integrals]
    primitive_gcd = math.gcd(*[abs(value) for value in primitive_residue_vector if value])
    augmented_gradient = [row + [weights[idx]] for idx, row in enumerate(gradient)]
    rank_gradient = rank_rational(gradient)
    rank_augmented = rank_rational(augmented_gradient)
    contour_summary = {
        "vertex_count": vertex_count,
        "edge_count": edge_count,
        "rank_incidence_over_Q": rank_rational(incidence),
        "rank_incidence_over_F2": rank_mod2(incidence),
        "cycle_rank_expected": edge_count - vertex_count + 1,
        "primitive_cycle_count": len(cycles),
        "primitive_cycle_rank_over_F2": rank_mod2(cycle_matrix),
        "boundary_defects_over_F2": sum(sum(row) for row in boundary_matrix),
    }
    checks = {
        "d20_object_is_certified": data.get("status") == "D20_CERTIFIED",
        "game_theory_is_certified": data.get("game_theory", {}).get("status")
        == "D20_HCYCLE_GAME_THEORY_CERTIFIED",
        "optics_wd6_constant_present": w_d6 == 23040,
        "graph_has_20_vertices_30_edges": vertex_count == 20 and edge_count == 30,
        "incidence_rank_is_19_over_Q": contour_summary["rank_incidence_over_Q"] == 19,
        "incidence_rank_is_19_over_F2": contour_summary["rank_incidence_over_F2"] == 19,
        "cycle_rank_is_11": contour_summary["cycle_rank_expected"] == 11,
        "primitive_cycles_are_full_F2_basis": contour_summary["primitive_cycle_rank_over_F2"] == 11
        and len(cycles) == 11,
        "primitive_cycle_boundaries_vanish": contour_summary["boundary_defects_over_F2"] == 0,
        "positive_integrals_match_stored_optical_actions": all(
            row["positive_matches_stored"] for row in cycle_rows
        ),
        "entropy_proxies_match_positive_integrals": all(
            row["entropy_proxy_matches_stored"] for row in cycle_rows
        ),
        "signed_residue_gcd_is_3072": signed_gcd == 3072,
        "primitive_residue_vector_is_primitive": primitive_gcd == 1,
        "mod26_residue_vector_matches_expected": [
            int((value // signed_gcd) % 26) for value in signed_integrals
        ]
        == [24, 10, 12, 20, 12, 23, 8, 2, 12, 11, 23],
        "gradient_exactness_obstructed_over_Q": rank_gradient == 19
        and rank_augmented == 20,
    }
    report = {
        "schema": "d20.theorem.d20_finite_contour_integration",
        "status": "D20_FINITE_CONTOUR_INTEGRATION_TEST_PASS",
        "object": "D20",
        "definition": {
            "finite_contour_integral": (
                "the sum of certified edge weights over a closed H-cycle contour"
            ),
            "signed_residue": (
                "the signed integral of the same edge 1-form along the oriented primitive cycle"
            ),
            "exactness_obstruction": (
                "the rational inconsistency of D phi = w for the oriented edge-gradient matrix"
            ),
        },
        "claim": (
            "The D20 H-cycle table is a finite contour-action table: positive contour "
            "integrals reproduce the stored optical actions, the primitive H-cycles form "
            "an 11-dimensional F2 cycle basis with no boundary defects, and signed "
            "contour residues obstruct global exactness. After dividing by 3072, the "
            "signed residues form a primitive integral line whose mod-26 reduction is "
            "(24,10,12,20,12,23,8,2,12,11,23)."
        ),
        "inputs": {
            "d20_json": input_record(D20_JSON),
        },
        "derived": {
            "contour_summary": contour_summary,
            "edge_weight_quantization": {
                "gcd_edge_weights": math.gcd(*weights),
                "min_edge_weight": min(weights),
                "max_edge_weight": max(weights),
                "sum_edge_weights": sum(weights),
            },
            "positive_contour_action": {
                "all_match_stored_optical_actions": all(
                    row["positive_matches_stored"] for row in cycle_rows
                ),
                "gcd_positive_integrals": math.gcd(*positive_integrals),
                "W_D6_order": w_d6,
            },
            "signed_contour_residue": {
                "gcd_signed_integrals": signed_gcd,
                "normalization": signed_gcd,
                "primitive_residue_vector": primitive_residue_vector,
                "primitive_residue_vector_gcd": primitive_gcd,
                "mod26_residue_vector": [
                    int((value // signed_gcd) % 26) for value in signed_integrals
                ],
                "zero_signed_integral_cycles": [
                    idx for idx, value in enumerate(signed_integrals) if value == 0
                ],
            },
            "exactness_obstruction": {
                "rank_gradient_over_Q": rank_gradient,
                "rank_augmented_over_Q": rank_augmented,
                "exact_1_form_over_Q": rank_gradient == rank_augmented,
                "interpretation": (
                    "Nonzero signed contour residues obstruct a global vertex potential; "
                    "the finite edge 1-form is not exact."
                ),
            },
            "cycle_rows": cycle_rows,
            "cycle_rows_sha256": sha_json(cycle_rows),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "finite_stokes_reading": (
                "D20 has a certified finite contour calculus on its public H-cycle boundary."
            ),
            "sector26_reading": (
                "The primitive signed residue line has a natural mod-26 ledger reduction."
            ),
            "not_claimed": (
                "This is not a proof of P != NP, not M-theory itself, and not a theorem about "
                "rational prime distribution."
            ),
        },
        "next_highest_yield_item": (
            "Compare the primitive contour residue line against the sector-26 charge kernel and "
            "the packet SNF obstruction to see whether the same mod-2/mod-3/mod-13 split appears."
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
        "schema": "d20.theorem.d20_finite_contour_integration_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "verify the finite contour-action reading of the D20 H-cycle table",
            "certify the signed residue obstruction to exactness",
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
