#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .solve_half_braiding import NREL, build_pair_terms, h_array, load_blocks
except ImportError:  # Supports `python src/derive_half_braiding_prime_sweep.py`.
    from certify_io import ROOT, h_file, h_json
    from solve_half_braiding import NREL, build_pair_terms, h_array, load_blocks


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    r = int(math.isqrt(n))
    f = 5
    while f <= r:
        if n % f == 0 or n % (f + 2) == 0:
            return False
        f += 6
    return True


def first_primes(count: int) -> list[int]:
    out: list[int] = []
    n = 2
    while len(out) < count:
        if is_prime(n):
            out.append(n)
        n += 1 if n == 2 else 2
    return out


def parse_primes(raw: str | None, count: int) -> list[int]:
    extras = [1009, 3253, 65537, 999983, 1000003, 1000033, 1000037]
    if raw:
        vals = [int(x.strip()) for x in raw.split(",") if x.strip()]
    else:
        vals = first_primes(count) + extras
    seen: set[int] = set()
    primes: list[int] = []
    for p in vals:
        if p in seen:
            continue
        if not is_prime(p):
            raise ValueError(f"not prime: {p}")
        seen.add(p)
        primes.append(p)
    return primes


def collect_integer_rows() -> tuple[list[dict[int, int]], int, list[int]]:
    """Build the full half-braiding system over Z.

    Rows are the integer coefficient rows behind
    z_src(alpha)*alpha = alpha*z_tgt(alpha).  Mod-p filtering is delayed so a
    sweep can report if rows vanish modulo an exceptional prime.
    """
    bi, bj, loops, unknowns, col_of = load_blocks()
    _, pair_terms = build_pair_terms()
    rows: list[dict[int, int]] = []
    for alpha in range(NREL):
        i = int(bi[alpha])
        j = int(bj[alpha])
        eqs: dict[int, dict[int, int]] = defaultdict(dict)
        for a in loops[i].tolist():
            col = col_of[(i, int(a))]
            for gamma, v in pair_terms.get((int(a), alpha), []):
                d = eqs[int(gamma)]
                d[col] = d.get(col, 0) + int(v)
        for b in loops[j].tolist():
            col = col_of[(j, int(b))]
            for gamma, v in pair_terms.get((alpha, int(b)), []):
                d = eqs[int(gamma)]
                d[col] = d.get(col, 0) - int(v)
        for row in eqs.values():
            clean = {int(c): int(v) for c, v in row.items() if int(v)}
            if clean:
                rows.append(clean)
    loop_counts = [int(len(x)) for x in loops]
    return rows, len(unknowns), loop_counts


def row_mod(row: dict[int, int], p: int) -> dict[int, int]:
    return {c: v % p for c, v in row.items() if v % p}


def sparse_rank_profile_mod(
    rows: Iterable[dict[int, int]], nvars: int, p: int, *, keep_rows: bool = False
) -> dict[str, Any]:
    pivots: dict[int, dict[int, int]] = {}
    selected_row_indices: list[int] = []
    raw_rows = 0
    reduction_events = 0
    coefficient_updates = 0
    max_live_width = 0
    for idx, raw in enumerate(rows):
        row = row_mod(raw, p)
        if not row:
            continue
        raw_rows += 1
        while row:
            max_live_width = max(max_live_width, len(row))
            pc = min(row)
            coeff = row[pc] % p
            if coeff == 0:
                del row[pc]
                continue
            if pc in pivots:
                prow = pivots[pc]
                reduction_events += 1
                coefficient_updates += len(prow)
                factor = coeff
                for c, v in prow.items():
                    nv = (row.get(c, 0) - factor * v) % p
                    if nv:
                        row[c] = nv
                    elif c in row:
                        del row[c]
            else:
                inv = pow(coeff, -1, p)
                row = {c: (v * inv) % p for c, v in row.items() if (v * inv) % p}
                pivots[pc] = row
                if keep_rows:
                    selected_row_indices.append(idx)
                break
    pivot_cols = sorted(pivots)
    pivot_set = set(pivot_cols)
    free_cols = [c for c in range(nvars) if c not in pivot_set]
    pivot_items = [(pc, tuple(sorted(pivots[pc].items()))) for pc in pivot_cols]
    result: dict[str, Any] = {
        "prime": int(p),
        "raw_rows_seen": int(raw_rows),
        "rank": int(len(pivot_cols)),
        "nullity": int(nvars - len(pivot_cols)),
        "pivot_count": int(len(pivot_cols)),
        "free_count": int(len(free_cols)),
        "pivot_columns_sha256": h_array(np.asarray(pivot_cols, dtype=np.int64)),
        "free_columns_sha256": h_array(np.asarray(free_cols, dtype=np.int64)),
        "reducer_sha256": hashlib.sha256(repr(pivot_items).encode("utf-8")).hexdigest(),
        "work_proxy": {
            "reduction_events": int(reduction_events),
            "coefficient_updates": int(coefficient_updates),
            "max_live_row_width": int(max_live_width),
        },
    }
    if keep_rows:
        result["selected_row_indices"] = selected_row_indices
        result["pivot_columns"] = pivot_cols
    return result


def bareiss_det(mat: list[list[int]]) -> int:
    n = len(mat)
    if n == 0:
        return 1
    a = [row[:] for row in mat]
    sign = 1
    prev = 1
    for k in range(n - 1):
        pivot = None
        for i in range(k, n):
            if a[i][k] != 0:
                pivot = i
                break
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign *= -1
        akk = a[k][k]
        for i in range(k + 1, n):
            aik = a[i][k]
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * akk - aik * a[k][j]) // prev
        prev = akk
        for i in range(k + 1, n):
            a[i][k] = 0
    return sign * a[n - 1][n - 1]


def det_mod_square(mat: list[list[int]], p: int) -> int:
    n = len(mat)
    if n == 0:
        return 1
    a = np.asarray(mat, dtype=np.int64) % p
    det = 1
    for c in range(n):
        pivot = None
        for i in range(c, n):
            if int(a[i, c]) % p:
                pivot = i
                break
        if pivot is None:
            return 0
        if pivot != c:
            a[[c, pivot]] = a[[pivot, c]]
            det = (-det) % p
        pivot_val = int(a[c, c]) % p
        det = (det * pivot_val) % p
        inv = pow(pivot_val, -1, p)
        for i in range(c + 1, n):
            factor = (int(a[i, c]) * inv) % p
            if factor:
                a[i, c:] = (a[i, c:] - factor * a[c, c:]) % p
    return int(det % p)


def int_sha256(n: int) -> str:
    sign = b"+" if n >= 0 else b"-"
    mag = abs(n)
    data = mag.to_bytes(max(1, (mag.bit_length() + 7) // 8), "big")
    return hashlib.sha256(sign + data).hexdigest()


def minor_witness(
    rows: list[dict[int, int]],
    profile: dict[str, Any],
    primes: list[int],
    factor_bound: int,
    *,
    exact_determinant: bool,
) -> dict[str, Any]:
    row_ids = [int(x) for x in profile["selected_row_indices"]]
    col_ids = [int(x) for x in profile["pivot_columns"]]
    n = len(col_ids)
    dense = [[int(rows[ri].get(c, 0)) for c in col_ids] for ri in row_ids]
    det: int | None = None
    small_factors: dict[str, int] | None = None
    det_sign: int | None = None
    det_bits: int | None = None
    det_hash: str | None = None
    if exact_determinant:
        det = bareiss_det(dense)
        absdet = abs(det)
        small_factors = {}
        tmp = absdet
        for p in first_primes(max(1, factor_bound)):
            if p > factor_bound:
                break
            exp = 0
            while tmp and tmp % p == 0:
                tmp //= p
                exp += 1
            if exp:
                small_factors[str(p)] = exp
        det_sign = 0 if det == 0 else (1 if det > 0 else -1)
        det_bits = int(absdet.bit_length())
        det_hash = int_sha256(det)
    residues = {str(p): det_mod_square(dense, p) for p in primes}
    certified_good = [p for p in primes if residues[str(p)] != 0]
    selected_rows = np.asarray(row_ids, dtype=np.int64)
    selected_cols = np.asarray(col_ids, dtype=np.int64)
    return {
        "rank_minor_size": int(n),
        "source_prime": int(profile["prime"]),
        "selected_row_indices_sha256": h_array(selected_rows),
        "selected_pivot_columns_sha256": h_array(selected_cols),
        "exact_determinant_computed": bool(exact_determinant),
        "determinant_sign": det_sign,
        "determinant_bit_length": det_bits,
        "determinant_sha256": det_hash,
        "small_prime_factor_scan_bound": int(factor_bound) if exact_determinant else None,
        "small_prime_valuations": small_factors,
        "tested_prime_determinant_residues": residues,
        "tested_primes_certified_by_this_minor": certified_good,
        "claim": "Any prime with nonzero determinant residue for this selected minor has half-braiding rank at least the recorded minor size for this integer matrix.",
    }


def layer_recorded_summary() -> dict[str, Any] | None:
    path = ROOT / "layers/core/a985.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    block = data.get("blocks", {}).get("half_braiding_prime_stability")
    if not isinstance(block, dict):
        return None
    return {
        "path": "layers/core/a985.json",
        "sha256": h_file(path),
        "field_primes": block.get("field_primes"),
        "stable": block.get("stable"),
        "status": block.get("status"),
    }


def build_report(primes: list[int], factor_bound: int, *, exact_determinant: bool) -> dict[str, Any]:
    started = time.perf_counter()
    rows, nvars, loop_counts = collect_integer_rows()
    row_build_elapsed_ms = (time.perf_counter() - started) * 1000.0
    records = []
    profiles: list[dict[str, Any]] = []
    for p in primes:
        t0 = time.perf_counter()
        rec = sparse_rank_profile_mod(rows, nvars, p, keep_rows=True)
        rec["elapsed_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
        records.append({k: v for k, v in rec.items() if k not in {"selected_row_indices", "pivot_columns"}})
        profiles.append(rec)
    ranks = sorted({int(r["rank"]) for r in records})
    nullities = sorted({int(r["nullity"]) for r in records})
    row_counts = sorted({int(r["raw_rows_seen"]) for r in records})
    max_rank = ranks[-1]
    max_rank_profiles: list[dict[str, Any]] = []
    seen_profile_hashes: set[str] = set()
    for profile in profiles:
        if int(profile["rank"]) != max_rank:
            continue
        key = str(profile["pivot_columns_sha256"])
        if key in seen_profile_hashes:
            continue
        seen_profile_hashes.add(key)
        max_rank_profiles.append(profile)
    minor_witnesses = [
        minor_witness(rows, profile, primes, factor_bound, exact_determinant=exact_determinant)
        for profile in max_rank_profiles
    ]
    combined_minor_certified_primes = sorted({
        int(p)
        for witness in minor_witnesses
        for p in witness["tested_primes_certified_by_this_minor"]
    })
    stable_records = [
        r for r in records
        if int(r["rank"]) == max_rank and int(r["nullity"]) == nvars - max_rank
    ]
    rank_drop_records = [r for r in records if int(r["rank"]) < max_rank]
    report = {
        "schema": "gnatural.c985.half_braiding_prime_sweep@1",
        "status": "HALF_BRAIDING_PRIME_SWEEP_COMPLETE",
        "scope": "Evidence sweep for the integer half-braiding linear system. This is a modular stability and rank-minor certificate, not a prime-number distribution theorem and not a complete Smith normal form.",
        "input": {
            "relations": int(NREL),
            "integer_rows": int(len(rows)),
            "unknown_count": int(nvars),
            "unknown_count_by_object": loop_counts,
            "row_build_elapsed_ms": round(row_build_elapsed_ms, 3),
        },
        "prime_sweep": {
            "primes": primes,
            "records": records,
            "rank_values_seen": ranks,
            "nullity_values_seen": nullities,
            "raw_rows_seen_values": row_counts,
            "all_tested_primes_stable": len(ranks) == 1 and len(nullities) == 1 and len(row_counts) == 1,
            "stable_record_count": len(stable_records),
            "rank_drop_primes": [int(r["prime"]) for r in rank_drop_records],
            "max_rank": int(max_rank),
        },
        "rank_minor_witness": minor_witnesses[0] if minor_witnesses else None,
        "rank_minor_witnesses": minor_witnesses,
        "rank_minor_witness_summary": {
            "distinct_max_rank_profiles": len(minor_witnesses),
            "tested_primes_certified_by_some_max_rank_minor": combined_minor_certified_primes,
            "tested_primes_not_certified_by_these_max_rank_minors": [
                int(p) for p in primes if int(p) not in set(combined_minor_certified_primes)
            ],
        },
        "recorded_core_claim": layer_recorded_summary(),
        "coherence": {
            "interprets_prime_as_finite_field_characteristic": True,
            "predicts_prime_counting_distribution": False,
            "bad_prime_status": "tested-prime minor certificate only; complete bad-prime set requires Smith normal form or full determinantal divisor factorization",
            "thermodynamic_cost_proxy": "elapsed_ms plus sparse reduction event/update counts per prime; no physical energy calibration is claimed",
        },
    }
    report["half_braiding_prime_sweep_sha256"] = h_json(report)
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/derived/half_braiding_prime_sweep.json")
    ap.add_argument("--prime-count", type=int, default=50)
    ap.add_argument("--primes")
    ap.add_argument("--factor-bound", type=int, default=5000)
    ap.add_argument("--exact-determinant", action="store_true")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    primes = parse_primes(args.primes, args.prime_count)
    report = build_report(primes, args.factor_bound, exact_determinant=args.exact_determinant)
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2 if args.pretty else None, sort_keys=True)
        f.write("\n")
    sweep = report["prime_sweep"]
    print("HALF_BRAIDING_PRIME_SWEEP", report["status"])
    print("primes =", len(sweep["primes"]))
    print("rank_values_seen =", sweep["rank_values_seen"])
    print("nullity_values_seen =", sweep["nullity_values_seen"])
    print("all_tested_primes_stable =", sweep["all_tested_primes_stable"])
    print("minor_exact_det =", report["rank_minor_witness"]["exact_determinant_computed"])
    print("sha256 =", report["half_braiding_prime_sweep_sha256"])
    print("written =", out)


if __name__ == "__main__":
    main()
