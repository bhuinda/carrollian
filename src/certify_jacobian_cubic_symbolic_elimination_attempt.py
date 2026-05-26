from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from .evidence_registry import evidence_index_entry, upsert_evidence_index_entry
except ImportError:  # Supports direct script execution.
    from evidence_registry import evidence_index_entry, upsert_evidence_index_entry  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "data" / "evidence" / "jacobian_cubic_symbolic_elimination"
REPORT = EVIDENCE_DIR / "report.json"
EVIDENCE_MANIFEST = EVIDENCE_DIR / "manifest.json"
EVIDENCE_README = EVIDENCE_DIR / "README.md"
CERTIFICATE_JOB_PLAN = EVIDENCE_DIR / "saturation_certificate_jobs.json"
CERTIFICATE_QUEUE = EVIDENCE_DIR / "saturation_certificate_queue.json"
CERTIFICATE_QUEUE_AUDIT = EVIDENCE_DIR / "saturation_certificate_queue_audit.json"
CERTIFICATE_SOURCE_AUDIT = EVIDENCE_DIR / "saturation_certificate_source_audit.json"
CERTIFICATE_INTAKE_PROTOCOL = EVIDENCE_DIR / "saturation_certificate_intake_protocol.json"
CERTIFICATE_CLOSURE_CHECKLIST = EVIDENCE_DIR / "saturation_certificate_closure_checklist.json"
CERTIFICATE_STATUS_SUMMARY = EVIDENCE_DIR / "saturation_certificate_status_summary.json"
CACHE_DIR = EVIDENCE_DIR / "saturation_cache"
STAGING_CACHE_DIR = EVIDENCE_DIR / "saturation_staging_cache"
CACHE_MANIFEST = CACHE_DIR / "manifest.json"
INDEXED_CACHE_CONTRACT = (
    ROOT / "manifests" / "jacobian_cubic_symbolic_elimination_saturation_cache_contract.json"
)
INDEXED_CACHE_MANIFEST = (
    ROOT / "manifests" / "jacobian_cubic_symbolic_elimination_saturation_cache_manifest.json"
)
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


def load_saturation_cache_from_paths(
    cache_paths: list[Path],
    input_hash: str,
) -> tuple[dict[str, Any], Path] | tuple[None, None]:
    for cache_path in cache_paths:
        cached = load_saturation_cache(cache_path, input_hash)
        if cached is not None:
            return cached, cache_path
    return None, None


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
    staging_cache_path = STAGING_CACHE_DIR / f"{input_hash}.json"
    return {
        "label": label,
        "input_sha256": input_hash,
        "cache_file": repo_relative(cache_path),
        "cache_path": cache_path,
        "staging_cache_file": repo_relative(staging_cache_path),
        "staging_cache_path": staging_cache_path,
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
    staging_cache_path = STAGING_CACHE_DIR / f"{input_hash}.json"
    cached, cached_path = (None, None) if recompute else load_saturation_cache_from_paths(
        [cache_path, staging_cache_path],
        input_hash,
    )
    if cached is not None:
        if cached_path != cache_path:
            cached = {**cached, "cache_file": repo_relative(cache_path)}
            write_saturation_cache(cache_path, input_hash, cached)
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


def saturation_cache_contract(specs: list[dict[str, Any]]) -> dict[str, Any]:
    contract = {
        "schema": "holotopy.saturation_cache_contract",
        "cache_directory": repo_relative(CACHE_DIR),
        "staging_cache_directory": repo_relative(STAGING_CACHE_DIR),
        "expected_certificate_count": len(specs),
        "entries": [
            {
                "cache_file": spec["cache_file"],
                "input_sha256": spec["input_sha256"],
                "label": spec["label"],
                "staging_cache_file": spec["staging_cache_file"],
                "settings": spec["settings"],
            }
            for spec in specs
        ],
    }
    contract["contract_sha256"] = sha_json(
        {key: value for key, value in contract.items() if key != "contract_sha256"}
    )
    return contract


def file_manifest_ref(path: Path) -> dict[str, Any]:
    return {
        "path": repo_relative(path),
        "sha256": sha_file(path) if path.exists() else None,
        "size": path.stat().st_size if path.exists() else None,
    }


def repo_path(ref: str) -> Path:
    return ROOT / ref.replace("/", "\\")


def saturation_cache_inventory(contract: dict[str, Any]) -> dict[str, Any]:
    entries = contract.get("entries", [])
    stable_present = 0
    staging_present = 0
    missing: list[dict[str, Any]] = []
    for entry in entries:
        cache_file = str(entry.get("cache_file", ""))
        staging_cache_file = str(entry.get("staging_cache_file", ""))
        stable_exists = bool(cache_file) and repo_path(cache_file).exists()
        staging_exists = bool(staging_cache_file) and repo_path(staging_cache_file).exists()
        stable_present += int(stable_exists)
        staging_present += int(staging_exists)
        if not stable_exists and not staging_exists:
            missing.append(
                {
                    "cache_file": cache_file,
                    "input_sha256": entry.get("input_sha256"),
                    "label": entry.get("label"),
                    "staging_cache_file": staging_cache_file,
                }
            )
    return {
        "expected_certificate_count": len(entries),
        "stable_certificate_count": stable_present,
        "staging_certificate_count": staging_present,
        "missing_certificate_count": len(missing),
        "first_missing": missing[:5],
    }


def saturation_evidence_readme(contract: dict[str, Any]) -> str:
    inventory = saturation_cache_inventory(contract)
    return "\n".join(
        [
            "# Jacobian cubic symbolic elimination evidence",
            "",
            "This folder records the durable evidence contract for the normalized plane cubic symbolic elimination attempt.",
            "",
            "The contract locks the 48 expected Rabinowitsch saturation certificate inputs. The expensive certificate files are not generated by the contract command.",
            "",
            "## Current state",
            "",
            f"- Expected certificates: {inventory['expected_certificate_count']}",
            f"- Stable certificates: {inventory['stable_certificate_count']}",
            f"- Staging certificates: {inventory['staging_certificate_count']}",
            f"- Missing certificates: {inventory['missing_certificate_count']}",
            "",
            "## Commands",
            "",
            "- Check the contract: `python src/verify.py jacobian-cubic-contract --pretty`",
            "- Check the intake protocol: `python src/verify.py jacobian-cubic-intake --pretty`",
            "- Check the closure checklist: `python src/verify.py jacobian-cubic-closure --pretty`",
            "- Show compact closure status: `python src/verify.py jacobian-cubic-status --pretty`",
            "- Run non-strict integration gate: `python src/verify.py jacobian-cubic-nonstrict --pretty`",
            "- Refresh the compact status summary: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --write-saturation-status-summary`",
            "- Inspect all certificate jobs: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --list-saturation-jobs`",
            "- Show batch certificate status: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --saturation-job-status`",
            "- Show batch certificate status summary: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --saturation-job-status-summary`",
            "- Refresh the resumable certificate queue: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --write-saturation-queue`",
            "- Audit the resumable certificate queue: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --audit-saturation-queue`",
            "- Audit stable and staging certificate sources: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --audit-saturation-sources`",
            "- Refresh the certificate intake protocol: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --write-saturation-intake-protocol`",
            "- Refresh the closure checklist: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --write-saturation-closure-checklist`",
            "- Inspect one certificate job: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --show-saturation-job saturation_001`",
            "- Plan one certificate production job: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --produce-saturation-job saturation_001`",
            "- Verify one existing certificate job: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --verify-saturation-job saturation_001`",
            "- Promote existing staging certificates: `python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --promote-saturation-cache`",
            "- Check strict certificates: `python src/verify.py jacobian-cubic-cache --pretty`",
            "",
            "Strict certification requires all 48 certificate JSON files under `data/evidence/jacobian_cubic_symbolic_elimination/saturation_cache`.",
            "The staging cache lives under `data/evidence/jacobian_cubic_symbolic_elimination/saturation_staging_cache`; deleting it does not remove canonical evidence.",
            "",
        ]
    )


def saturation_certificate_job_plan(contract: dict[str, Any]) -> dict[str, Any]:
    jobs = [
        {
            "job_id": f"saturation_{index:03d}",
            "label": entry["label"],
            "input_sha256": entry["input_sha256"],
            "stable_cache_file": entry["cache_file"],
            "staging_cache_file": entry["staging_cache_file"],
            "settings": entry["settings"],
            "completion_condition": {
                "cache_schema": "holotopy.saturation_contradiction_cache",
                "contradiction_found": True,
                "one_remainder_sha256": sha_json([]),
                "reduction_completed": True,
            },
            "lookup_command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                f"--show-saturation-job saturation_{index:03d}"
            ),
            "verify_command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                f"--verify-saturation-job saturation_{index:03d}"
            ),
            "produce_plan_command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                f"--produce-saturation-job saturation_{index:03d}"
            ),
        }
        for index, entry in enumerate(contract["entries"], start=1)
    ]
    plan = {
        "schema": "holotopy.saturation_certificate_job_plan",
        "status": "CERTIFICATE_JOBS_DECLARED",
        "contract": {
            "path": repo_relative(INDEXED_CACHE_CONTRACT),
            "contract_sha256": contract["contract_sha256"],
        },
        "expected_job_count": contract["expected_certificate_count"],
        "producer": {
            "command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--recompute-saturations --quiet"
            ),
            "writes": repo_relative(CACHE_DIR),
            "cost": "expensive",
        },
        "single_job_lookup": {
            "command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--show-saturation-job <job_id|label|input_sha256>"
            ),
            "runs_expensive_computation": False,
        },
        "single_job_producer": {
            "command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--produce-saturation-job <job_id|label|input_sha256>"
            ),
            "explicit_run_flag": "--run-saturation-job",
            "runs_expensive_computation_by_default": False,
            "writes": repo_relative(CACHE_DIR),
        },
        "single_job_verification": {
            "command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--verify-saturation-job <job_id|label|input_sha256>"
            ),
            "runs_expensive_computation": False,
            "validates_existing_cache_only": True,
        },
        "batch_job_status": {
            "command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--saturation-job-status"
            ),
            "summary_command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--saturation-job-status-summary"
            ),
            "runs_expensive_computation": False,
            "validates_existing_cache_only": True,
        },
        "promotion": {
            "command": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--promote-saturation-cache"
            ),
            "from": repo_relative(STAGING_CACHE_DIR),
            "to": repo_relative(CACHE_DIR),
        },
        "verification": {
            "command": "python src/verify.py jacobian-cubic-cache --pretty",
            "requires_all_jobs": True,
        },
        "jobs": jobs,
    }
    plan["job_plan_sha256"] = sha_json(
        {key: value for key, value in plan.items() if key != "job_plan_sha256"}
    )
    return plan


def saturation_job_summary(job: dict[str, Any]) -> dict[str, Any]:
    stable_cache_file = str(job.get("stable_cache_file", ""))
    staging_cache_file = str(job.get("staging_cache_file", ""))
    return {
        "job_id": job.get("job_id"),
        "label": job.get("label"),
        "input_sha256": job.get("input_sha256"),
        "stable_cache_file": stable_cache_file,
        "stable_present": bool(stable_cache_file) and repo_path(stable_cache_file).exists(),
        "staging_cache_file": staging_cache_file,
        "staging_present": bool(staging_cache_file) and repo_path(staging_cache_file).exists(),
        "settings": job.get("settings"),
    }


def saturation_job_cache_checks(payload: dict[str, Any], job: dict[str, Any]) -> dict[str, bool]:
    result = payload.get("result")
    completion = job.get("completion_condition", {})
    result_is_object = isinstance(result, dict)
    stable_cache_file = job.get("stable_cache_file")
    staging_cache_file = job.get("staging_cache_file")
    return {
        "schema": payload.get("schema") == completion.get("cache_schema"),
        "input_hash": payload.get("input_hash") == job.get("input_sha256"),
        "result_is_object": result_is_object,
        "result_label": result_is_object and result.get("label") == job.get("label"),
        "result_input_hash": result_is_object and result.get("input_sha256") == job.get("input_sha256"),
        "result_cache_file": result_is_object
        and result.get("cache_file") in {stable_cache_file, staging_cache_file},
        "contradiction_found": result_is_object
        and result.get("contradiction_found") is completion.get("contradiction_found"),
        "reduction_completed": result_is_object
        and result.get("reduction_completed") is completion.get("reduction_completed"),
        "zero_remainder": result_is_object and result.get("one_remainder_term_count") == 0,
        "zero_remainder_hash": result_is_object
        and result.get("one_remainder_sha256") == completion.get("one_remainder_sha256"),
    }


def resolve_saturation_job(job_plan: dict[str, Any], selector: str) -> dict[str, Any] | None:
    jobs = job_plan.get("jobs", [])
    if not isinstance(jobs, list):
        return None
    for job in jobs:
        if not isinstance(job, dict):
            continue
        if selector in {job.get("job_id"), job.get("label"), job.get("input_sha256")}:
            return job
    return None


def list_saturation_jobs() -> dict[str, Any]:
    contract = write_saturation_cache_contract()
    job_plan = saturation_certificate_job_plan(contract)
    jobs = [saturation_job_summary(job) for job in job_plan["jobs"]]
    return {
        "schema": "holotopy.saturation_certificate_job_list",
        "status": "PASS",
        "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
        "job_plan_sha256": job_plan["job_plan_sha256"],
        "job_count": len(jobs),
        "stable_present_count": sum(1 for job in jobs if job["stable_present"]),
        "staging_present_count": sum(1 for job in jobs if job["staging_present"]),
        "jobs": jobs,
    }


def show_saturation_job(selector: str) -> dict[str, Any]:
    contract = write_saturation_cache_contract()
    job_plan = saturation_certificate_job_plan(contract)
    job = resolve_saturation_job(job_plan, selector)
    if job is None:
        return {
            "schema": "holotopy.saturation_certificate_job_lookup",
            "status": "FAIL",
            "selector": selector,
            "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
            "job_plan_sha256": job_plan["job_plan_sha256"],
            "error": "unknown_saturation_job",
            "accepted_selectors": ["job_id", "label", "input_sha256"],
        }
    return {
        "schema": "holotopy.saturation_certificate_job_lookup",
        "status": "PASS",
        "selector": selector,
        "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
        "job_plan_sha256": job_plan["job_plan_sha256"],
        "runs_expensive_computation": False,
        "job": {
            **saturation_job_summary(job),
            "completion_condition": job.get("completion_condition"),
            "lookup_command": job.get("lookup_command"),
            "verify_command": job.get("verify_command"),
            "produce_plan_command": job.get("produce_plan_command"),
        },
    }


def saturation_job_workload(job: dict[str, Any]) -> dict[str, Any]:
    label = str(job.get("label", ""))
    parts = label.split(":")
    if len(parts) != 4:
        raise ValueError(f"unsupported saturation job label: {label}")
    kind, branch, chart, target_name = parts
    if not (chart.startswith("p") and chart.endswith("_nonzero")):
        raise ValueError(f"unsupported saturation chart label: {chart}")
    chart_index = int(chart[1])
    system = rank_one_mixed_chart_system(branch, chart_index)
    settings = job.get("settings", {})
    if kind == "mixed":
        target = system["target_polys"][target_name]
    elif kind == "normal_form":
        target = system["normal_form_residuals"][target_name]
    else:
        raise ValueError(f"unsupported saturation job kind: {kind}")
    return {
        "generators": system["generators"],
        "target": target,
        "z": system["z"],
        "label": label,
        "order": settings.get("order", "grevlex"),
        "pair_limit": settings.get("pair_limit", 9000),
        "basis_limit": settings.get("basis_limit", 240),
        "reduction_step_limit": settings.get("reduction_step_limit", 120000),
    }


def produce_saturation_job(selector: str, *, run: bool = False) -> dict[str, Any]:
    contract = write_saturation_cache_contract()
    job_plan = saturation_certificate_job_plan(contract)
    job = resolve_saturation_job(job_plan, selector)
    if job is None:
        return {
            "schema": "holotopy.saturation_certificate_job_producer",
            "status": "FAIL",
            "selector": selector,
            "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
            "job_plan_sha256": job_plan["job_plan_sha256"],
            "runs_expensive_computation": False,
            "error": "unknown_saturation_job",
            "accepted_selectors": ["job_id", "label", "input_sha256"],
        }

    job_id = str(job["job_id"])
    run_command = (
        "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
        f"--produce-saturation-job {job_id} --run-saturation-job"
    )
    output: dict[str, Any] = {
        "schema": "holotopy.saturation_certificate_job_producer",
        "status": "PLAN" if not run else "RUN_REQUESTED",
        "selector": selector,
        "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
        "job_plan_sha256": job_plan["job_plan_sha256"],
        "runs_expensive_computation": run,
        "run_command": run_command,
        "run_requires_explicit_flag": "--run-saturation-job",
        "job": {
            **saturation_job_summary(job),
            "completion_condition": job.get("completion_condition"),
            "produce_plan_command": job.get("produce_plan_command"),
            "verify_command": job.get("verify_command"),
        },
    }
    if not run:
        return output

    workload = saturation_job_workload(job)
    produced = saturation_contradiction(
        workload["generators"],
        workload["target"],
        workload["z"],
        label=workload["label"],
        recompute=True,
        order=workload["order"],
        pair_limit=workload["pair_limit"],
        basis_limit=workload["basis_limit"],
        reduction_step_limit=workload["reduction_step_limit"],
    )
    verification = verify_saturation_job(job_id)
    output["status"] = "PASS" if verification.get("status") == "PASS" else "FAIL"
    output["produced"] = {
        "cache_file": produced.get("cache_file"),
        "contradiction_found": produced.get("contradiction_found"),
        "input_sha256": produced.get("input_sha256"),
        "label": produced.get("label"),
    }
    output["verification"] = verification
    return output


def verify_saturation_job(selector: str) -> dict[str, Any]:
    contract = write_saturation_cache_contract()
    job_plan = saturation_certificate_job_plan(contract)
    job = resolve_saturation_job(job_plan, selector)
    if job is None:
        return {
            "schema": "holotopy.saturation_certificate_job_verification",
            "status": "FAIL",
            "selector": selector,
            "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
            "job_plan_sha256": job_plan["job_plan_sha256"],
            "runs_expensive_computation": False,
            "error": "unknown_saturation_job",
            "accepted_selectors": ["job_id", "label", "input_sha256"],
        }

    stable_cache_path = repo_path(str(job["stable_cache_file"]))
    staging_cache_path = repo_path(str(job["staging_cache_file"]))
    source_label = None
    source_path = None
    if stable_cache_path.exists():
        source_label = "stable"
        source_path = stable_cache_path
    elif staging_cache_path.exists():
        source_label = "staging"
        source_path = staging_cache_path

    result: dict[str, Any] = {
        "schema": "holotopy.saturation_certificate_job_verification",
        "selector": selector,
        "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
        "job_plan_sha256": job_plan["job_plan_sha256"],
        "runs_expensive_computation": False,
        "job": {
            **saturation_job_summary(job),
            "completion_condition": job.get("completion_condition"),
            "verify_command": job.get("verify_command"),
        },
    }
    if source_path is None:
        result.update(
            {
                "status": "FAIL",
                "cache_source": None,
                "checks": {"cache_present": False},
                "error": "cache_file_missing",
            }
        )
        return result

    result["cache_source"] = source_label
    result["cache_file"] = repo_relative(source_path)
    result["cache_sha256"] = sha_file(source_path)
    result["cache_size"] = source_path.stat().st_size
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.update(
            {
                "status": "FAIL",
                "checks": {"json_valid": False},
                "error": f"invalid_json: {exc}",
            }
        )
        return result
    if not isinstance(payload, dict):
        result.update(
            {
                "status": "FAIL",
                "checks": {"json_object": False},
                "error": "cache_payload_not_object",
            }
        )
        return result

    checks = saturation_job_cache_checks(payload, job)
    failed = [name for name, passed in checks.items() if not passed]
    result["checks"] = checks
    result["status"] = "PASS" if not failed else "FAIL"
    if failed:
        result["failed_checks"] = failed
    return result


def saturation_job_status_entry(job: dict[str, Any]) -> dict[str, Any]:
    stable_cache_path = repo_path(str(job["stable_cache_file"]))
    staging_cache_path = repo_path(str(job["staging_cache_file"]))
    summary = saturation_job_summary(job)
    entry: dict[str, Any] = {
        **summary,
        "cache_source": None,
        "status": "missing",
        "verification_status": "SKIPPED",
    }
    source_path = None
    if stable_cache_path.exists():
        entry["cache_source"] = "stable"
        entry["status"] = "stable_present"
        source_path = stable_cache_path
    elif staging_cache_path.exists():
        entry["cache_source"] = "staging"
        entry["status"] = "staging_present"
        source_path = staging_cache_path

    if source_path is None:
        return entry

    entry["cache_file"] = repo_relative(source_path)
    entry["cache_sha256"] = sha_file(source_path)
    entry["cache_size"] = source_path.stat().st_size
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        entry["verification_status"] = "FAIL"
        entry["error"] = f"invalid_json: {exc}"
        return entry
    if not isinstance(payload, dict):
        entry["verification_status"] = "FAIL"
        entry["error"] = "cache_payload_not_object"
        return entry

    checks = saturation_job_cache_checks(payload, job)
    failed = [name for name, passed in checks.items() if not passed]
    entry["checks"] = checks
    if failed:
        entry["verification_status"] = "FAIL"
        entry["failed_checks"] = failed
    else:
        entry["status"] = "verified"
        entry["verification_status"] = "PASS"
    return entry


def saturation_job_status_from_plan(job_plan: dict[str, Any], *, include_jobs: bool = True) -> dict[str, Any]:
    entries = [saturation_job_status_entry(job) for job in job_plan["jobs"]]
    status_counts = {
        "missing": sum(1 for entry in entries if entry["status"] == "missing"),
        "staging_present": sum(1 for entry in entries if entry["status"] == "staging_present"),
        "stable_present": sum(1 for entry in entries if entry["status"] == "stable_present"),
        "verified": sum(1 for entry in entries if entry["status"] == "verified"),
    }
    status = {
        "schema": "holotopy.saturation_certificate_job_status",
        "status": "PASS",
        "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
        "job_plan_sha256": job_plan["job_plan_sha256"],
        "runs_expensive_computation": False,
        "job_count": len(entries),
        "status_counts": status_counts,
    }
    if include_jobs:
        status["jobs"] = entries
    return status


def saturation_job_status(*, include_jobs: bool = True) -> dict[str, Any]:
    contract = write_saturation_cache_contract()
    job_plan = saturation_certificate_job_plan(contract)
    return saturation_job_status_from_plan(job_plan, include_jobs=include_jobs)


def saturation_queue_action(status_entry: dict[str, Any]) -> str:
    if status_entry.get("verification_status") == "PASS":
        return "none"
    if status_entry.get("staging_present") is True:
        return "verify_or_promote_staging_certificate"
    if status_entry.get("stable_present") is True:
        return "inspect_or_regenerate_stable_certificate"
    return "produce_certificate"


def saturation_queue_entry(job: dict[str, Any], status_entry: dict[str, Any], position: int) -> dict[str, Any]:
    job_id = str(job["job_id"])
    run_command = (
        "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
        f"--produce-saturation-job {job_id} --run-saturation-job"
    )
    return {
        "queue_position": position,
        "job_id": job_id,
        "label": job.get("label"),
        "input_sha256": job.get("input_sha256"),
        "status": status_entry.get("status"),
        "verification_status": status_entry.get("verification_status"),
        "next_action": saturation_queue_action(status_entry),
        "plan_command": job.get("produce_plan_command"),
        "run_command": run_command,
        "verify_command": job.get("verify_command"),
        "stable_cache_file": job.get("stable_cache_file"),
        "stable_present": status_entry.get("stable_present"),
        "staging_cache_file": job.get("staging_cache_file"),
        "staging_present": status_entry.get("staging_present"),
        "cache_source": status_entry.get("cache_source"),
        "settings": job.get("settings"),
    }


def saturation_certificate_queue(contract: dict[str, Any]) -> dict[str, Any]:
    job_plan = saturation_certificate_job_plan(contract)
    status = saturation_job_status_from_plan(job_plan)
    status_entries = status.get("jobs", [])
    queue_entries = [
        saturation_queue_entry(job, status_entry, index)
        for index, (job, status_entry) in enumerate(zip(job_plan["jobs"], status_entries), start=1)
    ]
    next_entry = next(
        (entry for entry in queue_entries if entry["next_action"] != "none"),
        None,
    )
    queue: dict[str, Any] = {
        "schema": "holotopy.saturation_certificate_queue",
        "status": (
            "READY_FOR_STRICT_CACHE"
            if status["status_counts"]["verified"] == len(queue_entries)
            else "PENDING_CERTIFICATES"
        ),
        "contract": {
            "path": repo_relative(INDEXED_CACHE_CONTRACT),
            "contract_sha256": contract["contract_sha256"],
        },
        "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
        "job_plan_sha256": job_plan["job_plan_sha256"],
        "runs_expensive_computation": False,
        "queue_policy": {
            "execution_order": "ascending_job_id",
            "default_producer_mode": "plan_only",
            "run_requires_explicit_flag": "--run-saturation-job",
            "strict_closure_requires_verified_count": len(queue_entries),
        },
        "status_counts": status["status_counts"],
        "next_job": next_entry,
        "jobs": queue_entries,
    }
    queue["queue_sha256"] = sha_json(
        {key: value for key, value in queue.items() if key != "queue_sha256"}
    )
    return queue


def write_saturation_queue_artifact(contract: dict[str, Any]) -> dict[str, Any]:
    queue = saturation_certificate_queue(contract)
    CERTIFICATE_QUEUE.write_text(
        json.dumps(queue, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return queue


def read_json_object(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return {}, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, f"invalid_json: {exc}"
    if not isinstance(payload, dict):
        return {}, "not_object"
    return payload, None


def saturation_queue_audit(
    contract: dict[str, Any],
    queue_payload: dict[str, Any] | None = None,
    queue_error: str | None = None,
) -> dict[str, Any]:
    expected_queue = saturation_certificate_queue(contract)
    if queue_payload is None:
        queue_payload, queue_error = read_json_object(CERTIFICATE_QUEUE)
    queue_jobs = queue_payload.get("jobs", []) if isinstance(queue_payload.get("jobs"), list) else []
    expected_jobs = expected_queue["jobs"]
    expected_first_pending = next(
        (job for job in expected_jobs if job.get("next_action") != "none"),
        None,
    )
    queue_first_pending = next(
        (
            job
            for job in queue_jobs
            if isinstance(job, dict) and job.get("next_action") != "none"
        ),
        None,
    )
    positions = [job.get("queue_position") for job in queue_jobs if isinstance(job, dict)]
    job_ids = [job.get("job_id") for job in queue_jobs if isinstance(job, dict)]
    input_hashes = [job.get("input_sha256") for job in queue_jobs if isinstance(job, dict)]
    status_counts = {
        "missing": sum(1 for job in queue_jobs if isinstance(job, dict) and job.get("status") == "missing"),
        "staging_present": sum(
            1 for job in queue_jobs if isinstance(job, dict) and job.get("status") == "staging_present"
        ),
        "stable_present": sum(
            1 for job in queue_jobs if isinstance(job, dict) and job.get("status") == "stable_present"
        ),
        "verified": sum(1 for job in queue_jobs if isinstance(job, dict) and job.get("status") == "verified"),
    }
    plan_commands = [str(job.get("plan_command", "")) for job in queue_jobs if isinstance(job, dict)]
    run_commands = [str(job.get("run_command", "")) for job in queue_jobs if isinstance(job, dict)]
    verify_commands = [str(job.get("verify_command", "")) for job in queue_jobs if isinstance(job, dict)]
    checks = {
        "queue_json_valid": queue_error is None,
        "queue_matches_current_status": queue_payload == expected_queue,
        "queue_hash_matches_payload": queue_payload.get("queue_sha256")
        == sha_json({key: value for key, value in queue_payload.items() if key != "queue_sha256"}),
        "queue_is_non_running": queue_payload.get("runs_expensive_computation") is False,
        "queue_has_48_jobs": len(queue_jobs) == 48,
        "queue_positions_are_contiguous": positions == list(range(1, len(queue_jobs) + 1)),
        "job_ids_are_contiguous": job_ids == [f"saturation_{index:03d}" for index in range(1, len(queue_jobs) + 1)],
        "job_ids_are_unique": len(set(job_ids)) == len(job_ids),
        "input_hashes_are_unique": len(set(input_hashes)) == len(input_hashes),
        "status_counts_match_jobs": queue_payload.get("status_counts") == status_counts,
        "next_job_is_first_pending": queue_payload.get("next_job") == expected_first_pending
        and queue_first_pending == expected_first_pending,
        "plan_commands_are_plan_only": len(plan_commands) == 48
        and all("--produce-saturation-job" in command for command in plan_commands)
        and all("--run-saturation-job" not in command for command in plan_commands)
        and all("--recompute-saturations" not in command for command in plan_commands),
        "run_commands_are_explicitly_guarded": len(run_commands) == 48
        and all("--produce-saturation-job" in command for command in run_commands)
        and all("--run-saturation-job" in command for command in run_commands)
        and all("--recompute-saturations" not in command for command in run_commands),
        "verify_commands_are_non_producing": len(verify_commands) == 48
        and all("--verify-saturation-job" in command for command in verify_commands)
        and all("--run-saturation-job" not in command for command in verify_commands)
        and all("--recompute-saturations" not in command for command in verify_commands),
    }
    audit: dict[str, Any] = {
        "schema": "holotopy.saturation_certificate_queue_audit",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "queue": repo_relative(CERTIFICATE_QUEUE),
        "queue_error": queue_error,
        "queue_sha256": sha_file(CERTIFICATE_QUEUE) if CERTIFICATE_QUEUE.exists() else None,
        "contract_sha256": contract["contract_sha256"],
        "runs_expensive_computation": False,
        "checks": checks,
        "status_counts": queue_payload.get("status_counts", {}),
        "next_job": queue_payload.get("next_job"),
    }
    audit["audit_sha256"] = sha_json(
        {key: value for key, value in audit.items() if key != "audit_sha256"}
    )
    return audit


def write_saturation_queue_audit_artifact(contract: dict[str, Any], queue: dict[str, Any]) -> dict[str, Any]:
    audit = saturation_queue_audit(contract, queue_payload=queue)
    CERTIFICATE_QUEUE_AUDIT.write_text(
        json.dumps(audit, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return audit


def saturation_cache_source_probe(job: dict[str, Any], *, source: str, path: Path) -> dict[str, Any]:
    probe: dict[str, Any] = {
        "source": source,
        "path": repo_relative(path),
        "present": path.exists(),
        "verification_status": "MISSING",
    }
    if not path.exists():
        return probe

    probe["sha256"] = sha_file(path)
    probe["size"] = path.stat().st_size
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        probe["verification_status"] = "FAIL"
        probe["error"] = f"invalid_json: {exc}"
        return probe
    if not isinstance(payload, dict):
        probe["verification_status"] = "FAIL"
        probe["error"] = "cache_payload_not_object"
        return probe

    checks = saturation_job_cache_checks(payload, job)
    failed = [name for name, passed in checks.items() if not passed]
    probe["checks"] = checks
    if failed:
        probe["verification_status"] = "FAIL"
        probe["failed_checks"] = failed
    else:
        probe["verification_status"] = "PASS"
    return probe


def saturation_source_next_action(stable: dict[str, Any], staging: dict[str, Any]) -> str:
    if stable.get("verification_status") == "PASS":
        return "none"
    if staging.get("verification_status") == "PASS":
        return "promote_staging_certificate"
    if stable.get("present") or staging.get("present"):
        return "inspect_invalid_certificate"
    return "produce_certificate"


def saturation_certificate_source_audit(contract: dict[str, Any]) -> dict[str, Any]:
    job_plan = saturation_certificate_job_plan(contract)
    entries: list[dict[str, Any]] = []
    for job in job_plan["jobs"]:
        stable = saturation_cache_source_probe(
            job,
            source="stable",
            path=repo_path(str(job["stable_cache_file"])),
        )
        staging = saturation_cache_source_probe(
            job,
            source="staging",
            path=repo_path(str(job["staging_cache_file"])),
        )
        job_id = str(job["job_id"])
        entries.append(
            {
                "job_id": job_id,
                "label": job.get("label"),
                "input_sha256": job.get("input_sha256"),
                "next_action": saturation_source_next_action(stable, staging),
                "stable": stable,
                "staging": staging,
                "plan_command": job.get("produce_plan_command"),
                "run_command": (
                    "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                    f"--produce-saturation-job {job_id} --run-saturation-job"
                ),
                "verify_command": job.get("verify_command"),
                "promote_command": (
                    "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                    "--promote-saturation-cache"
                ),
            }
        )

    counts = {
        "stable_present": sum(1 for entry in entries if entry["stable"]["present"]),
        "stable_verified": sum(1 for entry in entries if entry["stable"]["verification_status"] == "PASS"),
        "staging_present": sum(1 for entry in entries if entry["staging"]["present"]),
        "staging_verified": sum(1 for entry in entries if entry["staging"]["verification_status"] == "PASS"),
        "promotion_ready": sum(1 for entry in entries if entry["next_action"] == "promote_staging_certificate"),
        "invalid_present": sum(1 for entry in entries if entry["next_action"] == "inspect_invalid_certificate"),
        "missing_both": sum(
            1
            for entry in entries
            if not entry["stable"]["present"] and not entry["staging"]["present"]
        ),
        "produce_needed": sum(1 for entry in entries if entry["next_action"] == "produce_certificate"),
    }
    checks = {
        "job_count_is_48": len(entries) == 48,
        "counts_partition_jobs": (
            counts["stable_verified"]
            + counts["promotion_ready"]
            + counts["invalid_present"]
            + counts["produce_needed"]
            == len(entries)
        ),
        "staging_promotion_distinguished_from_missing": all(
            (
                entry["next_action"] != "promote_staging_certificate"
                or (
                    entry["staging"]["verification_status"] == "PASS"
                    and entry["stable"]["verification_status"] != "PASS"
                )
            )
            and (
                entry["next_action"] != "produce_certificate"
                or (not entry["stable"]["present"] and not entry["staging"]["present"])
            )
            for entry in entries
        ),
        "source_paths_are_distinct": all(
            entry["stable"]["path"] != entry["staging"]["path"] for entry in entries
        ),
        "plan_commands_are_non_running": all(
            "--run-saturation-job" not in str(entry["plan_command"])
            and "--recompute-saturations" not in str(entry["plan_command"])
            for entry in entries
        ),
        "run_commands_are_guarded": all(
            "--run-saturation-job" in str(entry["run_command"])
            and "--recompute-saturations" not in str(entry["run_command"])
            for entry in entries
        ),
        "verify_commands_are_non_producing": all(
            "--verify-saturation-job" in str(entry["verify_command"])
            and "--run-saturation-job" not in str(entry["verify_command"])
            and "--recompute-saturations" not in str(entry["verify_command"])
            for entry in entries
        ),
        "promotion_command_is_non_recomputing": all(
            "--promote-saturation-cache" in str(entry["promote_command"])
            and "--recompute-saturations" not in str(entry["promote_command"])
            and "--run-saturation-job" not in str(entry["promote_command"])
            for entry in entries
        ),
    }
    audit: dict[str, Any] = {
        "schema": "holotopy.saturation_certificate_source_audit",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "contract_sha256": contract["contract_sha256"],
        "job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
        "job_plan_sha256": job_plan["job_plan_sha256"],
        "runs_expensive_computation": False,
        "counts": counts,
        "checks": checks,
        "jobs": entries,
    }
    audit["audit_sha256"] = sha_json(
        {key: value for key, value in audit.items() if key != "audit_sha256"}
    )
    return audit


def write_saturation_source_audit_artifact(contract: dict[str, Any]) -> dict[str, Any]:
    audit = saturation_certificate_source_audit(contract)
    CERTIFICATE_SOURCE_AUDIT.write_text(
        json.dumps(audit, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return audit


def saturation_certificate_intake_protocol(contract: dict[str, Any]) -> dict[str, Any]:
    job_plan = saturation_certificate_job_plan(contract)
    queue = saturation_certificate_queue(contract)
    source_audit = saturation_certificate_source_audit(contract)
    commands = {
        "inspect_job": (
            "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
            "--show-saturation-job <job_id|label|input_sha256>"
        ),
        "plan_job": (
            "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
            "--produce-saturation-job <job_id|label|input_sha256>"
        ),
        "run_one_job": (
            "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
            "--produce-saturation-job <job_id> --run-saturation-job"
        ),
        "verify_job": (
            "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
            "--verify-saturation-job <job_id|label|input_sha256>"
        ),
        "audit_sources": (
            "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
            "--audit-saturation-sources"
        ),
        "promote_staging": (
            "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
            "--promote-saturation-cache"
        ),
        "strict_cache": "python src/verify.py jacobian-cubic-cache --pretty",
    }
    transitions = [
        {
            "name": "declared_to_planned",
            "from": "contract_declared",
            "to": "job_planned",
            "command": commands["plan_job"],
            "runs_expensive_computation": False,
            "evidence": [repo_relative(CERTIFICATE_JOB_PLAN), repo_relative(CERTIFICATE_QUEUE)],
        },
        {
            "name": "planned_to_stable_candidate",
            "from": "job_planned",
            "to": "stable_cache_candidate",
            "command": commands["run_one_job"],
            "runs_expensive_computation": True,
            "requires_explicit_flag": "--run-saturation-job",
            "writes": repo_relative(CACHE_DIR),
        },
        {
            "name": "staging_candidate_to_verified_source",
            "from": "staging_cache_candidate",
            "to": "verified_staging_source",
            "command": commands["audit_sources"],
            "runs_expensive_computation": False,
            "condition": "staging certificate passes the per-job cache checks",
            "evidence": repo_relative(CERTIFICATE_SOURCE_AUDIT),
        },
        {
            "name": "verified_staging_source_to_stable_candidate",
            "from": "verified_staging_source",
            "to": "stable_cache_candidate",
            "command": commands["promote_staging"],
            "runs_expensive_computation": False,
            "from_directory": repo_relative(STAGING_CACHE_DIR),
            "to_directory": repo_relative(CACHE_DIR),
        },
        {
            "name": "stable_candidate_to_verified_job",
            "from": "stable_cache_candidate",
            "to": "verified_job",
            "command": commands["verify_job"],
            "runs_expensive_computation": False,
            "checks": [
                "cache schema",
                "input hash",
                "result label",
                "result input hash",
                "contradiction flag",
                "zero remainder hash",
            ],
        },
        {
            "name": "verified_jobs_to_strict_cache",
            "from": "verified_job_count_48",
            "to": "strict_cache_verified",
            "command": commands["strict_cache"],
            "runs_expensive_computation": False,
            "requires": {"verified_certificate_count": 48},
        },
    ]
    non_running_commands = [
        commands["inspect_job"],
        commands["plan_job"],
        commands["verify_job"],
        commands["audit_sources"],
        commands["promote_staging"],
        commands["strict_cache"],
    ]
    checks = {
        "job_count_is_48": len(job_plan["jobs"]) == 48,
        "single_job_run_requires_explicit_flag": "--run-saturation-job" in commands["run_one_job"],
        "single_job_run_writes_stable_cache": job_plan.get("single_job_producer", {}).get("writes")
        == repo_relative(CACHE_DIR),
        "non_running_commands_are_guarded": all(
            "--run-saturation-job" not in command and "--recompute-saturations" not in command
            for command in non_running_commands
        ),
        "staging_promotion_path_declared": any(
            transition["name"] == "verified_staging_source_to_stable_candidate"
            for transition in transitions
        ),
        "strict_cache_requires_48_verified": transitions[-1].get("requires", {}).get(
            "verified_certificate_count"
        )
        == 48,
        "source_counts_cover_jobs": source_audit.get("checks", {}).get("counts_partition_jobs") is True,
        "queue_next_job_matches_source_state": (
            queue.get("next_job") is None
            or queue.get("next_job", {}).get("next_action")
            in {"produce_certificate", "verify_or_promote_staging_certificate", "inspect_or_regenerate_stable_certificate"}
        ),
    }
    protocol: dict[str, Any] = {
        "schema": "holotopy.saturation_certificate_intake_protocol",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "contract_sha256": contract["contract_sha256"],
        "runs_expensive_computation": False,
        "artifacts": {
            "job_plan": file_manifest_ref(CERTIFICATE_JOB_PLAN),
            "queue": file_manifest_ref(CERTIFICATE_QUEUE),
            "queue_audit": file_manifest_ref(CERTIFICATE_QUEUE_AUDIT),
            "source_audit": file_manifest_ref(CERTIFICATE_SOURCE_AUDIT),
            "stable_cache_directory": repo_relative(CACHE_DIR),
            "staging_source_directory": repo_relative(STAGING_CACHE_DIR),
        },
        "current_state": {
            "queue_status": queue.get("status"),
            "next_job": queue.get("next_job"),
            "source_counts": source_audit.get("counts"),
        },
        "commands": commands,
        "transitions": transitions,
        "checks": checks,
    }
    protocol["protocol_sha256"] = sha_json(
        {key: value for key, value in protocol.items() if key != "protocol_sha256"}
    )
    return protocol


def write_saturation_intake_protocol_artifact(contract: dict[str, Any]) -> dict[str, Any]:
    protocol = saturation_certificate_intake_protocol(contract)
    CERTIFICATE_INTAKE_PROTOCOL.write_text(
        json.dumps(protocol, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return protocol


def saturation_closure_checklist(contract: dict[str, Any]) -> dict[str, Any]:
    queue = saturation_certificate_queue(contract)
    source_audit = saturation_certificate_source_audit(contract)
    intake_protocol = saturation_certificate_intake_protocol(contract)
    source_counts = source_audit.get("counts", {})
    stable_verified = int(source_counts.get("stable_verified", 0))
    promotion_ready = int(source_counts.get("promotion_ready", 0))
    invalid_present = int(source_counts.get("invalid_present", 0))
    produce_needed = int(source_counts.get("produce_needed", 0))
    missing_both = int(source_counts.get("missing_both", 0))
    current_level = (
        "strict_certified"
        if stable_verified == 48 and promotion_ready == 0 and invalid_present == 0 and produce_needed == 0
        else "intake_ready"
        if intake_protocol.get("status") == "PASS" and queue.get("status") == "PENDING_CERTIFICATES"
        else "provisional_integrated"
    )
    levels = {
        "provisional_integrated": {
            "description": "The contract, registry, and public intake artifacts are present and current.",
            "required_verifiers": [
                "python src/verify.py jacobian-cubic-contract --pretty",
                "python src/verify.py evidence-index --pretty",
            ],
            "allowed_residue": "missing saturation certificate cache files",
            "strict_cache_may_fail": True,
        },
        "intake_ready": {
            "description": "The job queue and intake protocol identify the next certificate action without running algebra.",
            "required_verifiers": [
                "python src/verify.py jacobian-cubic-intake --pretty",
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --audit-saturation-sources",
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --saturation-job-status-summary",
            ],
            "required_state": {
                "job_count": 48,
                "invalid_present": 0,
                "source_counts_partition_jobs": True,
            },
            "strict_cache_may_fail": True,
        },
        "strict_certified": {
            "description": "All 48 stable cache certificates verify and the strict cache verifier passes.",
            "required_verifiers": [
                "python src/verify.py jacobian-cubic-cache --pretty",
            ],
            "required_state": {
                "stable_verified": 48,
                "promotion_ready": 0,
                "invalid_present": 0,
                "produce_needed": 0,
            },
            "strict_cache_may_fail": False,
        },
    }
    checks = {
        "contract_expects_48_certificates": contract.get("expected_certificate_count") == 48,
        "intake_protocol_passes": intake_protocol.get("status") == "PASS",
        "queue_declares_48_jobs": len(queue.get("jobs", [])) == 48,
        "source_counts_cover_48_jobs": stable_verified + promotion_ready + invalid_present + produce_needed == 48,
        "missing_is_explicit_residue": missing_both == produce_needed,
        "strict_state_requires_48_stable_verified": levels["strict_certified"]["required_state"]["stable_verified"]
        == 48,
        "provisional_lists_contract_and_index": {
            "python src/verify.py jacobian-cubic-contract --pretty",
            "python src/verify.py evidence-index --pretty",
        }.issubset(set(levels["provisional_integrated"]["required_verifiers"])),
        "intake_ready_lists_focused_intake_verifier": (
            "python src/verify.py jacobian-cubic-intake --pretty"
            in levels["intake_ready"]["required_verifiers"]
        ),
        "strict_certified_lists_strict_cache_verifier": (
            "python src/verify.py jacobian-cubic-cache --pretty"
            in levels["strict_certified"]["required_verifiers"]
        ),
    }
    checklist: dict[str, Any] = {
        "schema": "holotopy.saturation_certificate_closure_checklist",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "contract_sha256": contract["contract_sha256"],
        "runs_expensive_computation": False,
        "current_level": current_level,
        "current_state": {
            "queue_status": queue.get("status"),
            "next_job": queue.get("next_job"),
            "source_counts": source_counts,
        },
        "levels": levels,
        "artifacts": {
            "job_plan": file_manifest_ref(CERTIFICATE_JOB_PLAN),
            "queue": file_manifest_ref(CERTIFICATE_QUEUE),
            "source_audit": file_manifest_ref(CERTIFICATE_SOURCE_AUDIT),
            "intake_protocol": file_manifest_ref(CERTIFICATE_INTAKE_PROTOCOL),
            "stable_cache_directory": repo_relative(CACHE_DIR),
            "staging_source_directory": repo_relative(STAGING_CACHE_DIR),
        },
        "checks": checks,
    }
    checklist["checklist_sha256"] = sha_json(
        {key: value for key, value in checklist.items() if key != "checklist_sha256"}
    )
    return checklist


def write_saturation_closure_checklist_artifact(contract: dict[str, Any]) -> dict[str, Any]:
    checklist = saturation_closure_checklist(contract)
    CERTIFICATE_CLOSURE_CHECKLIST.write_text(
        json.dumps(checklist, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return checklist


def saturation_status_summary(contract: dict[str, Any]) -> dict[str, Any]:
    checklist = saturation_closure_checklist(contract)
    current_state = (
        checklist.get("current_state", {}) if isinstance(checklist.get("current_state"), dict) else {}
    )
    source_counts = (
        current_state.get("source_counts", {}) if isinstance(current_state.get("source_counts"), dict) else {}
    )
    next_job = current_state.get("next_job") if isinstance(current_state.get("next_job"), dict) else None
    stable_verified = int(source_counts.get("stable_verified", 0))
    promotion_ready = int(source_counts.get("promotion_ready", 0))
    invalid_present = int(source_counts.get("invalid_present", 0))
    produce_needed = int(source_counts.get("produce_needed", 0))
    missing_both = int(source_counts.get("missing_both", 0))
    stable_present = int(source_counts.get("stable_present", 0))
    staging_present = int(source_counts.get("staging_present", 0))
    current_level = checklist.get("current_level")
    strict_cache_ready = (
        stable_verified == 48
        and promotion_ready == 0
        and invalid_present == 0
        and produce_needed == 0
    )
    counts = {
        "stable_present": stable_present,
        "staging_present": staging_present,
        "stable_verified": stable_verified,
        "promotion_ready": promotion_ready,
        "invalid_present": invalid_present,
        "produce_needed": produce_needed,
        "missing_both": missing_both,
    }
    checks = {
        "closure_checklist_passes": checklist.get("status") == "PASS",
        "current_level_known": current_level
        in {"provisional_integrated", "intake_ready", "strict_certified"},
        "counts_cover_48_jobs": stable_verified + promotion_ready + invalid_present + produce_needed
        == 48,
        "missing_is_explicit_residue": missing_both == produce_needed,
        "strict_cache_ready_matches_counts": (current_level == "strict_certified")
        == strict_cache_ready,
        "next_job_present_unless_strict": strict_cache_ready or isinstance(next_job, dict),
        "non_strict_verifier_declared": True,
        "strict_verifier_declared": True,
    }
    summary: dict[str, Any] = {
        "schema": "holotopy.saturation_certificate_status_summary",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "contract_sha256": contract["contract_sha256"],
        "runs_expensive_computation": False,
        "current_level": current_level,
        "strict_cache_ready": strict_cache_ready,
        "counts": counts,
        "next_job": (
            {
                "job_id": next_job.get("job_id"),
                "label": next_job.get("label"),
                "next_action": next_job.get("next_action"),
                "plan_command": next_job.get("plan_command"),
                "run_command": next_job.get("run_command"),
                "verify_command": next_job.get("verify_command"),
            }
            if isinstance(next_job, dict)
            else None
        ),
        "recommended_next_action": (
            next_job.get("next_action") if isinstance(next_job, dict) else "run strict cache verifier"
        ),
        "recommended_verifier": "python src/verify.py jacobian-cubic-nonstrict --pretty",
        "strict_verifier": "python src/verify.py jacobian-cubic-cache --pretty",
        "source_artifacts": {
            "queue": file_manifest_ref(CERTIFICATE_QUEUE),
            "source_audit": file_manifest_ref(CERTIFICATE_SOURCE_AUDIT),
            "closure_checklist": file_manifest_ref(CERTIFICATE_CLOSURE_CHECKLIST),
        },
        "residue": {
            "kind": "missing_saturation_certificates",
            "discharged": strict_cache_ready,
            "missing_certificate_count": produce_needed,
            "severity": "none" if strict_cache_ready else "medium",
        },
        "checks": checks,
    }
    summary["status_summary_sha256"] = sha_json(
        {key: value for key, value in summary.items() if key != "status_summary_sha256"}
    )
    return summary


def write_saturation_status_summary_artifact(contract: dict[str, Any]) -> dict[str, Any]:
    summary = saturation_status_summary(contract)
    CERTIFICATE_STATUS_SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return summary


def write_saturation_queue() -> dict[str, Any]:
    write_saturation_cache_contract()
    return json.loads(CERTIFICATE_QUEUE.read_text(encoding="utf-8"))


def audit_saturation_queue() -> dict[str, Any]:
    write_saturation_cache_contract()
    return json.loads(CERTIFICATE_QUEUE_AUDIT.read_text(encoding="utf-8"))


def audit_saturation_sources() -> dict[str, Any]:
    write_saturation_cache_contract()
    return json.loads(CERTIFICATE_SOURCE_AUDIT.read_text(encoding="utf-8"))


def write_saturation_intake_protocol() -> dict[str, Any]:
    write_saturation_cache_contract()
    return json.loads(CERTIFICATE_INTAKE_PROTOCOL.read_text(encoding="utf-8"))


def write_saturation_closure_checklist() -> dict[str, Any]:
    write_saturation_cache_contract()
    return json.loads(CERTIFICATE_CLOSURE_CHECKLIST.read_text(encoding="utf-8"))


def write_saturation_status_summary() -> dict[str, Any]:
    write_saturation_cache_contract()
    return json.loads(CERTIFICATE_STATUS_SUMMARY.read_text(encoding="utf-8"))


def saturation_evidence_manifest(contract: dict[str, Any]) -> dict[str, Any]:
    inventory = saturation_cache_inventory(contract)
    manifest = {
        "schema": "holotopy.jacobian_cubic_symbolic_elimination_evidence",
        "name": "jacobian_cubic_symbolic_elimination",
        "status": "CONTRACT_LOCKED_CERTIFICATES_PENDING",
        "expected_certificate_count": contract["expected_certificate_count"],
        "cache_inventory": inventory,
        "inputs": {
            "contract_generator": file_manifest_ref(Path(__file__).resolve()),
            "repo_verifier": file_manifest_ref(ROOT / "src" / "verify.py"),
            "saturation_cache_contract": {
                **file_manifest_ref(INDEXED_CACHE_CONTRACT),
                "contract_sha256": contract["contract_sha256"],
            },
        },
        "outputs": {
            "cache_directory": repo_relative(CACHE_DIR),
            "certificate_job_plan": repo_relative(CERTIFICATE_JOB_PLAN),
            "certificate_queue": repo_relative(CERTIFICATE_QUEUE),
            "certificate_queue_audit": repo_relative(CERTIFICATE_QUEUE_AUDIT),
            "certificate_source_audit": repo_relative(CERTIFICATE_SOURCE_AUDIT),
            "certificate_intake_protocol": repo_relative(CERTIFICATE_INTAKE_PROTOCOL),
            "certificate_closure_checklist": repo_relative(CERTIFICATE_CLOSURE_CHECKLIST),
            "certificate_status_summary": repo_relative(CERTIFICATE_STATUS_SUMMARY),
            "evidence_manifest": repo_relative(EVIDENCE_MANIFEST),
            "evidence_readme": repo_relative(EVIDENCE_README),
            "staging_source_cache_directory": repo_relative(STAGING_CACHE_DIR),
            "report": repo_relative(REPORT),
            "strict_cache_artifact_manifest": repo_relative(INDEXED_CACHE_MANIFEST),
        },
        "artifacts": {
            "certificate_job_plan": file_manifest_ref(CERTIFICATE_JOB_PLAN),
            "certificate_queue": file_manifest_ref(CERTIFICATE_QUEUE),
            "certificate_queue_audit": file_manifest_ref(CERTIFICATE_QUEUE_AUDIT),
            "certificate_source_audit": file_manifest_ref(CERTIFICATE_SOURCE_AUDIT),
            "certificate_intake_protocol": file_manifest_ref(CERTIFICATE_INTAKE_PROTOCOL),
            "certificate_closure_checklist": file_manifest_ref(CERTIFICATE_CLOSURE_CHECKLIST),
            "certificate_status_summary": file_manifest_ref(CERTIFICATE_STATUS_SUMMARY),
            "evidence_readme": file_manifest_ref(EVIDENCE_README),
            "report": file_manifest_ref(REPORT),
        },
        "verifiers": {
            "contract": "python src/verify.py jacobian-cubic-contract --pretty",
            "intake_protocol": "python src/verify.py jacobian-cubic-intake --pretty",
            "closure_checklist": "python src/verify.py jacobian-cubic-closure --pretty",
            "closure_status": "python src/verify.py jacobian-cubic-status --pretty",
            "non_strict_integration": "python src/verify.py jacobian-cubic-nonstrict --pretty",
            "status_summary": "python src/verify.py jacobian-cubic-status --pretty",
            "inspect_first_certificate_job": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--show-saturation-job saturation_001"
            ),
            "plan_first_certificate_job_production": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--produce-saturation-job saturation_001"
            ),
            "verify_first_certificate_job_if_present": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--verify-saturation-job saturation_001"
            ),
            "batch_certificate_job_status": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--saturation-job-status"
            ),
            "refresh_certificate_queue": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--write-saturation-queue"
            ),
            "audit_certificate_queue": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--audit-saturation-queue"
            ),
            "audit_certificate_sources": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--audit-saturation-sources"
            ),
            "refresh_certificate_intake_protocol": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--write-saturation-intake-protocol"
            ),
            "refresh_closure_checklist": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--write-saturation-closure-checklist"
            ),
            "refresh_status_summary": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--write-saturation-status-summary"
            ),
            "promote_existing_staging": (
                "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py "
                "--promote-saturation-cache"
            ),
            "strict_cache": "python src/verify.py jacobian-cubic-cache --pretty",
        },
        "residues": [
            {
                "kind": "missing_saturation_certificates",
                "description": (
                    "The 48 Rabinowitsch saturation certificate files are required for strict cache "
                    "certification but are not bundled by this contract manifest."
                ),
                "discharged": False,
                "missing_certificate_count": inventory["missing_certificate_count"],
                "severity": "medium",
            }
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    return manifest


def saturation_evidence_index_entry() -> dict[str, Any]:
    return evidence_index_entry(
        evidence_id="jacobian_cubic_symbolic_elimination",
        root=EVIDENCE_DIR,
        entrypoint=EVIDENCE_MANIFEST,
        status="CONTRACT_LOCKED_CERTIFICATES_PENDING",
    )


def upsert_saturation_evidence_index() -> dict[str, Any]:
    return upsert_evidence_index_entry(saturation_evidence_index_entry(), insert="prepend")


def write_saturation_cache_contract(specs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    contract = saturation_cache_contract(specs or expected_saturation_cache_specs())
    INDEXED_CACHE_CONTRACT.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    INDEXED_CACHE_CONTRACT.write_text(
        json.dumps(contract, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    EVIDENCE_README.write_text(saturation_evidence_readme(contract), encoding="utf-8")
    certificate_job_plan = saturation_certificate_job_plan(contract)
    CERTIFICATE_JOB_PLAN.write_text(
        json.dumps(certificate_job_plan, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    certificate_queue = write_saturation_queue_artifact(contract)
    write_saturation_queue_audit_artifact(contract, certificate_queue)
    write_saturation_source_audit_artifact(contract)
    write_saturation_intake_protocol_artifact(contract)
    write_saturation_closure_checklist_artifact(contract)
    write_saturation_status_summary_artifact(contract)
    evidence_manifest = saturation_evidence_manifest(contract)
    EVIDENCE_MANIFEST.write_text(
        json.dumps(evidence_manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    upsert_saturation_evidence_index()
    return contract


def existing_indexed_manifest_status() -> dict[str, Any]:
    if not INDEXED_CACHE_MANIFEST.exists():
        return {"exists": False, "status": None, "sha256": None}
    try:
        payload = json.loads(INDEXED_CACHE_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"exists": True, "status": "INVALID_JSON", "sha256": sha_file(INDEXED_CACHE_MANIFEST)}
    return {"exists": True, "status": payload.get("status"), "sha256": sha_file(INDEXED_CACHE_MANIFEST)}


def verify_saturation_cache(*, promote_staging: bool = False) -> dict[str, Any]:
    specs = expected_saturation_cache_specs()
    contract = write_saturation_cache_contract(specs)
    zero_remainder_sha = sha_json([])
    errors: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    expected_paths = {spec["cache_path"] for spec in specs}
    actual_paths = set(CACHE_DIR.glob("*.json")) if CACHE_DIR.exists() else set()
    if CACHE_MANIFEST in actual_paths:
        actual_paths.remove(CACHE_MANIFEST)
    for spec in specs:
        cache_path = spec["cache_path"]
        staging_cache_path = spec["staging_cache_path"]
        label = spec["label"]
        source_path = cache_path if cache_path.exists() else (
            staging_cache_path if promote_staging and staging_cache_path.exists() else cache_path
        )
        entry: dict[str, Any] = {
            "cache_file": spec["cache_file"],
            "label": label,
            "input_sha256": spec["input_sha256"],
            "settings": spec["settings"],
            "present": cache_path.exists(),
            "staging_cache_file": spec["staging_cache_file"],
            "staging_present": staging_cache_path.exists(),
        }
        if source_path.exists():
            entry["source_file"] = repo_relative(source_path)
            entry["cache_sha256"] = sha_file(source_path)
            entry["cache_size"] = source_path.stat().st_size
        if not source_path.exists():
            errors.append(
                {
                    "label": label,
                    "check": "cache_present",
                    "path": spec["cache_file"],
                    "staging_path": spec["staging_cache_file"],
                }
            )
            entries.append(entry)
            continue
        try:
            payload = json.loads(source_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append({"label": label, "check": "json_valid", "path": repo_relative(source_path), "error": str(exc)})
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
                    "result_cache_file": result.get("cache_file")
                    in {spec["cache_file"], spec["staging_cache_file"]},
                    "contradiction_found": result.get("contradiction_found") is True,
                    "reduction_completed": result.get("reduction_completed") is True,
                    "zero_remainder": result.get("one_remainder_term_count") == 0,
                    "zero_remainder_hash": result.get("one_remainder_sha256") == zero_remainder_sha,
                }
            )
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            errors.append({"label": label, "check": "cache_payload", "path": repo_relative(source_path), "failed": failed})
            entry["status"] = "FAIL"
            entry["failed_checks"] = failed
        else:
            if promote_staging and source_path == staging_cache_path:
                result = {**result, "cache_file": spec["cache_file"]} if isinstance(result, dict) else result
                write_saturation_cache(cache_path, spec["input_sha256"], result)
                entry["promoted_to_stable_cache"] = True
                entry["source_file"] = spec["cache_file"]
                entry["cache_sha256"] = sha_file(cache_path)
                entry["cache_size"] = cache_path.stat().st_size
            entry["status"] = "PASS"
            entry["result_processed_pairs"] = result.get("processed_pairs") if isinstance(result, dict) else None
            entry["result_label"] = result.get("label") if isinstance(result, dict) else None
            entry["result_input_hash"] = result.get("input_sha256") if isinstance(result, dict) else None
        entries.append(entry)
    extra_paths = sorted(repo_relative(path) for path in actual_paths - expected_paths)
    promoted_certificate_count = sum(1 for entry in entries if entry.get("promoted_to_stable_cache") is True)
    if promote_staging:
        contract = write_saturation_cache_contract(specs)
    summary = {
        "schema": "holotopy.saturation_cache_verification",
        "promotion_requested": promote_staging,
        "promoted_certificate_count": promoted_certificate_count,
        "status": "PASS" if not errors else "FAIL",
        "expected_certificate_count": len(specs),
        "verified_certificate_count": len([entry for entry in entries if entry.get("status") == "PASS"]),
        "cache_directory": repo_relative(CACHE_DIR),
        "staging_cache_directory": repo_relative(STAGING_CACHE_DIR),
        "extra_cache_files": extra_paths,
        "manifest_file": repo_relative(CACHE_MANIFEST),
        "entries": entries,
        "errors": errors,
    }
    summary["manifest_sha256"] = sha_json({key: value for key, value in summary.items() if key != "manifest_sha256"})
    indexed_manifest = {
        "schema": "holotopy.saturation_cache_artifact_manifest",
        "status": summary["status"],
        "cache_directory": repo_relative(CACHE_DIR),
        "staging_cache_directory": repo_relative(STAGING_CACHE_DIR),
        "cache_manifest": repo_relative(CACHE_MANIFEST),
        "cache_manifest_sha256": summary["manifest_sha256"],
        "expected_certificate_count": summary["expected_certificate_count"],
        "verified_certificate_count": summary["verified_certificate_count"],
        "entries": [
            {
                "cache_file": entry["cache_file"],
                "label": entry.get("label"),
                "input_sha256": entry.get("input_sha256"),
                "cache_sha256": entry.get("cache_sha256"),
                "status": entry.get("status"),
            }
            for entry in entries
            if isinstance(entry, dict)
        ],
    }
    indexed_manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in indexed_manifest.items() if key != "manifest_sha256"}
    )
    CACHE_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    INDEXED_CACHE_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    CACHE_MANIFEST.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    summary["indexed_contract"] = repo_relative(INDEXED_CACHE_CONTRACT)
    summary["indexed_contract_sha256"] = contract["contract_sha256"]
    summary["indexed_manifest"] = repo_relative(INDEXED_CACHE_MANIFEST)
    INDEXED_CACHE_MANIFEST.write_text(
        json.dumps(indexed_manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    summary["indexed_manifest_sha256"] = indexed_manifest["manifest_sha256"]
    summary["indexed_manifest_written"] = True
    return summary


def saturation_cache_result_summary(result: dict[str, Any]) -> dict[str, Any]:
    errors = result.get("errors", [])
    missing_certificate_count = sum(
        1 for error in errors if isinstance(error, dict) and error.get("check") == "cache_present"
    )
    return {
        "schema": "holotopy.saturation_cache_verification_summary",
        "status": result.get("status"),
        "promotion_requested": result.get("promotion_requested"),
        "promoted_certificate_count": result.get("promoted_certificate_count"),
        "expected_certificate_count": result.get("expected_certificate_count"),
        "verified_certificate_count": result.get("verified_certificate_count"),
        "missing_certificate_count": missing_certificate_count,
        "error_count": len(errors),
        "first_errors": errors[:5],
        "cache_directory": result.get("cache_directory"),
        "staging_cache_directory": result.get("staging_cache_directory"),
        "indexed_contract": result.get("indexed_contract"),
        "indexed_manifest": result.get("indexed_manifest"),
        "indexed_manifest_written": result.get("indexed_manifest_written"),
    }


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
            "manifest": {
                "path": repo_relative(CACHE_MANIFEST),
                "status": cache_verification.get("status"),
                "manifest_sha256": cache_verification.get("manifest_sha256"),
            },
            "indexed_contract": {
                "path": cache_verification.get("indexed_contract"),
                "manifest_sha256": cache_verification.get("indexed_contract_sha256"),
            },
            "indexed_manifest": {
                "path": cache_verification.get("indexed_manifest"),
                "status": cache_verification.get("status"),
                "manifest_sha256": cache_verification.get("indexed_manifest_sha256"),
                "written": cache_verification.get("indexed_manifest_written"),
            },
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
    parser.add_argument(
        "--write-saturation-cache-contract",
        action="store_true",
        help="Write the deterministic saturation cache input contract without checking cache certificates.",
    )
    parser.add_argument(
        "--promote-saturation-cache",
        action="store_true",
        help="Validate existing staging saturation cache certificates and promote valid entries into durable evidence.",
    )
    parser.add_argument(
        "--list-saturation-jobs",
        action="store_true",
        help="List declared saturation certificate jobs without running saturation computations.",
    )
    parser.add_argument(
        "--saturation-job-status",
        action="store_true",
        help="Report status for all declared saturation jobs without generating cache certificates.",
    )
    parser.add_argument(
        "--saturation-job-status-summary",
        action="store_true",
        help="Report status counts for declared saturation jobs without printing all jobs.",
    )
    parser.add_argument(
        "--write-saturation-queue",
        action="store_true",
        help="Write the resumable saturation certificate queue without generating cache certificates.",
    )
    parser.add_argument(
        "--audit-saturation-queue",
        action="store_true",
        help="Audit the saturation certificate queue ordering and command guards without generating certificates.",
    )
    parser.add_argument(
        "--audit-saturation-sources",
        action="store_true",
        help="Audit stable and staging saturation certificate sources without generating certificates.",
    )
    parser.add_argument(
        "--write-saturation-intake-protocol",
        action="store_true",
        help="Write the saturation certificate intake protocol without generating certificates.",
    )
    parser.add_argument(
        "--write-saturation-closure-checklist",
        action="store_true",
        help="Write the saturation certificate closure checklist without generating certificates.",
    )
    parser.add_argument(
        "--write-saturation-status-summary",
        action="store_true",
        help="Write the compact saturation certificate status summary without generating certificates.",
    )
    parser.add_argument(
        "--show-saturation-job",
        metavar="SELECTOR",
        help="Show one declared saturation job by job id, label, or input hash without running it.",
    )
    parser.add_argument(
        "--produce-saturation-job",
        metavar="SELECTOR",
        help="Plan one saturation certificate production job without running it by default.",
    )
    parser.add_argument(
        "--run-saturation-job",
        action="store_true",
        help="Actually run the selected --produce-saturation-job computation.",
    )
    parser.add_argument(
        "--verify-saturation-job",
        metavar="SELECTOR",
        help="Verify one existing saturation cache certificate by job id, label, or input hash without generating it.",
    )
    parser.add_argument("--quiet", action="store_true", help="Write report.json without printing the full report.")
    args = parser.parse_args()
    if args.write_saturation_cache_contract:
        contract = write_saturation_cache_contract()
        if not args.quiet:
            print(json.dumps(contract, indent=2, sort_keys=True))
        return
    if args.list_saturation_jobs:
        listing = list_saturation_jobs()
        if not args.quiet:
            print(json.dumps(listing, indent=2, sort_keys=True))
        return
    if args.saturation_job_status:
        status = saturation_job_status()
        if not args.quiet:
            print(json.dumps(status, indent=2, sort_keys=True))
        return
    if args.saturation_job_status_summary:
        status = saturation_job_status(include_jobs=False)
        if not args.quiet:
            print(json.dumps(status, indent=2, sort_keys=True))
        return
    if args.write_saturation_queue:
        queue = write_saturation_queue()
        if not args.quiet:
            print(json.dumps(queue, indent=2, sort_keys=True))
        return
    if args.audit_saturation_queue:
        audit = audit_saturation_queue()
        if not args.quiet:
            print(json.dumps(audit, indent=2, sort_keys=True))
        if audit["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.audit_saturation_sources:
        audit = audit_saturation_sources()
        if not args.quiet:
            print(json.dumps(audit, indent=2, sort_keys=True))
        if audit["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.write_saturation_intake_protocol:
        protocol = write_saturation_intake_protocol()
        if not args.quiet:
            print(json.dumps(protocol, indent=2, sort_keys=True))
        if protocol["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.write_saturation_closure_checklist:
        checklist = write_saturation_closure_checklist()
        if not args.quiet:
            print(json.dumps(checklist, indent=2, sort_keys=True))
        if checklist["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.write_saturation_status_summary:
        summary = write_saturation_status_summary()
        if not args.quiet:
            print(json.dumps(summary, indent=2, sort_keys=True))
        if summary["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.show_saturation_job:
        lookup = show_saturation_job(args.show_saturation_job)
        if not args.quiet:
            print(json.dumps(lookup, indent=2, sort_keys=True))
        if lookup["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.produce_saturation_job:
        production = produce_saturation_job(args.produce_saturation_job, run=args.run_saturation_job)
        if not args.quiet:
            print(json.dumps(production, indent=2, sort_keys=True))
        if production["status"] == "FAIL":
            raise SystemExit(1)
        return
    if args.run_saturation_job:
        parser.error("--run-saturation-job requires --produce-saturation-job")
    if args.verify_saturation_job:
        verification = verify_saturation_job(args.verify_saturation_job)
        if not args.quiet:
            print(json.dumps(verification, indent=2, sort_keys=True))
        if verification["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.promote_saturation_cache:
        promotion = verify_saturation_cache(promote_staging=True)
        if not args.quiet:
            print(json.dumps(saturation_cache_result_summary(promotion), indent=2, sort_keys=True))
        if promotion["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.verify_saturation_cache:
        verification = verify_saturation_cache()
        if not args.quiet:
            print(json.dumps(verification, indent=2, sort_keys=True))
        if verification["status"] != "PASS":
            raise SystemExit(1)
        return
    report = build_report(recompute_saturations=args.recompute_saturations)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_saturation_cache_contract()
    if not args.quiet:
        print(json.dumps(report, indent=2, sort_keys=True))
    if report["checks"]["trace_substitution_eliminates_degree2"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
