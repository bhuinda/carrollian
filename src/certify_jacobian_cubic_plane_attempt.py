from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "temp" / "jacobian_cubic_plane_attempt"
REPORT = OUT_DIR / "report.json"
P3_KEYS = [(3, 0), (2, 1), (1, 2), (0, 3)]
SYMBOLIC_VARS = ("x", "y", "r", "s", "u", "v")
SYMBOLIC_VAR_INDEX = {name: index for index, name in enumerate(SYMBOLIC_VARS)}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


class QPoly:
    def __init__(self, terms: dict[tuple[int, ...], Fraction] | None = None):
        self.terms = {exp: coeff for exp, coeff in (terms or {}).items() if coeff}

    @staticmethod
    def const(value: int | Fraction) -> "QPoly":
        coeff = Fraction(value)
        return QPoly({(0,) * len(SYMBOLIC_VARS): coeff}) if coeff else QPoly()

    @staticmethod
    def var(name: str) -> "QPoly":
        exp = [0] * len(SYMBOLIC_VARS)
        exp[SYMBOLIC_VAR_INDEX[name]] = 1
        return QPoly({tuple(exp): Fraction(1)})

    def __add__(self, other: Any) -> "QPoly":
        rhs = qpoly(other)
        out = dict(self.terms)
        for exp, coeff in rhs.terms.items():
            out[exp] = out.get(exp, Fraction(0)) + coeff
        return QPoly(out)

    __radd__ = __add__

    def __neg__(self) -> "QPoly":
        return QPoly({exp: -coeff for exp, coeff in self.terms.items()})

    def __sub__(self, other: Any) -> "QPoly":
        return self + (-qpoly(other))

    def __rsub__(self, other: Any) -> "QPoly":
        return qpoly(other) + (-self)

    def __mul__(self, other: Any) -> "QPoly":
        rhs = qpoly(other)
        out: dict[tuple[int, ...], Fraction] = {}
        for left_exp, left_coeff in self.terms.items():
            for right_exp, right_coeff in rhs.terms.items():
                exp = tuple(a + b for a, b in zip(left_exp, right_exp))
                out[exp] = out.get(exp, Fraction(0)) + left_coeff * right_coeff
        return QPoly(out)

    __rmul__ = __mul__

    def __pow__(self, power: int) -> "QPoly":
        out = QPoly.const(1)
        base = self
        n = power
        while n:
            if n & 1:
                out = out * base
            base = base * base
            n >>= 1
        return out

    def derivative(self, name: str) -> "QPoly":
        idx = SYMBOLIC_VAR_INDEX[name]
        out: dict[tuple[int, ...], Fraction] = {}
        for exp, coeff in self.terms.items():
            degree = exp[idx]
            if degree == 0:
                continue
            new_exp = list(exp)
            new_exp[idx] -= 1
            out[tuple(new_exp)] = out.get(tuple(new_exp), Fraction(0)) + coeff * degree
        return QPoly(out)

    def is_zero(self) -> bool:
        return not self.terms

    def rows(self) -> list[dict[str, Any]]:
        return [
            {
                "coeff": [coeff.numerator, coeff.denominator],
                "exp": {name: power for name, power in zip(SYMBOLIC_VARS, exp) if power},
            }
            for exp, coeff in sorted(self.terms.items())
        ]


def qpoly(value: Any) -> QPoly:
    if isinstance(value, QPoly):
        return value
    if isinstance(value, (int, Fraction)):
        return QPoly.const(value)
    raise TypeError(f"cannot coerce {type(value).__name__} to QPoly")


def qcompose(poly: QPoly, sx: QPoly, sy: QPoly) -> QPoly:
    out = QPoly()
    for exp, coeff in poly.terms.items():
        x_power = exp[SYMBOLIC_VAR_INDEX["x"]]
        y_power = exp[SYMBOLIC_VAR_INDEX["y"]]
        rest = list(exp)
        rest[SYMBOLIC_VAR_INDEX["x"]] = 0
        rest[SYMBOLIC_VAR_INDEX["y"]] = 0
        out = out + QPoly({tuple(rest): coeff}) * (sx**x_power) * (sy**y_power)
    return out


def symbolic_cubic_shear_identity() -> dict[str, Any]:
    x = QPoly.var("x")
    y = QPoly.var("y")
    r = QPoly.var("r")
    s = QPoly.var("s")
    u = QPoly.var("u")
    v = QPoly.var("v")
    linear = r * x + s * y
    scalar = u * linear**2 + v * linear**3
    h1 = s * scalar
    h2 = -r * scalar
    f1 = x + h1
    f2 = y + h2
    g1 = x - h1
    g2 = y - h2
    det_minus_one = f1.derivative("x") * f2.derivative("y") - f1.derivative("y") * f2.derivative("x") - 1
    checks = {
        "linear_form_annihilates_vector": qcompose(linear, h1, h2).is_zero(),
        "det_jacobian_is_one": det_minus_one.is_zero(),
        "F_after_I_minus_H_x_is_x": (qcompose(f1, g1, g2) - x).is_zero(),
        "F_after_I_minus_H_y_is_y": (qcompose(f2, g1, g2) - y).is_zero(),
        "I_minus_H_after_F_x_is_x": (qcompose(g1, f1, f2) - x).is_zero(),
        "I_minus_H_after_F_y_is_y": (qcompose(g2, f1, f2) - y).is_zero(),
    }
    return {
        "engine": "exact_polynomial_Q[x,y,r,s,u,v]",
        "family": "H=(s,-r)*(u*(r*x+s*y)^2+v*(r*x+s*y)^3)",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def add_poly(a: dict[tuple[int, int], int], b: dict[tuple[int, int], int], p: int, scale: int = 1) -> dict[tuple[int, int], int]:
    out = dict(a)
    for key, value in b.items():
        new_value = (out.get(key, 0) + scale * value) % p
        if new_value:
            out[key] = new_value
        elif key in out:
            del out[key]
    return out


def mul_poly(a: dict[tuple[int, int], int], b: dict[tuple[int, int], int], p: int) -> dict[tuple[int, int], int]:
    out: dict[tuple[int, int], int] = {}
    for (ax, ay), av in a.items():
        for (bx, by), bv in b.items():
            key = (ax + bx, ay + by)
            out[key] = (out.get(key, 0) + av * bv) % p
    return {key: value for key, value in out.items() if value % p}


def p2_derivatives(h2: tuple[int, int, int, int, int, int], p: int) -> tuple[dict[tuple[int, int], int], ...]:
    a, b, c, d, e, f = h2
    p2x = {(1, 0): 2 * a % p, (0, 1): b % p}
    p2y = {(1, 0): b % p, (0, 1): 2 * c % p}
    q2x = {(1, 0): 2 * d % p, (0, 1): e % p}
    q2y = {(1, 0): e % p, (0, 1): 2 * f % p}
    return tuple({key: value for key, value in poly.items() if value % p} for poly in (p2x, p2y, q2x, q2y))


def p3_derivatives(h3: tuple[int, int, int, int, int, int, int, int], p: int) -> tuple[dict[tuple[int, int], int], ...]:
    a, b, c, d, e, f, g, h = h3
    p3x = {(2, 0): 3 * a % p, (1, 1): 2 * b % p, (0, 2): c % p}
    p3y = {(2, 0): b % p, (1, 1): 2 * c % p, (0, 2): 3 * d % p}
    q3x = {(2, 0): 3 * e % p, (1, 1): 2 * f % p, (0, 2): g % p}
    q3y = {(2, 0): f % p, (1, 1): 2 * g % p, (0, 2): 3 * h % p}
    return tuple({key: value for key, value in poly.items() if value % p} for poly in (p3x, p3y, q3x, q3y))


def determinant_constraints(h2: tuple[int, int, int, int, int, int], h3: tuple[int, ...], p: int) -> dict[tuple[int, int], int]:
    p2x, p2y, q2x, q2y = p2_derivatives(h2, p)
    p3x, p3y, q3x, q3y = p3_derivatives(tuple(h3), p)
    trace_a = add_poly(p2x, q2y, p)
    trace_b = add_poly(p3x, q3y, p)
    det_a = add_poly(mul_poly(p2x, q2y, p), mul_poly(p2y, q2x, p), p, scale=-1)
    mixed = add_poly(mul_poly(p2x, q3y, p), mul_poly(p3x, q2y, p), p)
    mixed = add_poly(mixed, mul_poly(p2y, q3x, p), p, scale=-1)
    mixed = add_poly(mixed, mul_poly(p3y, q2x, p), p, scale=-1)
    det_b = add_poly(mul_poly(p3x, q3y, p), mul_poly(p3y, q3x, p), p, scale=-1)
    out: dict[tuple[int, int], int] = {}
    for part in (trace_a, trace_b, det_a, mixed, det_b):
        out = add_poly(out, part, p)
    return out


def trace_a_is_zero(h2: tuple[int, int, int, int, int, int], p: int) -> bool:
    p2x, _p2y, _q2x, q2y = p2_derivatives(h2, p)
    return not add_poly(p2x, q2y, p)


def linear_rows_for_h3(h2: tuple[int, int, int, int, int, int], p: int) -> tuple[list[list[int]], list[int]]:
    p2x, p2y, q2x, q2y = p2_derivatives(h2, p)
    det_a = add_poly(mul_poly(p2x, q2y, p), mul_poly(p2y, q2x, p), p, scale=-1)
    rows: list[list[int]] = []
    rhs: list[int] = []
    keys = [(2, 0), (1, 1), (0, 2), (3, 0), (2, 1), (1, 2), (0, 3)]
    basis_constraints: list[dict[tuple[int, int], int]] = []
    for index in range(8):
        basis = [0] * 8
        basis[index] = 1
        p3x, p3y, q3x, q3y = p3_derivatives(tuple(basis), p)
        trace_b = add_poly(p3x, q3y, p)
        mixed = add_poly(mul_poly(p2x, q3y, p), mul_poly(p3x, q2y, p), p)
        mixed = add_poly(mixed, mul_poly(p2y, q3x, p), p, scale=-1)
        mixed = add_poly(mixed, mul_poly(p3y, q2x, p), p, scale=-1)
        basis_constraints.append(add_poly(trace_b, mixed, p))

    for key in keys:
        rows.append([basis_constraints[index].get(key, 0) % p for index in range(8)])
        rhs.append((-det_a.get(key, 0)) % p)
    return rows, rhs


def rref_solutions(rows: list[list[int]], rhs: list[int], p: int) -> tuple[list[int], list[list[int]], int] | None:
    matrix = [row[:] + [value % p] for row, value in zip(rows, rhs)]
    row_count = len(matrix)
    col_count = len(rows[0]) if rows else 0
    pivots: list[int] = []
    pivot_row = 0
    for col in range(col_count):
        found = None
        for r in range(pivot_row, row_count):
            if matrix[r][col] % p:
                found = r
                break
        if found is None:
            continue
        matrix[pivot_row], matrix[found] = matrix[found], matrix[pivot_row]
        inv = pow(matrix[pivot_row][col] % p, -1, p)
        matrix[pivot_row] = [(value * inv) % p for value in matrix[pivot_row]]
        for r in range(row_count):
            if r == pivot_row:
                continue
            factor = matrix[r][col] % p
            if factor:
                matrix[r] = [(value - factor * pivot) % p for value, pivot in zip(matrix[r], matrix[pivot_row])]
        pivots.append(col)
        pivot_row += 1
        if pivot_row == row_count:
            break
    for r in range(row_count):
        if all(matrix[r][c] % p == 0 for c in range(col_count)) and matrix[r][-1] % p:
            return None
    free = [col for col in range(col_count) if col not in pivots]
    particular = [0] * col_count
    for row_index, col in enumerate(pivots):
        particular[col] = matrix[row_index][-1] % p
    basis: list[list[int]] = []
    for free_col in free:
        vec = [0] * col_count
        vec[free_col] = 1
        for row_index, pivot_col in enumerate(pivots):
            vec[pivot_col] = (-matrix[row_index][free_col]) % p
        basis.append(vec)
    return particular, basis, len(pivots)


def iter_affine_space(particular: list[int], basis: list[list[int]], p: int):
    if not basis:
        yield tuple(particular)
        return
    for coeffs in itertools.product(range(p), repeat=len(basis)):
        vec = particular[:]
        for coeff, base in zip(coeffs, basis):
            if not coeff:
                continue
            vec = [(value + coeff * delta) % p for value, delta in zip(vec, base)]
        yield tuple(vec)


def det_b_zero(h3: tuple[int, ...], p: int) -> bool:
    p3x, p3y, q3x, q3y = p3_derivatives(tuple(h3), p)
    return not add_poly(mul_poly(p3x, q3y, p), mul_poly(p3y, q3x, p), p, scale=-1)


def eval_map(h2: tuple[int, ...], h3: tuple[int, ...], x: int, y: int, p: int) -> tuple[int, int]:
    a, b, c, d, e, f = h2
    A, B, C, D, E, F, G, H = h3
    x2, xy, y2 = x * x, x * y, y * y
    x3, x2y, xy2, y3 = x2 * x, x2 * y, x * y2, y2 * y
    first = x + a * x2 + b * xy + c * y2 + A * x3 + B * x2y + C * xy2 + D * y3
    second = y + d * x2 + e * xy + f * y2 + E * x3 + F * x2y + G * xy2 + H * y3
    return first % p, second % p


def is_permutation(h2: tuple[int, ...], h3: tuple[int, ...], p: int) -> bool:
    seen = {eval_map(h2, h3, x, y, p) for x in range(p) for y in range(p)}
    return len(seen) == p * p


def projective_lines(p: int) -> list[tuple[int, int]]:
    return [(1, s) for s in range(p)] + [(0, 1)]


def rank_one_shear_coeffs(r: int, s: int, u: int, v: int, p: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    h2 = (
        s * u * r * r,
        2 * u * r * s * s,
        u * s * s * s,
        -u * r * r * r,
        -2 * u * r * r * s,
        -u * r * s * s,
    )
    h3 = (
        s * v * r * r * r,
        3 * v * r * r * s * s,
        3 * v * r * s * s * s,
        v * s * s * s * s,
        -v * r * r * r * r,
        -3 * v * r * r * r * s,
        -3 * v * r * r * s * s,
        -v * r * s * s * s,
    )
    return tuple(value % p for value in h2), tuple(value % p for value in h3)


def rank_one_shear_set(p: int) -> dict[tuple[tuple[int, ...], tuple[int, ...]], dict[str, int]]:
    out: dict[tuple[tuple[int, ...], tuple[int, ...]], dict[str, int]] = {}
    for r, s in projective_lines(p):
        for u in range(p):
            for v in range(p):
                key = rank_one_shear_coeffs(r, s, u, v, p)
                out.setdefault(key, {"r": r, "s": s, "u": u, "v": v})
    return out


def search_field(p: int) -> dict[str, Any]:
    h2_total = p**6
    h2_trace_zero = 0
    linear_solution_count = 0
    jacobian_one_count = 0
    jacobian_candidates: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    non_permutation: list[dict[str, Any]] = []
    rank_histogram: dict[str, int] = {}
    max_free_dimension = 0
    for h2 in itertools.product(range(p), repeat=6):
        if not trace_a_is_zero(tuple(h2), p):
            continue
        h2_trace_zero += 1
        rows, rhs = linear_rows_for_h3(tuple(h2), p)
        solved = rref_solutions(rows, rhs, p)
        if solved is None:
            continue
        particular, basis, rank = solved
        free_dim = len(basis)
        max_free_dimension = max(max_free_dimension, free_dim)
        rank_histogram[str(rank)] = rank_histogram.get(str(rank), 0) + 1
        for h3 in iter_affine_space(particular, basis, p):
            linear_solution_count += 1
            if not det_b_zero(h3, p):
                continue
            if determinant_constraints(tuple(h2), h3, p):
                continue
            jacobian_one_count += 1
            jacobian_candidates.add((tuple(h2), tuple(h3)))
            if not is_permutation(tuple(h2), h3, p):
                non_permutation.append({"h2": list(h2), "h3": list(h3)})
                if len(non_permutation) >= 3:
                    break
        if len(non_permutation) >= 3:
            break
    shears = rank_one_shear_set(p)
    shear_keys = set(shears)
    missing_from_shear = sorted(jacobian_candidates - shear_keys)[:3]
    extra_shears = sorted(shear_keys - jacobian_candidates)[:3]
    expected_shear_count = 1 + (p + 1) * (p * p - 1)
    return {
        "field": f"F_{p}",
        "h2_tuples_checked": h2_total,
        "h2_trace_zero": h2_trace_zero,
        "h3_linear_solution_count": linear_solution_count,
        "jacobian_one_candidates": jacobian_one_count,
        "non_permutation_candidates": len(non_permutation),
        "first_non_permutation_candidates": non_permutation,
        "rank_one_shear_candidates": len(shears),
        "expected_rank_one_shear_candidates": expected_shear_count,
        "keller_candidates_equal_rank_one_shears": jacobian_candidates == shear_keys,
        "missing_keller_candidates_from_shear_sample": [
            {"h2": list(item[0]), "h3": list(item[1])} for item in missing_from_shear
        ],
        "extra_shear_candidates_sample": [
            {"h2": list(item[0]), "h3": list(item[1])} for item in extra_shears
        ],
        "sample_shear_parameterization": {
            "form": "H=(s,-r)*(u*(r*x+s*y)^2+v*(r*x+s*y)^3)",
            "projective_line_count": p + 1,
            "scalar_pair_count": p * p,
            "duplicate_zero_removed_count": p,
        },
        "linear_rank_histogram": rank_histogram,
        "max_h3_free_dimension": max_free_dimension,
    }


def build_report() -> dict[str, Any]:
    symbolic_identity = symbolic_cubic_shear_identity()
    rows = [search_field(5), search_field(7), search_field(11)]
    checks = {
        "symbolic_rank_one_shear_identity_verified": symbolic_identity["all_checks_pass"],
        "finite_field_elimination_found_no_cubic_counterexample": all(row["non_permutation_candidates"] == 0 for row in rows),
        "finite_field_keller_candidates_equal_rank_one_shears": all(row["keller_candidates_equal_rank_one_shears"] for row in rows),
        "full_jacobian_conjecture_solved": False,
    }
    report = {
        "schema": "holotopy.polynomial_attempt.jacobian_cubic_plane",
        "status": "BOUNDED_PROGRESS",
        "problem": "Jacobian conjecture for polynomial maps",
        "target": (
            "Normalized plane maps F=(x+P,y+Q) with P,Q containing all degree-2 and degree-3 terms."
        ),
        "method": {
            "decomposition": "H=H2+H3",
            "degree_equations": [
                "degree 1: trace(JH2)=0",
                "degree 2: trace(JH3)+det(JH2)=0",
                "degree 3: mixed determinant term det(JH2,JH3)=0",
                "degree 4: det(JH3)=0",
            ],
            "elimination": (
                "For each H2 over F_p, solve the degree 2 and 3 equations as a linear system in H3, "
                "then test the remaining quartic determinant and permutation property."
            ),
            "classification": (
                "Compare the surviving Keller candidates to the generated rank-one shear family "
                "H=(s,-r)*(u*(r*x+s*y)^2+v*(r*x+s*y)^3)."
            ),
        },
        "finite_field_elimination": {
            "fields": rows,
            "fields_sha256": sha_json(rows),
        },
        "symbolic_identity_check": symbolic_identity,
        "checks": checks,
        "residue": [
            {
                "kind": "finite_field_only",
                "description": "This is an odd-prime finite-field elimination search, not a characteristic-zero proof.",
                "discharged": False,
            },
            {
                "kind": "degree_bound_only",
                "description": "Only normalized plane maps of degree at most 3 are searched.",
                "discharged": False,
            },
            {
                "kind": "open_problem_not_solved",
                "description": "The full Jacobian conjecture remains outside this finite bounded search.",
                "discharged": False,
            },
        ],
    }
    report["certificate_sha256"] = sha_json({key: value for key, value in report.items() if key != "certificate_sha256"})
    return report


def main() -> None:
    report = build_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["checks"]["symbolic_rank_one_shear_identity_verified"] is not True:
        raise SystemExit(1)
    if report["checks"]["finite_field_elimination_found_no_cubic_counterexample"] is not True:
        raise SystemExit(1)
    if report["checks"]["finite_field_keller_candidates_equal_rank_one_shears"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
