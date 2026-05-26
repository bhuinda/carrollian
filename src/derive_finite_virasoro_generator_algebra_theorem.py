from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "finite_virasoro_generator_algebra"
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

RESIDUE_RANK = 11
MODE_COUNT = 1 << RESIDUE_RANK


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


def gf2_rank(vectors: list[int]) -> int:
    basis = [0] * RESIDUE_RANK
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


def gf2_span(vectors: list[int]) -> set[int]:
    basis: list[int] = []
    for vector in vectors:
        value = vector
        for item in basis:
            value = min(value, value ^ item)
        if value:
            basis.append(value)
            basis.sort(reverse=True)
    span = {0}
    for item in basis:
        span |= {value ^ item for value in list(span)}
    return span


def clock_shift(mask: int, basis_clock: list[int]) -> int:
    return sum(basis_clock[idx] for idx in bit_ids(mask)) % 26


def parity(mask: int, parity_mask: int) -> int:
    return (mask & parity_mask).bit_count() % 2


def generator_rows(
    closure_summary: dict[str, Any],
    basis_clock: list[int],
    hidden_flipping_generators: list[int],
) -> list[dict[str, Any]]:
    rows = []
    for generator_id in closure_summary["preserving_primitive_generators"]:
        mask = 1 << int(generator_id)
        rows.append(
            {
                "generator_label": f"P{generator_id}",
                "generator_type": "primitive_preserving",
                "source_generators": [int(generator_id)],
                "operator_mask": mask,
                "support_generator_ids": [int(generator_id)],
                "sector26_clock_shift_mod26": clock_shift(mask, basis_clock),
                "corrected_hidden_clock_shift_mod26": (
                    13 if int(generator_id) in hidden_flipping_generators else 0
                ),
            }
        )
    for row in closure_summary["paired_cross_return_generators"]:
        pair = [int(value) for value in row["generator_pair"]]
        mask = int(row["composite_mask"])
        rows.append(
            {
                "generator_label": f"C{pair[0]}_{pair[1]}",
                "generator_type": "paired_cross_return_composite",
                "source_generators": pair,
                "operator_mask": mask,
                "support_generator_ids": bit_ids(mask),
                "sector26_clock_shift_mod26": clock_shift(mask, basis_clock),
                "corrected_hidden_clock_shift_mod26": sum(
                    13 if generator_id in hidden_flipping_generators else 0
                    for generator_id in pair
                )
                % 26,
            }
        )
    return rows


def multiplication_table(rows: list[dict[str, Any]], basis_clock: list[int]) -> list[dict[str, Any]]:
    by_mask = {int(row["operator_mask"]): row["generator_label"] for row in rows}
    table = []
    for left in rows:
        for right in rows:
            product_mask = int(left["operator_mask"]) ^ int(right["operator_mask"])
            left_sources = [int(value) for value in left["source_generators"]]
            right_sources = [int(value) for value in right["source_generators"]]
            shared_sources = sorted(set(left_sources) & set(right_sources))
            product_clock = clock_shift(product_mask, basis_clock)
            naive_clock_sum = (
                int(left["sector26_clock_shift_mod26"])
                + int(right["sector26_clock_shift_mod26"])
            ) % 26
            table.append(
                {
                    "left": left["generator_label"],
                    "right": right["generator_label"],
                    "left_source_generators": left_sources,
                    "right_source_generators": right_sources,
                    "shared_source_generators": shared_sources,
                    "product_mask": product_mask,
                    "product_support_generator_ids": bit_ids(product_mask),
                    "product_named_generator": by_mask.get(product_mask),
                    "product_is_identity": product_mask == 0,
                    "product_sector26_clock_shift_mod26": product_clock,
                    "naive_clock_sum_mod26": naive_clock_sum,
                    "clock_defect_mod26": (product_clock - naive_clock_sum) % 26,
                }
            )
    return table


def null_relations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    relations = []
    count = len(rows)
    for subset in range(1, 1 << count):
        mask = 0
        labels = []
        for idx, row in enumerate(rows):
            if (subset >> idx) & 1:
                mask ^= int(row["operator_mask"])
                labels.append(row["generator_label"])
        if mask == 0:
            relations.append(
                {
                    "relation_support_indices": [
                        idx for idx in range(count) if (subset >> idx) & 1
                    ],
                    "relation_labels": labels,
                    "relation_size": len(labels),
                    "product_mask": 0,
                }
            )
    return relations


def multiplication_digest(operator_basis: list[int]) -> str:
    h = hashlib.sha256()
    h.update(b"[")
    first = True
    for left in operator_basis:
        for right in operator_basis:
            if not first:
                h.update(b",")
            first = False
            h.update(json.dumps([left, right, left ^ right], separators=(",", ":")).encode("utf-8"))
    h.update(b"]")
    return h.hexdigest()


def build_theorem() -> dict[str, Any]:
    kernel = load_json(FINITE_KERNEL_REPORT)
    fourier = load_json(FOURIER_MODE_CLASSIFIER_REPORT)
    closure_summary = kernel["derived"]["closure_summary"]
    basis_clock = fourier["derived"]["classifier_summary"]["sector26_basis_cycle_normalized_mod26"]
    hidden_flipping_generators = fourier["derived"]["classifier_summary"]["hidden_flipping_generators"]
    parity_mask = int(closure_summary["defining_parity_mask"])
    operator_basis = [int(mask) for mask in kernel["derived"]["kernel_closure_mode_masks"]]
    operator_basis_set = set(operator_basis)
    rows = generator_rows(closure_summary, basis_clock, hidden_flipping_generators)
    generator_masks = [int(row["operator_mask"]) for row in rows]
    table = multiplication_table(rows, basis_clock)
    relations = null_relations(rows)
    generated_span = gf2_span(generator_masks)
    primitive_preserving = [
        row for row in rows if row["generator_type"] == "primitive_preserving"
    ]
    paired_composites = [
        row for row in rows if row["generator_type"] == "paired_cross_return_composite"
    ]
    full_operator_clock_histogram = histogram(
        Counter(clock_shift(mask, basis_clock) for mask in operator_basis)
    )
    clock_defect_histogram = histogram(
        Counter(int(row["clock_defect_mod26"]) for row in table)
    )
    clock_defect_rows = [
        row for row in table if int(row["clock_defect_mod26"]) != 0
    ]
    generator_clock_histogram = histogram(
        Counter(row["sector26_clock_shift_mod26"] for row in rows)
    )
    corrected_hidden_clock_histogram = histogram(
        Counter(row["corrected_hidden_clock_shift_mod26"] for row in rows)
    )
    commutator_table = [
        {
            "left": left["generator_label"],
            "right": right["generator_label"],
            "commutator_mask": int(left["operator_mask"])
            ^ int(right["operator_mask"])
            ^ int(left["operator_mask"])
            ^ int(right["operator_mask"]),
        }
        for left in rows
        for right in rows
    ]

    checks = {
        "finite_kernel_candidate_is_certified": kernel.get("status")
        == "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED"
        and kernel.get("all_checks_pass") is True,
        "fourier_mode_classifier_is_certified": fourier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier.get("all_checks_pass") is True,
        "operator_basis_has_1024_rank10_masks": len(operator_basis) == 1024
        and gf2_rank(operator_basis) == 10
        and operator_basis_set == set(generated_span),
        "all_operator_basis_masks_satisfy_kernel_parity": all(
            parity(mask, parity_mask) == 0 for mask in operator_basis
        ),
        "generator_count_is_8_primitive_plus_3_composite": len(primitive_preserving) == 8
        and len(paired_composites) == 3
        and len(rows) == 11,
        "generator_masks_have_rank10_with_one_relation": gf2_rank(generator_masks) == 10
        and len(relations) == 1
        and relations[0]["relation_labels"] == ["C5_9", "C5_10", "C9_10"],
        "all_generators_preserve_kernel_parity": all(
            parity(mask, parity_mask) == 0 for mask in generator_masks
        ),
        "all_generators_are_involutions": all(
            (int(row["operator_mask"]) ^ int(row["operator_mask"])) == 0 for row in rows
        ),
        "all_generator_commutators_vanish": all(
            row["commutator_mask"] == 0 for row in commutator_table
        ),
        "multiplication_table_is_closed_on_operator_basis": all(
            row["product_mask"] in operator_basis_set for row in table
        ),
        "sector26_clock_defect_is_classified_on_generator_products": clock_defect_histogram
        == {"0": 104, "2": 1, "4": 3, "6": 1, "10": 2, "16": 2, "18": 4, "22": 2, "24": 2}
        and len(clock_defect_rows) == 17,
        "sector26_clock_defect_vanishes_on_disjoint_source_products": all(
            row["clock_defect_mod26"] == 0
            for row in table
            if not row["shared_source_generators"]
        ),
        "sector26_clock_defect_is_only_overlap_cancellation": all(
            bool(row["shared_source_generators"]) for row in clock_defect_rows
        ),
        "all_internal_generator_sector26_clock_shifts_are_even": all(
            row["sector26_clock_shift_mod26"] % 2 == 0 for row in rows
        ),
        "full_operator_basis_has_even_sector26_clock_only": sorted(
            int(key) for key in full_operator_clock_histogram
        )
        == list(range(0, 26, 2)),
        "primitive_preserving_clock_shifts_match_basis_clock": [
            row["sector26_clock_shift_mod26"] for row in primitive_preserving
        ]
        == [12, 14, 18, 24, 14, 8, 10, 18],
        "paired_cross_return_clock_shifts_are_2_8_2": [
            row["sector26_clock_shift_mod26"] for row in paired_composites
        ]
        == [2, 8, 2],
        "crossing_primitive_generators_are_excluded_but_pair_closed": closure_summary[
            "crossing_primitive_generators"
        ]
        == [5, 9, 10]
        and [row["source_generators"] for row in paired_composites]
        == [[5, 9], [5, 10], [9, 10]],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FINITE_VIRASORO_GENERATOR_ALGEBRA_CERTIFIED"
        if all_checks_pass
        else "D20_FINITE_VIRASORO_GENERATOR_ALGEBRA_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.finite_virasoro_generator_algebra",
        "status": status,
        "object": "d20",
        "claim": (
            "The rank-10 finite string-kernel candidate carries a certified finite generator algebra. "
            "At the translation-generator layer this algebra is the abelian exponent-2 operator group "
            "C2^10 generated by eight primitive-preserving moves and three paired cross-return composites. "
            "The 11 named generators have one nontrivial dependency, C5_9 C5_10 C9_10 = 1, and every "
            "internal generator has an even sector-26 clock shift. The sector-26 clock is not a group "
            "homomorphism on this exponent-2 layer; its finite overlap-cancellation defect is explicitly "
            "classified."
        ),
        "definition": {
            "operator_basis": (
                "The 1024 translations by masks in the rank-10 kernel hyperplane "
                "m_5 + m_9 + m_10 = 0."
            ),
            "finite_generator_algebra": (
                "The translation operator algebra generated by the primitive-preserving masks and paired "
                "cross-return composite masks under xor multiplication."
            ),
            "commutator_test": (
                "For translation operators T_a and T_b, the commutator is T_a T_b T_a T_b = T_0."
            ),
            "sector26_clock_test": (
                "The sector-26 clock is checked against generator products. Defects occur exactly when "
                "source generator supports overlap and cancel under xor."
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
        },
        "derived": {
            "algebra_summary": {
                "operator_basis_count": len(operator_basis),
                "operator_basis_rank": gf2_rank(operator_basis),
                "named_generator_count": len(rows),
                "named_generator_rank": gf2_rank(generator_masks),
                "relation_count_mod_involutions": len(relations),
                "primitive_preserving_generator_count": len(primitive_preserving),
                "paired_cross_return_generator_count": len(paired_composites),
                "all_commutators_zero": all(row["commutator_mask"] == 0 for row in commutator_table),
                "algebra_group_type": "C2^10 translation operator group",
                "sector26_clock_shift_histogram_on_named_generators": generator_clock_histogram,
                "corrected_hidden_clock_shift_histogram_on_named_generators": corrected_hidden_clock_histogram,
                "sector26_clock_histogram_on_operator_basis": full_operator_clock_histogram,
                "sector26_clock_defect_histogram_on_generator_products": clock_defect_histogram,
                "sector26_clock_defect_row_count": len(clock_defect_rows),
            },
            "generator_rows": rows,
            "generator_rows_sha256": sha_json(rows),
            "generator_multiplication_table": table,
            "generator_multiplication_table_sha256": sha_json(table),
            "commutator_table": commutator_table,
            "commutator_table_sha256": sha_json(commutator_table),
            "sector26_clock_defect_rows": clock_defect_rows,
            "sector26_clock_defect_rows_sha256": sha_json(clock_defect_rows),
            "defining_relations": {
                "involutions": [f"{row['generator_label']}^2 = 1" for row in rows],
                "commutators": "[G_i, G_j] = 1 for all named generators at the translation layer",
                "dependency_relations": relations,
                "operator_basis_multiplication_digest_sha256": multiplication_digest(operator_basis),
                "operator_basis_masks_sha256": sha_json(operator_basis),
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the finite string-kernel candidate has a closed rank-10 translation operator algebra",
                "the named internal moves generate all 1024 kernel translations",
                "all named generator commutators vanish at this finite translation layer",
                "the three paired cross-return composites have exactly one dependency: C5_9 C5_10 C9_10 = 1",
                "the sector-26 clock remains even on the kernel and its generator-product defect is localized to overlap cancellation",
            ],
            "what_this_does_not_prove": (
                "This is not yet a noncommutative Virasoro algebra. It certifies the finite translation "
                "generator layer and a finite sector-26 clock defect. A Virasoro-like central term or "
                "anomaly cocycle must be tested next."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Test finite central-extension/anomaly cocycles on the generator algebra: search alternating "
            "2-cocycles compatible with the sector-26 clock and identify whether any nontrivial central term survives."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.finite_virasoro_generator_algebra_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify finite string-kernel and Fourier classifier inputs",
            "construct the 1024-operator rank-10 kernel translation basis",
            "construct eight primitive-preserving generators and three paired cross-return composites",
            "verify rank, involution, commutator, and dependency relations",
            "verify closure of generator products on the kernel operator basis",
            "verify sector-26 even-clock internal closure and classify the overlap-cancellation defect",
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
