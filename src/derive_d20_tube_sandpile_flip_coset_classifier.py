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
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_flip_coset_classifier.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.paths import D20_INVARIANTS


THEOREM_ID = "tube_sandpile_flip_coset_classifier"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
PRESENTATION_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_flip_move_presentation" / "report.json"
)
KERNEL_FLIPS_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_kernel_flips" / "report.json"
)

RESIDUE_RANK = 11
SCREEN0_DEFECT_MASK = (1 << 7) | (1 << 9)
COVER_DELTAS = [1560, 128, 512, 130, 421]
SINGLE_BIT_DEFECT_DELTAS = [128, 512]


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


def coordinate_indices(mask: int, width: int = RESIDUE_RANK) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def xor_all(values: list[int]) -> int:
    out = 0
    for value in values:
        out ^= value
    return out


def span_from_coordinate_masks(values: list[int]) -> set[int]:
    out: set[int] = set()
    for selector in range(1 << len(values)):
        selected = [values[idx] for idx in range(len(values)) if (selector >> idx) & 1]
        out.add(xor_all(selected))
    return out


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items())}


def grade_split_key(plus_count: int, minus_count: int) -> str:
    return f"{plus_count}:{minus_count}"


def grade_pair_key(grade_a: int, grade_b: int) -> str:
    return f"{grade_a}->{grade_b}"


def build_theorem() -> dict[str, Any]:
    presentation = load_json(PRESENTATION_REPORT)
    kernel = load_json(KERNEL_FLIPS_REPORT)
    pres_derived = presentation["derived"]
    kernel_derived = kernel["derived"]

    cover_coordinate_masks = [
        int(row["basis_coordinate_mask"])
        for row in pres_derived["cover_coordinate_rows"]
    ]
    cover_coordinate_span = span_from_coordinate_masks(cover_coordinate_masks)
    coset_index_by_representative = {
        int(row["coset_representative_coordinate_mask"]): int(row["coset_index"])
        for row in pres_derived["cover_coset_rows"]
    }

    def representative(coords: int) -> int:
        return min(coords ^ span_coords for span_coords in cover_coordinate_span)

    delta_to_generator_row: dict[int, dict[str, Any]] = {}
    delta_to_coset_index: dict[int, int] = {}
    for row in pres_derived["generator_rows"]:
        delta = int(row["delta_mask"])
        coords = int(row["basis_coordinate_mask"])
        rep = representative(coords)
        delta_to_generator_row[delta] = row
        delta_to_coset_index[delta] = coset_index_by_representative[rep]

    fiber_rows_by_index = {
        int(row["fiber_index"]): row
        for row in kernel_derived["divisor_fiber_rows"]
    }

    by_coset: dict[int, dict[str, Any]] = {}
    for row in pres_derived["cover_coset_rows"]:
        coset_index = int(row["coset_index"])
        by_coset[coset_index] = {
            "representative_coordinate_mask": int(row["coset_representative_coordinate_mask"]),
            "representative_basis_indices": [
                int(idx) for idx in row["coset_representative_basis_indices"]
            ],
            "generator_delta_masks": [],
            "grade_flip_pair_rows": [],
            "exact_divisor_fiber_indices": set(),
            "sandpile_class_indices": set(),
        }

    for delta, coset_index in sorted(delta_to_coset_index.items()):
        by_coset[coset_index]["generator_delta_masks"].append(delta)

    for pair in kernel_derived["grade_flip_pair_rows"]:
        delta = int(pair["delta_mask"])
        coset_index = delta_to_coset_index[delta]
        by_coset[coset_index]["grade_flip_pair_rows"].append(pair)
        by_coset[coset_index]["exact_divisor_fiber_indices"].add(int(pair["fiber_index"]))
        by_coset[coset_index]["sandpile_class_indices"].add(int(pair["class_index"]))

    coset_rows = []
    for coset_index in sorted(by_coset):
        item = by_coset[coset_index]
        deltas = sorted(int(delta) for delta in item["generator_delta_masks"])
        pair_rows = sorted(
            item["grade_flip_pair_rows"],
            key=lambda row: (
                int(row["fiber_index"]),
                int(row["pair_index"]),
                int(row["delta_mask"]),
            ),
        )
        fiber_indices = sorted(int(idx) for idx in item["exact_divisor_fiber_indices"])
        class_indices = sorted(int(idx) for idx in item["sandpile_class_indices"])
        fiber_rows = [fiber_rows_by_index[idx] for idx in fiber_indices]

        pair_order_histogram = Counter(
            int(fiber_rows_by_index[int(row["fiber_index"])]["sandpile_class_order"])
            for row in pair_rows
        )
        fiber_order_histogram = Counter(
            int(row["sandpile_class_order"])
            for row in fiber_rows
        )
        fiber_size_histogram = Counter(int(row["mask_count"]) for row in fiber_rows)
        grade_split_histogram = Counter(
            grade_split_key(int(row["plus_count"]), int(row["minus_count"]))
            for row in fiber_rows
        )
        pair_orientation_histogram = Counter(
            grade_pair_key(int(row["grade_a"]), int(row["grade_b"]))
            for row in pair_rows
        )

        coset_rows.append(
            {
                "coset_index": coset_index,
                "representative_coordinate_mask": item["representative_coordinate_mask"],
                "representative_basis_indices": item["representative_basis_indices"],
                "in_five_cover_span": item["representative_coordinate_mask"] == 0,
                "generator_delta_count": len(deltas),
                "generator_delta_masks": deltas,
                "generator_delta_weight_histogram": histogram(
                    Counter(delta.bit_count() for delta in deltas)
                ),
                "cover_move_deltas": sorted(set(deltas) & set(COVER_DELTAS)),
                "single_bit_defect_deltas": sorted(set(deltas) & set(SINGLE_BIT_DEFECT_DELTAS)),
                "grade_flip_pair_count": len(pair_rows),
                "exact_divisor_fiber_count": len(fiber_indices),
                "exact_divisor_fiber_indices": fiber_indices,
                "sandpile_class_count": len(class_indices),
                "sandpile_class_indices": class_indices,
                "pair_sandpile_class_order_histogram": histogram(pair_order_histogram),
                "fiber_sandpile_class_order_histogram": histogram(fiber_order_histogram),
                "exact_divisor_fiber_size_histogram": histogram(fiber_size_histogram),
                "mixed_fiber_grade_split_histogram": histogram(grade_split_histogram),
                "pair_grade_orientation_histogram": histogram(pair_orientation_histogram),
            }
        )

    generator_delta_count_histogram = Counter(
        int(row["generator_delta_count"]) for row in coset_rows
    )
    grade_flip_pair_count_histogram = Counter(
        int(row["grade_flip_pair_count"]) for row in coset_rows
    )
    exact_divisor_fiber_count_histogram = Counter(
        int(row["exact_divisor_fiber_count"]) for row in coset_rows
    )
    sandpile_class_count_histogram = Counter(
        int(row["sandpile_class_count"]) for row in coset_rows
    )
    total_pair_order_histogram = Counter()
    for row in coset_rows:
        total_pair_order_histogram.update(
            {int(key): int(value) for key, value in row["pair_sandpile_class_order_histogram"].items()}
        )

    cover_span_row = next(row for row in coset_rows if row["in_five_cover_span"])
    max_pair_row = max(coset_rows, key=lambda row: int(row["grade_flip_pair_count"]))
    min_pair_row = min(coset_rows, key=lambda row: int(row["grade_flip_pair_count"]))

    all_generator_deltas = sorted(
        delta for row in coset_rows for delta in row["generator_delta_masks"]
    )
    all_pair_count = sum(int(row["grade_flip_pair_count"]) for row in coset_rows)
    all_fiber_indices = sorted(
        {fiber for row in coset_rows for fiber in row["exact_divisor_fiber_indices"]}
    )
    all_class_indices = sorted(
        {class_idx for row in coset_rows for class_idx in row["sandpile_class_indices"]}
    )

    checks = {
        "presentation_source_is_certified": presentation.get("status")
        == "D20_TUBE_SANDPILE_FLIP_MOVE_PRESENTATION_CERTIFIED"
        and presentation.get("all_checks_pass") is True,
        "kernel_flip_source_is_certified": kernel.get("status")
        == "D20_TUBE_SANDPILE_KERNEL_FLIPS_CERTIFIED"
        and kernel.get("all_checks_pass") is True,
        "coset_count_is_64": len(coset_rows) == 64,
        "coset_indices_are_complete": [row["coset_index"] for row in coset_rows] == list(range(64)),
        "generator_delta_mass_is_392": len(all_generator_deltas) == 392,
        "generator_delta_partition_is_exact": all_generator_deltas
        == sorted(int(row["delta_mask"]) for row in pres_derived["generator_rows"]),
        "grade_flip_pair_mass_is_1285": all_pair_count == 1285,
        "exact_divisor_fiber_union_is_154": len(all_fiber_indices) == 154,
        "sandpile_class_union_is_154": len(all_class_indices) == 154,
        "coset_fiber_and_class_counts_match": all(
            int(row["exact_divisor_fiber_count"]) == int(row["sandpile_class_count"])
            for row in coset_rows
        ),
        "all_generators_are_screen0_odd": all(
            ((delta & SCREEN0_DEFECT_MASK).bit_count() & 1) == 1
            for delta in all_generator_deltas
        ),
        "cover_span_coset_index_is_0": cover_span_row["coset_index"] == 0,
        "cover_span_contains_all_five_cover_moves": cover_span_row["cover_move_deltas"] == sorted(COVER_DELTAS),
        "cover_span_generator_count_is_9": cover_span_row["generator_delta_count"] == 9,
        "cover_span_pair_count_is_271": cover_span_row["grade_flip_pair_count"] == 271,
        "cover_span_hits_all_154_mixed_fibers": cover_span_row["exact_divisor_fiber_count"] == 154,
        "noncover_cosets_contain_no_cover_moves": all(
            row["cover_move_deltas"] == []
            for row in coset_rows
            if not row["in_five_cover_span"]
        ),
        "max_pair_coset_is_cover_span": max_pair_row["coset_index"] == cover_span_row["coset_index"],
        "min_pair_count_is_1": min_pair_row["grade_flip_pair_count"] == 1,
        "generator_count_histogram_matches": histogram(generator_delta_count_histogram)
        == {
            "1": 1,
            "2": 6,
            "3": 3,
            "4": 8,
            "5": 7,
            "6": 13,
            "7": 7,
            "8": 6,
            "9": 8,
            "10": 2,
            "11": 1,
            "12": 1,
            "13": 1,
        },
        "grade_flip_pair_count_histogram_matches": histogram(grade_flip_pair_count_histogram)
        == {
            "1": 1,
            "2": 1,
            "4": 5,
            "5": 2,
            "6": 2,
            "7": 2,
            "8": 6,
            "9": 3,
            "10": 5,
            "11": 3,
            "12": 3,
            "13": 1,
            "14": 1,
            "15": 5,
            "16": 3,
            "17": 2,
            "18": 3,
            "20": 2,
            "21": 3,
            "22": 1,
            "24": 1,
            "27": 1,
            "29": 1,
            "40": 1,
            "43": 1,
            "49": 1,
            "57": 1,
            "63": 1,
            "66": 1,
            "271": 1,
        },
        "exact_divisor_fiber_count_histogram_matches": histogram(exact_divisor_fiber_count_histogram)
        == {
            "1": 24,
            "2": 15,
            "3": 5,
            "4": 7,
            "6": 3,
            "8": 1,
            "10": 1,
            "12": 2,
            "14": 1,
            "18": 1,
            "22": 1,
            "27": 1,
            "32": 1,
            "154": 1,
        },
        "sandpile_class_count_histogram_matches": histogram(sandpile_class_count_histogram)
        == {
            "1": 24,
            "2": 15,
            "3": 5,
            "4": 7,
            "6": 3,
            "8": 1,
            "10": 1,
            "12": 2,
            "14": 1,
            "18": 1,
            "22": 1,
            "27": 1,
            "32": 1,
            "154": 1,
        },
        "pair_sandpile_order_histogram_matches": histogram(total_pair_order_histogram)
        == {"2": 2, "6": 7, "10": 1, "15": 31, "30": 1244},
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_FLIP_COSET_CLASSIFIER_CERTIFIED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_FLIP_COSET_CLASSIFIER_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_flip_coset_classifier",
        "status": status,
        "object": "d20",
        "claim": (
            "The quotient of the 392 exact-divisor grade-flip moves by the five-cover "
            "span has 64 observable cosets. The cover-span coset is the unique coset "
            "containing the five cover moves and it touches all 154 mixed exact-divisor "
            "fibers; the remaining cosets split the residual tube/sandpile observables."
        ),
        "definition": {
            "cover_span_coset": (
                "The coset represented by coordinate zero modulo the rank-5 span of the "
                "five deterministic cover moves."
            ),
            "observable_profile": (
                "For each coset, the profile records generator deltas, grade-flip pair mass, "
                "exact-divisor fibers, sandpile classes, class orders, fiber sizes, and grade "
                "split data."
            ),
        },
        "inputs": {
            "tube_sandpile_flip_move_presentation_report": {
                "path": rel(PRESENTATION_REPORT),
                "sha256": sha_file(PRESENTATION_REPORT),
            },
            "tube_sandpile_kernel_flips_report": {
                "path": rel(KERNEL_FLIPS_REPORT),
                "sha256": sha_file(KERNEL_FLIPS_REPORT),
            },
        },
        "derived": {
            "residue_rank": RESIDUE_RANK,
            "cover_rank": 5,
            "cover_delta_masks": COVER_DELTAS,
            "quotient_dimension": 6,
            "coset_count": len(coset_rows),
            "generator_delta_mass": len(all_generator_deltas),
            "grade_flip_pair_mass": all_pair_count,
            "exact_divisor_fiber_union_count": len(all_fiber_indices),
            "sandpile_class_union_count": len(all_class_indices),
            "cover_span_coset_summary": {
                key: cover_span_row[key]
                for key in [
                    "coset_index",
                    "generator_delta_count",
                    "generator_delta_masks",
                    "grade_flip_pair_count",
                    "exact_divisor_fiber_count",
                    "sandpile_class_count",
                    "cover_move_deltas",
                    "single_bit_defect_deltas",
                ]
            },
            "max_pair_coset_index": max_pair_row["coset_index"],
            "min_pair_coset_index": min_pair_row["coset_index"],
            "generator_delta_count_histogram": histogram(generator_delta_count_histogram),
            "grade_flip_pair_count_histogram": histogram(grade_flip_pair_count_histogram),
            "exact_divisor_fiber_count_histogram": histogram(exact_divisor_fiber_count_histogram),
            "sandpile_class_count_histogram": histogram(sandpile_class_count_histogram),
            "pair_sandpile_class_order_histogram": histogram(total_pair_order_histogram),
            "coset_rows_sha256": sha_json(coset_rows),
            "coset_rows": coset_rows,
        },
        "interpretation": {
            "what_is_certified": (
                "The 64 quotient cosets are classified by finite observables already "
                "present in the tube-to-sandpile comparison."
            ),
            "what_this_does_not_prove": (
                "This classifies the quotient cosets by measured finite observables; it does "
                "not identify a smaller canonical quotient or prove that the 64 profiles are "
                "minimal invariants."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Compress the 64 observable profiles by automorphism or sandpile-order symmetry "
            "and test whether the compressed classes are canonical."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_flip_coset_classifier_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "load the certified flip-move presentation and exact-divisor flip census",
            "quotient every flip generator by the five-cover span",
            "partition all 1285 grade-flip pairs into 64 cosets",
            "aggregate exact-divisor fiber and sandpile-class observables per coset",
            "verify the cover-span coset contains the five cover moves and hits all mixed fibers",
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
