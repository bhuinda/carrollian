from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, deque
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT
except ImportError:  # Supports `python src/derive_d20_sandpile_critical_group_theorem.py`.
    from paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "sandpile_critical_group"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
VERTEX_COUNT = 20
EXPECTED_EDGE_COUNT = 30
EXPECTED_CRITICAL_GROUP_FACTORS = [2, 12, 60, 60, 60]
EXPECTED_CRITICAL_GROUP_ORDER = 5_184_000


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


def read_edges(path: Path = EDGES_CSV) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    edges = []
    for row in rows:
        edges.append(
            {
                "edge_id": int(row["edge_id"]),
                "u": int(row["u"]),
                "v": int(row["v"]),
                "u_label": row["u_label"],
                "v_label": row["v_label"],
                "interface_weight": int(row["interface_weight"]),
                "selector_duad": row["selector_duad"],
                "selector_choice": int(row["selector_choice"]),
            }
        )
    return sorted(edges, key=lambda row: row["edge_id"])


def adjacency_matrix(edges: list[dict[str, Any]], vertex_count: int = VERTEX_COUNT) -> list[list[int]]:
    adjacency = [[0 for _ in range(vertex_count)] for _ in range(vertex_count)]
    for edge in edges:
        u = int(edge["u"])
        v = int(edge["v"])
        if not (0 <= u < vertex_count and 0 <= v < vertex_count):
            raise ValueError(f"edge {edge['edge_id']} has vertex outside 0..{vertex_count - 1}")
        adjacency[u][v] += 1
        adjacency[v][u] += 1
    return adjacency


def laplacian(adjacency: list[list[int]]) -> list[list[int]]:
    n = len(adjacency)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for i, row in enumerate(adjacency):
        matrix[i][i] = sum(row)
        for j, value in enumerate(row):
            if i != j:
                matrix[i][j] = -value
    return matrix


def reduced_matrix(matrix: list[list[int]], sink: int) -> list[list[int]]:
    return [
        [value for c, value in enumerate(row) if c != sink]
        for r, row in enumerate(matrix)
        if r != sink
    ]


def bareiss_det(matrix: list[list[int]]) -> int:
    n = len(matrix)
    if n == 0:
        return 1
    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for k in range(n - 1):
        pivot = k
        while pivot < n and work[pivot][k] == 0:
            pivot += 1
        if pivot == n:
            return 0
        if pivot != k:
            work[k], work[pivot] = work[pivot], work[k]
            sign *= -1
        pivot_value = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                work[i][j] = (work[i][j] * pivot_value - work[i][k] * work[k][j]) // previous
        previous = pivot_value
        for i in range(k + 1, n):
            work[i][k] = 0
        for j in range(k + 1, n):
            work[k][j] = 0
    return sign * work[n - 1][n - 1]


def smith_normal_form_diagonal(matrix: list[list[int]]) -> dict[str, Any]:
    """Return an exact Smith diagonal using integer row and column operations."""
    work = [row[:] for row in matrix]
    row_count = len(work)
    col_count = len(work[0]) if row_count else 0

    def swap_rows(left: int, right: int) -> None:
        if left != right:
            work[left], work[right] = work[right], work[left]

    def swap_cols(left: int, right: int) -> None:
        if left != right:
            for row in work:
                row[left], row[right] = row[right], row[left]

    def add_row(target: int, source: int, multiple: int) -> None:
        if multiple:
            work[target] = [x + multiple * y for x, y in zip(work[target], work[source])]

    def add_col(target: int, source: int, multiple: int) -> None:
        if multiple:
            for row in work:
                row[target] += multiple * row[source]

    def negate_row(row_index: int) -> None:
        work[row_index] = [-value for value in work[row_index]]

    pivot_row = 0
    pivot_col = 0
    reduction_steps = 0
    while pivot_row < row_count and pivot_col < col_count:
        pivot = None
        for r in range(pivot_row, row_count):
            for c in range(pivot_col, col_count):
                if work[r][c] and (
                    pivot is None or abs(work[r][c]) < abs(work[pivot[0]][pivot[1]])
                ):
                    pivot = (r, c)
        if pivot is None:
            break
        swap_rows(pivot_row, pivot[0])
        swap_cols(pivot_col, pivot[1])

        while True:
            reduction_steps += 1
            if reduction_steps > 1_000_000:
                raise RuntimeError("Smith normal form reduction did not converge")
            if work[pivot_row][pivot_col] < 0:
                negate_row(pivot_row)

            changed = False
            for r in range(row_count):
                if r == pivot_row or work[r][pivot_col] == 0:
                    continue
                quotient = work[r][pivot_col] // work[pivot_row][pivot_col]
                add_row(r, pivot_row, -quotient)
                if work[r][pivot_col] and abs(work[r][pivot_col]) < abs(work[pivot_row][pivot_col]):
                    swap_rows(r, pivot_row)
                    changed = True
                    break
            if changed:
                continue

            for c in range(col_count):
                if c == pivot_col or work[pivot_row][c] == 0:
                    continue
                quotient = work[pivot_row][c] // work[pivot_row][pivot_col]
                add_col(c, pivot_col, -quotient)
                if work[pivot_row][c] and abs(work[pivot_row][c]) < abs(work[pivot_row][pivot_col]):
                    swap_cols(c, pivot_col)
                    changed = True
                    break
            if changed:
                continue

            eliminated = False
            for r in range(row_count):
                if r != pivot_row and work[r][pivot_col]:
                    if work[r][pivot_col] % work[pivot_row][pivot_col] == 0:
                        add_row(r, pivot_row, -(work[r][pivot_col] // work[pivot_row][pivot_col]))
                        eliminated = True
                        break
            if eliminated:
                continue
            for c in range(col_count):
                if c != pivot_col and work[pivot_row][c]:
                    if work[pivot_row][c] % work[pivot_row][pivot_col] == 0:
                        add_col(c, pivot_col, -(work[pivot_row][c] // work[pivot_row][pivot_col]))
                        eliminated = True
                        break
            if eliminated:
                continue

            if any(work[r][pivot_col] for r in range(row_count) if r != pivot_row):
                continue
            if any(work[pivot_row][c] for c in range(col_count) if c != pivot_col):
                continue

            pivot_value = work[pivot_row][pivot_col]
            offender = None
            for r in range(pivot_row + 1, row_count):
                for c in range(pivot_col + 1, col_count):
                    if work[r][c] % pivot_value != 0:
                        offender = (r, c)
                        break
                if offender is not None:
                    break
            if offender is not None:
                add_row(pivot_row, offender[0], 1)
                continue
            break

        if work[pivot_row][pivot_col] < 0:
            negate_row(pivot_row)
        pivot_row += 1
        pivot_col += 1

    diagonal = [abs(work[i][i]) for i in range(min(row_count, col_count)) if work[i][i]]
    off_diagonal_nonzero = sum(
        1
        for r in range(row_count)
        for c in range(col_count)
        if r != c and work[r][c] != 0
    )
    divides = all(diagonal[i + 1] % diagonal[i] == 0 for i in range(len(diagonal) - 1))
    return {
        "diagonal": diagonal,
        "diagonal_multiplicities": {str(k): int(v) for k, v in sorted(Counter(diagonal).items())},
        "nonunit_invariant_factors": [value for value in diagonal if value != 1],
        "off_diagonal_nonzero": int(off_diagonal_nonzero),
        "divisibility_chain_valid": bool(divides),
        "reduction_steps": int(reduction_steps),
    }


def connected(adjacency: list[list[int]]) -> bool:
    seen = {0}
    queue: deque[int] = deque([0])
    while queue:
        node = queue.popleft()
        for other, value in enumerate(adjacency[node]):
            if value and other not in seen:
                seen.add(other)
                queue.append(other)
    return len(seen) == len(adjacency)


def build_theorem() -> dict[str, Any]:
    edges = read_edges()
    adjacency = adjacency_matrix(edges)
    lap = laplacian(adjacency)
    sink = 0
    reduced = reduced_matrix(lap, sink)
    snf = smith_normal_form_diagonal(reduced)
    cofactor_determinants = [abs(bareiss_det(reduced_matrix(lap, k))) for k in range(VERTEX_COUNT)]
    critical_group_order = math.prod(snf["nonunit_invariant_factors"])
    degree_histogram = Counter(sum(row) for row in adjacency)

    checks = {
        "edge_table_has_30_edges": len(edges) == EXPECTED_EDGE_COUNT,
        "edge_ids_are_contiguous": [edge["edge_id"] for edge in edges] == list(range(EXPECTED_EDGE_COUNT)),
        "graph_has_20_vertices": len(adjacency) == VERTEX_COUNT,
        "graph_is_simple": all(adjacency[i][i] == 0 for i in range(VERTEX_COUNT))
        and all(adjacency[i][j] in (0, 1) for i in range(VERTEX_COUNT) for j in range(VERTEX_COUNT)),
        "graph_is_cubic": dict(degree_histogram) == {3: VERTEX_COUNT},
        "graph_is_connected": connected(adjacency),
        "reduced_laplacian_is_19_by_19": len(reduced) == 19 and all(len(row) == 19 for row in reduced),
        "smith_form_is_diagonal": snf["off_diagonal_nonzero"] == 0,
        "smith_divisibility_chain_valid": snf["divisibility_chain_valid"] is True,
        "smith_diagonal_matches_d20_critical_group": snf["nonunit_invariant_factors"]
        == EXPECTED_CRITICAL_GROUP_FACTORS,
        "cofactors_are_sink_independent": sorted(set(cofactor_determinants))
        == [EXPECTED_CRITICAL_GROUP_ORDER],
        "critical_group_order_matches_spanning_tree_count": critical_group_order
        == cofactor_determinants[sink]
        == EXPECTED_CRITICAL_GROUP_ORDER,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SANDPILE_CRITICAL_GROUP_CERTIFIED"
        if all_checks_pass
        else "D20_SANDPILE_CRITICAL_GROUP_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sandpile_critical_group",
        "status": status,
        "object": "d20",
        "claim": (
            "The D20 H-cycle boundary graph has sandpile critical group "
            "Z/2 x Z/12 x Z/60^3. Equivalently, the reduced graph Laplacian "
            "has Smith invariant factors 1^14, 2, 12, 60, 60, 60, and the "
            "spanning-tree count is 5,184,000."
        ),
        "definition": {
            "transition_graph": "The 20-vertex, 30-edge H-cycle boundary graph from subscript_Hcycle_d20_edges.csv.",
            "laplacian": "L = degree_matrix - adjacency_matrix for the unweighted legal D20 graph.",
            "critical_group": "coker(L_reduced), where one sink row and column are deleted.",
            "sandpile_reading": (
                "The nonunit Smith invariant factors classify recurrent chip-firing states "
                "up to the graph Laplacian firing relation."
            ),
        },
        "inputs": {
            "hcycle_edge_table": {
                "path": rel(EDGES_CSV),
                "sha256": sha_file(EDGES_CSV),
            }
        },
        "derived": {
            "graph": {
                "vertices": VERTEX_COUNT,
                "edges": len(edges),
                "degree_histogram": {str(k): int(v) for k, v in sorted(degree_histogram.items())},
                "connected": connected(adjacency),
                "sink_vertex": sink,
            },
            "matrices": {
                "adjacency_matrix": adjacency,
                "laplacian_matrix": lap,
                "reduced_laplacian_sink_0": reduced,
            },
            "smith_normal_form": {
                "reduced_laplacian_diagonal": snf["diagonal"],
                "diagonal_multiplicities": snf["diagonal_multiplicities"],
                "nonunit_invariant_factors": snf["nonunit_invariant_factors"],
                "rank": len(snf["diagonal"]),
                "zero_invariant_factors_full_laplacian": 1,
                "off_diagonal_nonzero_after_reduction": snf["off_diagonal_nonzero"],
                "divisibility_chain_valid": snf["divisibility_chain_valid"],
                "reduction_steps": snf["reduction_steps"],
            },
            "critical_group": {
                "invariant_factors": snf["nonunit_invariant_factors"],
                "presentation": "Z/2 x Z/12 x Z/60^3",
                "order": int(critical_group_order),
                "spanning_tree_count": int(cofactor_determinants[sink]),
                "cofactor_determinants_by_deleted_vertex": cofactor_determinants,
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the README/imported critical-group value is reproduced from the canonical D20 H-cycle edge table",
                "the unweighted D20 legal transition graph has exactly 5,184,000 recurrent sandpile states",
                "the torsion structure is not only the order; it splits as Z/2 x Z/12 x Z/60^3",
            ],
            "what_this_does_not_prove": (
                "This certifies the unweighted H-cycle graph critical group. It does not yet classify "
                "which optical or hidden-residue sectors are recurrent, dissipating, or boundary-stable."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Pair the 2048 closed-return residue masks with the sandpile recurrent classes to classify "
            "which D20 residues are recurrent, dissipating, or boundary-stable."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sandpile_critical_group_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the H-cycle edge table is a connected cubic graph on 20 vertices and 30 edges",
            "compute the unweighted graph Laplacian and the sink-0 reduced Laplacian",
            "compute the exact Smith normal form of the reduced Laplacian",
            "verify every reduced cofactor determinant equals 5,184,000",
            "verify the critical group invariant factors are 2, 12, 60, 60, 60",
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
