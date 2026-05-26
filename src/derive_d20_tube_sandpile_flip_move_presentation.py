from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_flip_move_presentation.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.paths import D20_INVARIANTS


THEOREM_ID = "tube_sandpile_flip_move_presentation"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
KERNEL_FLIPS_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_kernel_flips" / "report.json"
)

RESIDUE_RANK = 11
SCREEN0_DEFECT_MASK = (1 << 7) | (1 << 9)


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


def rank_over_f2(values: list[int]) -> int:
    echelon: dict[int, int] = {}
    for value in values:
        x = value
        for pivot in sorted(echelon, reverse=True):
            if (x >> pivot) & 1:
                x ^= echelon[pivot]
        if x:
            echelon[x.bit_length() - 1] = x
    return len(echelon)


def greedy_source_basis(values: list[int]) -> list[int]:
    echelon: dict[int, int] = {}
    basis: list[int] = []
    for value in values:
        x = value
        for pivot in sorted(echelon, reverse=True):
            if (x >> pivot) & 1:
                x ^= echelon[pivot]
        if x:
            echelon[x.bit_length() - 1] = x
            basis.append(value)
    return basis


def solver_echelon(basis: list[int]) -> dict[int, tuple[int, int]]:
    echelon: dict[int, tuple[int, int]] = {}
    for idx, value in enumerate(basis):
        x = value
        coords = 1 << idx
        for pivot in sorted(echelon, reverse=True):
            if (x >> pivot) & 1:
                vec, vec_coords = echelon[pivot]
                x ^= vec
                coords ^= vec_coords
        if not x:
            raise ValueError("dependent basis vector")
        echelon[x.bit_length() - 1] = (x, coords)
    return echelon


def coordinates_for(value: int, basis: list[int]) -> int:
    x = value
    coords = 0
    for pivot, (vec, vec_coords) in sorted(solver_echelon(basis).items(), reverse=True):
        if (x >> pivot) & 1:
            x ^= vec
            coords ^= vec_coords
    if x:
        raise ValueError(f"value {value} is outside the span")
    return coords


def values_from_coordinate_mask(mask: int, basis: list[int]) -> list[int]:
    return [basis[idx] for idx in range(len(basis)) if (mask >> idx) & 1]


def coordinate_indices(mask: int, width: int) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def xor_all(values: list[int]) -> int:
    out = 0
    for value in values:
        out ^= value
    return out


def span_rows(values: list[int]) -> list[dict[str, Any]]:
    rows = []
    for selector in range(1, 1 << len(values)):
        selected = [values[idx] for idx in range(len(values)) if (selector >> idx) & 1]
        rows.append(
            {
                "selector_mask": selector,
                "selected_cover_indices": coordinate_indices(selector, len(values)),
                "sum_delta_mask": xor_all(selected),
                "sum_delta_bits": bit_indices(xor_all(selected)),
            }
        )
    return rows


def canonical_cover_coset_rows(
    generator_deltas: list[int],
    basis: list[int],
    cover_coordinate_span: set[int],
) -> list[dict[str, Any]]:
    buckets: dict[int, list[int]] = {}
    for delta in generator_deltas:
        coords = coordinates_for(delta, basis)
        representative = min(coords ^ span_coords for span_coords in cover_coordinate_span)
        buckets.setdefault(representative, []).append(delta)
    return [
        {
            "coset_index": idx,
            "coset_representative_coordinate_mask": representative,
            "coset_representative_basis_indices": coordinate_indices(representative, len(basis)),
            "generator_delta_count": len(deltas),
            "generator_delta_masks_first_16": sorted(deltas)[:16],
        }
        for idx, (representative, deltas) in enumerate(sorted(buckets.items()))
    ]


def build_theorem() -> dict[str, Any]:
    source = load_json(KERNEL_FLIPS_REPORT)
    source_derived = source["derived"]
    source_flip_rows = sorted(
        source_derived["flip_delta_rows"],
        key=lambda row: int(row["delta_mask"]),
    )
    generator_deltas = [int(row["delta_mask"]) for row in source_flip_rows]
    generator_index_by_delta = {delta: idx for idx, delta in enumerate(generator_deltas)}

    basis_deltas = greedy_source_basis(generator_deltas)
    basis_index_by_delta = {delta: idx for idx, delta in enumerate(basis_deltas)}
    basis_rows = [
        {
            "basis_index": idx,
            "source_generator_index": generator_index_by_delta[delta],
            "delta_mask": delta,
            "delta_bits": bit_indices(delta),
        }
        for idx, delta in enumerate(basis_deltas)
    ]

    generator_rows = []
    relation_rows = []
    for idx, row in enumerate(source_flip_rows):
        delta = int(row["delta_mask"])
        coords = coordinates_for(delta, basis_deltas)
        coord_indices = coordinate_indices(coords, len(basis_deltas))
        coord_deltas = values_from_coordinate_mask(coords, basis_deltas)
        generator_rows.append(
            {
                "generator_index": idx,
                "delta_mask": delta,
                "delta_bits": bit_indices(delta),
                "basis_coordinate_mask": coords,
                "basis_indices": coord_indices,
                "opposite_grade_pair_count": int(row["opposite_grade_pair_count"]),
                "mixed_fiber_count": int(row["mixed_fiber_count"]),
            }
        )
        if delta in basis_index_by_delta:
            continue
        relation_deltas = [delta] + coord_deltas
        relation_rows.append(
            {
                "relation_index": len(relation_rows),
                "source_generator_index": idx,
                "source_delta_mask": delta,
                "source_delta_bits": bit_indices(delta),
                "basis_coordinate_mask": coords,
                "basis_indices": coord_indices,
                "basis_delta_masks": coord_deltas,
                "relation_delta_masks": relation_deltas,
                "relation_weight": len(relation_deltas),
                "xor_sum": xor_all(relation_deltas),
            }
        )

    cover_source_rows = source_derived["small_flip_cover_rows"]
    cover_deltas = [int(row["delta_mask"]) for row in cover_source_rows]
    cover_coordinate_rows = []
    for row in cover_source_rows:
        delta = int(row["delta_mask"])
        coords = coordinates_for(delta, basis_deltas)
        cover_coordinate_rows.append(
            {
                "cover_step": int(row["cover_step"]),
                "delta_mask": delta,
                "delta_bits": bit_indices(delta),
                "basis_coordinate_mask": coords,
                "basis_indices": coordinate_indices(coords, len(basis_deltas)),
                "basis_delta_masks": values_from_coordinate_mask(coords, basis_deltas),
                "new_mixed_fiber_count": int(row["new_mixed_fiber_count"]),
                "total_mixed_fiber_count": int(row["total_mixed_fiber_count"]),
            }
        )

    cover_nonzero_sum_rows = span_rows(cover_deltas)
    cover_coordinate_span = {
        xor_all(
            [
                coordinates_for(cover_deltas[idx], basis_deltas)
                for idx in range(len(cover_deltas))
                if (selector >> idx) & 1
            ]
        )
        for selector in range(1 << len(cover_deltas))
    }
    cover_delta_span = {row["sum_delta_mask"] for row in cover_nonzero_sum_rows} | {0}
    cover_span_flip_deltas = sorted(set(generator_deltas) & cover_delta_span)
    cover_coset_rows = canonical_cover_coset_rows(
        generator_deltas,
        basis_deltas,
        cover_coordinate_span,
    )

    relation_weight_histogram = Counter(int(row["relation_weight"]) for row in relation_rows)
    cover_coset_size_histogram = Counter(
        int(row["generator_delta_count"]) for row in cover_coset_rows
    )

    checks = {
        "source_kernel_flips_is_certified": source.get("status")
        == "D20_TUBE_SANDPILE_KERNEL_FLIPS_CERTIFIED"
        and source.get("all_checks_pass") is True,
        "source_flip_delta_count_is_392": int(source_derived.get("unique_grade_flip_delta_count")) == 392,
        "source_flip_delta_rank_is_11": int(source_derived.get("grade_flip_delta_rank_over_f2")) == 11,
        "generator_count_is_392": len(generator_deltas) == 392,
        "generator_deltas_are_unique": len(set(generator_deltas)) == len(generator_deltas),
        "all_generator_deltas_are_screen0_odd": all(
            ((delta & SCREEN0_DEFECT_MASK).bit_count() & 1) == 1 for delta in generator_deltas
        ),
        "canonical_basis_deltas_match": basis_deltas
        == [128, 129, 130, 134, 136, 144, 161, 192, 384, 512, 1152],
        "presentation_rank_is_11": rank_over_f2(generator_deltas) == RESIDUE_RANK,
        "basis_rank_is_11": rank_over_f2(basis_deltas) == RESIDUE_RANK,
        "relation_count_is_381": len(relation_rows) == len(generator_deltas) - RESIDUE_RANK,
        "relations_all_xor_to_zero": all(int(row["xor_sum"]) == 0 for row in relation_rows),
        "relations_cover_all_nonbasis_generators": sorted(
            int(row["source_delta_mask"]) for row in relation_rows
        )
        == sorted(set(generator_deltas) - set(basis_deltas)),
        "relation_weight_histogram_matches": {
            str(key): int(value) for key, value in sorted(relation_weight_histogram.items())
        }
        == {"4": 93, "6": 199, "8": 86, "10": 3},
        "presentation_quotient_order_is_2048": 2 ** rank_over_f2(generator_deltas) == 2048,
        "cover_deltas_match_kernel_flip_cover": cover_deltas == [1560, 128, 512, 130, 421],
        "cover_moves_are_generator_deltas": set(cover_deltas).issubset(set(generator_deltas)),
        "cover_rank_is_5": rank_over_f2(cover_deltas) == 5,
        "cover_has_no_nonzero_relation": all(
            int(row["sum_delta_mask"]) != 0 for row in cover_nonzero_sum_rows
        ),
        "cover_nonzero_sum_count_is_31": len(cover_nonzero_sum_rows) == 31,
        "cover_span_size_is_32": len(cover_delta_span) == 32,
        "cover_span_flip_delta_count_is_9": len(cover_span_flip_deltas) == 9,
        "cover_quotient_dimension_is_6": RESIDUE_RANK - rank_over_f2(cover_deltas) == 6,
        "cover_coset_count_is_64": len(cover_coset_rows) == 64,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_FLIP_MOVE_PRESENTATION_CERTIFIED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_FLIP_MOVE_PRESENTATION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_flip_move_presentation",
        "status": status,
        "object": "d20",
        "claim": (
            "The 392 exact-divisor tube-grade flip moves present the full 11-dimensional "
            "F2 residue move space. A canonical 11-move basis yields 381 linear relations, "
            "and the deterministic five-cover moves are F2-independent."
        ),
        "definition": {
            "flip_move_generator": (
                "One named generator is assigned to each distinct grade-flipping XOR move "
                "from the exact-divisor flip census."
            ),
            "presentation_map": (
                "The finite F2 presentation map sends each named generator to its 11-bit "
                "residue delta mask. The kernel of this map is the linear relation space."
            ),
            "cover_move_relation": (
                "A relation among the five cover moves is a nonempty F2 sum of their delta "
                "masks equal to zero."
            ),
        },
        "inputs": {
            "tube_sandpile_kernel_flips_report": {
                "path": rel(KERNEL_FLIPS_REPORT),
                "sha256": sha_file(KERNEL_FLIPS_REPORT),
            }
        },
        "derived": {
            "residue_rank": RESIDUE_RANK,
            "screen0_defect_mask": SCREEN0_DEFECT_MASK,
            "presentation": {
                "generator_count": len(generator_deltas),
                "basis_count": len(basis_deltas),
                "relation_count": len(relation_rows),
                "rank_over_f2": rank_over_f2(generator_deltas),
                "relation_space_dimension": len(relation_rows),
                "quotient_order": 2 ** rank_over_f2(generator_deltas),
                "basis_delta_masks": basis_deltas,
                "basis_delta_bits": [bit_indices(delta) for delta in basis_deltas],
                "relation_weight_histogram": {
                    str(key): int(value) for key, value in sorted(relation_weight_histogram.items())
                },
            },
            "five_cover": {
                "cover_delta_masks": cover_deltas,
                "cover_delta_bits": [bit_indices(delta) for delta in cover_deltas],
                "rank_over_f2": rank_over_f2(cover_deltas),
                "relation_count": 0,
                "nonzero_sum_count": len(cover_nonzero_sum_rows),
                "span_size": len(cover_delta_span),
                "span_flip_delta_count": len(cover_span_flip_deltas),
                "span_flip_delta_masks": cover_span_flip_deltas,
                "quotient_dimension": RESIDUE_RANK - rank_over_f2(cover_deltas),
                "coset_count": len(cover_coset_rows),
                "coset_size_histogram": {
                    str(key): int(value) for key, value in sorted(cover_coset_size_histogram.items())
                },
            },
            "basis_rows_sha256": sha_json(basis_rows),
            "generator_rows_sha256": sha_json(generator_rows),
            "relation_rows_sha256": sha_json(relation_rows),
            "cover_coordinate_rows_sha256": sha_json(cover_coordinate_rows),
            "cover_nonzero_sum_rows_sha256": sha_json(cover_nonzero_sum_rows),
            "cover_coset_rows_sha256": sha_json(cover_coset_rows),
            "basis_rows": basis_rows,
            "generator_rows": generator_rows,
            "relation_rows": relation_rows,
            "cover_coordinate_rows": cover_coordinate_rows,
            "cover_nonzero_sum_rows": cover_nonzero_sum_rows,
            "cover_coset_rows": cover_coset_rows,
        },
        "interpretation": {
            "what_is_certified": (
                "The flip moves are no longer only a census: they have a finite linear "
                "presentation over F2. The full move span is 11-dimensional, while the "
                "five cover moves form a free rank-5 subspace."
            ),
            "what_this_does_not_prove": (
                "The five cover moves hit every mixed exact-divisor fiber by incidence, but "
                "their span is not the full 11-dimensional flip-move space."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Use the six-dimensional quotient by the five-cover span to classify the "
            "remaining flip-move cosets against tube and sandpile observables."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_flip_move_presentation_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "load the certified exact-divisor flip-move census",
            "build the 392-generator F2 presentation map",
            "choose the canonical 11-move basis by ascending delta masks",
            "derive all 381 linear relations against that basis",
            "prove the five cover moves have no nonzero F2 relation",
            "classify the quotient by the five-cover span into 64 cosets",
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
