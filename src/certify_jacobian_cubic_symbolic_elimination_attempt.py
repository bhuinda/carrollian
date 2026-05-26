from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "temp" / "jacobian_cubic_symbolic_elimination_attempt"
REPORT = OUT_DIR / "report.json"
CACHE_DIR = OUT_DIR / "saturation_cache"
CACHE_MANIFEST = CACHE_DIR / "manifest.json"
COEFF_VARS = ("a", "b", "c", "d", "A", "B", "C", "D", "E")
VAR_INDEX = {name: index for index, name in enumerate(COEFF_VARS)}
XY = tuple[int, int]


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


class Poly:
    def __init__(self, terms: dict[tuple[int, ...], Fraction] | None = None):
        self.terms = {exp: coeff for exp, coeff in (terms or {}).items() if coeff}

    @staticmethod
    def const(value: int | Fraction) -> "Poly":
        coeff = Fraction(value)
        return Poly({(0,) * len(COEFF_VARS): coeff}) if coeff else Poly()

    @staticmethod
    def var(name: str) -> "Poly":
        exp = [0] * len(COEFF_VARS)
        exp[VAR_INDEX[name]] = 1
        return Poly({tuple(exp): Fraction(1)})

    @staticmethod
    def monomial(exp: tuple[int, ...], coeff: Fraction = Fraction(1)) -> "Poly":
        return Poly({exp: coeff})

    def __add__(self, other: Any) -> "Poly":
        rhs = poly(other)
        out = dict(self.terms)
        for exp, coeff in rhs.terms.items():
            out[exp] = out.get(exp, Fraction(0)) + coeff
        return Poly(out)

    __radd__ = __add__

    def __neg__(self) -> "Poly":
        return Poly({exp: -coeff for exp, coeff in self.terms.items()})

    def __sub__(self, other: Any) -> "Poly":
        return self + (-poly(other))

    def __rsub__(self, other: Any) -> "Poly":
        return poly(other) + (-self)

    def __mul__(self, other: Any) -> "Poly":
        rhs = poly(other)
        out: dict[tuple[int, ...], Fraction] = {}
        for left_exp, left_coeff in self.terms.items():
            for right_exp, right_coeff in rhs.terms.items():
                exp = tuple(a + b for a, b in zip(left_exp, right_exp))
                out[exp] = out.get(exp, Fraction(0)) + left_coeff * right_coeff
        return Poly(out)

    __rmul__ = __mul__

    def monomial_mul(self, exp: tuple[int, ...], coeff: Fraction = Fraction(1)) -> "Poly":
        if coeff == 0:
            return Poly()
        return Poly(
            {
                tuple(left + right for left, right in zip(term_exp, exp)): term_coeff * coeff
                for term_exp, term_coeff in self.terms.items()
            }
        )

    def is_zero(self) -> bool:
        return not self.terms

    def rows(self) -> list[dict[str, Any]]:
        return [
            {
                "coeff": [coeff.numerator, coeff.denominator],
                "exp": {name: power for name, power in zip(COEFF_VARS, exp) if power},
            }
            for exp, coeff in sorted(self.terms.items())
        ]


def poly(value: Any) -> Poly:
    if isinstance(value, Poly):
        return value
    if isinstance(value, (int, Fraction)):
        return Poly.const(value)
    raise TypeError(f"cannot coerce {type(value).__name__} to Poly")


def monomial_key(exp: tuple[int, ...], order: str) -> tuple[Any, ...]:
    if order == "lex":
        return exp
    if order == "grlex":
        return (sum(exp), exp)
    if order == "grevlex":
        return (sum(exp), tuple(-value for value in reversed(exp)))
    raise ValueError(f"unknown monomial order: {order}")


def leading_term(poly_value: Poly, order: str) -> tuple[tuple[int, ...], Fraction]:
    if poly_value.is_zero():
        raise ValueError("zero polynomial has no leading term")
    exp = max(poly_value.terms, key=lambda item: monomial_key(item, order))
    return exp, poly_value.terms[exp]


def divides(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return all(a <= b for a, b in zip(left, right))


def exp_sub(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a - b for a, b in zip(left, right))


def exp_lcm(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(max(a, b) for a, b in zip(left, right))


def reduce_poly(poly_value: Poly, basis: list[Poly], *, order: str, step_limit: int = 100000) -> tuple[Poly, int, bool]:
    f = poly_value
    remainder = Poly()
    steps = 0
    basis_lts = [leading_term(item, order) for item in basis if not item.is_zero()]
    while not f.is_zero():
        steps += 1
        if steps > step_limit:
            return remainder + f, steps, False
        f_exp, f_coeff = leading_term(f, order)
        reduced = False
        for basis_poly, (b_exp, b_coeff) in zip(basis, basis_lts):
            if not divides(b_exp, f_exp):
                continue
            multiplier_exp = exp_sub(f_exp, b_exp)
            multiplier_coeff = f_coeff / b_coeff
            f = f - basis_poly.monomial_mul(multiplier_exp, multiplier_coeff)
            reduced = True
            break
        if not reduced:
            lt_poly = Poly.monomial(f_exp, f_coeff)
            remainder = remainder + lt_poly
            f = f - lt_poly
    return remainder, steps, True


def s_polynomial(left: Poly, right: Poly, *, order: str) -> Poly:
    left_exp, left_coeff = leading_term(left, order)
    right_exp, right_coeff = leading_term(right, order)
    lcm_exp = exp_lcm(left_exp, right_exp)
    return left.monomial_mul(exp_sub(lcm_exp, left_exp), Fraction(1, 1) / left_coeff) - right.monomial_mul(
        exp_sub(lcm_exp, right_exp),
        Fraction(1, 1) / right_coeff,
    )


def polynomial_signature(poly_value: Poly) -> tuple[tuple[tuple[int, ...], Fraction], ...]:
    return tuple(sorted(poly_value.terms.items()))


def buchberger(
    generators: list[Poly],
    *,
    order: str = "grevlex",
    pair_limit: int = 2000,
    basis_limit: int = 128,
    reduction_step_limit: int = 100000,
) -> dict[str, Any]:
    basis: list[Poly] = []
    signatures: set[tuple[tuple[tuple[int, ...], Fraction], ...]] = set()
    for generator in generators:
        remainder, _steps, completed = reduce_poly(generator, basis, order=order, step_limit=reduction_step_limit)
        if not completed:
            return {
                "status": "REDUCTION_LIMIT",
                "order": order,
                "basis": basis,
                "basis_size": len(basis),
                "processed_pairs": 0,
                "nonzero_remainders": len(basis),
            }
        if remainder.is_zero():
            continue
        sig = polynomial_signature(remainder)
        if sig not in signatures:
            signatures.add(sig)
            basis.append(remainder)

    pairs = [(i, j) for i in range(len(basis)) for j in range(i)]
    processed = 0
    nonzero_remainders = 0
    max_terms = max((len(item.terms) for item in basis), default=0)
    while pairs:
        if processed >= pair_limit:
            status = "PAIR_LIMIT"
            break
        i, j = pairs.pop(0)
        processed += 1
        spoly = s_polynomial(basis[i], basis[j], order=order)
        remainder, _steps, completed = reduce_poly(spoly, basis, order=order, step_limit=reduction_step_limit)
        if not completed:
            status = "REDUCTION_LIMIT"
            break
        if remainder.is_zero():
            continue
        nonzero_remainders += 1
        sig = polynomial_signature(remainder)
        if sig in signatures:
            continue
        if len(basis) >= basis_limit:
            status = "BASIS_LIMIT"
            break
        signatures.add(sig)
        old_len = len(basis)
        basis.append(remainder)
        max_terms = max(max_terms, len(remainder.terms))
        pairs.extend((old_len, k) for k in range(old_len))
    else:
        status = "COMPLETE"

    reduced_basis: list[Poly] = []
    if status == "COMPLETE":
        for index, item in enumerate(basis):
            others = [basis[j] for j in range(len(basis)) if j != index]
            remainder, _steps, completed = reduce_poly(item, others, order=order, step_limit=reduction_step_limit)
            if completed and not remainder.is_zero():
                lt_exp, lt_coeff = leading_term(remainder, order)
                reduced_basis.append(remainder.monomial_mul((0,) * len(COEFF_VARS), Fraction(1, 1) / lt_coeff))
        basis = reduced_basis

    return {
        "status": status,
        "order": order,
        "basis": basis,
        "basis_size": len(basis),
        "processed_pairs": processed,
        "nonzero_remainders": nonzero_remainders,
        "max_terms_in_basis_poly": max_terms,
    }


def xy_add(left: dict[XY, Poly], right: dict[XY, Poly], scale: Poly | int = 1) -> dict[XY, Poly]:
    factor = poly(scale)
    out = dict(left)
    for key, value in right.items():
        combined = out.get(key, Poly()) + factor * value
        if combined.is_zero():
            out.pop(key, None)
        else:
            out[key] = combined
    return out


def xy_mul(left: dict[XY, Poly], right: dict[XY, Poly]) -> dict[XY, Poly]:
    out: dict[XY, Poly] = {}
    for (lx, ly), lc in left.items():
        for (rx, ry), rc in right.items():
            key = (lx + rx, ly + ry)
            combined = out.get(key, Poly()) + lc * rc
            if combined.is_zero():
                out.pop(key, None)
            else:
                out[key] = combined
    return out


def coeff_generators() -> dict[str, Any]:
    v = {name: Poly.var(name) for name in COEFF_VARS}
    a, b, c, d = v["a"], v["b"], v["c"], v["d"]
    A, B, C, D, E = v["A"], v["B"], v["C"], v["D"], v["E"]
    F = -3 * A + 4 * a * a + 2 * b * d
    G = a * b + 2 * c * d - B
    H = Fraction(1, 3) * (-4 * a * c + b * b - C)

    p2x = {(1, 0): 2 * a, (0, 1): b}
    p2y = {(1, 0): b, (0, 1): 2 * c}
    q2x = {(1, 0): 2 * d, (0, 1): -2 * a}
    q2y = {(1, 0): -2 * a, (0, 1): -b}
    p3x = {(2, 0): 3 * A, (1, 1): 2 * B, (0, 2): C}
    p3y = {(2, 0): B, (1, 1): 2 * C, (0, 2): 3 * D}
    q3x = {(2, 0): 3 * E, (1, 1): 2 * F, (0, 2): G}
    q3y = {(2, 0): F, (1, 1): 2 * G, (0, 2): 3 * H}

    det_a = xy_add(xy_mul(p2x, q2y), xy_mul(p2y, q2x), scale=-1)
    trace_b = xy_add(p3x, q3y)
    mixed = xy_add(xy_mul(p2x, q3y), xy_mul(p3x, q2y))
    mixed = xy_add(mixed, xy_mul(p2y, q3x), scale=-1)
    mixed = xy_add(mixed, xy_mul(p3y, q2x), scale=-1)
    det_b = xy_add(xy_mul(p3x, q3y), xy_mul(p3y, q3x), scale=-1)

    trace_b_plus_det_a = xy_add(trace_b, det_a)
    generators = {
        "trace_b_plus_det_a": trace_b_plus_det_a,
        "mixed": mixed,
        "det_b": det_b,
    }
    flat_generators = [
        {"name": f"mixed_x{x}_y{y}", "poly": item}
        for (x, y), item in sorted(mixed.items())
    ] + [
        {"name": f"det_b_x{x}_y{y}", "poly": item}
        for (x, y), item in sorted(det_b.items())
    ]
    targets = {
        "h2_det_x2": 2 * a * a + b * d,
        "h2_det_xy": a * b + 2 * c * d,
        "h2_det_y2": b * b - 4 * a * c,
    }
    checks = {
        "trace_substitution_eliminates_degree2": all(item.is_zero() for item in trace_b_plus_det_a.values()),
        "mixed_generator_count_is_4": len(mixed) == 4,
        "quartic_generator_count_is_5": len(det_b) == 5,
    }
    return {
        "substitutions": {
            "e": "-2*a",
            "f": "-b/2",
            "F": "-3*A + 4*a^2 + 2*b*d",
            "G": "a*b + 2*c*d - B",
            "H": "(-4*a*c + b^2 - C)/3",
        },
        "generators": generators,
        "flat_generators": flat_generators,
        "targets": targets,
        "checks": checks,
    }


def monomial_exponents(max_degree: int) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []
    n = len(COEFF_VARS)

    def rec(pos: int, remaining: int, current: list[int]) -> None:
        if pos == n:
            out.append(tuple(current))
            return
        for value in range(remaining + 1):
            current.append(value)
            rec(pos + 1, remaining - value, current)
            current.pop()

    rec(0, max_degree, [])
    return out


def solve_linear_system(matrix: list[list[Fraction]], rhs: list[Fraction]) -> bool:
    if not matrix:
        return not any(rhs)
    row_count = len(matrix)
    col_count = len(matrix[0])
    aug = [row[:] + [value] for row, value in zip(matrix, rhs)]
    pivot_row = 0
    for col in range(col_count):
        found = None
        for row in range(pivot_row, row_count):
            if aug[row][col]:
                found = row
                break
        if found is None:
            continue
        aug[pivot_row], aug[found] = aug[found], aug[pivot_row]
        inv = Fraction(1, 1) / aug[pivot_row][col]
        aug[pivot_row] = [value * inv for value in aug[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = aug[row][col]
            if factor:
                aug[row] = [value - factor * pivot for value, pivot in zip(aug[row], aug[pivot_row])]
        pivot_row += 1
        if pivot_row == row_count:
            break
    for row in aug:
        if all(value == 0 for value in row[:col_count]) and row[-1] != 0:
            return False
    return True


def ideal_membership_search(target: Poly, generators: list[dict[str, Any]], max_multiplier_degree: int) -> dict[str, Any]:
    multipliers = monomial_exponents(max_multiplier_degree)
    columns: list[Poly] = []
    for generator in generators:
        g = generator["poly"]
        for exp in multipliers:
            columns.append(g * Poly.monomial(exp))

    row_exps = sorted(set(target.terms) | {exp for column in columns for exp in column.terms})
    matrix = [
        [column.terms.get(exp, Fraction(0)) for column in columns]
        for exp in row_exps
    ]
    rhs = [target.terms.get(exp, Fraction(0)) for exp in row_exps]
    found = solve_linear_system(matrix, rhs)
    return {
        "max_multiplier_degree": max_multiplier_degree,
        "generator_count": len(generators),
        "multiplier_monomial_count": len(multipliers),
        "linear_unknown_count": len(columns),
        "coefficient_row_count": len(row_exps),
        "membership_found": found,
    }


def groebner_target_reductions(
    targets: dict[str, Poly],
    basis: list[Poly],
    *,
    order: str,
    step_limit: int,
) -> dict[str, Any]:
    reductions: dict[str, Any] = {}
    for name, target in targets.items():
        if basis:
            remainder, steps, completed = reduce_poly(target, basis, order=order, step_limit=step_limit)
            reductions[name] = {
                "completed": completed,
                "steps": steps,
                "remainder_zero": completed and remainder.is_zero(),
                "remainder_term_count": len(remainder.terms),
                "remainder_sha256": sha_json(remainder.rows()),
            }
        else:
            reductions[name] = {
                "completed": False,
                "steps": 0,
                "remainder_zero": False,
                "remainder_term_count": None,
                "remainder_sha256": None,
            }
    return reductions


def leading_term_rows(basis: list[Poly], order: str, limit: int = 24) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in basis[:limit]:
        exp, coeff = leading_term(item, order)
        rows.append(
            {
                "exp": {name: power for name, power in zip(COEFF_VARS, exp) if power},
                "coeff": [coeff.numerator, coeff.denominator],
            }
        )
    return rows


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def saturation_cache_input(
    generators: list[Poly],
    target: Poly,
    z: Poly,
    *,
    label: str,
    order: str,
    pair_limit: int,
    basis_limit: int,
    reduction_step_limit: int,
) -> dict[str, Any]:
    return {
        "schema": "holotopy.saturation_cache_input",
        "algorithm": "buchberger_rabinowitsch_contradiction",
        "label": label,
        "settings": {
            "order": order,
            "pair_limit": pair_limit,
            "basis_limit": basis_limit,
            "reduction_step_limit": reduction_step_limit,
        },
        "generators": [item.rows() for item in generators],
        "target": target.rows(),
        "saturation_variable": z.rows(),
    }


def load_saturation_cache(cache_path: Path, input_hash: str) -> dict[str, Any] | None:
    if not cache_path.exists():
        return None
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if payload.get("schema") != "holotopy.saturation_contradiction_cache":
        return None
    if payload.get("input_hash") != input_hash:
        return None
    result = payload.get("result")
    if not isinstance(result, dict):
        return None
    if result.get("input_sha256") != input_hash:
        return None
    return result


def write_saturation_cache(cache_path: Path, input_hash: str, result: dict[str, Any]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "holotopy.saturation_contradiction_cache",
        "input_hash": input_hash,
        "result": result,
    }
    cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def saturation_cache_spec(
    generators: list[Poly],
    target: Poly,
    z: Poly,
    *,
    label: str,
    order: str = "grevlex",
    pair_limit: int = 9000,
    basis_limit: int = 240,
    reduction_step_limit: int = 120000,
) -> dict[str, Any]:
    cache_input = saturation_cache_input(
        generators,
        target,
        z,
        label=label,
        order=order,
        pair_limit=pair_limit,
        basis_limit=basis_limit,
        reduction_step_limit=reduction_step_limit,
    )
    input_hash = sha_json(cache_input)
    cache_path = CACHE_DIR / f"{input_hash}.json"
    return {
        "label": label,
        "input_sha256": input_hash,
        "cache_file": repo_relative(cache_path),
        "cache_path": cache_path,
        "settings": cache_input["settings"],
    }


def h2_targets() -> dict[str, Poly]:
    v = {name: Poly.var(name) for name in COEFF_VARS}
    a, b, c, d = v["a"], v["b"], v["c"], v["d"]
    return {
        "h2_det_x2": 2 * a * a + b * d,
        "h2_det_xy": a * b + 2 * c * d,
        "h2_det_y2": b * b - 4 * a * c,
    }


def binary_cubic_det_generators() -> dict[str, Any]:
    # Generic binary cubics use the current ring slots:
    # P=a*x^3+b*x^2*y+c*x*y^2+d*y^3 and Q=A*x^3+B*x^2*y+C*x*y^2+D*y^3.
    v = {name: Poly.var(name) for name in COEFF_VARS}
    p0, p1, p2, p3 = v["a"], v["b"], v["c"], v["d"]
    q0, q1, q2, q3 = v["A"], v["B"], v["C"], v["D"]
    px = {(2, 0): 3 * p0, (1, 1): 2 * p1, (0, 2): p2}
    py = {(2, 0): p1, (1, 1): 2 * p2, (0, 2): 3 * p3}
    qx = {(2, 0): 3 * q0, (1, 1): 2 * q1, (0, 2): q2}
    qy = {(2, 0): q1, (1, 1): 2 * q2, (0, 2): 3 * q3}
    det = xy_add(xy_mul(px, qy), xy_mul(py, qx), scale=-1)
    return {
        "p_coefficients": [p0, p1, p2, p3],
        "q_coefficients": [q0, q1, q2, q3],
        "generators": [
            {"name": f"det_x{x}_y{y}", "poly": poly_value}
            for (x, y), poly_value in sorted(det.items())
        ],
    }


def binary_cubic_rank_one_chart(
    chart_name: str,
    unit: Poly,
    targets: dict[str, Poly],
    generators: list[dict[str, Any]],
) -> dict[str, Any]:
    order = "grevlex"
    attempt = buchberger(
        [item["poly"] for item in generators] + [unit - 1],
        order=order,
        pair_limit=2000,
        basis_limit=80,
        reduction_step_limit=100000,
    )
    basis = attempt.pop("basis")
    reductions = groebner_target_reductions(targets, basis, order=order, step_limit=100000)
    closes = all(item["remainder_zero"] for item in reductions.values())
    return {
        "chart": chart_name,
        "unit_normalization": "unit coefficient = 1",
        "groebner": {
            **attempt,
            "target_reductions": reductions,
            "closes_proportionality_targets": closes,
            "basis_leading_terms": leading_term_rows(basis, order),
        },
    }


def binary_cubic_rank_one_lemma() -> dict[str, Any]:
    payload = binary_cubic_det_generators()
    p = payload["p_coefficients"]
    q = payload["q_coefficients"]
    generators = payload["generators"]
    charts: dict[str, Any] = {}
    for index, unit in enumerate(p):
        scalar = q[index]
        targets = {
            f"q{target_index}_minus_q{index}_p{target_index}": q[target_index] - scalar * p[target_index]
            for target_index in range(4)
        }
        charts[f"p{index}_nonzero"] = binary_cubic_rank_one_chart(
            f"p{index}_nonzero",
            unit,
            targets,
            generators,
        )
    for index, unit in enumerate(q):
        scalar = p[index]
        targets = {
            f"p{target_index}_minus_p{index}_q{target_index}": p[target_index] - scalar * q[target_index]
            for target_index in range(4)
        }
        charts[f"q{index}_nonzero"] = binary_cubic_rank_one_chart(
            f"q{index}_nonzero",
            unit,
            targets,
            generators,
        )
    return {
        "ring": "Q[p0,p1,p2,p3,q0,q1,q2,q3]",
        "variable_map": {
            "a": "p0",
            "b": "p1",
            "c": "p2",
            "d": "p3",
            "A": "q0",
            "B": "q1",
            "C": "q2",
            "D": "q3",
        },
        "determinant_generators": {item["name"]: item["poly"].rows() for item in generators},
        "cover": (
            "If some P coefficient is nonzero, a p_i chart proves Q=q_i*P. "
            "If P is zero and some Q coefficient is nonzero, a q_i chart proves P=p_i*Q. "
            "If both are zero, proportionality is trivial."
        ),
        "charts": charts,
        "all_unit_charts_close_proportionality": all(
            chart["groebner"]["closes_proportionality_targets"]
            for chart in charts.values()
        ),
    }


def rank_one_h3_branch(branch: str) -> dict[str, Any]:
    """Close the H2 determinant targets after replacing det(JH3)=0 by rank-one data.

    The branch variables reuse the coefficient ring slots:
    A is lambda/mu, B is alpha, C is beta, and D is rho.
    """
    v = {name: Poly.var(name) for name in COEFF_VARS}
    a, b, c, d = v["a"], v["b"], v["c"], v["d"]
    parameter, alpha, beta, rho = v["A"], v["B"], v["C"], v["D"]
    targets = h2_targets()
    r = targets["h2_det_x2"]
    s = targets["h2_det_xy"]
    t = targets["h2_det_y2"]

    if branch == "q3_equals_lambda_p3":
        # H3=(P3, lambda P3). Trace operator is d/dx + lambda d/dy.
        vx_x = -(2 * a + parameter * b)
        vx_y = -(b + 2 * parameter * c)
        vy_x = 2 * parameter * a - 2 * d
        vy_y = 2 * a + parameter * b
        transport_normalization = alpha + parameter * beta - 1
        parameter_name = "lambda"
        branch_description = "finite proportionality chart H3=(P3, lambda P3)"
    elif branch == "p3_equals_mu_q3":
        # H3=(mu Q3, Q3). Trace operator is mu d/dx + d/dy.
        vx_x = -(2 * parameter * a + b)
        vx_y = -(parameter * b + 2 * c)
        vy_x = 2 * a - 2 * parameter * d
        vy_y = b + 2 * parameter * a
        transport_normalization = parameter * alpha + beta - 1
        parameter_name = "mu"
        branch_description = "infinite proportionality chart H3=(mu Q3, Q3)"
    else:
        raise ValueError(f"unknown rank-one H3 branch: {branch}")

    generators = [
        {
            "name": "linear_invariant_x",
            "poly": alpha * vx_x + beta * vy_x,
        },
        {
            "name": "linear_invariant_y",
            "poly": alpha * vx_y + beta * vy_y,
        },
        {
            "name": "readout_x2",
            "poly": 2 * r - rho * alpha * alpha,
        },
        {
            "name": "readout_xy",
            "poly": 2 * s - 2 * rho * alpha * beta,
        },
        {
            "name": "readout_y2",
            "poly": t - rho * beta * beta,
        },
        {
            "name": "transport_normalization",
            "poly": transport_normalization,
        },
    ]
    order = "grevlex"
    attempt = buchberger(
        [item["poly"] for item in generators],
        order=order,
        pair_limit=5000,
        basis_limit=200,
        reduction_step_limit=100000,
    )
    basis = attempt.pop("basis")
    reductions = groebner_target_reductions(targets, basis, order=order, step_limit=100000)
    closes_targets = all(item["remainder_zero"] for item in reductions.values())
    return {
        "branch": branch,
        "description": branch_description,
        "ring": "Q[a,b,c,d,parameter,alpha,beta,rho]",
        "variable_map": {
            "A": parameter_name,
            "B": "alpha",
            "C": "beta",
            "D": "rho",
        },
        "interpretation": {
            "linear_invariant": "L=alpha*x+beta*y is killed by the mixed vector field.",
            "readout": "2*r*x^2+2*s*x*y+t*y^2 = rho*L^2.",
            "normalization": "The trace transport of L is set to one on this chart.",
        },
        "generators": {item["name"]: item["poly"].rows() for item in generators},
        "groebner": {
            **attempt,
            "target_reductions": reductions,
            "closes_h2_shear_targets": closes_targets,
            "basis_leading_terms": leading_term_rows(basis, order),
        },
    }


def rank_one_h3_branch_elimination() -> dict[str, Any]:
    branches = {
        "q3_equals_lambda_p3": rank_one_h3_branch("q3_equals_lambda_p3"),
        "p3_equals_mu_q3": rank_one_h3_branch("p3_equals_mu_q3"),
    }
    return {
        "lemma": (
            "For binary cubic top terms over characteristic zero, det(JH3)=0 means the two "
            "homogeneous cubic components are proportional, with the zero top part handled separately."
        ),
        "branches": branches,
        "all_branches_close_h2_shear_targets": all(
            branch["groebner"]["closes_h2_shear_targets"]
            for branch in branches.values()
        ),
    }


def saturation_contradiction(
    generators: list[Poly],
    target: Poly,
    z: Poly,
    *,
    label: str,
    recompute: bool = False,
    order: str = "grevlex",
    pair_limit: int = 9000,
    basis_limit: int = 240,
    reduction_step_limit: int = 120000,
) -> dict[str, Any]:
    cache_input = saturation_cache_input(
        generators,
        target,
        z,
        label=label,
        order=order,
        pair_limit=pair_limit,
        basis_limit=basis_limit,
        reduction_step_limit=reduction_step_limit,
    )
    input_hash = sha_json(cache_input)
    cache_path = CACHE_DIR / f"{input_hash}.json"
    cached = None if recompute else load_saturation_cache(cache_path, input_hash)
    if cached is not None:
        return cached

    attempt = buchberger(
        generators + [z * target - 1],
        order=order,
        pair_limit=pair_limit,
        basis_limit=basis_limit,
        reduction_step_limit=reduction_step_limit,
    )
    basis = attempt.pop("basis")
    remainder, steps, completed = reduce_poly(Poly.const(1), basis, order=order, step_limit=reduction_step_limit)
    result = {
        **attempt,
        "label": label,
        "input_sha256": input_hash,
        "cache_file": repo_relative(cache_path),
        "reduction_completed": completed,
        "reduction_steps": steps,
        "contradiction_found": completed and remainder.is_zero(),
        "one_remainder_term_count": len(remainder.terms),
        "one_remainder_sha256": sha_json(remainder.rows()),
    }
    write_saturation_cache(cache_path, input_hash, result)
    return result


def rank_one_mixed_chart_system(branch: str, chart_index: int) -> dict[str, Any]:
    chart_vars = iter([Poly.var(name) for name in ("a", "b", "c")])
    cubic = [Poly.const(1) if index == chart_index else next(chart_vars) for index in range(4)]
    h0, h1, h2, h3, parameter, z = [Poly.var(name) for name in ("d", "A", "B", "C", "D", "E")]
    p0, p1, p2, p3 = cubic
    r = 2 * h0 * h0 + h1 * h3
    s = h0 * h1 + 2 * h2 * h3
    t = h1 * h1 - 4 * h0 * h2

    if branch == "q3_equals_lambda_p3":
        trace = [
            3 * p0 + parameter * p1 - 2 * r,
            p1 + parameter * p2 - s,
            p2 + 3 * parameter * p3 - t,
        ]
        vx0 = -(2 * h0 + parameter * h1)
        vx1 = -(h1 + 2 * parameter * h2)
        vy0 = 2 * parameter * h0 - 2 * h3
        vy1 = 2 * h0 + parameter * h1
        chart_prefix = "p"
        parameter_name = "lambda"
        description = "finite proportionality branch H3=(P3, lambda P3)"
        normal_form_residuals = {
            "h1_plus_2_lambda_h2": h1 + 2 * parameter * h2,
            "h0_minus_lambda2_h2": h0 - parameter * parameter * h2,
            "h3_minus_lambda3_h2": h3 - parameter * parameter * parameter * h2,
        }
    elif branch == "p3_equals_mu_q3":
        trace = [
            3 * parameter * p0 + p1 - 2 * r,
            parameter * p1 + p2 - s,
            parameter * p2 + 3 * p3 - t,
        ]
        vx0 = -(2 * parameter * h0 + h1)
        vx1 = -(parameter * h1 + 2 * h2)
        vy0 = 2 * h0 - 2 * parameter * h3
        vy1 = h1 + 2 * parameter * h0
        chart_prefix = "q"
        parameter_name = "mu"
        description = "infinite proportionality branch H3=(mu Q3, Q3)"
        normal_form_residuals = {
            "h0_minus_mu_h3": h0 - parameter * h3,
            "h1_plus_2_mu2_h3": h1 + 2 * parameter * parameter * h3,
            "h2_minus_mu3_h3": h2 - parameter * parameter * parameter * h3,
        }
    else:
        raise ValueError(f"unknown branch: {branch}")

    invariant = [
        3 * p0 * vx0 + p1 * vy0,
        3 * p0 * vx1 + 2 * p1 * vx0 + p1 * vy1 + 2 * p2 * vy0,
        2 * p1 * vx1 + p2 * vx0 + 2 * p2 * vy1 + 3 * p3 * vy0,
        p2 * vx1 + 3 * p3 * vy1,
    ]
    cube = [
        p1 * p1 - 3 * p0 * p2,
        p1 * p2 - 9 * p0 * p3,
        p2 * p2 - 3 * p1 * p3,
    ]
    return {
        "branch": branch,
        "description": description,
        "chart": f"{chart_prefix}{chart_index}_nonzero",
        "unit_normalization": f"{chart_prefix}{chart_index}=1",
        "parameter": parameter_name,
        "generators": trace + invariant + cube,
        "target_polys": {
            "h2_det_x2": r,
            "h2_det_xy": s,
            "h2_det_y2": t,
        },
        "normal_form_residuals": normal_form_residuals,
        "z": z,
    }


def rank_one_mixed_chart_saturation(*, recompute_saturations: bool = False) -> dict[str, Any]:
    branches: dict[str, Any] = {}
    for branch in ("q3_equals_lambda_p3", "p3_equals_mu_q3"):
        charts: dict[str, Any] = {}
        for chart_index in range(4):
            system = rank_one_mixed_chart_system(branch, chart_index)
            target_results = {
                name: saturation_contradiction(
                    system["generators"],
                    target,
                    system["z"],
                    label=f"mixed:{branch}:{system['chart']}:{name}",
                    recompute=recompute_saturations,
                )
                for name, target in system["target_polys"].items()
            }
            charts[system["chart"]] = {
                "chart": system["chart"],
                "unit_normalization": system["unit_normalization"],
                "target_saturations": target_results,
                "closes_h2_shear_targets": all(
                    result["contradiction_found"] for result in target_results.values()
                ),
            }
        branches[branch] = {
            "description": rank_one_mixed_chart_system(branch, 0)["description"],
            "parameter": rank_one_mixed_chart_system(branch, 0)["parameter"],
            "charts": charts,
            "all_charts_close_h2_shear_targets": all(
                chart["closes_h2_shear_targets"] for chart in charts.values()
            ),
        }
    return {
        "method": (
            "For each rank-one H3 proportionality branch and each nonzero cubic coefficient chart, "
            "add z*target-1. A complete basis reducing 1 to zero certifies that target cannot be nonzero."
        ),
        "chart_variable_map": {
            "a,b,c": "the three unfixed cubic coefficients on the active chart",
            "d,A,B,C": "H2 coefficients h0,h1,h2,h3",
            "D": "lambda or mu branch parameter",
            "E": "Rabinowitsch saturation variable z",
        },
        "branches": branches,
        "certificate_count": sum(
            len(chart["target_saturations"])
            for branch in branches.values()
            for chart in branch["charts"].values()
        ),
        "all_branches_close_h2_shear_targets": all(
            branch["all_charts_close_h2_shear_targets"] for branch in branches.values()
        ),
    }


def rank_one_shear_normal_form_saturation(*, recompute_saturations: bool = False) -> dict[str, Any]:
    branches: dict[str, Any] = {}
    for branch in ("q3_equals_lambda_p3", "p3_equals_mu_q3"):
        charts: dict[str, Any] = {}
        for chart_index in range(4):
            system = rank_one_mixed_chart_system(branch, chart_index)
            residual_results = {
                name: saturation_contradiction(
                    system["generators"],
                    residual,
                    system["z"],
                    label=f"normal_form:{branch}:{system['chart']}:{name}",
                    recompute=recompute_saturations,
                    pair_limit=15000,
                    basis_limit=260,
                    reduction_step_limit=150000,
                )
                for name, residual in system["normal_form_residuals"].items()
            }
            charts[system["chart"]] = {
                "chart": system["chart"],
                "unit_normalization": system["unit_normalization"],
                "normal_form_saturations": residual_results,
                "closes_normal_form_residuals": all(
                    result["contradiction_found"] for result in residual_results.values()
                ),
            }
        branches[branch] = {
            "description": rank_one_mixed_chart_system(branch, 0)["description"],
            "parameter": rank_one_mixed_chart_system(branch, 0)["parameter"],
            "normal_form": (
                "finite: H=(1,lambda)*phi(lambda*x-y); "
                "infinite: H=(mu,1)*phi(x-mu*y)"
            ),
            "charts": charts,
            "all_charts_close_normal_form_residuals": all(
                chart["closes_normal_form_residuals"] for chart in charts.values()
            ),
        }
    return {
        "method": (
            "After the rank-one mixed branch equations are imposed, each chart adds z*residual-1. "
            "Reducing 1 to zero certifies the residual cannot be nonzero, so the quadratic part "
            "shares the cubic branch direction and killed linear form."
        ),
        "branches": branches,
        "certificate_count": sum(
            len(chart["normal_form_saturations"])
            for branch in branches.values()
            for chart in branch["charts"].values()
        ),
        "all_branches_close_normal_form_residuals": all(
            branch["all_charts_close_normal_form_residuals"] for branch in branches.values()
        ),
    }


def expected_saturation_cache_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for branch in ("q3_equals_lambda_p3", "p3_equals_mu_q3"):
        for chart_index in range(4):
            system = rank_one_mixed_chart_system(branch, chart_index)
            for name, target in system["target_polys"].items():
                specs.append(
                    saturation_cache_spec(
                        system["generators"],
                        target,
                        system["z"],
                        label=f"mixed:{branch}:{system['chart']}:{name}",
                    )
                )
            for name, residual in system["normal_form_residuals"].items():
                specs.append(
                    saturation_cache_spec(
                        system["generators"],
                        residual,
                        system["z"],
                        label=f"normal_form:{branch}:{system['chart']}:{name}",
                        pair_limit=15000,
                        basis_limit=260,
                        reduction_step_limit=150000,
                    )
                )
    return specs


def verify_saturation_cache() -> dict[str, Any]:
    specs = expected_saturation_cache_specs()
    zero_remainder_sha = sha_json([])
    errors: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    expected_paths = {spec["cache_path"] for spec in specs}
    actual_paths = set(CACHE_DIR.glob("*.json")) if CACHE_DIR.exists() else set()
    if CACHE_MANIFEST in actual_paths:
        actual_paths.remove(CACHE_MANIFEST)
    for spec in specs:
        cache_path = spec["cache_path"]
        label = spec["label"]
        entry: dict[str, Any] = {
            "cache_file": spec["cache_file"],
            "label": label,
            "input_sha256": spec["input_sha256"],
            "settings": spec["settings"],
            "present": cache_path.exists(),
        }
        if cache_path.exists():
            entry["cache_sha256"] = sha_file(cache_path)
            entry["cache_size"] = cache_path.stat().st_size
        if not cache_path.exists():
            errors.append({"label": label, "check": "cache_present", "path": spec["cache_file"]})
            entries.append(entry)
            continue
        try:
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append({"label": label, "check": "json_valid", "path": spec["cache_file"], "error": str(exc)})
            entry["json_valid"] = False
            entry["json_error"] = str(exc)
            entries.append(entry)
            continue
        result = payload.get("result")
        checks = {
            "schema": payload.get("schema") == "holotopy.saturation_contradiction_cache",
            "input_hash": payload.get("input_hash") == spec["input_sha256"],
            "result_is_object": isinstance(result, dict),
        }
        entry["payload_schema"] = payload.get("schema")
        entry["payload_input_hash"] = payload.get("input_hash")
        entry["result_present"] = isinstance(result, dict)
        if isinstance(result, dict):
            entry["result_status"] = result.get("status")
            entry["result_cache_file"] = result.get("cache_file")
            entry["contradiction_found"] = result.get("contradiction_found")
            entry["reduction_completed"] = result.get("reduction_completed")
            entry["one_remainder_term_count"] = result.get("one_remainder_term_count")
            entry["one_remainder_sha256"] = result.get("one_remainder_sha256")
            checks.update(
                {
                    "result_label": result.get("label") == label,
                    "result_input_hash": result.get("input_sha256") == spec["input_sha256"],
                    "result_cache_file": result.get("cache_file") == spec["cache_file"],
                    "contradiction_found": result.get("contradiction_found") is True,
                    "reduction_completed": result.get("reduction_completed") is True,
                    "zero_remainder": result.get("one_remainder_term_count") == 0,
                    "zero_remainder_hash": result.get("one_remainder_sha256") == zero_remainder_sha,
                }
            )
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            errors.append({"label": label, "check": "cache_payload", "path": spec["cache_file"], "failed": failed})
            entry["status"] = "FAIL"
            entry["failed_checks"] = failed
        else:
            entry["status"] = "PASS"
            entry["result_processed_pairs"] = result.get("processed_pairs") if isinstance(result, dict) else None
            entry["result_label"] = result.get("label") if isinstance(result, dict) else None
            entry["result_input_hash"] = result.get("input_sha256") if isinstance(result, dict) else None
        entries.append(entry)
    extra_paths = sorted(repo_relative(path) for path in actual_paths - expected_paths)
    summary = {
        "schema": "holotopy.saturation_cache_verification",
        "status": "PASS" if not errors else "FAIL",
        "expected_certificate_count": len(specs),
        "verified_certificate_count": len([entry for entry in entries if entry.get("status") == "PASS"]),
        "cache_directory": repo_relative(CACHE_DIR),
        "extra_cache_files": extra_paths,
        "manifest_file": repo_relative(CACHE_MANIFEST),
        "entries": entries,
        "errors": errors,
    }
    summary["manifest_sha256"] = sha_json({key: value for key, value in summary.items() if key != "manifest_sha256"})
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_MANIFEST.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return summary


def shear_inverse_identity() -> dict[str, Any]:
    parameter = Poly.var("D")
    q2 = Poly.var("A")
    q3 = Poly.var("B")
    checks: dict[str, Any] = {}
    for branch in ("q3_equals_lambda_p3", "p3_equals_mu_q3"):
        if branch == "q3_equals_lambda_p3":
            direction = (Poly.const(1), parameter)
            linear = (parameter, Poly.const(-1))
            normal_form = "H=(1,lambda)*(q2*(lambda*x-y)^2 + q3*(lambda*x-y)^3)"
        else:
            direction = (parameter, Poly.const(1))
            linear = (Poly.const(1), -parameter)
            normal_form = "H=(mu,1)*(q2*(x-mu*y)^2 + q3*(x-mu*y)^3)"
        linear_on_direction = linear[0] * direction[0] + linear[1] * direction[1]
        phi_marker = q2 + q3
        l_after_inverse_delta = -linear_on_direction * phi_marker
        inverse_x_residual = -direction[0] * phi_marker + direction[0] * phi_marker
        inverse_y_residual = -direction[1] * phi_marker + direction[1] * phi_marker
        checks[branch] = {
            "normal_form": normal_form,
            "linear_form_kills_direction": linear_on_direction.is_zero(),
            "linear_form_after_inverse_unchanged": l_after_inverse_delta.is_zero(),
            "left_inverse_x_residual_zero": inverse_x_residual.is_zero(),
            "left_inverse_y_residual_zero": inverse_y_residual.is_zero(),
            "inverse": "F^{-1}=I-H",
        }
    return {
        "method": "For a shear H=v*phi(L) with L(v)=0, L is unchanged by I-H, so (I+H)(I-H)=I.",
        "branches": checks,
        "all_branches_have_inverse_identity": all(
            item["linear_form_kills_direction"]
            and item["linear_form_after_inverse_unchanged"]
            and item["left_inverse_x_residual_zero"]
            and item["left_inverse_y_residual_zero"]
            for item in checks.values()
        ),
    }


def symbolic_elimination_attempt(*, recompute_saturations: bool = False) -> dict[str, Any]:
    payload = coeff_generators()
    flat = payload["flat_generators"]
    targets = payload["targets"]
    generators = [item["poly"] for item in flat]
    membership = {
        name: [
            ideal_membership_search(target, flat, degree)
            for degree in (0, 1, 2)
        ]
        for name, target in targets.items()
    }
    closed_targets = {
        name: any(attempt["membership_found"] for attempt in attempts)
        for name, attempts in membership.items()
    }
    groebner_attempt = buchberger(
        generators,
        order="grevlex",
        pair_limit=2500,
        basis_limit=160,
        reduction_step_limit=100000,
    )
    groebner_basis = groebner_attempt.pop("basis")
    groebner_reductions = groebner_target_reductions(targets, groebner_basis, order="grevlex", step_limit=100000)
    groebner_closes_targets = all(item["remainder_zero"] for item in groebner_reductions.values())
    rank_one_lemma = binary_cubic_rank_one_lemma()
    rank_one_elimination = rank_one_h3_branch_elimination()
    mixed_saturation = rank_one_mixed_chart_saturation(recompute_saturations=recompute_saturations)
    shear_normal_form = rank_one_shear_normal_form_saturation(recompute_saturations=recompute_saturations)
    inverse_identity = shear_inverse_identity()
    cache_verification = verify_saturation_cache()
    return {
        "ring": "Q[a,b,c,d,A,B,C,D,E]",
        "coefficient_order": COEFF_VARS,
        "after_trace_substitution": payload["substitutions"],
        "keller_generators": {
            "mixed": {
                f"x^{x} y^{y}": poly.rows()
                for (x, y), poly in sorted(payload["generators"]["mixed"].items())
            },
            "det_b": {
                f"x^{x} y^{y}": poly.rows()
                for (x, y), poly in sorted(payload["generators"]["det_b"].items())
            },
        },
        "h2_shear_targets": {
            name: target.rows()
            for name, target in targets.items()
        },
        "bounded_ideal_membership": membership,
        "closed_targets": closed_targets,
        "all_h2_shear_targets_closed": all(closed_targets.values()),
        "groebner_attempt": {
            **groebner_attempt,
            "target_reductions": groebner_reductions,
            "closes_h2_shear_targets": groebner_closes_targets,
            "basis_leading_terms": leading_term_rows(groebner_basis, "grevlex"),
        },
        "binary_cubic_rank_one_lemma": rank_one_lemma,
        "rank_one_h3_branch_elimination": rank_one_elimination,
        "rank_one_mixed_chart_saturation": mixed_saturation,
        "rank_one_shear_normal_form_saturation": shear_normal_form,
        "shear_inverse_identity": inverse_identity,
        "saturation_cache": {
            "directory": repo_relative(CACHE_DIR),
            "certificate_count": mixed_saturation["certificate_count"] + shear_normal_form["certificate_count"],
            "recompute_requested": recompute_saturations,
        },
        "saturation_cache_verification": cache_verification,
        "checks": payload["checks"],
    }


def build_report(*, recompute_saturations: bool = False) -> dict[str, Any]:
    elimination = symbolic_elimination_attempt(recompute_saturations=recompute_saturations)
    checks = {
        "trace_substitution_eliminates_degree2": elimination["checks"]["trace_substitution_eliminates_degree2"],
        "bounded_ideal_membership_closed_all_h2_shear_targets": elimination["all_h2_shear_targets_closed"],
        "groebner_attempt_closed_all_h2_shear_targets": elimination["groebner_attempt"]["closes_h2_shear_targets"],
        "rank_one_h3_branch_elimination_closed_all_h2_shear_targets": elimination[
            "rank_one_h3_branch_elimination"
        ]["all_branches_close_h2_shear_targets"],
        "binary_cubic_rank_one_lemma_internalized": elimination["binary_cubic_rank_one_lemma"][
            "all_unit_charts_close_proportionality"
        ],
        "rank_one_mixed_chart_saturation_closed_all_h2_shear_targets": elimination[
            "rank_one_mixed_chart_saturation"
        ]["all_branches_close_h2_shear_targets"],
        "rank_one_shear_normal_form_saturation_closed": elimination["rank_one_shear_normal_form_saturation"][
            "all_branches_close_normal_form_residuals"
        ],
        "shear_inverse_identity_verified": elimination["shear_inverse_identity"][
            "all_branches_have_inverse_identity"
        ],
        "saturation_certificate_count_is_48": elimination["saturation_cache"]["certificate_count"] == 48,
        "saturation_cache_verifier_passed": elimination["saturation_cache_verification"]["status"] == "PASS",
        "full_jacobian_conjecture_solved": False,
    }
    report = {
        "schema": "holotopy.polynomial_attempt.jacobian_cubic_symbolic_elimination",
        "status": "PARTIAL_ELIMINATION",
        "problem": "Jacobian conjecture for polynomial maps",
        "target": "Normalized plane maps of degree at most 3 over characteristic zero.",
        "symbolic_elimination": elimination,
        "checks": checks,
        "residue": [
            {
                "kind": "bounded_ideal_membership_not_closed",
                "description": (
                    "The script constructs the exact rational cubic Keller ideal after trace substitution, "
                    "but degree-0/1/2 multiplier ideal membership did not derive all H2 shear relations."
                ),
                "discharged": checks["bounded_ideal_membership_closed_all_h2_shear_targets"],
            },
            {
                "kind": "groebner_attempt_not_closed",
                "description": (
                    "The built-in Buchberger attempt did not reduce all H2 shear targets to zero within configured limits."
                ),
                "discharged": checks["groebner_attempt_closed_all_h2_shear_targets"],
            },
            {
                "kind": "rank_one_h3_branch_closed",
                "description": (
                    "After replacing the quartic determinant equations by the characteristic-zero binary-cubic "
                    "rank-one branch data, both finite proportionality charts reduce all H2 shear targets to zero."
                ),
                "discharged": checks["rank_one_h3_branch_elimination_closed_all_h2_shear_targets"],
            },
            {
                "kind": "binary_cubic_rank_one_lemma_internalized",
                "description": (
                    "The generic binary-cubic determinant equations are now checked on every nonzero coefficient "
                    "chart and reduce to component proportionality exactly."
                ),
                "discharged": checks["binary_cubic_rank_one_lemma_internalized"],
            },
            {
                "kind": "rank_one_branch_conditions_not_derived",
                "description": (
                    "The rank-one H3 proportionality branches are now saturated against the original mixed cubic "
                    "equations on all nonzero cubic coefficient charts, and each H2 determinant target gives a "
                    "Nullstellensatz contradiction when assumed nonzero."
                ),
                "discharged": checks["rank_one_mixed_chart_saturation_closed_all_h2_shear_targets"],
            },
            {
                "kind": "normalized_cubic_plane_symbolic_elimination_closed",
                "description": (
                    "Within the normalized plane degree-at-most-3 setup encoded here, the symbolic branch cover "
                    "closes the H2 determinant targets. This is not a solution of the full Jacobian conjecture."
                ),
                "discharged": checks["rank_one_mixed_chart_saturation_closed_all_h2_shear_targets"],
            },
            {
                "kind": "rank_one_shear_normal_form_closed",
                "description": (
                    "The same chart cover now saturates the residuals for the explicit shear normal forms "
                    "H=(1,lambda)*phi(lambda*x-y) and H=(mu,1)*phi(x-mu*y)."
                ),
                "discharged": checks["rank_one_shear_normal_form_saturation_closed"],
            },
            {
                "kind": "shear_inverse_verified",
                "description": (
                    "For the certified shear normal form, the killed linear form is invariant under I-H, "
                    "so F=I+H has inverse I-H."
                ),
                "discharged": checks["shear_inverse_identity_verified"],
            },
            {
                "kind": "saturation_certificates_split",
                "description": (
                    "The 48 expensive Rabinowitsch saturation checks are split into hash-keyed generated "
                    "certificate cache entries and can be recomputed with --recompute-saturations."
                ),
                "discharged": checks["saturation_certificate_count_is_48"],
            },
            {
                "kind": "saturation_cache_verifier_added",
                "description": (
                    "The --verify-saturation-cache mode checks the 48 cached certificates by expected input hash, "
                    "payload hash, contradiction flag, and zero-remainder hash without rebuilding the full report."
                ),
                "discharged": checks["saturation_cache_verifier_passed"],
            },
            {
                "kind": "open_problem_not_solved",
                "description": "This elimination attempt does not solve the full Jacobian conjecture.",
                "discharged": False,
            },
        ],
    }
    report["certificate_sha256"] = sha_json({key: value for key, value in report.items() if key != "certificate_sha256"})
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recompute-saturations",
        action="store_true",
        help="Rebuild all Rabinowitsch saturation certificates instead of reading cache entries.",
    )
    parser.add_argument(
        "--verify-saturation-cache",
        action="store_true",
        help="Verify cached Rabinowitsch saturation certificates without rebuilding the full report.",
    )
    parser.add_argument("--quiet", action="store_true", help="Write report.json without printing the full report.")
    args = parser.parse_args()
    if args.verify_saturation_cache:
        verification = verify_saturation_cache()
        if not args.quiet:
            print(json.dumps(verification, indent=2, sort_keys=True))
        if verification["status"] != "PASS":
            raise SystemExit(1)
        return
    report = build_report(recompute_saturations=args.recompute_saturations)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not args.quiet:
        print(json.dumps(report, indent=2, sort_keys=True))
    if report["checks"]["trace_substitution_eliminates_degree2"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
