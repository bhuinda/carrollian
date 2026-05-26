from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "finite_central_extension_anomaly_cocycle"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_KERNEL_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_virasoro_string_kernel_candidate"
    / "report.json"
)
FOURIER_MODE_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
)
FINITE_GENERATOR_ALGEBRA_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_virasoro_generator_algebra"
    / "report.json"
)

RESIDUE_RANK = 11
MODULUS = 26


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


def bit_ids(mask: int) -> list[int]:
    return [idx for idx in range(RESIDUE_RANK) if (mask >> idx) & 1]


def clock(mask: int, basis_clock: list[int]) -> int:
    return sum(int(basis_clock[idx]) for idx in bit_ids(mask)) % MODULUS


def clock_defect(left: int, right: int, basis_clock: list[int]) -> int:
    return (clock(left ^ right, basis_clock) - clock(left, basis_clock) - clock(right, basis_clock)) % MODULUS


def gf2_rank(vectors: list[int]) -> int:
    basis: dict[int, int] = {}
    rank = 0
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                rank += 1
                break
            value ^= basis[pivot]
    return rank


def gf2_rref(row_masks: list[int], variable_count: int) -> tuple[list[int], list[int]]:
    rows = [row for row in row_masks if row]
    pivot_cols: list[int] = []
    row_idx = 0
    for col in range(variable_count):
        pivot_idx = next((idx for idx in range(row_idx, len(rows)) if (rows[idx] >> col) & 1), None)
        if pivot_idx is None:
            continue
        rows[row_idx], rows[pivot_idx] = rows[pivot_idx], rows[row_idx]
        for idx in range(len(rows)):
            if idx != row_idx and ((rows[idx] >> col) & 1):
                rows[idx] ^= rows[row_idx]
        pivot_cols.append(col)
        row_idx += 1
        if row_idx == len(rows):
            break
    return rows[:row_idx], pivot_cols


def gf2_nullspace_basis(row_masks: list[int], variable_count: int) -> list[int]:
    pivot_rows, pivot_cols = gf2_rref(row_masks, variable_count)
    pivot_set = set(pivot_cols)
    free_cols = [col for col in range(variable_count) if col not in pivot_set]
    basis = []
    for free_col in free_cols:
        vector = 1 << free_col
        for row, pivot_col in zip(pivot_rows, pivot_cols):
            if (row >> free_col) & 1:
                vector |= 1 << pivot_col
        basis.append(vector)
    return basis


def variable_key(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def build_alternating_f2_search(
    generator_rows: list[dict[str, Any]],
    multiplication_table: list[dict[str, Any]],
    dependency_relation: dict[str, Any],
) -> dict[str, Any]:
    labels = [str(row["generator_label"]) for row in generator_rows]
    label_to_index = {label: idx for idx, label in enumerate(labels)}
    variables = list(combinations(range(len(labels)), 2))
    variable_to_index = {pair: idx for idx, pair in enumerate(variables)}
    defect_by_pair = {
        (str(row["left"]), str(row["right"])): int(row["clock_defect_mod26"])
        for row in multiplication_table
    }
    allowed_pairs = []
    for pair in variables:
        left_label = labels[pair[0]]
        right_label = labels[pair[1]]
        defect = defect_by_pair[(left_label, right_label)]
        if defect != 0:
            allowed_pairs.append(pair)
    allowed_pair_set = set(allowed_pairs)
    constraint_rows: list[int] = []
    for pair in variables:
        if pair not in allowed_pair_set:
            constraint_rows.append(1 << variable_to_index[pair])

    relation_indices = [int(value) for value in dependency_relation["relation_support_indices"]]
    for generator_index in range(len(labels)):
        row_mask = 0
        for relation_index in relation_indices:
            if relation_index == generator_index:
                continue
            pair = variable_key(relation_index, generator_index)
            row_mask ^= 1 << variable_to_index[pair]
        if row_mask:
            constraint_rows.append(row_mask)

    nullspace = gf2_nullspace_basis(constraint_rows, len(variables))
    representative = min((vector for vector in nullspace if vector), default=0)
    representative_pairs = [
        {
            "left": labels[left],
            "right": labels[right],
            "left_index": left,
            "right_index": right,
            "sector26_clock_defect_mod26": defect_by_pair[(labels[left], labels[right])],
            "central_value_mod2": 1,
        }
        for idx, (left, right) in enumerate(variables)
        if (representative >> idx) & 1
    ]
    relation_checks = []
    for generator_index in range(len(labels)):
        total = 0
        support_pairs = []
        for relation_index in relation_indices:
            if relation_index == generator_index:
                continue
            pair = variable_key(relation_index, generator_index)
            variable_index = variable_to_index[pair]
            value = (representative >> variable_index) & 1
            total ^= value
            support_pairs.append(
                {
                    "relation_label": labels[relation_index],
                    "test_label": labels[generator_index],
                    "central_value_mod2": value,
                }
            )
        relation_checks.append(
            {
                "test_label": labels[generator_index],
                "relation_pair_sum_mod2": total,
                "terms": support_pairs,
            }
        )

    return {
        "coefficient_ring": "F2",
        "generator_labels": labels,
        "variable_count": len(variables),
        "variable_labels": [
            {"left": labels[left], "right": labels[right], "variable_index": idx}
            for idx, (left, right) in enumerate(variables)
        ],
        "constraint_count": len(constraint_rows),
        "constraint_rank": gf2_rank(constraint_rows),
        "solution_dimension": len(variables) - gf2_rank(constraint_rows),
        "allowed_nonzero_pairs": [
            {
                "left": labels[left],
                "right": labels[right],
                "left_index": left,
                "right_index": right,
                "sector26_clock_defect_mod26": defect_by_pair[(labels[left], labels[right])],
            }
            for left, right in allowed_pairs
        ],
        "dependency_relation_labels": dependency_relation["relation_labels"],
        "dependency_relation_indices": relation_indices,
        "nullspace_basis_bitmasks": nullspace,
        "representative_bitmask": representative,
        "representative_support_pairs": representative_pairs,
        "representative_relation_descent_checks": relation_checks,
    }


def build_clock_defect_summary(
    operator_basis: list[int],
    basis_clock: list[int],
    generator_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    pair_histogram: Counter[int] = Counter()
    symmetric_failure_count = 0
    alternating_failure_count = 0
    normalized_failure_count = 0
    for left in operator_basis:
        if clock_defect(0, left, basis_clock) != 0 or clock_defect(left, 0, basis_clock) != 0:
            normalized_failure_count += 1
        for right in operator_basis:
            left_right = clock_defect(left, right, basis_clock)
            right_left = clock_defect(right, left, basis_clock)
            pair_histogram[left_right] += 1
            if left_right != right_left:
                symmetric_failure_count += 1
            if (left_right - right_left) % MODULUS != 0:
                alternating_failure_count += 1
    triple_cocycle_failure_count = 0
    named_masks = [int(row["operator_mask"]) for row in generator_rows]
    for left in named_masks:
        for middle in named_masks:
            for right in named_masks:
                lhs = (
                    clock_defect(middle, right, basis_clock)
                    - clock_defect(left ^ middle, right, basis_clock)
                    + clock_defect(left, middle ^ right, basis_clock)
                    - clock_defect(left, middle, basis_clock)
                ) % MODULUS
                if lhs != 0:
                    triple_cocycle_failure_count += 1
    return {
        "coefficient_ring": "Z/26",
        "definition": "D(a,b) = q(a xor b) - q(a) - q(b) mod 26 on the rank-10 operator basis.",
        "operator_pair_count": len(operator_basis) * len(operator_basis),
        "operator_pair_defect_histogram": histogram(pair_histogram),
        "symmetric_failure_count": symmetric_failure_count,
        "alternating_part_nonzero_count": alternating_failure_count,
        "normalized_failure_count": normalized_failure_count,
        "named_generator_triple_count": len(named_masks) ** 3,
        "named_generator_cocycle_failure_count": triple_cocycle_failure_count,
        "canonical_alternating_central_term": "zero",
    }


def build_theorem() -> dict[str, Any]:
    kernel = load_json(FINITE_KERNEL_REPORT)
    fourier = load_json(FOURIER_MODE_CLASSIFIER_REPORT)
    algebra = load_json(FINITE_GENERATOR_ALGEBRA_REPORT)
    operator_basis = [int(mask) for mask in kernel["derived"]["kernel_closure_mode_masks"]]
    basis_clock = [
        int(value)
        for value in fourier["derived"]["classifier_summary"]["sector26_basis_cycle_normalized_mod26"]
    ]
    generator_rows = algebra["derived"]["generator_rows"]
    multiplication_table = algebra["derived"]["generator_multiplication_table"]
    dependency_relations = algebra["derived"]["defining_relations"]["dependency_relations"]
    dependency_relation = dependency_relations[0] if dependency_relations else {}

    clock_summary = build_clock_defect_summary(operator_basis, basis_clock, generator_rows)
    f2_search = build_alternating_f2_search(generator_rows, multiplication_table, dependency_relation)
    composite_triangle_pairs = [
        {"left": "C5_9", "right": "C5_10", "sector26_clock_defect_mod26": 18},
        {"left": "C5_9", "right": "C9_10", "sector26_clock_defect_mod26": 4},
        {"left": "C5_10", "right": "C9_10", "sector26_clock_defect_mod26": 18},
    ]
    representative_pair_labels = [
        (row["left"], row["right"]) for row in f2_search["representative_support_pairs"]
    ]
    expected_triangle_labels = [(row["left"], row["right"]) for row in composite_triangle_pairs]

    checks = {
        "finite_kernel_candidate_is_certified": kernel.get("status")
        == "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED"
        and kernel.get("all_checks_pass") is True,
        "fourier_mode_classifier_is_certified": fourier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier.get("all_checks_pass") is True,
        "finite_generator_algebra_is_certified": algebra.get("status")
        == "D20_FINITE_VIRASORO_GENERATOR_ALGEBRA_CERTIFIED"
        and algebra.get("all_checks_pass") is True,
        "operator_basis_is_rank10_1024_kernel": len(operator_basis) == 1024
        and gf2_rank(operator_basis) == 10,
        "named_generator_relation_is_cross_composite_triangle": dependency_relation.get(
            "relation_labels"
        )
        == ["C5_9", "C5_10", "C9_10"]
        and dependency_relation.get("relation_support_indices") == [8, 9, 10],
        "canonical_z26_clock_defect_histogram_matches_witness": clock_summary[
            "operator_pair_defect_histogram"
        ]
        == {
            "0": 114309,
            "2": 80069,
            "4": 81414,
            "6": 79341,
            "8": 75661,
            "10": 74256,
            "12": 56931,
            "14": 67980,
            "16": 92566,
            "18": 85464,
            "20": 74732,
            "22": 77043,
            "24": 88810,
        },
        "canonical_z26_clock_defect_is_normalized": clock_summary["normalized_failure_count"] == 0,
        "canonical_z26_clock_defect_is_symmetric": clock_summary["symmetric_failure_count"] == 0,
        "canonical_z26_alternating_central_term_vanishes": clock_summary[
            "alternating_part_nonzero_count"
        ]
        == 0,
        "canonical_z26_clock_defect_is_coboundary_2_cocycle_on_named_generators": clock_summary[
            "named_generator_triple_count"
        ]
        == 1331
        and clock_summary["named_generator_cocycle_failure_count"] == 0,
        "f2_alternating_search_has_55_named_pair_variables": f2_search["variable_count"] == 55,
        "f2_compatible_alternating_solution_is_one_dimensional": f2_search[
            "constraint_rank"
        ]
        == 54
        and f2_search["solution_dimension"] == 1,
        "f2_representative_is_supported_on_cross_composite_triangle": representative_pair_labels
        == expected_triangle_labels,
        "f2_representative_descends_through_cross_composite_relation": all(
            row["relation_pair_sum_mod2"] == 0
            for row in f2_search["representative_relation_descent_checks"]
        ),
        "f2_representative_is_nontrivial": f2_search["representative_bitmask"] != 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_CERTIFIED"
        if all_checks_pass
        else "D20_FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.finite_central_extension_anomaly_cocycle",
        "status": status,
        "object": "d20",
        "claim": (
            "The finite Virasoro generator layer has a genuine sector-26 clock defect, but its canonical "
            "Z/26 defect is a symmetric coboundary and therefore contributes no alternating central term. "
            "After reducing to compatible F2 alternating forms on the 11 named generators and imposing the "
            "single cross-composite relation C5_9 C5_10 C9_10 = 1, exactly one nontrivial parity central "
            "cocycle survives, supported on the three paired cross-return composites."
        ),
        "definition": {
            "canonical_clock_defect": (
                "For the sector-26 clock q on the rank-10 operator basis, D(a,b)=q(a xor b)-q(a)-q(b) mod 26."
            ),
            "alternating_central_term_test": (
                "A central anomaly at this layer must have nonzero alternating part D(a,b)-D(b,a)."
            ),
            "compatible_f2_search": (
                "Search alternating F2 forms on unordered named-generator pairs, force zero on pairs with "
                "zero sector-26 clock defect, and require descent through C5_9+C5_10+C9_10=0."
            ),
        },
        "inputs": {
            "finite_virasoro_string_kernel_candidate_report": {
                "path": rel(FINITE_KERNEL_REPORT),
                "sha256": sha_file(FINITE_KERNEL_REPORT),
            },
            "amplitude_quotient_fourier_mode_classifier_report": {
                "path": rel(FOURIER_MODE_CLASSIFIER_REPORT),
                "sha256": sha_file(FOURIER_MODE_CLASSIFIER_REPORT),
            },
            "finite_virasoro_generator_algebra_report": {
                "path": rel(FINITE_GENERATOR_ALGEBRA_REPORT),
                "sha256": sha_file(FINITE_GENERATOR_ALGEBRA_REPORT),
            },
        },
        "derived": {
            "central_extension_summary": {
                "operator_basis_count": len(operator_basis),
                "operator_basis_rank": gf2_rank(operator_basis),
                "named_generator_count": len(generator_rows),
                "canonical_z26_alternating_term": "zero",
                "canonical_z26_clock_defect_is_symmetric_coboundary": True,
                "compatible_f2_cocycle_dimension": f2_search["solution_dimension"],
                "compatible_f2_cocycle_support": "paired_cross_return_composite_triangle",
                "surviving_central_extension_type": "parity F2 central cocycle",
            },
            "canonical_z26_clock_defect": clock_summary,
            "compatible_f2_alternating_search": f2_search,
            "composite_triangle_expected_support": composite_triangle_pairs,
        },
        "interpretation": {
            "what_this_proves": [
                "the sector-26 clock defect does not by itself give a Z/26 Virasoro central term",
                "the canonical Z/26 defect is a symmetric coboundary with zero alternating part",
                "there is exactly one compatible F2 alternating cocycle after imposing the cross-composite relation",
                "the surviving parity anomaly is localized on the C5_9, C5_10, C9_10 composite triangle",
            ],
            "what_this_does_not_prove": (
                "This does not yet construct the corresponding central extension group or prove a projective "
                "representation on the full kernel. It certifies the cocycle test that such a construction "
                "must use."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Construct the F2 central extension group from the surviving composite-triangle cocycle and "
            "certify its commutator table and projective action on the rank-10 kernel."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.finite_central_extension_anomaly_cocycle_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify finite string-kernel, Fourier classifier, and generator algebra inputs",
            "evaluate the canonical Z/26 clock defect on all 1024^2 operator pairs",
            "verify normalization, symmetry, zero alternating part, and named-generator 2-cocycle identity",
            "solve the compatible F2 alternating-form linear system on 55 named-generator pair variables",
            "verify the unique surviving F2 cocycle descends through C5_9 C5_10 C9_10 = 1",
            "verify the survivor is supported exactly on the paired cross-return composite triangle",
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
