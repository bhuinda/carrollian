from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_kernel_flips.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.paths import D20_INVARIANTS


THEOREM_ID = "tube_sandpile_kernel_flips"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
TUBE_SANDPILE_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_divisor_map" / "report.json"
)

RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK
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


def grade_parity(delta_mask: int) -> int:
    return (delta_mask & SCREEN0_DEFECT_MASK).bit_count() & 1


def f2_rank(values: list[int]) -> tuple[int, list[int]]:
    basis: dict[int, int] = {}
    for value in sorted(set(values), reverse=True):
        x = value
        while x:
            pivot = x.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = x
                break
            x ^= basis[pivot]
    return len(basis), [basis[pivot] for pivot in sorted(basis, reverse=True)]


def class_key(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int(value) for value in row["sandpile_class_key_mod_tree_count"])


def divisor_key(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int(value) for value in row["reduced_divisor_sink0"])


def grade_set(rows: list[dict[str, Any]]) -> list[int]:
    return sorted({int(row["tube_grade"]) for row in rows})


def build_theorem() -> dict[str, Any]:
    source = load_json(TUBE_SANDPILE_REPORT)
    mask_rows = sorted(source["derived"]["mask_divisor_rows"], key=lambda row: int(row["mask"]))
    source_class_rows = source["derived"]["sandpile_class_rows"]
    class_index_by_key = {
        tuple(int(value) for value in row["class_key_mod_tree_count"]): int(row["class_index"])
        for row in source_class_rows
    }

    by_class: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
    by_divisor: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in mask_rows:
        by_class[class_key(row)].append(row)
        by_divisor[divisor_key(row)].append(row)

    divisor_fiber_rows = []
    same_divisor_pair_count = 0
    grade_flip_pair_rows = []
    grade_preserving_pair_count = 0
    flip_delta_counter: Counter[int] = Counter()
    preserve_delta_counter: Counter[int] = Counter()
    delta_fibers: dict[int, set[int]] = defaultdict(set)
    canonical_flip_witness_rows = []

    sorted_divisor_items = sorted(
        by_divisor.items(),
        key=lambda item: min(int(row["mask"]) for row in item[1]),
    )
    fiber_index_by_divisor = {key: idx for idx, (key, _rows) in enumerate(sorted_divisor_items)}

    for divisor, rows in sorted_divisor_items:
        rows = sorted(rows, key=lambda row: int(row["mask"]))
        masks = [int(row["mask"]) for row in rows]
        key = class_key(rows[0])
        class_index = class_index_by_key[key]
        grades = grade_set(rows)
        plus_count = sum(1 for row in rows if int(row["tube_grade"]) == 1)
        minus_count = sum(1 for row in rows if int(row["tube_grade"]) == -1)
        opposite_pair_count = plus_count * minus_count
        fiber_index = fiber_index_by_divisor[divisor]

        divisor_fiber_rows.append(
            {
                "fiber_index": fiber_index,
                "class_index": class_index,
                "min_mask": min(masks),
                "mask_count": len(rows),
                "masks_first_16": masks[:16],
                "tube_grades_present": grades,
                "plus_count": plus_count,
                "minus_count": minus_count,
                "opposite_grade_pair_count": opposite_pair_count,
                "sandpile_class_order": int(rows[0]["sandpile_class_order"]),
            }
        )

        pair_candidates = []
        for left_idx, left in enumerate(rows):
            for right in rows[left_idx + 1 :]:
                same_divisor_pair_count += 1
                left_mask = int(left["mask"])
                right_mask = int(right["mask"])
                delta = left_mask ^ right_mask
                if int(left["tube_grade"]) == int(right["tube_grade"]):
                    grade_preserving_pair_count += 1
                    preserve_delta_counter[delta] += 1
                    continue
                flip_delta_counter[delta] += 1
                delta_fibers[delta].add(fiber_index)
                pair_row = {
                    "pair_index": len(grade_flip_pair_rows),
                    "fiber_index": fiber_index,
                    "class_index": class_index,
                    "mask_a": left_mask,
                    "mask_b": right_mask,
                    "grade_a": int(left["tube_grade"]),
                    "grade_b": int(right["tube_grade"]),
                    "delta_mask": delta,
                    "delta_bits": bit_indices(delta),
                    "delta_hamming_weight": delta.bit_count(),
                }
                grade_flip_pair_rows.append(pair_row)
                pair_candidates.append(
                    (
                        delta.bit_count(),
                        delta,
                        left_mask,
                        right_mask,
                        pair_row,
                    )
                )

        if pair_candidates:
            _weight, _delta, _left, _right, pair_row = sorted(pair_candidates)[0]
            canonical_flip_witness_rows.append(
                {
                    "fiber_index": fiber_index,
                    "class_index": class_index,
                    "mask_a": pair_row["mask_a"],
                    "mask_b": pair_row["mask_b"],
                    "grade_a": pair_row["grade_a"],
                    "grade_b": pair_row["grade_b"],
                    "delta_mask": pair_row["delta_mask"],
                    "delta_bits": pair_row["delta_bits"],
                    "delta_hamming_weight": pair_row["delta_hamming_weight"],
                    "shared_reduced_divisor": list(divisor),
                    "sandpile_class_order": int(rows[0]["sandpile_class_order"]),
                }
            )

    flip_delta_rows = [
        {
            "delta_mask": delta,
            "delta_bits": bit_indices(delta),
            "delta_hamming_weight": delta.bit_count(),
            "screen0_parity": grade_parity(delta),
            "opposite_grade_pair_count": int(flip_delta_counter[delta]),
            "mixed_fiber_count": len(delta_fibers[delta]),
            "mixed_fibers_first_16": sorted(delta_fibers[delta])[:16],
        }
        for delta in sorted(flip_delta_counter)
    ]

    preserve_delta_rows = [
        {
            "delta_mask": delta,
            "delta_bits": bit_indices(delta),
            "delta_hamming_weight": delta.bit_count(),
            "screen0_parity": grade_parity(delta),
            "same_grade_pair_count": int(preserve_delta_counter[delta]),
        }
        for delta in sorted(preserve_delta_counter)
    ]

    mixed_fiber_indices = {
        row["fiber_index"]
        for row in divisor_fiber_rows
        if row["tube_grades_present"] == [-1, 1]
    }
    covered_fibers: set[int] = set()
    remaining_deltas = set(flip_delta_counter)
    small_flip_cover_rows = []
    while covered_fibers != mixed_fiber_indices:
        best_delta = min(
            remaining_deltas,
            key=lambda delta: (
                -len(delta_fibers[delta] - covered_fibers),
                delta.bit_count(),
                delta,
            ),
        )
        new_fibers = sorted(delta_fibers[best_delta] - covered_fibers)
        small_flip_cover_rows.append(
            {
                "cover_step": len(small_flip_cover_rows),
                "delta_mask": best_delta,
                "delta_bits": bit_indices(best_delta),
                "delta_hamming_weight": best_delta.bit_count(),
                "new_mixed_fiber_count": len(new_fibers),
                "total_mixed_fiber_count": len(delta_fibers[best_delta]),
                "opposite_grade_pair_count": int(flip_delta_counter[best_delta]),
                "new_mixed_fibers_first_16": new_fibers[:16],
            }
        )
        covered_fibers.update(delta_fibers[best_delta])
        remaining_deltas.remove(best_delta)

    class_divisor_counts = Counter()
    mixed_classes_from_divisors = set()
    for key, rows in by_class.items():
        divisor_count = len({divisor_key(row) for row in rows})
        class_divisor_counts[divisor_count] += 1
        if {int(row["tube_grade"]) for row in rows} == {-1, 1}:
            mixed_classes_from_divisors.add(class_index_by_key[key])

    flip_rank, flip_rank_basis = f2_rank(list(flip_delta_counter))
    mixed_mask_count = sum(
        row["mask_count"] for row in divisor_fiber_rows if row["tube_grades_present"] == [-1, 1]
    )

    grade_flip_pair_delta_weight_histogram = Counter(
        int(row["delta_hamming_weight"]) for row in grade_flip_pair_rows
    )
    unique_flip_delta_weight_histogram = Counter(delta.bit_count() for delta in flip_delta_counter)
    unique_preserve_delta_weight_histogram = Counter(delta.bit_count() for delta in preserve_delta_counter)
    divisor_fiber_histogram = Counter(len(rows) for rows in by_divisor.values())
    mixed_fiber_mask_count_histogram = Counter(
        row["mask_count"] for row in divisor_fiber_rows if row["tube_grades_present"] == [-1, 1]
    )
    mixed_fiber_grade_split_histogram = Counter(
        (row["plus_count"], row["minus_count"])
        for row in divisor_fiber_rows
        if row["tube_grades_present"] == [-1, 1]
    )
    single_bit_flip_deltas = sorted(delta for delta in flip_delta_counter if delta.bit_count() == 1)

    checks = {
        "source_tube_sandpile_divisor_map_is_certified": source.get("status")
        == "D20_TUBE_SANDPILE_DIVISOR_MAP_CERTIFIED"
        and source.get("all_checks_pass") is True,
        "mask_rows_are_complete": [int(row["mask"]) for row in mask_rows] == list(range(MASK_COUNT)),
        "exact_divisor_fiber_count_is_1368": len(by_divisor) == 1368,
        "sandpile_class_count_is_1360": len(by_class) == 1360,
        "eight_sandpile_classes_merge_two_exact_divisors": dict(sorted(class_divisor_counts.items()))
        == {1: 1352, 2: 8},
        "mixed_exact_divisor_fiber_count_is_154": len(mixed_fiber_indices) == 154,
        "mixed_exact_divisor_masks_count_is_576": mixed_mask_count == 576,
        "mixed_exact_divisor_fibers_match_mixed_sandpile_classes": len(mixed_classes_from_divisors)
        == 154
        and mixed_classes_from_divisors
        == {
            row["class_index"]
            for row in divisor_fiber_rows
            if row["tube_grades_present"] == [-1, 1]
        },
        "same_divisor_pair_count_is_2801": same_divisor_pair_count == 2801,
        "grade_flip_pair_count_is_1285": len(grade_flip_pair_rows) == 1285,
        "grade_preserving_pair_count_is_1516": grade_preserving_pair_count == 1516,
        "unique_grade_flip_delta_count_is_392": len(flip_delta_counter) == 392,
        "unique_grade_preserving_delta_count_is_365": len(preserve_delta_counter) == 365,
        "all_flip_deltas_are_screen0_odd": all(grade_parity(delta) == 1 for delta in flip_delta_counter),
        "all_preserving_deltas_are_screen0_even": all(
            grade_parity(delta) == 0 for delta in preserve_delta_counter
        ),
        "single_bit_flip_deltas_are_the_two_screen0_defects": single_bit_flip_deltas == [128, 512],
        "flip_delta_rank_over_f2_is_11": flip_rank == 11,
        "canonical_witness_count_is_154": len(canonical_flip_witness_rows) == 154,
        "small_flip_cover_has_5_moves": len(small_flip_cover_rows) == 5,
        "small_flip_cover_hits_all_154_mixed_fibers": len(covered_fibers) == 154,
        "divisor_fiber_histogram_matches": dict(sorted(divisor_fiber_histogram.items()))
        == {1: 1040, 2: 189, 3: 66, 4: 30, 5: 22, 6: 6, 7: 8, 9: 6, 56: 1},
        "mixed_fiber_mask_count_histogram_matches": dict(sorted(mixed_fiber_mask_count_histogram.items()))
        == {2: 59, 3: 42, 4: 21, 5: 15, 6: 5, 7: 6, 9: 5, 56: 1},
        "grade_flip_pair_delta_weight_histogram_matches": dict(
            sorted(grade_flip_pair_delta_weight_histogram.items())
        )
        == {1: 128, 2: 172, 3: 177, 4: 310, 5: 217, 6: 192, 7: 74, 8: 14, 9: 1},
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_KERNEL_FLIPS_CERTIFIED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_KERNEL_FLIPS_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_kernel_flips",
        "status": status,
        "object": "d20",
        "claim": (
            "The 154 sandpile classes with both screen-0 tube grades are already explained "
            "inside exact oriented-divisor fibers. There are 1285 same-divisor grade-flip "
            "mask pairs, with 392 distinct XOR move masks spanning rank 11 over F2."
        ),
        "definition": {
            "exact_divisor_fiber": (
                "Masks lie in the same exact divisor fiber when their reduced oriented-divisor "
                "vectors are equal before passing to the sandpile cokernel."
            ),
            "kernel_flip_move": (
                "A kernel flip move is an unordered same-divisor mask pair whose screen-0 tube "
                "grades are opposite; the move mask is the XOR of the two residue masks."
            ),
            "screen0_parity": "A move flips the tube grade exactly when it has odd pairing with bits 7 and 9.",
        },
        "inputs": {
            "tube_sandpile_divisor_map_report": {
                "path": rel(TUBE_SANDPILE_REPORT),
                "sha256": sha_file(TUBE_SANDPILE_REPORT),
            }
        },
        "derived": {
            "screen0_defect_mask": SCREEN0_DEFECT_MASK,
            "exact_divisor_fiber_count": len(by_divisor),
            "sandpile_class_count": len(by_class),
            "sandpile_class_exact_divisor_count_histogram": {
                str(key): int(value) for key, value in sorted(class_divisor_counts.items())
            },
            "exact_divisor_fiber_size_histogram": {
                str(key): int(value) for key, value in sorted(divisor_fiber_histogram.items())
            },
            "mixed_exact_divisor_fiber_count": len(mixed_fiber_indices),
            "mixed_exact_divisor_mask_count": mixed_mask_count,
            "mixed_fiber_mask_count_histogram": {
                str(key): int(value) for key, value in sorted(mixed_fiber_mask_count_histogram.items())
            },
            "mixed_fiber_grade_split_histogram": {
                f"{plus}:{minus}": int(value)
                for (plus, minus), value in sorted(mixed_fiber_grade_split_histogram.items())
            },
            "same_divisor_pair_count": same_divisor_pair_count,
            "grade_flip_pair_count": len(grade_flip_pair_rows),
            "grade_preserving_pair_count": grade_preserving_pair_count,
            "unique_grade_flip_delta_count": len(flip_delta_counter),
            "unique_grade_preserving_delta_count": len(preserve_delta_counter),
            "single_bit_flip_deltas": single_bit_flip_deltas,
            "single_bit_flip_delta_bits": [bit_indices(delta) for delta in single_bit_flip_deltas],
            "grade_flip_delta_rank_over_f2": flip_rank,
            "grade_flip_delta_rank_basis": flip_rank_basis,
            "unique_flip_delta_weight_histogram": {
                str(key): int(value) for key, value in sorted(unique_flip_delta_weight_histogram.items())
            },
            "unique_preserve_delta_weight_histogram": {
                str(key): int(value) for key, value in sorted(unique_preserve_delta_weight_histogram.items())
            },
            "grade_flip_pair_delta_weight_histogram": {
                str(key): int(value)
                for key, value in sorted(grade_flip_pair_delta_weight_histogram.items())
            },
            "divisor_fiber_rows_sha256": sha_json(divisor_fiber_rows),
            "grade_flip_pair_rows_sha256": sha_json(grade_flip_pair_rows),
            "flip_delta_rows_sha256": sha_json(flip_delta_rows),
            "preserve_delta_rows_sha256": sha_json(preserve_delta_rows),
            "canonical_flip_witness_rows_sha256": sha_json(canonical_flip_witness_rows),
            "small_flip_cover_rows_sha256": sha_json(small_flip_cover_rows),
            "divisor_fiber_rows": divisor_fiber_rows,
            "grade_flip_pair_rows": grade_flip_pair_rows,
            "flip_delta_rows": flip_delta_rows,
            "preserve_delta_rows": preserve_delta_rows,
            "canonical_flip_witness_rows": canonical_flip_witness_rows,
            "small_flip_cover_rows": small_flip_cover_rows,
        },
        "interpretation": {
            "what_is_certified": (
                "The mixed sandpile classes do not require nonzero Laplacian firing vectors: "
                "their grade flips occur inside exact oriented-divisor fibers."
            ),
            "what_this_does_not_prove": (
                "The five-move cover is deterministic and useful, but it is not certified as "
                "a minimum cover or as a presentation of all exact-divisor fibers."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Turn the 392 exact-divisor grade-flip move masks into a finite F2 presentation "
            "and identify the relations among the five-cover moves."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_kernel_flips_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "load the certified tube-to-sandpile divisor map",
            "partition the 2048 masks by exact reduced oriented divisor",
            "enumerate all same-divisor grade-flipping mask pairs",
            "group the flip pairs by XOR move mask and verify screen-0 parity",
            "build a deterministic five-move cover of all mixed exact-divisor fibers",
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
