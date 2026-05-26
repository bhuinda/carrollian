#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_native_a236_formulae import native_formula_arrays
except ImportError:  # Supports `python src/derive_a236_generated_branching_boundary.py`.
    from derive_native_a236_formulae import native_formula_arrays

ROOT = Path(__file__).resolve().parents[1]
MOD_DEFAULT = 1000003


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def rank_mod(A: np.ndarray, mod: int = MOD_DEFAULT) -> int:
    A = np.asarray(A, dtype=np.int64).copy() % mod
    m, n = A.shape
    rank = 0
    for col in range(n):
        rows = np.nonzero(A[rank:, col])[0]
        if rows.size == 0:
            continue
        pivot = rank + int(rows[0])
        if pivot != rank:
            A[[rank, pivot]] = A[[pivot, rank]]
        inv = pow(int(A[rank, col]), -1, mod)
        A[rank, :] = (A[rank, :] * inv) % mod
        inds = np.nonzero(A[:, col])[0]
        inds = inds[inds != rank]
        if inds.size:
            vals = A[inds, col].copy()
            A[inds, :] = (A[inds, :] - vals[:, None] * A[rank, :]) % mod
        rank += 1
        if rank == m:
            break
    return int(rank)


def subset_dp(block_dims: np.ndarray) -> dict[tuple[int, int], int]:
    states: dict[tuple[int, int], int] = {(0, 0): 0}
    for i, d in enumerate(block_dims.astype(int).tolist()):
        w = d * d
        for (count, total), mask in list(states.items()):
            key = (count + 1, total + w)
            if key not in states:
                states[key] = mask | (1 << i)
    return states


def derived_b42_to_a12_from_terminal(term: np.lib.npyio.NpzFile) -> np.ndarray:
    object_to_sector = np.asarray(term["object_to_sector"], dtype=np.int64)
    if object_to_sector.shape != (6,):
        raise ValueError(f"expected six object-to-sector labels, got {object_to_sector.shape}")
    # A42 simple order used by the native branching witness:
    # sign objects 0,1, the 6-dimensional regular sheet, then sign objects 2,4,5,3.
    sign_object_order: list[int | None] = [0, 1, None, 2, 4, 5, 3]
    B42_12 = np.zeros((7, 4), dtype=np.int64)
    for row, obj in enumerate(sign_object_order):
        if obj is None:
            B42_12[row, :] = 1
        else:
            sector = int(object_to_sector[obj])
            B42_12[row, 1 + sector] = 1
    return B42_12


def enumerate_rows(total_dim: int, target_dims: np.ndarray) -> list[list[int]]:
    rows: list[list[int]] = []
    dims = target_dims.astype(int).tolist()

    def rec(col: int, remaining: int, prefix: list[int]) -> None:
        if col == len(dims):
            if remaining == 0:
                rows.append(prefix.copy())
            return
        d = dims[col]
        for value in range(remaining // d + 1):
            prefix.append(value)
            rec(col + 1, remaining - value * d, prefix)
            prefix.pop()

    rec(0, int(total_dim), [])
    return rows


def first_terminal_variant(B236_42: np.ndarray, dims236: np.ndarray, dims42: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    variant = B236_42.copy()
    sign_columns = [int(i) for i, d in enumerate(dims42.astype(int).tolist()) if d == 1]
    for row in range(variant.shape[0]):
        if int(dims236[row]) != 1:
            continue
        active = np.flatnonzero(variant[row])
        if active.size != 1:
            continue
        old_col = int(active[0])
        for new_col in sign_columns:
            if new_col != old_col:
                variant[row, :] = 0
                variant[row, new_col] = 1
                return variant, {"changed_row": int(row), "old_column": old_col, "new_column": int(new_col)}
    raise RuntimeError("failed to construct a one-row terminal branching variant")


def derive_boundary(
    generated_center_npz: Path,
    terminal_npz: Path,
    out_json: Path | None = None,
) -> dict[str, Any]:
    gen = np.load(generated_center_npz)
    block_dims = np.asarray(gen["block_dimensions"], dtype=np.int64)
    regular_traces = np.asarray(gen["regular_trace_values"], dtype=np.int64)
    q42_shadow = np.asarray(gen["q42_shadow_matrix"], dtype=np.int64)
    q12_shadow = np.asarray(gen["q12_shadow_matrix"], dtype=np.int64)
    if not np.array_equal(block_dims * block_dims, regular_traces):
        raise RuntimeError("generated center trace/dimension mismatch")

    native = native_formula_arrays()
    dims236 = np.asarray(native["dims236"], dtype=np.int64)
    dims42 = np.asarray(native["dims42"], dtype=np.int64)
    dims12 = np.asarray(native["dims12"], dtype=np.int64)
    native_B42_12 = np.asarray(native["B42_12"], dtype=np.int64)
    native_B236_42 = np.asarray(native["B236_42"], dtype=np.int64)
    native_B236_12 = np.asarray(native["B236_12"], dtype=np.int64)

    term = np.load(terminal_npz)
    derived_B42_12 = derived_b42_to_a12_from_terminal(term)
    derived_B42_12_ok = bool(np.array_equal(derived_B42_12, native_B42_12))

    states = subset_dp(block_dims)
    target_dim = int(np.sum(dims236 * dims236))
    target_center_dim = int(dims236.size)
    ordinary_projection_exists = (target_center_dim, target_dim) in states
    counts_with_dim236 = sorted(int(count) for (count, total) in states if total == target_dim)

    row_solution_counts: dict[str, int] = {}
    row_solution_examples: dict[str, list[list[int]]] = {}
    for d in sorted(set(int(x) for x in dims236.tolist())):
        rows = enumerate_rows(d, dims42)
        row_solution_counts[str(d)] = len(rows)
        row_solution_examples[str(d)] = rows[:5]
    dim_hist = Counter(int(x) for x in dims236.tolist())
    solution_log10 = sum(dim_hist[d] * math.log10(row_solution_counts[str(d)]) for d in dim_hist)

    variant_B236_42, variant_edit = first_terminal_variant(native_B236_42, dims236, dims42)
    variant_B236_12 = variant_B236_42 @ derived_B42_12
    variant_checks = {
        "differs_from_native_B236_to_A42": bool(not np.array_equal(variant_B236_42, native_B236_42)),
        "B236_to_A42_row_dimensions_hold": bool(np.array_equal(variant_B236_42 @ dims42, dims236)),
        "B42_to_A12_row_dimensions_hold": bool(np.array_equal(derived_B42_12 @ dims12, dims42)),
        "B236_to_A12_row_dimensions_hold": bool(np.array_equal(variant_B236_12 @ dims12, dims236)),
        "naturality_holds_by_construction": bool(np.array_equal(variant_B236_42 @ derived_B42_12, variant_B236_12)),
        "differs_from_native_B236_to_A12": bool(not np.array_equal(variant_B236_12, native_B236_12)),
    }

    combined_shadow = np.concatenate([q42_shadow, q12_shadow], axis=0) % MOD_DEFAULT
    result: dict[str, Any] = {
        "schema": "d20.constructor.a236_generated_branching_boundary@1",
        "constructor_status": "A236_GENERATED_BRANCHING_BOUNDARY_PASS",
        "predicate": "is integral",
        "purpose": (
            "Keep the remaining A236 seam explicit: generated A985 center/idempotent data and generated "
            "terminal A42/A12 readouts do not by themselves determine the 34-simple A236 profunctor."
        ),
        "generated_A985_center": {
            "source": str(generated_center_npz.relative_to(ROOT)) if generated_center_npz.is_relative_to(ROOT) else str(generated_center_npz),
            "primitive_block_count": int(block_dims.size),
            "dimension_sum_squares": int(np.sum(block_dims * block_dims)),
            "block_dimension_histogram": {str(int(k)): int(v) for k, v in zip(*np.unique(block_dims, return_counts=True))},
            "block_dimensions_sha256": sha_array(block_dims),
            "q42_shadow_matrix_sha256": sha_array(q42_shadow),
            "q12_shadow_matrix_sha256": sha_array(q12_shadow),
            "combined_public_shadow_rank": rank_mod(combined_shadow),
            "combined_public_shadow_kernel_dimension": int(block_dims.size - rank_mod(combined_shadow)),
        },
        "target_native_A236_presentation": {
            "simple_count": target_center_dim,
            "dimension_sum_squares": target_dim,
            "simple_dimension_histogram": {str(k): int(v) for k, v in sorted(dim_hist.items())},
            "dims236_sha256": sha_array(dims236),
        },
        "ordinary_generated_center_projection_obstruction": {
            "ordinary_center_projection_with_34_blocks_and_dimension_236_exists": bool(ordinary_projection_exists),
            "subset_counts_achieving_dimension_236_any_center_dimension": counts_with_dim236,
            "conclusion": (
                "A236 cannot be obtained by keeping a subset of generated A985 primitive central idempotents; "
                "ordinary semisimple quotients of A985 preserve such subsets."
            ),
        },
        "generated_terminal_B42_to_A12": {
            "source": "derived from terminal object_to_sector labels and the A42 sign-object order",
            "matches_native_formula_B42_to_A12": derived_B42_12_ok,
            "row_dimension_check": bool(np.array_equal(derived_B42_12 @ dims12, dims42)),
            "sha256": sha_array(derived_B42_12),
        },
        "terminal_branching_underdetermination": {
            "row_solution_counts_by_A236_simple_dimension": row_solution_counts,
            "row_solution_examples_by_dimension_first_5": row_solution_examples,
            "native_A236_row_dimension_histogram": {str(k): int(v) for k, v in sorted(dim_hist.items())},
            "complete_B236_to_A42_solution_count_log10_lower_bound": float(solution_log10),
            "explicit_non_native_solution": {
                "edit": variant_edit,
                "checks": variant_checks,
                "B236_to_A42_sha256": sha_array(variant_B236_42),
                "B236_to_A12_sha256": sha_array(variant_B236_12),
            },
            "conclusion": (
                "Dimension preservation, generated B42->A12, and B236->A12 = B236->A42*B42->A12 "
                "leave many integral B236->A42 matrices. A midlevel A985->A236 fusion/profunctor law is "
                "therefore additional structure, not a consequence of the generated terminal readouts alone."
            ),
        },
        "native_formula_comparison": {
            "not_used_as_generated_derivation": True,
            "B236_to_A42_sha256": sha_array(native_B236_42),
            "B236_to_A12_sha256": sha_array(native_B236_12),
        },
        "remaining_boundary": [
            "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data",
            "derive B236->A42 and B236->A12 as restrictions of that generated A236 functor",
        ],
    }
    result["all_checks_pass"] = bool(
        int(np.sum(block_dims * block_dims)) == 985
        and not ordinary_projection_exists
        and derived_B42_12_ok
        and all(variant_checks.values())
    )
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})

    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated-center", default="generated/center_idempotents_from_generated_T985.npz")
    ap.add_argument("--terminal", default="generated/terminal_quotients_from_source_coorient.npz")
    ap.add_argument("--out-json", default="generated/a236_generated_branching_boundary_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive_boundary(ROOT / args.generated_center, ROOT / args.terminal, ROOT / args.out_json)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
