from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import csv
import hashlib
import json
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

try:
    from scipy.optimize import nnls
except ModuleNotFoundError:

    def nnls(A: np.ndarray, b: np.ndarray, maxiter: int = 1000):
        """Projected-gradient fallback for exploratory NNLS when scipy is absent."""
        A = np.asarray(A, dtype=np.float64)
        b = np.asarray(b, dtype=np.float64)
        x = np.zeros(A.shape[1], dtype=np.float64)
        ata = A.T @ A
        atb = A.T @ b
        step = 1.0 / (np.linalg.norm(ata, ord=2) + 1.0)
        for _ in range(int(maxiter)):
            grad = 2.0 * (ata @ x - atb)
            x = np.maximum(0.0, x - step * grad)
        residual = A @ x - b
        return x, float(np.dot(residual, residual))


try:
    from .derive_d20_golay_shell_three_level_terwilliger_profile_reps import (
        PROFILE_CSV,
    )
    from .paths import GENERATED
except ImportError:  # Supports direct script execution.
    from derive_d20_golay_shell_three_level_terwilliger_profile_reps import (
        PROFILE_CSV,
    )
    from paths import GENERATED


PROBE_ID = "d20_golay_shell_three_level_pairwise_square_cone_probe"
REPORT_SCHEMA = f"{PROBE_ID}.report@1"

# Weight enumerator shell sizes for the extended binary Golay code W24.
W24_SHELL_COUNTS = {12: 2576, 16: 759}


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
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows: list[dict[str, Any]] = []
        for row in csv.DictReader(f):
            rows.append(
                {
                    "shell": int(row["shell"]),
                    "profile_id": int(row["profile_id"]),
                    "first_size": int(row["first_size"]),
                    "second_size": int(row["second_size"]),
                    "rest_size": int(row["rest_size"]),
                    "first_representative_id": int(row["first_representative_id"]),
                    "first_representative_mask": int(row["first_representative_mask"]),
                    "second_representative_mask": int(row["second_representative_mask"]),
                    "representative_fiber_count": int(row["representative_fiber_count"]),
                    "profile_sha256": row["profile_sha256"],
                    "profile": row["profile"],
                }
            )
        return rows


def monomials_deg(degree: int) -> list[tuple[int, int, int]]:
    """All monomials a^i b^j c^k with i+j+k = degree."""
    return [
        (i, j, degree - i - j)
        for i in range(degree + 1)
        for j in range(degree + 1 - i)
    ]


@lru_cache(None)
def pairwise_square_matrix(
    shell: int,
) -> tuple[list[tuple[int, int, int]], np.ndarray, list[tuple[str, int, int, int]]]:
    """
    Build the coefficient matrix for pairwise-square cone generators.

    Each column is one monomial coefficient vector of
    (a-b)^2 a^i b^j c^k, (a-c)^2 a^i b^j c^k, or
    (b-c)^2 a^i b^j c^k with i+j+k=shell-2.
    """
    mono = monomials_deg(shell)
    idx = {m: i for i, m in enumerate(mono)}

    cols: list[np.ndarray] = []
    meta: list[tuple[str, int, int, int]] = []

    for name, pair in [("ab", (0, 1)), ("ac", (0, 2)), ("bc", (1, 2))]:
        for m in monomials_deg(shell - 2):
            col = np.zeros(len(mono), dtype=np.float64)
            p, q = pair

            e = list(m)
            e[p] += 2
            col[idx[tuple(e)]] += 1.0

            e = list(m)
            e[p] += 1
            e[q] += 1
            col[idx[tuple(e)]] += -2.0

            e = list(m)
            e[q] += 2
            col[idx[tuple(e)]] += 1.0

            cols.append(col)
            meta.append((name, m[0], m[1], m[2]))

    return mono, np.stack(cols, axis=1), meta


def gap_vector_from_row(
    row: dict[str, Any],
    mono: list[tuple[int, int, int]],
    idx: dict[tuple[int, int, int], int],
) -> np.ndarray:
    """
    Coefficient vector of the homogeneous gap polynomial

      A_w(1) (n1 a^2+n2 b^2+n3 c^2)^(w/2)
      - 24^(w/2) A_profile(a,b,c).

    The 24^(w/2) factor clears the denominator from the normalized shell
    average. Numerical cone membership here is exploratory evidence, not a
    certificate-grade rational proof.
    """
    shell = int(row["shell"])
    degree = shell // 2
    shell_count = W24_SHELL_COUNTS[shell]
    n1 = int(row["first_size"])
    n2 = int(row["second_size"])
    n3 = int(row["rest_size"])

    gap = np.zeros(len(mono), dtype=np.float64)
    fact = math.factorial
    fd = fact(degree)

    for p in range(degree + 1):
        for q in range(degree + 1 - p):
            r = degree - p - q
            coeff = (
                shell_count
                * fd
                // (fact(p) * fact(q) * fact(r))
                * (n1**p)
                * (n2**q)
                * (n3**r)
            )
            gap[idx[(2 * p, 2 * q, 2 * r)]] += coeff

    profile = np.fromstring(str(row["profile"]), sep=",", dtype=np.int64).reshape(
        (shell + 1, shell + 1)
    )
    if int(profile.sum()) != shell_count:
        raise ValueError(f"profile row shell count mismatch for shell {shell}")

    scale = 24**degree
    nz = np.argwhere(profile)
    for j, k in nz:
        j = int(j)
        k = int(k)
        count = int(profile[j, k])
        gap[idx[(j, k, shell - j - k)]] -= scale * count

    return gap


def solve_one(
    row: dict[str, Any],
    maxiter: int,
    tol: float,
    save_coefficients: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    shell = int(row["shell"])
    mono, matrix, meta = pairwise_square_matrix(shell)
    idx = {m: i for i, m in enumerate(mono)}
    gap = gap_vector_from_row(row, mono, idx)

    scale = max(1.0, float(np.max(np.abs(gap))))
    scaled_gap = gap / scale

    x, resnorm = nnls(matrix, scaled_gap, maxiter=maxiter)
    residual_vec = matrix @ x - scaled_gap
    linf = float(np.max(np.abs(residual_vec)))
    l2 = float(np.linalg.norm(residual_vec))
    nz = int(np.sum(x > tol))

    result = {
        "shell": shell,
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
                coeff_rows.append(
                    {
                        "shell": shell,
                        "profile_id": int(row["profile_id"]),
                        "column": col,
                        "pair": pair,
                        "monomial_a": i,
                        "monomial_b": j,
                        "monomial_c": k,
                        "scaled_coefficient": float(val),
                    }
                )

    return result, coeff_rows


def parse_profile_ids(value: str | None) -> set[int] | None:
    if not value:
        return None
    if value.strip().lower() == "all":
        return None
    return {int(x) for x in value.split(",") if x.strip()}


def default_output(shell: int) -> Path:
    return GENERATED / f"{PROBE_ID}_shell{shell}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Exploratory pairwise-square cone probe for the W24 three-level "
            "Terwilliger shell profiles."
        )
    )
    parser.add_argument(
        "csv",
        nargs="?",
        default=str(PROFILE_CSV),
        help="three_level_terwilliger_profiles.csv; defaults to the canonical profile table",
    )
    parser.add_argument("--shell", type=int, required=True, choices=sorted(W24_SHELL_COUNTS))
    parser.add_argument("--start", type=int, default=None, help="start row after shell/profile sorting")
    parser.add_argument("--stop", type=int, default=None, help="stop row after shell/profile sorting")
    parser.add_argument("--profile-ids", default=None, help="comma-separated profile ids, or all")
    parser.add_argument("--out", default=None)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--maxiter", type=int, default=2000)
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--save-coefficients", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    csv_path = Path(args.csv)
    out = Path(args.out) if args.out else default_output(args.shell)
    out.mkdir(parents=True, exist_ok=True)

    rows = read_csv_records(csv_path)
    selected = [row for row in rows if row["shell"] == args.shell]
    selected.sort(key=lambda row: row["profile_id"])

    ids = parse_profile_ids(args.profile_ids)
    if ids is not None:
        selected = [row for row in selected if row["profile_id"] in ids]

    if args.start is not None or args.stop is not None:
        start = args.start or 0
        stop = args.stop if args.stop is not None else len(selected)
        selected = selected[start:stop]
    else:
        start = 0
        stop = len(selected)

    records = list(selected)
    if not records:
        raise SystemExit("no rows selected")

    _, _, meta = pairwise_square_matrix(args.shell)
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
        for row in records:
            result, coeff_rows = solve_one(row, args.maxiter, args.tol, args.save_coefficients)
            results.append(result)
            coeffs.extend(coeff_rows)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = [
                executor.submit(solve_one, row, args.maxiter, args.tol, args.save_coefficients)
                for row in records
            ]
            for future in as_completed(futures):
                result, coeff_rows = future.result()
                results.append(result)
                coeffs.extend(coeff_rows)
        results.sort(key=lambda row: row["profile_id"])
        coeffs.sort(key=lambda row: (row["profile_id"], row["column"]))

    write_csv(out / "pairwise_square_results.csv", results)
    if args.save_coefficients:
        write_csv(out / "pairwise_square_coefficients.csv", coeffs)

    failures = [row for row in results if row["status"] != "PASS_NUMERICAL"]
    report = {
        "schema": REPORT_SCHEMA,
        "probe_id": PROBE_ID,
        "status": "PASS_NUMERICAL" if not failures else "FAIL_NUMERICAL",
        "certificate_grade": False,
        "input_csv": str(csv_path),
        "input_csv_sha256": sha256_file(csv_path),
        "shell": args.shell,
        "shell_word_count": W24_SHELL_COUNTS[args.shell],
        "selected_rows": len(records),
        "start": start,
        "stop": stop,
        "profile_ids_filter": args.profile_ids,
        "workers": args.workers,
        "maxiter": args.maxiter,
        "tol": args.tol,
        "save_coefficients": args.save_coefficients,
        "result_csv": "pairwise_square_results.csv",
        "basis_csv": "pairwise_square_basis_columns.csv",
        "failures": len(failures),
        "worst_linf_residual": max(row["nnls_linf_residual"] for row in results),
        "worst_l2_residual": max(row["nnls_l2_residual"] for row in results),
        "max_nonzero_coefficients": max(row["nnls_nonzero_coefficients"] for row in results),
        "median_nonzero_coefficients": float(
            np.median([row["nnls_nonzero_coefficients"] for row in results])
        ),
        "note": (
            "This is an exploratory NNLS support-pattern probe. Passing output is "
            "not a rational SOS certificate; failing output is negative numerical "
            "evidence for this particular cone ansatz."
        ),
    }
    write_json(out / "pairwise_square_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
