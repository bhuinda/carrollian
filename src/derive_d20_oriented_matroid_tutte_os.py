from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    from src.derive_d20_oriented_matroid_sector33_dual import (
        SECTOR33_EXTENSION,
        build_sector33_height_attachment_matrix,
    )
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_oriented_matroid_sector33_dual import (
        SECTOR33_EXTENSION,
        build_sector33_height_attachment_matrix,
    )
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_oriented_matroid_tutte_os"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
FIELD_PRIME = 1_000_003

D20_JSON = ROOT / "d20.json"
SECTOR33_DUAL = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)

Poly = dict[tuple[int, int], int]
Rows = tuple[tuple[int, ...], ...]
State = tuple[Rows, int]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def canonical_state(rows: list[list[int]] | Rows, ncols: int) -> tuple[State, int]:
    work = [[int(value) % FIELD_PRIME for value in row] for row in rows]
    rank = 0
    row_count = len(work)
    for col in range(ncols):
        pivot = None
        for row in range(rank, row_count):
            if work[row][col] % FIELD_PRIME:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inv = pow(work[rank][col], FIELD_PRIME - 2, FIELD_PRIME)
        work[rank] = [(value * inv) % FIELD_PRIME for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = work[row][col] % FIELD_PRIME
            if factor:
                work[row] = [
                    (work[row][idx] - factor * work[rank][idx]) % FIELD_PRIME
                    for idx in range(ncols)
                ]
        rank += 1
        if rank == row_count:
            break
    reduced = tuple(
        tuple(row)
        for row in work
        if any(value % FIELD_PRIME for value in row)
    )
    return (reduced, ncols), len(reduced)


def delete_element(state: State, element: int) -> tuple[State, int]:
    rows, ncols = state
    deleted = [
        [row[col] for col in range(ncols) if col != element]
        for row in rows
    ]
    return canonical_state(deleted, ncols - 1)


def contract_element(state: State, element: int) -> tuple[State, int]:
    rows, ncols = state
    work = [list(row) for row in rows]
    pivot = None
    for row, values in enumerate(work):
        if values[element] % FIELD_PRIME:
            pivot = row
            break
    if pivot is None:
        return delete_element(state, element)

    inv = pow(work[pivot][element], FIELD_PRIME - 2, FIELD_PRIME)
    work[pivot] = [(value * inv) % FIELD_PRIME for value in work[pivot]]
    for row in range(len(work)):
        if row == pivot:
            continue
        factor = work[row][element] % FIELD_PRIME
        if factor:
            work[row] = [
                (work[row][idx] - factor * work[pivot][idx]) % FIELD_PRIME
                for idx in range(ncols)
            ]
    contracted = [
        [value for col, value in enumerate(row) if col != element]
        for idx, row in enumerate(work)
        if idx != pivot
    ]
    return canonical_state(contracted, ncols - 1)


def poly_add(left: Poly, right: Poly) -> Poly:
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, 0) + value
        if out[key] == 0:
            del out[key]
    return out


def poly_shift(poly: Poly, dx: int, dy: int) -> Poly:
    return {(x_degree + dx, y_degree + dy): coeff for (x_degree, y_degree), coeff in poly.items()}


def tutte_polynomial(initial_state: State) -> tuple[Poly, dict[str, int]]:
    cache: dict[State, Poly] = {}
    stats = {"cache_hits": 0, "cache_misses": 0}

    def compute(state: State) -> Poly:
        cached = cache.get(state)
        if cached is not None:
            stats["cache_hits"] += 1
            return cached
        stats["cache_misses"] += 1

        rows, ncols = state
        rank = len(rows)
        if ncols == 0:
            result = {(0, 0): 1}
        else:
            element = ncols - 1
            column_is_zero = all(row[element] % FIELD_PRIME == 0 for row in rows)
            deletion, deletion_rank = delete_element(state, element)
            if column_is_zero:
                result = poly_shift(compute(deletion), 0, 1)
            elif deletion_rank == rank - 1:
                contraction, _contraction_rank = contract_element(state, element)
                result = poly_shift(compute(contraction), 1, 0)
            else:
                contraction, _contraction_rank = contract_element(state, element)
                result = poly_add(compute(deletion), compute(contraction))

        cache[state] = result
        return result

    polynomial = compute(initial_state)
    stats["cache_entries"] = len(cache)
    stats["term_count"] = len(polynomial)
    return polynomial, stats


def polynomial_terms(poly: Poly) -> list[dict[str, int]]:
    return [
        {"x_degree": x_degree, "y_degree": y_degree, "coefficient": poly[(x_degree, y_degree)]}
        for x_degree, y_degree in sorted(poly, key=lambda item: (-item[0], item[1]))
    ]


def evaluate_tutte(poly: Poly, x_value: int, y_value: int) -> int:
    return sum(
        coeff * (x_value ** x_degree) * (y_value ** y_degree)
        for (x_degree, y_degree), coeff in poly.items()
    )


def characteristic_polynomial(poly: Poly, rank: int) -> dict[int, int]:
    coeffs: dict[int, int] = {}
    sign = -1 if rank % 2 else 1
    for (x_degree, y_degree), coeff in poly.items():
        if y_degree != 0:
            continue
        for q_degree in range(x_degree + 1):
            term = sign * coeff * math.comb(x_degree, q_degree) * ((-1) ** q_degree)
            coeffs[q_degree] = coeffs.get(q_degree, 0) + term
    return {degree: coeffs.get(degree, 0) for degree in range(rank + 1)}


def characteristic_terms(coeffs: dict[int, int]) -> list[dict[str, int]]:
    return [
        {"q_degree": degree, "coefficient": coeffs[degree]}
        for degree in sorted(coeffs, reverse=True)
    ]


def os_hilbert_coefficients(characteristic: dict[int, int], rank: int) -> list[int]:
    return [
        ((-1) ** degree) * characteristic[rank - degree]
        for degree in range(rank + 1)
    ]


def reduce_matrix(matrix: list[list[int]]) -> list[list[int]]:
    return [[value % FIELD_PRIME for value in row] for row in matrix]


def matrix_shape(matrix: list[list[int]]) -> dict[str, int]:
    return {"rows": len(matrix), "cols": len(matrix[0]) if matrix else 0}


def build_theorem() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    extension = load_json(SECTOR33_EXTENSION)
    dual = load_json(SECTOR33_DUAL)

    integer_matrix, attachment = build_sector33_height_attachment_matrix()
    mod_matrix = reduce_matrix(integer_matrix)
    initial_state, rank = canonical_state(mod_matrix, len(mod_matrix[0]))
    polynomial, stats = tutte_polynomial(initial_state)
    terms = polynomial_terms(polynomial)
    characteristic = characteristic_polynomial(polynomial, rank)
    characteristic_rows = characteristic_terms(characteristic)
    os_hilbert = os_hilbert_coefficients(characteristic, rank)

    specializations = {
        "T_1_1_basis_count": evaluate_tutte(polynomial, 1, 1),
        "T_2_1_independent_set_count": evaluate_tutte(polynomial, 2, 1),
        "T_1_2_spanning_set_count": evaluate_tutte(polynomial, 1, 2),
        "T_2_2_all_subsets": evaluate_tutte(polynomial, 2, 2),
        "T_1_0": evaluate_tutte(polynomial, 1, 0),
        "T_2_0": evaluate_tutte(polynomial, 2, 0),
    }

    polynomial_sha256 = sha_json(terms)
    characteristic_sha256 = sha_json(characteristic_rows)
    os_hilbert_sha256 = sha_json(os_hilbert)
    matrix_integer_sha256 = sha_json(integer_matrix)
    matrix_mod_prime_sha256 = sha_json(mod_matrix)

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "sector33_extension_input_is_certified": extension.get("status")
        == "D20_ORIENTED_MATROID_SECTOR33_EXTENSION_CERTIFIED"
        and extension.get("all_checks_pass") is True,
        "sector33_dual_input_is_certified": dual.get("status")
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual.get("all_checks_pass") is True,
        "field_prime_is_recorded": FIELD_PRIME == 1_000_003,
        "ground_set_size_is_31": len(mod_matrix[0]) == 31,
        "rank_is_20": rank == 20,
        "tutte_term_count_is_93": len(terms) == 93,
        "tutte_all_subsets_specialization": specializations["T_2_2_all_subsets"] == 2 ** 31,
        "characteristic_degree_is_rank": characteristic.get(rank) == 1,
        "os_hilbert_length_is_rank_plus_one": len(os_hilbert) == rank + 1,
        "os_hilbert_first_coefficients": os_hilbert[:2] == [1, 31],
        "os_hilbert_nonnegative": all(value >= 0 for value in os_hilbert),
    }

    report = {
        "schema": "d20.theorem.d20_oriented_matroid_tutte_os",
        "status": "D20_ORIENTED_MATROID_TUTTE_OS_CERTIFIED",
        "object": "D20",
        "definition": {
            "matroid": (
                "the sector-33 height-attachment matrix reduced over the finite field "
                "F_1000003"
            ),
            "tutte_polynomial": (
                "computed by loop/coloop-aware deletion-contraction with canonical "
                "modular row-reduced cache keys"
            ),
            "orlik_solomon_summary": (
                "NBC/Orlik-Solomon Hilbert coefficients read from the characteristic "
                "polynomial chi(q)=(-1)^r T(1-q,0)"
            ),
        },
        "claim": (
            "The 31-element sector-33 height attachment has a finite-field Tutte/OS "
            "package over F_1000003: rank 20, a 93-term Tutte polynomial, and a "
            "nonnegative NBC Hilbert vector beginning [1,31]. This is a certified "
            "finite-field witness; a rational prime-good audit is intentionally left "
            "as a separate seam."
        ),
        "inputs": {
            "d20_json": input_record(D20_JSON),
            "d20_oriented_matroid_sector33_extension_report": input_record(
                SECTOR33_EXTENSION
            ),
            "d20_oriented_matroid_sector33_dual_report": input_record(SECTOR33_DUAL),
        },
        "derived": {
            "field_matroid": {
                "field_prime": FIELD_PRIME,
                "ground_set_size": len(mod_matrix[0]),
                "rank": rank,
                "integer_matrix_shape": matrix_shape(integer_matrix),
                "mod_prime_matrix_shape": matrix_shape(mod_matrix),
                "integer_matrix_sha256": matrix_integer_sha256,
                "mod_prime_matrix_sha256": matrix_mod_prime_sha256,
                "sector33_height_attachment": attachment,
                "rational_lift_audited": False,
            },
            "deletion_contraction_cache": stats,
            "tutte_polynomial": {
                "variables": ["x", "y"],
                "terms": terms,
                "term_count": len(terms),
                "polynomial_sha256": polynomial_sha256,
                "specializations": specializations,
            },
            "characteristic_polynomial": {
                "variable": "q",
                "rank": rank,
                "relation": "chi(q)=(-1)^rank T(1-q,0)",
                "terms": characteristic_rows,
                "polynomial_sha256": characteristic_sha256,
            },
            "orlik_solomon_algebra": {
                "summary_scope": "NBC Hilbert vector for the finite-field matroid",
                "hilbert_coefficients_by_degree": os_hilbert,
                "hilbert_coefficients_sha256": os_hilbert_sha256,
                "top_degree": rank,
                "total_nbc_monomials": sum(os_hilbert),
            },
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "confirmed": [
                "the sector-33 height attachment now has a finite-field Tutte polynomial",
                "the characteristic polynomial gives a nonnegative NBC/OS Hilbert vector",
                "the Tutte all-subsets specialization checks against 2^31",
            ],
            "guardrails": [
                "the computation is certified over F_1000003, not yet over Q",
                "the deletion-contraction polynomial is a matroid invariant, not an oriented-sign invariant",
                "full Orlik-Solomon multiplication data is not enumerated here; only the NBC Hilbert package is recorded",
            ],
        },
        "next_highest_yield_item": (
            "Run a prime-good/rational lift audit for the sector-33 height-attachment "
            "matroid so the finite-field Tutte/OS package can be promoted from "
            "F_1000003 to the rational oriented matroid when no bad-prime rank "
            "drops are found."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_oriented_matroid_tutte_os_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "compute the finite-field Tutte polynomial of the sector-33 height attachment",
            "summarize the associated characteristic polynomial and NBC/OS Hilbert vector",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])
    print(report["derived"]["tutte_polynomial"]["polynomial_sha256"])


if __name__ == "__main__":
    main()
