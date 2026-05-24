#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_json
    from .derive_half_braiding_prime_sweep import collect_integer_rows
except ImportError:  # Supports `python src/derive_half_braiding_local_snf.py`.
    from certify_io import ROOT, h_json
    from derive_half_braiding_prime_sweep import collect_integer_rows


def p_powers(p: int, precision: int) -> list[int]:
    out = [1]
    for _ in range(precision):
        out.append(out[-1] * p)
    return out


def dense_mod_matrix(rows: list[dict[int, int]], nvars: int, modulus: int) -> np.ndarray:
    mat = np.zeros((len(rows), nvars), dtype=np.int64)
    for i, row in enumerate(rows):
        for c, v in row.items():
            mat[i, c] = int(v) % modulus
    return mat


def find_min_valuation_pivot(
    mat: np.ndarray, row0: int, col0: int, p: int, powers: list[int]
) -> tuple[int, int, int] | None:
    active = mat[row0:, col0:]
    precision = len(powers) - 1
    for val in range(precision):
        if val == 0:
            mask = (active % p) != 0
        else:
            mask = ((active % powers[val]) == 0) & ((active % powers[val + 1]) != 0)
        loc = np.nonzero(mask)
        if loc[0].size:
            return row0 + int(loc[0][0]), col0 + int(loc[1][0]), val
    return None


def local_snf_valuations(rows: list[dict[int, int]], nvars: int, p: int, precision: int) -> dict[str, Any]:
    powers = p_powers(p, precision)
    modulus = powers[-1]
    mat = dense_mod_matrix(rows, nvars, modulus)
    m, n = mat.shape
    r = 0
    c = 0
    valuations: list[int] = []
    pivot_samples: list[dict[str, Any]] = []
    row_ops = 0
    col_ops = 0
    started = time.perf_counter()
    while r < m and c < n:
        found = find_min_valuation_pivot(mat, r, c, p, powers)
        if found is None:
            break
        pr, pc, val = found
        if pr != r:
            mat[[r, pr], c:] = mat[[pr, r], c:]
        if pc != c:
            mat[:, [c, pc]] = mat[:, [pc, c]]

        pv = powers[val]
        pivot = int(mat[r, c]) % modulus
        if pivot == 0 or pivot % pv != 0 or pivot % powers[val + 1] == 0:
            raise AssertionError("invalid local pivot valuation")
        unit = (pivot // pv) % modulus
        inv_unit = pow(unit, -1, modulus)
        mat[r, c:] = (mat[r, c:] * inv_unit) % modulus
        pivot = int(mat[r, c]) % modulus
        if pivot != pv:
            raise AssertionError("failed to normalize local pivot")

        row_pivot = mat[r, c:].copy()
        below = mat[r + 1 :, c]
        below_mask = below != 0
        if below_mask.any():
            if np.any((below[below_mask] % pv) != 0):
                raise AssertionError("pivot does not divide active column entry in local ring")
            qs = (below[below_mask] // pv) % powers[precision - val]
            mat[r + 1 :, c:][below_mask, :] = (
                mat[r + 1 :, c:][below_mask, :] - qs[:, None] * row_pivot[None, :]
            ) % modulus
            row_ops += int(below_mask.sum())
        mat[r + 1 :, c] = 0

        row_entries = mat[r, c + 1 :]
        row_mask = row_entries != 0
        if row_mask.any():
            if np.any((row_entries[row_mask] % pv) != 0):
                raise AssertionError("pivot does not divide active row entry in local ring")
            qs = (row_entries[row_mask] // pv) % powers[precision - val]
            cols = np.nonzero(row_mask)[0] + c + 1
            pivot_col = mat[r:, c].copy()
            mat[r:, cols] = (mat[r:, cols] - pivot_col[:, None] * qs[None, :]) % modulus
            col_ops += int(row_mask.sum())
        mat[r, c + 1 :] = 0

        valuations.append(int(val))
        if len(pivot_samples) < 24:
            pivot_samples.append(
                {
                    "pivot_index": len(valuations) - 1,
                    "valuation": int(val),
                    "active_row": int(r),
                    "active_col": int(c),
                }
            )
        r += 1
        c += 1

    hist = Counter(valuations)
    unresolved_rows, unresolved_cols = 0, 0
    if r < m and c < n:
        unresolved = mat[r:, c:]
        unresolved_rows = int(np.count_nonzero(np.any(unresolved != 0, axis=1)))
        unresolved_cols = int(np.count_nonzero(np.any(unresolved != 0, axis=0)))

    return {
        "prime": int(p),
        "precision": int(precision),
        "modulus": int(modulus),
        "matrix_shape": [int(m), int(n)],
        "pivots_found_below_precision": int(len(valuations)),
        "valuation_histogram_below_precision": {str(k): int(v) for k, v in sorted(hist.items())},
        "valuation_sequence_prefix": valuations[:80],
        "unresolved_active_rows_mod_p_power": unresolved_rows,
        "unresolved_active_cols_mod_p_power": unresolved_cols,
        "row_operations": int(row_ops),
        "column_operations": int(col_ops),
        "pivot_samples": pivot_samples,
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }


def build_report(p: int, precision: int, expected_rank: int | None) -> dict[str, Any]:
    started = time.perf_counter()
    rows, nvars, loop_counts = collect_integer_rows()
    collect_ms = (time.perf_counter() - started) * 1000.0
    local = local_snf_valuations(rows, nvars, p, precision)
    valuation_count = sum(local["valuation_histogram_below_precision"].values())
    valuation_sum = sum(
        int(k) * int(v) for k, v in local["valuation_histogram_below_precision"].items()
    )
    unresolved_nonzero = None
    rank_drop = None
    complete_to_expected_rank = None
    if expected_rank is not None:
        unresolved_nonzero = max(0, int(expected_rank) - int(valuation_count))
        rank_drop = int(expected_rank) - int(local["valuation_histogram_below_precision"].get("0", 0))
        complete_to_expected_rank = unresolved_nonzero == 0
    report = {
        "schema": "gnatural.c985.half_braiding_local_snf@1",
        "status": "HALF_BRAIDING_LOCAL_SNF_COMPLETE",
        "scope": "p-local Smith normal form valuation computation modulo p^precision for the integer half-braiding matrix. Invariant factors with valuation >= precision remain unresolved at this precision.",
        "input": {
            "integer_rows": len(rows),
            "unknown_count": int(nvars),
            "unknown_count_by_object": loop_counts,
            "collect_elapsed_ms": round(collect_ms, 3),
        },
        "local_snf": local,
        "interpretation": {
            "expected_integer_rank": expected_rank,
            "rank_mod_p_from_valuation_0": int(local["valuation_histogram_below_precision"].get("0", 0)),
            "rank_drop_mod_p_against_expected_rank": rank_drop,
            "nonzero_invariant_factors_seen_below_precision": int(valuation_count),
            "nonzero_invariant_factors_unresolved_at_or_above_precision": unresolved_nonzero,
            "complete_to_expected_rank_at_this_precision": complete_to_expected_rank,
            "p_adic_valuation_of_seen_rank_determinantal_divisor": int(valuation_sum),
            "unresolved_means": "If unresolved active columns are nonzero, raise --precision to continue separating higher p-adic valuations.",
        },
    }
    report["half_braiding_local_snf_sha256"] = h_json(report)
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prime", type=int, default=2)
    ap.add_argument("--precision", type=int, default=8)
    ap.add_argument("--expected-rank", type=int, default=258)
    ap.add_argument("--out", default="generated/derived/half_braiding_local_snf_p2.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    report = build_report(args.prime, args.precision, args.expected_rank)
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2 if args.pretty else None, sort_keys=True)
        f.write("\n")
    local = report["local_snf"]
    print("HALF_BRAIDING_LOCAL_SNF", report["status"])
    print("prime =", local["prime"])
    print("precision =", local["precision"])
    print("pivots =", local["pivots_found_below_precision"])
    print("valuation_histogram =", local["valuation_histogram_below_precision"])
    print("unresolved_cols =", local["unresolved_active_cols_mod_p_power"])
    print("sha256 =", report["half_braiding_local_snf_sha256"])
    print("written =", out)


if __name__ == "__main__":
    main()
