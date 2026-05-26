#!/usr/bin/env python3
"""
Chunked pairwise-square cone attack for three-level Golay/Terwilliger profiles.

Input:
  three_level_terwilliger_profiles.csv

Target:
  For each profile, test whether the homogeneous gap polynomial lies numerically in

      Gap(a,b,c)
        =
        (a-b)^2 P_ab(a,b,c)
        +
        (a-c)^2 P_ac(a,b,c)
        +
        (b-c)^2 P_bc(a,b,c),

  with nonnegative monomial coefficients in P_ab, P_ac, P_bc.

This is a floating NNLS certificate generator. It is not the final rational proof,
but it gives the support pattern and residuals needed for rationalization.

Examples:

  # Run all w=16 profiles in chunks
  python chunked_pairwise_square_cone_attack.py three_level_terwilliger_profiles.csv \
    --shell 16 --start 0 --stop 500 --out out_w16_000_500

  python chunked_pairwise_square_cone_attack.py three_level_terwilliger_profiles.csv \
    --shell 16 --start 500 --stop 1000 --out out_w16_500_1000

  # Run all w=12 profiles
  python chunked_pairwise_square_cone_attack.py three_level_terwilliger_profiles.csv \
    --shell 12 --out out_w12_all

  # Use multiple processes
  python chunked_pairwise_square_cone_attack.py three_level_terwilliger_profiles.csv \
    --shell 16 --start 0 --stop 500 --workers 8 --out out_w16_000_500

  # Save nonzero NNLS coefficients for later rationalization
  python chunked_pairwise_square_cone_attack.py three_level_terwilliger_profiles.csv \
    --shell 16 --start 0 --stop 100 --save-coefficients --out out_w16_coeffs
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import nnls


EXPECTED_COUNTS = {12: 2576, 16: 759}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def monomials_deg(d: int) -> list[tuple[int, int, int]]:
    """All monomials a^i b^j c^k of total degree d."""
    return [(i, j, d - i - j) for i in range(d + 1) for j in range(d + 1 - i)]


@lru_cache(None)
def pairwise_square_matrix(w: int) -> tuple[list[tuple[int, int, int]], np.ndarray, list[tuple[str, int, int, int]]]:
    """
    Matrix whose columns are monomial coefficient vectors of

      (a-b)^2 * a^i b^j c^k,
      (a-c)^2 * a^i b^j c^k,
      (b-c)^2 * a^i b^j c^k,

    for all i+j+k=w-2.
    """
    mono = monomials_deg(w)
    idx = {m: i for i, m in enumerate(mono)}

    cols: list[np.ndarray] = []
    meta: list[tuple[str, int, int, int]] = []

    for name, pair in [("ab", (0, 1)), ("ac", (0, 2)), ("bc", (1, 2))]:
        for m in monomials_deg(w - 2):
            col = np.zeros(len(mono), dtype=np.float64)
            p, q = pair

            # x_p^2 term
            e = list(m)
            e[p] += 2
            col[idx[tuple(e)]] += 1.0

            # -2 x_p x_q term
            e = list(m)
            e[p] += 1
            e[q] += 1
            col[idx[tuple(e)]] += -2.0

            # x_q^2 term
            e = list(m)
            e[q] += 2
            col[idx[tuple(e)]] += 1.0

            cols.append(col)
            meta.append((name, m[0], m[1], m[2]))

    return mono, np.stack(cols, axis=1), meta


def gap_vector_from_row(row: dict[str, Any], mono: list[tuple[int, int, int]], idx: dict[tuple[int, int, int], int]) -> np.ndarray:
    """
    Build coefficient vector of

      H(a,b,c)
        =
        A_w(1) (n1 a^2+n2 b^2+n3 c^2)^(w/2)
        -
        24^(w/2) A_profile(a,b,c).

    The 24^(w/2) factor clears the denominator from
    ((n1 a^2+n2 b^2+n3 c^2)/24)^(w/2).
    """
    w = int(row["shell"])
    d = w // 2
    A1 = EXPECTED_COUNTS[w]
    n1 = int(row["first_size"])
    n2 = int(row["second_size"])
    n3 = int(row["rest_size"])

    b = np.zeros(len(mono), dtype=np.float64)
    fact = math.factorial
    fd = fact(d)

    # A_w(1) (n1 a^2+n2 b^2+n3 c^2)^d
    for p in range(d + 1):
        for q in range(d + 1 - p):
            r = d - p - q
            coeff = (
                A1
                * fd
                // (fact(p) * fact(q) * fact(r))
                * (n1 ** p)
                * (n2 ** q)
                * (n3 ** r)
            )
            b[idx[(2 * p, 2 * q, 2 * r)]] += coeff

    # -24^d * profile polynomial
    prof = np.fromstring(str(row["profile"]), sep=",", dtype=np.int64).reshape((w + 1, w + 1))
    scale = 24 ** d
    nz = np.argwhere(prof)
    for j, k in nz:
        j = int(j)
        k = int(k)
        count = int(prof[j, k])
        b[idx[(j, k, w - j - k)]] -= scale * count

    return b


def solve_one(row: dict[str, Any], maxiter: int, tol: float, save_coefficients: bool) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    w = int(row["shell"])
    mono, A, meta = pairwise_square_matrix(w)
    idx = {m: i for i, m in enumerate(mono)}

    b = gap_vector_from_row(row, mono, idx)

    # Scale to improve conditioning. We only certify numerical cone membership here.
    scale = max(1.0, float(np.max(np.abs(b))))
    bs = b / scale

    x, resnorm = nnls(A, bs, maxiter=maxiter)

    residual_vec = A @ x - bs
    linf = float(np.max(np.abs(residual_vec)))
    l2 = float(np.linalg.norm(residual_vec))
    nz = int(np.sum(x > tol))

    result = {
        "shell": w,
        "profile_id": int(row["profile_id"]),
        "first_size": int(row["first_size"]),
        "second_size": int(row["second_size"]),
        "rest_size": int(row["rest_size"]),
        "scale_max_abs_gap_coeff": scale,
        "nnls_linf_residual": linf,
        "nnls_l2_residual": l2,
        "nnls_reported_resnorm": float(resnorm),
        "nnls_nonzero_coefficients": nz,
        "max_scaled_coefficient": float(np.max(x)) if x.size else 0.0,
        "status": "PASS_NUMERICAL" if linf < 1e-8 else "FAIL_NUMERICAL",
    }

    coeff_rows: list[dict[str, Any]] = []
    if save_coefficients:
        for col, val in enumerate(x):
            if val > tol:
                pair, i, j, k = meta[col]
                coeff_rows.append({
                    "shell": w,
                    "profile_id": int(row["profile_id"]),
                    "column": col,
                    "pair": pair,
                    "monomial_a": i,
                    "monomial_b": j,
                    "monomial_c": k,
                    "scaled_coefficient": float(val),
                })

    return result, coeff_rows


def parse_profile_ids(s: str | None) -> set[int] | None:
    if not s:
        return None
    if s.strip().lower() == "all":
        return None
    return {int(x) for x in s.split(",") if x.strip()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="three_level_terwilliger_profiles.csv")
    ap.add_argument("--shell", type=int, required=True, choices=[12, 16])
    ap.add_argument("--start", type=int, default=None, help="start row after shell/profile sorting")
    ap.add_argument("--stop", type=int, default=None, help="stop row after shell/profile sorting")
    ap.add_argument("--profile-ids", default=None, help="comma-separated profile ids, or all")
    ap.add_argument("--out", default=None)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--maxiter", type=int, default=2000)
    ap.add_argument("--tol", type=float, default=1e-10)
    ap.add_argument("--save-coefficients", action="store_true")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out = Path(args.out or f"pairwise_square_shell_{args.shell}")
    out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    sub = df[df.shell == args.shell].sort_values("profile_id").reset_index(drop=True)

    ids = parse_profile_ids(args.profile_ids)
    if ids is not None:
        sub = sub[sub.profile_id.isin(ids)].reset_index(drop=True)

    if args.start is not None or args.stop is not None:
        start = args.start or 0
        stop = args.stop if args.stop is not None else len(sub)
        sub = sub.iloc[start:stop].reset_index(drop=True)
    else:
        start = 0
        stop = len(sub)

    records = sub.to_dict(orient="records")
    if not records:
        raise SystemExit("no rows selected")

    # Save basis metadata once.
    mono, A, meta = pairwise_square_matrix(args.shell)
    basis_rows = [
        {
            "column": col,
            "pair": pair,
            "monomial_a": i,
            "monomial_b": j,
            "monomial_c": k,
        }
        for col, (pair, i, j, k) in enumerate(meta)
    ]
    write_csv(out / "pairwise_square_basis_columns.csv", basis_rows)

    results: list[dict[str, Any]] = []
    coeffs: list[dict[str, Any]] = []

    if args.workers <= 1:
        for n, row in enumerate(records, 1):
            result, coeff_rows = solve_one(row, args.maxiter, args.tol, args.save_coefficients)
            results.append(result)
            coeffs.extend(coeff_rows)
            if n % 250 == 0:
                print(f"processed {n}/{len(records)}")
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = [
                ex.submit(solve_one, row, args.maxiter, args.tol, args.save_coefficients)
                for row in records
            ]
            for n, fut in enumerate(as_completed(futs), 1):
                result, coeff_rows = fut.result()
                results.append(result)
                coeffs.extend(coeff_rows)
                if n % 250 == 0:
                    print(f"processed {n}/{len(records)}")

        results.sort(key=lambda r: r["profile_id"])
        coeffs.sort(key=lambda r: (r["profile_id"], r["column"]))

    write_csv(out / "pairwise_square_results.csv", results)
    if args.save_coefficients:
        write_csv(out / "pairwise_square_coefficients.csv", coeffs)

    failures = [r for r in results if r["status"] != "PASS_NUMERICAL"]
    report = {
        "status": "PASS_NUMERICAL" if not failures else "FAIL_NUMERICAL",
        "input_csv": str(csv_path),
        "input_csv_sha256": sha256_file(csv_path),
        "shell": args.shell,
        "selected_rows": len(records),
        "start": start,
        "stop": stop,
        "profile_ids_filter": args.profile_ids,
        "workers": args.workers,
        "maxiter": args.maxiter,
        "tol": args.tol,
        "save_coefficients": args.save_coefficients,
        "result_csv": "pairwise_square_results.csv",
        "failures": len(failures),
        "worst_linf_residual": max(r["nnls_linf_residual"] for r in results),
        "worst_l2_residual": max(r["nnls_l2_residual"] for r in results),
        "max_nonzero_coefficients": max(r["nnls_nonzero_coefficients"] for r in results),
        "median_nonzero_coefficients": float(np.median([r["nnls_nonzero_coefficients"] for r in results])),
    }
    write_json(out / "pairwise_square_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
