from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "temp" / "jacobian_quadratic_attempt"
REPORT = OUT_DIR / "report.json"
VARS = ("x", "y", "a", "b", "c", "d", "e", "f")
VAR_INDEX = {name: index for index, name in enumerate(VARS)}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


class LP:
    def __init__(self, terms: dict[tuple[int, ...], Fraction] | None = None):
        self.terms = {key: value for key, value in (terms or {}).items() if value}

    @staticmethod
    def const(value: int | Fraction) -> "LP":
        coeff = Fraction(value)
        return LP({(0,) * len(VARS): coeff}) if coeff else LP()

    @staticmethod
    def var(name: str) -> "LP":
        exp = [0] * len(VARS)
        exp[VAR_INDEX[name]] = 1
        return LP({tuple(exp): Fraction(1)})

    @staticmethod
    def monomial(exponents: dict[str, int], coeff: int | Fraction = 1) -> "LP":
        exp = [0] * len(VARS)
        for name, value in exponents.items():
            exp[VAR_INDEX[name]] = int(value)
        return LP({tuple(exp): Fraction(coeff)})

    def __add__(self, other: Any) -> "LP":
        rhs = _lp(other)
        out = dict(self.terms)
        for exp, coeff in rhs.terms.items():
            out[exp] = out.get(exp, Fraction(0)) + coeff
        return LP(out)

    __radd__ = __add__

    def __neg__(self) -> "LP":
        return LP({exp: -coeff for exp, coeff in self.terms.items()})

    def __sub__(self, other: Any) -> "LP":
        return self + (-_lp(other))

    def __rsub__(self, other: Any) -> "LP":
        return _lp(other) + (-self)

    def __mul__(self, other: Any) -> "LP":
        rhs = _lp(other)
        out: dict[tuple[int, ...], Fraction] = {}
        for left_exp, left_coeff in self.terms.items():
            for right_exp, right_coeff in rhs.terms.items():
                exp = tuple(a + b for a, b in zip(left_exp, right_exp))
                out[exp] = out.get(exp, Fraction(0)) + left_coeff * right_coeff
        return LP(out)

    __rmul__ = __mul__

    def __pow__(self, power: int) -> "LP":
        if power < 0:
            raise ValueError("negative polynomial powers are not supported")
        out = LP.const(1)
        base = self
        n = power
        while n:
            if n & 1:
                out = out * base
            base = base * base
            n >>= 1
        return out

    def derivative(self, var_name: str) -> "LP":
        index = VAR_INDEX[var_name]
        out: dict[tuple[int, ...], Fraction] = {}
        for exp, coeff in self.terms.items():
            degree = exp[index]
            if degree == 0:
                continue
            new_exp = list(exp)
            new_exp[index] -= 1
            out[tuple(new_exp)] = out.get(tuple(new_exp), Fraction(0)) + coeff * degree
        return LP(out)

    def is_zero(self) -> bool:
        return not self.terms

    def to_rows(self) -> list[dict[str, Any]]:
        rows = []
        for exp, coeff in sorted(self.terms.items()):
            rows.append(
                {
                    "coeff": [coeff.numerator, coeff.denominator],
                    "exp": {name: power for name, power in zip(VARS, exp) if power},
                }
            )
        return rows


def _lp(value: Any) -> LP:
    if isinstance(value, LP):
        return value
    if isinstance(value, (int, Fraction)):
        return LP.const(value)
    raise TypeError(f"cannot coerce {type(value).__name__} to LP")


def _vars() -> dict[str, LP]:
    return {name: LP.var(name) for name in VARS}


def _coeff_by_xy(poly: LP) -> dict[tuple[int, int], LP]:
    out: dict[tuple[int, int], LP] = {}
    for exp, coeff in poly.terms.items():
        xy = (exp[VAR_INDEX["x"]], exp[VAR_INDEX["y"]])
        rest = list(exp)
        rest[VAR_INDEX["x"]] = 0
        rest[VAR_INDEX["y"]] = 0
        out[xy] = out.get(xy, LP()) + LP({tuple(rest): coeff})
    return out


def _compose(poly: LP, sx: LP, sy: LP) -> LP:
    out = LP()
    for exp, coeff in poly.terms.items():
        x_power = exp[VAR_INDEX["x"]]
        y_power = exp[VAR_INDEX["y"]]
        param_exp = list(exp)
        param_exp[VAR_INDEX["x"]] = 0
        param_exp[VAR_INDEX["y"]] = 0
        out = out + LP({tuple(param_exp): coeff}) * (sx**x_power) * (sy**y_power)
    return out


def _det_minus_one(h1: LP, h2: LP) -> LP:
    v = _vars()
    f1 = v["x"] + h1
    f2 = v["y"] + h2
    return f1.derivative("x") * f2.derivative("y") - f1.derivative("y") * f2.derivative("x") - 1


def _inverse_identity_checks(h1: LP, h2: LP) -> dict[str, bool]:
    v = _vars()
    f1 = v["x"] + h1
    f2 = v["y"] + h2
    g1 = v["x"] - h1
    g2 = v["y"] - h2
    return {
        "det_jacobian_is_one": _det_minus_one(h1, h2).is_zero(),
        "F_after_I_minus_H_x_is_x": (_compose(f1, g1, g2) - v["x"]).is_zero(),
        "F_after_I_minus_H_y_is_y": (_compose(f2, g1, g2) - v["y"]).is_zero(),
        "I_minus_H_after_F_x_is_x": (_compose(g1, f1, f2) - v["x"]).is_zero(),
        "I_minus_H_after_F_y_is_y": (_compose(g2, f1, f2) - v["y"]).is_zero(),
    }


def formal_identity_check() -> dict[str, Any]:
    v = _vars()
    x, y = v["x"], v["y"]
    a, b, c, d, e, f = v["a"], v["b"], v["c"], v["d"], v["e"], v["f"]
    h1 = a * x**2 + b * x * y + c * y**2
    h2 = d * x**2 + e * x * y + f * y**2
    coeffs = _coeff_by_xy(_det_minus_one(h1, h2))
    expected = {
        (1, 0): 2 * a + e,
        (0, 1): b + 2 * f,
        (2, 0): 2 * a * e - 2 * b * d,
        (1, 1): 4 * a * f - 4 * c * d,
        (0, 2): 2 * b * f - 2 * c * e,
    }
    determinant_constraints_match = set(coeffs) == set(expected) and all(
        (coeffs[key] - value).is_zero() for key, value in expected.items()
    )

    case_a = _inverse_identity_checks(LP.const(0), d * x**2)
    case_b = _inverse_identity_checks(c * y**2, LP.const(0))
    inv_a = LP.monomial({"a": -1})
    inv_b = LP.monomial({"b": -1})
    h1_case_c = a * x**2 + b * x * y + Fraction(1, 4) * b**2 * inv_a * y**2
    h2_case_c = -2 * a**2 * inv_b * x**2 - 2 * a * x * y - Fraction(1, 2) * b * y**2
    case_c = _inverse_identity_checks(h1_case_c, h2_case_c)

    checks = {
        "determinant_constraints_match": determinant_constraints_match,
        "case_a_triangular_x_identity": all(case_a.values()),
        "case_b_triangular_y_identity": all(case_b.values()),
        "case_c_rank_one_laurent_identity": all(case_c.values()),
    }
    return {
        "engine": "exact_laurent_polynomial_Q[x,y,a,b,c,d,e,f]",
        "determinant_coefficients": {
            f"x^{key[0]} y^{key[1]}": value.to_rows()
            for key, value in sorted(coeffs.items())
        },
        "determinant_coefficients_sha256": sha_json(
            {f"{key[0]},{key[1]}": value.to_rows() for key, value in sorted(coeffs.items())}
        ),
        "case_checks": {
            "a=b=c=0": case_a,
            "a=0_nonzero_H1": case_b,
            "a_nonzero_rank_one": case_c,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def jacobian_is_one_mod_p(coeffs: tuple[int, int, int, int, int, int], p: int) -> bool:
    a, b, c, d, e, f = coeffs
    return all(
        value % p == 0
        for value in (
            2 * a + e,
            b + 2 * f,
            2 * a * e - 2 * b * d,
            4 * a * f - 4 * c * d,
            2 * b * f - 2 * c * e,
        )
    )


def apply_map(coeffs: tuple[int, int, int, int, int, int], x: int, y: int, p: int) -> tuple[int, int]:
    a, b, c, d, e, f = coeffs
    first = x + a * x * x + b * x * y + c * y * y
    second = y + d * x * x + e * x * y + f * y * y
    return first % p, second % p


def is_permutation_mod_p(coeffs: tuple[int, int, int, int, int, int], p: int) -> bool:
    seen = {apply_map(coeffs, x, y, p) for x in range(p) for y in range(p)}
    return len(seen) == p * p


def finite_field_search(primes: list[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in primes:
        total = p**6
        jacobian_one = 0
        non_permutation = []
        for a in range(p):
            for b in range(p):
                for c in range(p):
                    for d in range(p):
                        for e in range(p):
                            for f in range(p):
                                coeffs = (a, b, c, d, e, f)
                                if not jacobian_is_one_mod_p(coeffs, p):
                                    continue
                                jacobian_one += 1
                                if not is_permutation_mod_p(coeffs, p):
                                    non_permutation.append(coeffs)
        rows.append(
            {
                "field": f"F_{p}",
                "coefficient_tuples_checked": total,
                "jacobian_one_candidates": jacobian_one,
                "non_permutation_candidates": len(non_permutation),
                "first_non_permutation": list(non_permutation[0]) if non_permutation else None,
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    formal = formal_identity_check()
    search_rows = finite_field_search([3, 5, 7])
    checks = {
        "formal_quadratic_identity_check_passed": formal["all_checks_pass"],
        "finite_search_found_no_quadratic_counterexample": all(
            row["non_permutation_candidates"] == 0 for row in search_rows
        ),
        "full_jacobian_conjecture_solved": False,
    }
    report = {
        "schema": "holotopy.polynomial_attempt.jacobian_quadratic",
        "status": "BOUNDED_PROGRESS",
        "problem": "Jacobian conjecture for polynomial maps",
        "target": (
            "Normalized quadratic plane maps F=(x+H1,y+H2), where H1,H2 are homogeneous "
            "quadratics and det JF is identically 1."
        ),
        "symbolic_result": {
            "claim": (
                "In characteristic zero, every normalized homogeneous quadratic plane map "
                "with det JF=1 is invertible."
            ),
            "setup": {
                "H1": "a*x^2 + b*x*y + c*y^2",
                "H2": "d*x^2 + e*x*y + f*y^2",
                "linear_jacobian_constraints": ["e=-2a", "f=-b/2"],
                "quadratic_jacobian_constraints": [
                    "2*a^2 + b*d = 0",
                    "a*b + 2*c*d = 0",
                    "b^2 - 4*a*c = 0",
                ],
            },
            "case_split": [
                {
                    "case": "a=b=c=0",
                    "normal_form": "H=(0,d*x^2)",
                    "reason": "H composed with H is zero.",
                },
                {
                    "case": "a=0 and H1 is not zero",
                    "normal_form": "H=(c*y^2,0)",
                    "reason": "b=0 and c*d=0, so the nonzero direction is triangular.",
                },
                {
                    "case": "a != 0",
                    "normal_form": "H=v*L^2, L=2*a*x+b*y, v=(1/(4a),-1/(2b))",
                    "reason": "The constraints force b != 0, c=b^2/(4a), d=-2a^2/b, and L(v)=0.",
                },
            ],
            "inverse_certificate": (
                "In every case H=v*L^2 with L(v)=0, including triangular degenerations. "
                "Thus H(z+/-H(z))=H(z), so F^{-1}=I-H."
            ),
        },
        "formal_identity_check": formal,
        "finite_field_search": {
            "family": "same normalized homogeneous quadratic family over F_p",
            "fields": search_rows,
            "interpretation": (
                "This finite search is not a proof of the characteristic-zero open problem; "
                "it checks that the same bounded family has no counterexample over small odd prime fields."
            ),
        },
        "checks": checks,
        "residue": [
            {
                "kind": "open_problem_not_solved",
                "description": "The full Jacobian conjecture remains outside this bounded quadratic subcase.",
                "discharged": False,
            },
            {
                "kind": "bounded_case_split_only",
                "description": "The formal identity checker covers the normalized homogeneous quadratic subcase, not higher-degree or non-normalized maps.",
                "discharged": False,
            },
            {
                "kind": "characteristic_two_excluded",
                "description": "The finite search excludes F_2 because characteristic 2 collapses derivative constraints outside the characteristic-zero target.",
                "discharged": True,
            },
        ],
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def main() -> None:
    report = build_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["checks"]["formal_quadratic_identity_check_passed"] is not True:
        raise SystemExit(1)
    if report["checks"]["finite_search_found_no_quadratic_counterexample"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
