from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import (
        adjacency_matrix,
        bareiss_det,
        laplacian,
        read_edges,
        reduced_matrix,
        rel,
        sha_file,
        sha_json,
    )
    from .paths import D20_INVARIANTS, HCYCLE_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_divisor_map.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import (
        adjacency_matrix,
        bareiss_det,
        laplacian,
        read_edges,
        reduced_matrix,
        rel,
        sha_file,
        sha_json,
    )
    from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS


THEOREM_ID = "tube_sandpile_divisor_map"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SCREEN0_TUBE_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_screen0_tube_central_element" / "report.json"
)
SANDPILE_REPORT = D20_INVARIANTS / "theorems" / "sandpile_critical_group" / "report.json"
RESIDUE_CSV = HCYCLE_INVARIANTS / "d20_Hcycle_mod2_residue_spectrum_all_subsets.csv"
EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"

RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK
SCREEN0_DEFECT_MASK = (1 << 7) | (1 << 9)
SINK_VERTEX = 0


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
        schema = index.get("schema", "d20.theorem_registry")
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        schema = "d20.theorem_registry"
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


def bit_indices(mask: int, width: int = RESIDUE_RANK) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def parse_basis_cycle_ids(value: str) -> list[int]:
    if not value.strip():
        return []
    return [int(part) for part in value.split()]


def load_residue_rows(path: Path = RESIDUE_CSV) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = []
        for row in csv.DictReader(f):
            mask = int(row["mask"])
            basis_cycle_ids = parse_basis_cycle_ids(row["basis_cycle_ids"])
            parsed_mask = sum(1 << idx for idx in basis_cycle_ids)
            incidence = row["incidence_vector_mod2"].strip()
            rows.append(
                {
                    "mask": mask,
                    "basis_cycle_ids": basis_cycle_ids,
                    "parsed_mask_from_basis_cycle_ids": parsed_mask,
                    "residue_edge_weight": int(row["residue_edge_weight"]),
                    "incidence_vector_mod2": incidence,
                }
            )
    return sorted(rows, key=lambda row: row["mask"])


def matrix_minor(matrix: list[list[int]], remove_row: int, remove_col: int) -> list[list[int]]:
    return [
        [value for col, value in enumerate(row) if col != remove_col]
        for row_idx, row in enumerate(matrix)
        if row_idx != remove_row
    ]


def adjugate(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    return [
        [
            ((-1) ** (row + col)) * bareiss_det(matrix_minor(matrix, col, row))
            for col in range(n)
        ]
        for row in range(n)
    ]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    rows = len(left)
    inner = len(right)
    cols = len(right[0]) if right else 0
    return [
        [sum(left[row][idx] * right[idx][col] for idx in range(inner)) for col in range(cols)]
        for row in range(rows)
    ]


def tube_grade(mask: int) -> int:
    return -1 if (mask & SCREEN0_DEFECT_MASK).bit_count() & 1 else 1


def oriented_divisor(incidence_vector_mod2: str, edges: list[dict[str, Any]]) -> list[int]:
    divisor = [0] * 20
    for bit, edge in zip(incidence_vector_mod2, edges):
        if bit != "1":
            continue
        divisor[int(edge["u"])] -= 1
        divisor[int(edge["v"])] += 1
    return divisor


def sandpile_key(reduced_divisor: list[int], adj: list[list[int]], determinant: int) -> tuple[int, ...]:
    return tuple(
        sum(adj[row][col] * reduced_divisor[col] for col in range(len(reduced_divisor))) % determinant
        for row in range(len(reduced_divisor))
    )


def class_order(key: tuple[int, ...], determinant: int) -> int:
    order = 1
    for value in key:
        order = math.lcm(order, determinant // math.gcd(determinant, int(value)))
    return order


def build_theorem() -> dict[str, Any]:
    screen0_tube = load_json(SCREEN0_TUBE_REPORT)
    sandpile = load_json(SANDPILE_REPORT)
    edges = read_edges(EDGES_CSV)
    residue_rows = load_residue_rows()

    lap = laplacian(adjacency_matrix(edges))
    reduced_laplacian = reduced_matrix(lap, SINK_VERTEX)
    determinant = abs(bareiss_det(reduced_laplacian))
    adj = adjugate(reduced_laplacian)
    adj_identity = matmul(adj, reduced_laplacian)
    expected_identity = [
        [determinant if row == col else 0 for col in range(len(reduced_laplacian))]
        for row in range(len(reduced_laplacian))
    ]

    rows = []
    classes: dict[tuple[int, ...], list[int]] = defaultdict(list)
    grades_by_class: dict[tuple[int, ...], set[int]] = defaultdict(set)
    class_order_by_key: dict[tuple[int, ...], int] = {}
    for residue in residue_rows:
        mask = int(residue["mask"])
        divisor = oriented_divisor(residue["incidence_vector_mod2"], edges)
        reduced_divisor = [
            value for vertex, value in enumerate(divisor) if vertex != SINK_VERTEX
        ]
        key = sandpile_key(reduced_divisor, adj, determinant)
        grade = tube_grade(mask)
        order = class_order(key, determinant)
        class_order_by_key[key] = order
        classes[key].append(mask)
        grades_by_class[key].add(grade)
        rows.append(
            {
                "mask": mask,
                "basis_cycle_ids": residue["basis_cycle_ids"],
                "tube_grade": grade,
                "tube_grade_parity": 0 if grade == 1 else 1,
                "active_edge_count": int(residue["residue_edge_weight"]),
                "oriented_divisor": divisor,
                "divisor_degree": int(sum(divisor)),
                "reduced_divisor_sink0": reduced_divisor,
                "sandpile_class_key_mod_tree_count": list(key),
                "sandpile_class_order": order,
            }
        )

    class_rows = []
    for idx, (key, masks) in enumerate(sorted(classes.items(), key=lambda item: item[1][0])):
        grades = sorted(grades_by_class[key])
        class_rows.append(
            {
                "class_index": idx,
                "class_key_mod_tree_count": list(key),
                "class_order": class_order_by_key[key],
                "mask_count": len(masks),
                "masks_first_16": masks[:16],
                "tube_grades_present": grades,
                "tube_grade_invariant_on_class": len(grades) == 1,
            }
        )

    grade_counts = Counter(row["tube_grade"] for row in rows)
    class_multiplicity_histogram = Counter(len(masks) for masks in classes.values())
    class_order_histogram = Counter(class_order_by_key.values())
    mask_order_histogram = Counter(row["sandpile_class_order"] for row in rows)
    mixed_classes = [row for row in class_rows if not row["tube_grade_invariant_on_class"]]
    pure_plus_classes = [
        row for row in class_rows if row["tube_grades_present"] == [1]
    ]
    pure_minus_classes = [
        row for row in class_rows if row["tube_grades_present"] == [-1]
    ]
    zero_key = tuple([0] * len(reduced_laplacian))
    zero_class_masks = classes.get(zero_key, [])
    parsed_consistent = all(
        row["mask"] == row["parsed_mask_from_basis_cycle_ids"] for row in residue_rows
    )
    active_counts_match = all(
        row["residue_edge_weight"] == row["incidence_vector_mod2"].count("1")
        for row in residue_rows
    )
    all_degrees_zero = all(row["divisor_degree"] == 0 for row in rows)

    checks = {
        "screen0_tube_element_is_certified": screen0_tube.get("status")
        == "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_CERTIFIED"
        and screen0_tube.get("all_checks_pass") is True,
        "sandpile_critical_group_is_certified": sandpile.get("status")
        == "D20_SANDPILE_CRITICAL_GROUP_CERTIFIED"
        and sandpile.get("all_checks_pass") is True,
        "residue_mask_count_is_2048": len(residue_rows) == MASK_COUNT,
        "residue_masks_are_complete": [row["mask"] for row in residue_rows] == list(range(MASK_COUNT)),
        "basis_cycle_ids_parse_to_mask": parsed_consistent,
        "incidence_vectors_have_30_bits": all(
            len(row["incidence_vector_mod2"]) == len(edges) == 30 for row in residue_rows
        ),
        "incidence_active_counts_match_residue_edge_weight": active_counts_match,
        "reduced_laplacian_determinant_is_tree_count": determinant == 5_184_000,
        "adjugate_identity_holds": adj_identity == expected_identity,
        "all_oriented_divisors_have_degree_zero": all_degrees_zero,
        "tube_grade_splits_masks_1024_1024": dict(grade_counts) == {1: 1024, -1: 1024},
        "sandpile_class_count_is_1360": len(classes) == 1360,
        "zero_mask_is_unique_zero_sandpile_class_in_image": zero_class_masks == [0],
        "tube_grade_is_not_sandpile_class_invariant": len(mixed_classes) == 154,
        "mixed_class_mask_count_is_576": sum(row["mask_count"] for row in mixed_classes) == 576,
        "class_order_histogram_matches": dict(sorted(class_order_histogram.items()))
        == {1: 1, 2: 2, 5: 3, 6: 19, 10: 23, 15: 94, 30: 1218},
        "mask_order_histogram_matches": dict(sorted(mask_order_histogram.items()))
        == {1: 1, 2: 6, 5: 3, 6: 31, 10: 24, 15: 124, 30: 1859},
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_DIVISOR_MAP_CERTIFIED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_DIVISOR_MAP_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_divisor_map",
        "status": status,
        "object": "d20",
        "claim": (
            "The screen-0 closed-loop tube involution grades all 2048 closed-return masks "
            "while the canonical oriented-edge divisor map sends those masks into 1360 "
            "distinct classes of the D20 sandpile critical group. The tube grade is not a "
            "function of this sandpile class: 154 sandpile classes contain masks of both grades."
        ),
        "definition": {
            "tube_grade": (
                "screen0(mask)=(-1)^(bit_7+bit_9), matching the closed-loop tube involution "
                "from signed_turn_screen_0."
            ),
            "oriented_divisor_map": (
                "For the canonical edge orientation u->v in subscript_Hcycle_d20_edges.csv, "
                "an active edge contributes e_v-e_u to a degree-zero graph divisor."
            ),
            "sandpile_class_key": (
                "With sink vertex 0 removed, key(mask)=adj(L_reduced)*divisor_reduced mod "
                "det(L_reduced). This embeds the critical group class in (Z/det Z)^19."
            ),
            "scope_boundary": (
                "This is a divisor-class comparison, not a recurrent-configuration burning "
                "algorithm and not a proof that tube grade is sandpile-class invariant."
            ),
        },
        "inputs": {
            "screen0_tube_central_element_report": {
                "path": rel(SCREEN0_TUBE_REPORT),
                "sha256": sha_file(SCREEN0_TUBE_REPORT),
            },
            "sandpile_critical_group_report": {
                "path": rel(SANDPILE_REPORT),
                "sha256": sha_file(SANDPILE_REPORT),
            },
            "closed_return_residue_spectrum": {
                "path": rel(RESIDUE_CSV),
                "sha256": sha_file(RESIDUE_CSV),
            },
            "hcycle_edge_table": {
                "path": rel(EDGES_CSV),
                "sha256": sha_file(EDGES_CSV),
            },
        },
        "derived": {
            "sink_vertex": SINK_VERTEX,
            "tree_count": determinant,
            "screen0_defect_mask": SCREEN0_DEFECT_MASK,
            "tube_grade_counts": {str(key): int(value) for key, value in sorted(grade_counts.items())},
            "sandpile_class_count_in_mask_image": len(classes),
            "sandpile_recurrent_class_count": int(
                sandpile["derived"]["critical_group"]["order"]
            ),
            "zero_class_masks": zero_class_masks,
            "class_multiplicity_histogram": {
                str(key): int(value) for key, value in sorted(class_multiplicity_histogram.items())
            },
            "sandpile_class_order_histogram_by_class": {
                str(key): int(value) for key, value in sorted(class_order_histogram.items())
            },
            "sandpile_class_order_histogram_by_mask": {
                str(key): int(value) for key, value in sorted(mask_order_histogram.items())
            },
            "tube_grade_vs_sandpile_class": {
                "tube_grade_class_invariant": False,
                "pure_plus_class_count": len(pure_plus_classes),
                "pure_minus_class_count": len(pure_minus_classes),
                "mixed_class_count": len(mixed_classes),
                "mixed_class_mask_count": sum(row["mask_count"] for row in mixed_classes),
                "mixed_classes_first_16": mixed_classes[:16],
            },
            "adjugate_certificate": {
                "reduced_laplacian_shape": [len(reduced_laplacian), len(reduced_laplacian[0])],
                "determinant": determinant,
                "adjugate_sha256": hashlib.sha256(canonical(adj)).hexdigest(),
                "adjugate_identity_holds": adj_identity == expected_identity,
            },
            "mask_divisor_rows_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
            "sandpile_class_rows_sha256": hashlib.sha256(canonical(class_rows)).hexdigest(),
            "mask_divisor_rows": rows,
            "sandpile_class_rows": class_rows,
        },
        "interpretation": {
            "what_is_certified": (
                "Every closed-return mask now has both a tube grade and an explicit sandpile "
                "critical-group class key under a stated oriented-edge divisor map."
            ),
            "what_this_does_not_prove": (
                "The tube grade does not descend to the certified sandpile class key. A stronger "
                "comparison would need a different divisor map, extra tube data, or a quotient that "
                "remembers the tube grade."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Explain the 154 mixed sandpile classes by extracting the kernel moves that preserve "
            "the oriented divisor class while flipping the screen-0 tube grade."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_divisor_map_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the screen-0 tube central element and sandpile group certificates",
            "map every residue mask to a degree-zero oriented graph divisor",
            "verify adj(L_reduced) L_reduced = det(L_reduced) I",
            "embed every divisor class as adj(L_reduced)d mod det(L_reduced)",
            "compare the screen-0 tube grade against the sandpile class image",
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
