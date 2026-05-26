from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "evidence" / "jacobian_homogeneous_plane_attempt"
REPORT = OUT_DIR / "report.json"
VARS = ("x", "y", "r", "s", "t")
VAR_INDEX = {name: index for index, name in enumerate(VARS)}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


class Poly:
    def __init__(self, terms: dict[tuple[int, ...], Fraction] | None = None):
        self.terms = {exp: coeff for exp, coeff in (terms or {}).items() if coeff}

    @staticmethod
    def const(value: int | Fraction) -> "Poly":
        coeff = Fraction(value)
        return Poly({(0,) * len(VARS): coeff}) if coeff else Poly()

    @staticmethod
    def var(name: str) -> "Poly":
        exp = [0] * len(VARS)
        exp[VAR_INDEX[name]] = 1
        return Poly({tuple(exp): Fraction(1)})

    def __add__(self, other: Any) -> "Poly":
        rhs = coerce(other)
        out = dict(self.terms)
        for exp, coeff in rhs.terms.items():
            out[exp] = out.get(exp, Fraction(0)) + coeff
        return Poly(out)

    __radd__ = __add__

    def __neg__(self) -> "Poly":
        return Poly({exp: -coeff for exp, coeff in self.terms.items()})

    def __sub__(self, other: Any) -> "Poly":
        return self + (-coerce(other))

    def __rsub__(self, other: Any) -> "Poly":
        return coerce(other) + (-self)

    def __mul__(self, other: Any) -> "Poly":
        rhs = coerce(other)
        out: dict[tuple[int, ...], Fraction] = {}
        for left_exp, left_coeff in self.terms.items():
            for right_exp, right_coeff in rhs.terms.items():
                exp = tuple(a + b for a, b in zip(left_exp, right_exp))
                out[exp] = out.get(exp, Fraction(0)) + left_coeff * right_coeff
        return Poly(out)

    __rmul__ = __mul__

    def __pow__(self, power: int) -> "Poly":
        if power < 0:
            raise ValueError("negative powers are not supported")
        out = Poly.const(1)
        base = self
        n = power
        while n:
            if n & 1:
                out = out * base
            base = base * base
            n >>= 1
        return out

    def derivative(self, name: str) -> "Poly":
        idx = VAR_INDEX[name]
        out: dict[tuple[int, ...], Fraction] = {}
        for exp, coeff in self.terms.items():
            degree = exp[idx]
            if degree == 0:
                continue
            new_exp = list(exp)
            new_exp[idx] -= 1
            out[tuple(new_exp)] = out.get(tuple(new_exp), Fraction(0)) + coeff * degree
        return Poly(out)

    def is_zero(self) -> bool:
        return not self.terms

    def rows(self) -> list[dict[str, Any]]:
        return [
            {
                "coeff": [coeff.numerator, coeff.denominator],
                "exp": {name: power for name, power in zip(VARS, exp) if power},
            }
            for exp, coeff in sorted(self.terms.items())
        ]


def coerce(value: Any) -> Poly:
    if isinstance(value, Poly):
        return value
    if isinstance(value, (int, Fraction)):
        return Poly.const(value)
    raise TypeError(f"cannot coerce {type(value).__name__} to Poly")


def compose(poly: Poly, sx: Poly, sy: Poly) -> Poly:
    out = Poly()
    for exp, coeff in poly.terms.items():
        x_power = exp[VAR_INDEX["x"]]
        y_power = exp[VAR_INDEX["y"]]
        rest = list(exp)
        rest[VAR_INDEX["x"]] = 0
        rest[VAR_INDEX["y"]] = 0
        out = out + Poly({tuple(rest): coeff}) * (sx**x_power) * (sy**y_power)
    return out


def det_minus_one(f1: Poly, f2: Poly) -> Poly:
    return f1.derivative("x") * f2.derivative("y") - f1.derivative("y") * f2.derivative("x") - 1


def normal_form_identity(degree: int) -> dict[str, Any]:
    x = Poly.var("x")
    y = Poly.var("y")
    r = Poly.var("r")
    s = Poly.var("s")
    t = Poly.var("t")
    linear = r * x + s * y
    h1 = s * t * linear**degree
    h2 = -r * t * linear**degree
    f1 = x + h1
    f2 = y + h2
    g1 = x - h1
    g2 = y - h2
    checks = {
        "linear_form_annihilates_vector": (compose(linear, h1, h2)).is_zero(),
        "det_jacobian_is_one": det_minus_one(f1, f2).is_zero(),
        "F_after_I_minus_H_x_is_x": (compose(f1, g1, g2) - x).is_zero(),
        "F_after_I_minus_H_y_is_y": (compose(f2, g1, g2) - y).is_zero(),
        "I_minus_H_after_F_x_is_x": (compose(g1, f1, f2) - x).is_zero(),
        "I_minus_H_after_F_y_is_y": (compose(g2, f1, f2) - y).is_zero(),
    }
    return {
        "degree": degree,
        "normal_form": "H=t*(s,-r)*(r*x+s*y)^degree",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def build_report() -> dict[str, Any]:
    degree_checks = [normal_form_identity(degree) for degree in range(2, 13)]
    lemmas = [
        {
            "id": "homogeneous_keller_splits_by_degree",
            "statement": (
                "For F=I+H with H homogeneous of degree m>1 in two variables, det JF=1 "
                "forces trace(JH)=0 and det(JH)=0 because these terms have distinct degrees."
            ),
            "status": "elementary_degree_argument",
        },
        {
            "id": "binary_jacobian_zero_dependence",
            "statement": (
                "For binary forms P,Q over characteristic zero, det J(P,Q)=0 implies "
                "P and Q are algebraically dependent; same-degree homogeneity forces a common factor form H=vR."
            ),
            "status": "standard_commutative_algebra_lemma_not_formalized_here",
        },
        {
            "id": "divergence_zero_rank_one_form",
            "statement": (
                "With H=vR and trace(JH)=v dot grad(R)=0, a linear change gives R=L^m "
                "and L(v)=0."
            ),
            "status": "standard_binary_form_reduction_not_formalized_here",
        },
    ]
    checks = {
        "normal_form_identities_verified_degrees_2_to_12": all(row["all_checks_pass"] for row in degree_checks),
        "full_jacobian_conjecture_solved": False,
    }
    report = {
        "schema": "holotopy.polynomial_attempt.jacobian_homogeneous_plane",
        "status": "BOUNDED_PROGRESS",
        "problem": "Jacobian conjecture for polynomial maps",
        "claim": (
            "The homogeneous two-variable Keller subproblem reduces to maps "
            "H=t*(s,-r)*(r*x+s*y)^m, and this normal form has inverse I-H."
        ),
        "scope": {
            "dimension": 2,
            "degree": "homogeneous m>1",
            "field": "characteristic zero",
            "not_covered": "non-homogeneous maps, higher dimension, and general degree mixtures",
        },
        "reduction_lemmas": lemmas,
        "formal_identity_check": {
            "engine": "exact_polynomial_Q[x,y,r,s,t]",
            "degree_range_checked": [2, 12],
            "degree_checks": degree_checks,
            "degree_checks_sha256": sha_json(degree_checks),
        },
        "checks": checks,
        "residue": [
            {
                "kind": "open_problem_not_solved",
                "description": "The full Jacobian conjecture remains outside this homogeneous plane subcase.",
                "discharged": False,
            },
            {
                "kind": "standard_lemma_dependency",
                "description": "The reduction from arbitrary homogeneous H to rank-one normal form uses standard binary-form algebra not formalized by this script.",
                "discharged": False,
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
    if report["checks"]["normal_form_identities_verified_degrees_2_to_12"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
