#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def subset_dp(block_dims: np.ndarray) -> dict[tuple[int, int], int]:
    states: dict[tuple[int, int], int] = {(0, 0): 0}
    for i, d in enumerate(block_dims.astype(int).tolist()):
        w = d * d
        current = list(states.items())
        for (c, s), mask in current:
            key = (c + 1, s + w)
            if key not in states:
                states[key] = mask | (1 << i)
    return states


def derive_obstruction(
    generated_center_npz: Path,
    simple_branching_npz: Path,
    out_json: Path | None = None,
) -> dict[str, Any]:
    gen = np.load(generated_center_npz)
    block_dims = np.asarray(gen["block_dimensions"], dtype=np.int64)
    regular_traces = np.asarray(gen["regular_trace_values"], dtype=np.int64)
    if not np.array_equal(block_dims * block_dims, regular_traces):
        raise RuntimeError("generated center trace/dimension mismatch")

    br = np.load(simple_branching_npz)
    dims236 = np.asarray(br["dims236"], dtype=np.int64)
    target_dim = int(np.sum(dims236 * dims236))
    target_center_dim = int(dims236.size)

    states = subset_dp(block_dims)
    exact_center_projection_exists = (target_center_dim, target_dim) in states
    counts_with_dim236 = sorted(int(c) for (c, s) in states if s == target_dim)

    # Check whether the A236 simple dimension multiset is literally a submultiset of A985 dimensions.
    from collections import Counter

    c985 = Counter(block_dims.astype(int).tolist())
    c236 = Counter(dims236.astype(int).tolist())
    a236_dims_submultiset_of_a985 = all(c985[k] >= v for k, v in c236.items())

    # Ordinary semisimple quotients of A985 are central projections: they preserve a subset of
    # the 39 primitive blocks.  A236 would need 34 kept primitive blocks and total dimension 236.
    result = {
        "schema": "d20.constructor.a236_center_obstruction@1",
        "constructor_status": "A236_NOT_ORDINARY_CENTER_PROJECTION_PASS"
        if (not exact_center_projection_exists and not a236_dims_submultiset_of_a985)
        else "A236_CENTER_PROJECTION_BOUNDARY",
        "statement": (
            "The A236 layer cannot be obtained as an ordinary semisimple central projection/quotient "
            "of generated A985.  Any ordinary semisimple quotient of A985 keeps a subset of the 39 "
            "primitive central blocks; no subset of 34 generated A985 blocks has squared-dimension sum 236."
        ),
        "generated_A985": {
            "primitive_block_count": int(block_dims.size),
            "dimension_sum_squares": int(np.sum(block_dims * block_dims)),
            "block_dimensions_sorted": sorted(int(x) for x in block_dims),
            "block_dimension_histogram": {str(int(k)): int(v) for k, v in zip(*np.unique(block_dims, return_counts=True))},
            "block_dimensions_sha256": sha_array(block_dims),
        },
        "target_A236_semisimple_presentation": {
            "simple_count": target_center_dim,
            "dimension_sum_squares": target_dim,
            "simple_dimensions_sorted": sorted(int(x) for x in dims236),
            "simple_dimension_histogram": {str(int(k)): int(v) for k, v in zip(*np.unique(dims236, return_counts=True))},
            "dims236_sha256": sha_array(dims236),
        },
        "central_projection_search": {
            "ordinary_center_projection_with_34_blocks_and_dimension_236_exists": bool(exact_center_projection_exists),
            "subset_counts_achieving_dimension_236_any_center_dimension": counts_with_dim236,
            "count_34_in_dimension_236_counts": bool(34 in counts_with_dim236),
            "a236_simple_dims_are_submultiset_of_a985_block_dims": bool(a236_dims_submultiset_of_a985),
        },
        "conclusion": (
            "The remaining A236 branching seed is not hiding inside the generated A985 center as an "
            "ordinary central subset.  It is extra representation/fusion functor data between the terminal "
            "Pin/CY layers and the full generated algebra."
        ),
        "remaining_boundary_refined": [
            "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data",
            "derive B236->A42 and B236->A12 as restrictions of that generated A236 functor",
            "derive fixed coorient generator permutations from a smaller typed coorient formula",
        ],
    }
    result["all_checks_pass"] = bool(result["constructor_status"] == "A236_NOT_ORDINARY_CENTER_PROJECTION_PASS")
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})

    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated-center", default="generated/center_idempotents_from_generated_T985.npz")
    ap.add_argument("--simple-branching", default="data/raw/simple_branching_matrices.npz")
    ap.add_argument("--out-json", default="generated/a236_center_obstruction_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    res = derive_obstruction(ROOT / args.generated_center, ROOT / args.simple_branching, ROOT / args.out_json)
    print(json.dumps(res, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
