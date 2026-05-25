from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_radical_gate_stabilizer"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_rank10_tenfold_alignment"
    / "report.json"
)

LOCAL_WIDTH = 4


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


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def bit_ids(mask: int, width: int = LOCAL_WIDTH) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def pattern_bits(pattern: int, width: int = LOCAL_WIDTH) -> str:
    return "".join("1" if (pattern >> idx) & 1 else "0" for idx in range(width))


def local_gate(pattern: int) -> bool:
    x2 = bool(pattern & 1)
    x3 = bool((pattern >> 1) & 1)
    x5 = bool((pattern >> 2) & 1)
    return x2 or (x3 and x5)


def gf2_rank(vectors: list[int], width: int = LOCAL_WIDTH) -> int:
    basis = [0] * width
    rank = 0
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot] == 0:
                basis[pivot] = value
                rank += 1
                break
            value ^= basis[pivot]
    return rank


def affine_rank(points: set[int], width: int = LOCAL_WIDTH) -> int:
    base = min(points)
    return gf2_rank([point ^ base for point in points], width)


def apply_linear(columns: tuple[int, ...], vector: int) -> int:
    target = 0
    for idx, column in enumerate(columns):
        if (vector >> idx) & 1:
            target ^= column
    return target


def matrix_rows(columns: tuple[int, ...]) -> list[list[int]]:
    return [
        [(columns[col] >> row) & 1 for col in range(LOCAL_WIDTH)]
        for row in range(LOCAL_WIDTH)
    ]


def all_gl4() -> list[tuple[int, ...]]:
    return [
        tuple(columns)
        for columns in product(range(1 << LOCAL_WIDTH), repeat=LOCAL_WIDTH)
        if gf2_rank(list(columns), LOCAL_WIDTH) == LOCAL_WIDTH
    ]


def point_permutation(columns: tuple[int, ...], translation: int, points: list[int]) -> list[int]:
    target_by_point = {
        point: apply_linear(columns, point) ^ translation
        for point in points
    }
    return [points.index(target_by_point[point]) for point in points]


def orbit_rows(
    affine_rows: list[dict[str, Any]],
    points: set[int],
) -> list[dict[str, Any]]:
    remaining = set(points)
    rows = []
    while remaining:
        start = min(remaining)
        orbit = {
            apply_linear(tuple(row["linear_columns"]), start) ^ int(row["translation"])
            for row in affine_rows
        }
        rows.append(
            {
                "start_pattern": pattern_bits(start),
                "orbit_size": len(orbit),
                "orbit_patterns": [pattern_bits(point) for point in sorted(orbit)],
            }
        )
        remaining -= orbit
    return rows


def build_theorem() -> dict[str, Any]:
    alignment = load_json(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT)
    alignment_derived = alignment.get("derived", {})
    alignment_summary = alignment_derived.get("alignment_summary", {})
    boolean_gate = alignment_derived.get("boolean_gate_witness", {})
    variable_axes = [int(axis) for axis in boolean_gate.get("variable_radical_axes", [])]
    radical_anchors = [int(value) for value in alignment_summary.get("radical_anchors", [])]
    common_core = int(alignment_summary.get("common_radical_core", 0))

    gate_support = {
        sum(
            (1 << idx)
            for idx, axis in enumerate(variable_axes)
            if (radical >> axis) & 1
        )
        for radical in radical_anchors
    }
    expected_support = {pattern for pattern in range(1 << LOCAL_WIDTH) if local_gate(pattern)}
    gate_complement = set(range(1 << LOCAL_WIDTH)) - gate_support
    gl4 = all_gl4()
    linear_stabilizers = [
        columns
        for columns in gl4
        if {apply_linear(columns, point) for point in gate_support} == gate_support
    ]
    affine_stabilizers = [
        {
            "linear_columns": list(columns),
            "linear_rows": matrix_rows(columns),
            "translation": translation,
            "translation_pattern": pattern_bits(translation),
            "support_permutation": point_permutation(
                columns,
                translation,
                sorted(gate_support),
            ),
        }
        for columns in gl4
        for translation in range(1 << LOCAL_WIDTH)
        if {apply_linear(columns, point) ^ translation for point in gate_support}
        == gate_support
    ]
    linear_stabilizer_rows = [
        {
            "linear_columns": list(columns),
            "linear_rows": matrix_rows(columns),
            "support_permutation": point_permutation(columns, 0, sorted(gate_support)),
        }
        for columns in linear_stabilizers
    ]

    identity_columns = tuple(1 << idx for idx in range(LOCAL_WIDTH))
    pure_translation_patterns = sorted(
        int(row["translation"])
        for row in affine_stabilizers
        if tuple(row["linear_columns"]) == identity_columns
    )
    all_translation_patterns = sorted({int(row["translation"]) for row in affine_stabilizers})
    support_orbits = orbit_rows(affine_stabilizers, gate_support)
    complement_orbits = orbit_rows(affine_stabilizers, gate_complement)

    transverse_shear_rows = [
        row
        for row in linear_stabilizer_rows
        if row["linear_columns"][1:] == [2, 4, 8]
    ]
    hyperplane_affine_rows = [
        row
        for row in affine_stabilizers
        if row["linear_columns"][0] == 1
    ]
    hyperplane_linear_rows = [
        row
        for row in linear_stabilizer_rows
        if row["linear_columns"][0] == 1
    ]

    stabilizer_summary = {
        "local_coordinate_order": ["x2", "x3", "x5", "x7"],
        "support_size": len(gate_support),
        "support_patterns": [pattern_bits(point) for point in sorted(gate_support)],
        "complement_size": len(gate_complement),
        "complement_patterns": [pattern_bits(point) for point in sorted(gate_complement)],
        "support_affine_rank": affine_rank(gate_support),
        "complement_affine_rank": affine_rank(gate_complement),
        "linear_stabilizer_order": len(linear_stabilizer_rows),
        "affine_stabilizer_order": len(affine_stabilizers),
        "pure_translation_stabilizer_order": len(pure_translation_patterns),
        "pure_translation_patterns": [
            pattern_bits(pattern) for pattern in pure_translation_patterns
        ],
        "all_affine_translation_patterns": [
            pattern_bits(pattern) for pattern in all_translation_patterns
        ],
        "transverse_shear_order": len(transverse_shear_rows),
        "hyperplane_linear_prism_stabilizer_order": len(hyperplane_linear_rows),
        "hyperplane_affine_prism_stabilizer_order": len(hyperplane_affine_rows),
        "support_orbit_sizes": [row["orbit_size"] for row in support_orbits],
        "complement_orbit_sizes": [row["orbit_size"] for row in complement_orbits],
    }
    complement_prism_witness = {
        "description": "The excluded six-point set is {x2=0} cap not(x3 and x5), equivalently {0,x3,x5} x F2_x7.",
        "affine_hull_equation": "x2 = 0",
        "base_triangle_patterns_x3x5": ["00", "10", "01"],
        "fiber_axis": "x7",
        "base_point_count": 3,
        "fiber_point_count": 2,
        "product_point_count": 6,
        "affine_hull_dimension": affine_rank(gate_complement),
    }
    group_decomposition = {
        "affine_order_factorization": "384 = 8 transverse shears * 48 complement-prism affine stabilizers",
        "linear_order_factorization": "64 = 8 transverse shears * 8 complement-prism linear stabilizers",
        "transverse_shear_group": "C2^3, sending x2-axis representatives to x2 plus any vector in the complement hyperplane",
        "hyperplane_affine_prism_stabilizer": "order 48 = 8 affine x7-shears over the base triangle times S3 on {0,x3,x5}",
        "hyperplane_linear_prism_stabilizer": "order 8 = 4 linear x7-shears over span{x3,x5} times S2 swapping x3 and x5",
        "support_orbits": support_orbits,
        "complement_orbits": complement_orbits,
    }

    checks = {
        "rank10_tenfold_alignment_is_certified": alignment.get("status")
        == "D20_FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_CERTIFIED"
        and alignment.get("all_checks_pass") is True,
        "gate_support_matches_alignment_radicals": gate_support == expected_support
        and len(gate_support) == 10
        and common_core == 83
        and variable_axes == [2, 3, 5, 7],
        "gate_complement_is_six_point_prism": len(gate_complement) == 6
        and affine_rank(gate_complement) == 3
        and sorted(gate_complement) == [0, 2, 4, 8, 10, 12],
        "support_is_full_affine_rank_but_not_affine_subspace": affine_rank(gate_support)
        == 4
        and len(gate_support) not in {1, 2, 4, 8, 16},
        "linear_stabilizer_order_is_64": len(linear_stabilizer_rows) == 64,
        "affine_stabilizer_order_is_384": len(affine_stabilizers) == 384,
        "pure_translation_stabilizer_is_x7_flip": pure_translation_patterns == [0, 8],
        "all_affine_translation_parts_are_complement_patterns": all_translation_patterns
        == sorted(gate_complement),
        "group_decomposition_orders_match": len(transverse_shear_rows) == 8
        and len(hyperplane_linear_rows) == 8
        and len(hyperplane_affine_rows) == 48
        and len(transverse_shear_rows) * len(hyperplane_affine_rows) == 384,
        "orbit_structure_matches_prism_gate": sorted(row["orbit_size"] for row in support_orbits)
        == [2, 8]
        and [row["orbit_size"] for row in complement_orbits] == [6],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_radical_gate_stabilizer",
        "status": status,
        "object": "d20",
        "claim": (
            "The full-exposure radical gate with fixed core 83 and condition x2 or (x3 and x5) "
            "has affine stabilizer order 384 and linear stabilizer order 64 on the four moving "
            "radical axes. Its six-point complement is a prism {0,x3,x5} x F2_x7 in the hyperplane "
            "x2=0; the stabilizer is the corresponding complement-prism stabilizer, extended by "
            "transverse x2 shears."
        ),
        "definition": {
            "local_gate": "A point in F2^4 with coordinates [x2,x3,x5,x7] is full-exposure iff x2 or (x3 and x5).",
            "affine_stabilizer": "All invertible affine transformations of F2^4 preserving the ten gate-support points.",
            "linear_stabilizer": "The zero-translation subgroup of the affine stabilizer.",
            "complement_prism": "The six excluded points {x2=0, not(x3 and x5)} = {0,x3,x5} x F2_x7.",
        },
        "inputs": {
            "full_exposure_rank10_tenfold_alignment_report": {
                "path": rel(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT),
            }
        },
        "derived": {
            "stabilizer_summary": stabilizer_summary,
            "complement_prism_witness": complement_prism_witness,
            "group_decomposition": group_decomposition,
            "linear_stabilizer_rows_sha256": sha_json(linear_stabilizer_rows),
            "affine_stabilizer_rows_sha256": sha_json(affine_stabilizers),
            "linear_stabilizer_sample_rows": linear_stabilizer_rows[:16],
            "affine_stabilizer_sample_rows": affine_stabilizers[:16],
        },
        "interpretation": {
            "what_this_proves": [
                "the ten full-exposure radical anchors have a nontrivial 384-element affine symmetry group",
                "the hidden organizing object is the six-point complement prism, not a ten-axis coordinate basis",
                "the gate splits the ten support points into two stabilizer orbits of sizes 8 and 2",
                "the x7 flip is the only pure translation symmetry of the gate",
            ],
            "what_this_does_not_prove": (
                "This classifies the four-moving-axis radical gate only. It does not yet lift every gate "
                "stabilizer element to a symmetry of the full packet propagation graph with charge-frame labels."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Lift the 384 radical-gate affine stabilizers to the full packet propagation graph and test which "
            "ones preserve charge-frame, gamma8, and action labels."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_radical_gate_stabilizer_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify rank-10/tenfold alignment input",
            "reconstruct the ten-point radical gate in local coordinates [x2,x3,x5,x7]",
            "enumerate GL(4,2) and AGL(4,2) stabilizers of the gate support",
            "verify the complement-prism description and affine ranks",
            "verify linear, affine, translation, decomposition, and orbit-order invariants",
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
