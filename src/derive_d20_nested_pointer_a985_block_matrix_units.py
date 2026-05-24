from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np

try:
    from src.paths import GENERATED, ROOT
except ImportError:  # Supports `python src/derive_d20_nested_pointer_a985_block_matrix_units.py`.
    from paths import GENERATED, ROOT


FIELD_PRIME = 1_000_003
RELATION_COUNT = 985
MAX_BLOCK_DIMENSION = 12
STATUS_CERTIFIED = "D20_NESTED_POINTER_A985_BLOCK_MATRIX_UNITS_CERTIFIED"
STATUS_NEEDS_REVIEW = "D20_NESTED_POINTER_A985_BLOCK_MATRIX_UNITS_NEEDS_REVIEW"

DEFAULT_TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"
DEFAULT_CENTER_NPZ = ROOT / "data" / "a236_compute" / "cache" / "a985_center_idempotents_mod1000003.npz"
DEFAULT_OUT_NPZ = GENERATED / "d20_nested_pointer_a985_block_matrix_units.npz"
DEFAULT_OUT_JSON = GENERATED / "d20_nested_pointer_a985_block_matrix_units_report.json"


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


def array_digest(array: np.ndarray) -> str:
    data = np.ascontiguousarray(array)
    h = hashlib.sha256()
    h.update(str(data.dtype).encode("ascii"))
    h.update(str(data.shape).encode("ascii"))
    h.update(data.tobytes())
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def signed_mod(value: int, mod: int = FIELD_PRIME) -> int:
    value %= mod
    return value if value <= mod // 2 else value - mod


def vector_digest(vec: np.ndarray) -> dict[str, Any]:
    entries = [[int(i), int(vec[i]) % FIELD_PRIME] for i in np.nonzero(vec % FIELD_PRIME)[0]]
    values = [value for _, value in entries]
    return {
        "support": len(entries),
        "coefficient_sum": int(sum(values) % FIELD_PRIME),
        "coefficient_sum_signed": signed_mod(int(sum(values))),
        "coefficient_abs_sum_signed_lift": int(sum(abs(signed_mod(value)) for value in values)),
        "sha256": hashlib.sha256(canonical(entries)).hexdigest(),
    }


def rank_mod(matrix: np.ndarray, mod: int = FIELD_PRIME) -> int:
    matrix = np.asarray(matrix, dtype=np.int64).copy() % mod
    row_count, col_count = matrix.shape
    rank = 0
    for col in range(col_count):
        rows = np.nonzero(matrix[rank:, col])[0]
        if rows.size == 0:
            continue
        pivot = rank + int(rows[0])
        if pivot != rank:
            matrix[[rank, pivot]] = matrix[[pivot, rank]]
        inv = pow(int(matrix[rank, col]), -1, mod)
        matrix[rank, :] = (matrix[rank, :] * inv) % mod
        indices = np.nonzero(matrix[:, col])[0]
        indices = indices[indices != rank]
        if len(indices):
            values = matrix[indices, col].copy()
            matrix[indices, :] = (matrix[indices, :] - values[:, None] * matrix[rank, :]) % mod
        rank += 1
        if rank == row_count:
            break
    return rank


def inv_mod_matrix(matrix: np.ndarray, mod: int = FIELD_PRIME) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.int64).copy() % mod
    n = int(matrix.shape[0])
    if matrix.shape != (n, n):
        raise ValueError(f"expected a square matrix, got {matrix.shape}")
    aug = np.concatenate([matrix, np.eye(n, dtype=np.int64)], axis=1)
    rank = 0
    for col in range(n):
        rows = np.nonzero(aug[rank:, col])[0]
        if rows.size == 0:
            raise ValueError("singular matrix over verifier field")
        pivot = rank + int(rows[0])
        if pivot != rank:
            aug[[rank, pivot]] = aug[[pivot, rank]]
        inv = pow(int(aug[rank, col]), -1, mod)
        aug[rank, :] = (aug[rank, :] * inv) % mod
        indices = np.nonzero(aug[:, col])[0]
        indices = indices[indices != rank]
        if len(indices):
            values = aug[indices, col].copy()
            aug[indices, :] = (aug[indices, :] - values[:, None] * aug[rank, :]) % mod
        rank += 1
    return aug[:, n:]


def pivot_rows_for_columns(columns: np.ndarray, mod: int = FIELD_PRIME) -> list[int]:
    rows: list[int] = []
    chart: list[list[int]] = []
    rank = 0
    for idx in range(columns.shape[0]):
        candidate = (
            np.array(chart + [columns[idx].astype(int).tolist()], dtype=np.int64)
            if chart
            else columns[idx : idx + 1]
        )
        candidate_rank = rank_mod(candidate, mod)
        if candidate_rank > rank:
            rows.append(idx)
            chart = candidate.astype(int).tolist()
            rank = candidate_rank
            if rank == columns.shape[1]:
                return rows
    raise RuntimeError("failed to select a full-rank row chart")


class MultiplicationOracle:
    def __init__(self, triples: np.ndarray, mod: int = FIELD_PRIME) -> None:
        self.triples = np.asarray(triples, dtype=np.int64)
        self.mod = mod
        self.alpha = self.triples[:, 0]
        self.beta = self.triples[:, 1]
        self.gamma = self.triples[:, 2]
        self.weights = self.triples[:, 3] % mod
        self.by_alpha = [np.where(self.alpha == idx)[0] for idx in range(RELATION_COUNT)]
        self.by_beta = [np.where(self.beta == idx)[0] for idx in range(RELATION_COUNT)]

    def product(self, left: np.ndarray, right: np.ndarray) -> np.ndarray:
        values = (((left[self.alpha] * right[self.beta]) % self.mod) * self.weights) % self.mod
        out = np.zeros(RELATION_COUNT, dtype=np.int64)
        np.add.at(out, self.gamma, values)
        return out % self.mod

    def basis_left_product(self, basis_index: int, right: np.ndarray) -> np.ndarray:
        rows = self.by_alpha[basis_index]
        out = np.zeros(RELATION_COUNT, dtype=np.int64)
        values = (self.weights[rows] * right[self.beta[rows]]) % self.mod
        np.add.at(out, self.gamma[rows], values)
        return out % self.mod

    def basis_right_product(self, left: np.ndarray, basis_index: int) -> np.ndarray:
        rows = self.by_beta[basis_index]
        out = np.zeros(RELATION_COUNT, dtype=np.int64)
        values = (self.weights[rows] * left[self.alpha[rows]]) % self.mod
        np.add.at(out, self.gamma[rows], values)
        return out % self.mod


def roots_by_field_scan(coefficients: np.ndarray, mod: int = FIELD_PRIME, chunk: int = 250_000) -> list[int]:
    """Return verifier-field roots of x^d - sum_i coefficients[i] x^i."""
    coefficients = np.asarray(coefficients, dtype=np.int64) % mod
    degree = int(coefficients.size)
    roots: list[int] = []
    for start in range(0, mod, chunk):
        x = np.arange(start, min(start + chunk, mod), dtype=np.int64)
        values = np.ones_like(x)
        for idx in range(degree - 1, -1, -1):
            values = (values * x - int(coefficients[idx])) % mod
        hits = x[values == 0]
        if hits.size:
            roots.extend(int(value) for value in hits.tolist())
        if len(roots) > degree:
            break
    return roots


def derivative_at_relation(coefficients: np.ndarray, lam: int, mod: int = FIELD_PRIME) -> int:
    degree = int(coefficients.size)
    value = (degree * pow(int(lam), degree - 1, mod)) % mod
    for idx in range(1, degree):
        term = (idx * int(coefficients[idx]) % mod) * pow(int(lam), idx - 1, mod)
        value = (value - term) % mod
    return value % mod


def quotient_by_linear_root(coefficients: np.ndarray, lam: int, mod: int = FIELD_PRIME) -> np.ndarray:
    f_ascending = [(-int(c)) % mod for c in coefficients] + [1]
    f_descending = list(reversed(f_ascending))
    quotient_descending = [f_descending[0]]
    for value in f_descending[1:-1]:
        quotient_descending.append((int(value) + int(lam) * quotient_descending[-1]) % mod)
    remainder = (f_descending[-1] + int(lam) * quotient_descending[-1]) % mod
    if remainder:
        raise ValueError("linear root division produced a nonzero remainder")
    return np.array(list(reversed(quotient_descending)), dtype=np.int64)


def evaluate_polynomial_in_powers(coefficients: np.ndarray, powers: list[np.ndarray]) -> np.ndarray:
    out = np.zeros(RELATION_COUNT, dtype=np.int64)
    for idx, coeff in enumerate(coefficients):
        if int(coeff):
            out = (out + int(coeff) * powers[idx]) % FIELD_PRIME
    return out % FIELD_PRIME


def ideal_basis(
    oracle: MultiplicationOracle,
    primitive_idempotent: np.ndarray,
    target_dimension: int,
    side: str,
) -> tuple[np.ndarray | None, list[int], int]:
    columns: list[np.ndarray] = []
    source_indices: list[int] = []
    rank = 0
    for source_index in [-1, *range(RELATION_COUNT)]:
        if source_index == -1:
            candidate = primitive_idempotent % FIELD_PRIME
        elif side == "left":
            candidate = oracle.basis_left_product(source_index, primitive_idempotent)
        else:
            candidate = oracle.basis_right_product(primitive_idempotent, source_index)
        if not np.count_nonzero(candidate):
            continue
        candidate_columns = columns + [candidate]
        candidate_rank = rank_mod(np.stack(candidate_columns, axis=1))
        if candidate_rank > rank:
            columns.append(candidate)
            source_indices.append(int(source_index))
            rank = candidate_rank
            if rank > target_dimension:
                return None, source_indices, rank
    if rank != target_dimension:
        return None, source_indices, rank
    return np.stack(columns, axis=1) % FIELD_PRIME, source_indices, rank


def scalar_multiple_of(reference: np.ndarray, vector: np.ndarray) -> int | None:
    support = np.nonzero(reference % FIELD_PRIME)[0]
    if support.size == 0:
        return None
    pivot = int(support[0])
    scalar = (int(vector[pivot]) * pow(int(reference[pivot]), -1, FIELD_PRIME)) % FIELD_PRIME
    if np.array_equal(vector % FIELD_PRIME, (scalar * reference) % FIELD_PRIME):
        return scalar
    return None


def find_first_relation(
    oracle: MultiplicationOracle,
    central_page: np.ndarray,
    block_dimension: int,
    rng: np.random.Generator,
    max_trials: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    if block_dimension == 1:
        return central_page % FIELD_PRIME, {
            "random_trials": 0,
            "minimal_relation_degree": 1,
            "roots_seen": 1,
            "chosen_root": 0,
        }

    best_degree = 0
    best_root_count = 0
    for trial in range(max_trials):
        random_coefficients = rng.integers(0, FIELD_PRIME, size=RELATION_COUNT, dtype=np.int64)
        element = oracle.product(central_page, random_coefficients)
        powers = [central_page % FIELD_PRIME]
        value = central_page % FIELD_PRIME
        for _ in range(block_dimension):
            value = oracle.product(value, element)
            powers.append(value)

        minimal_degree = None
        relation_coefficients = None
        for degree in range(1, block_dimension + 1):
            prior_powers = np.stack(powers[:degree], axis=1)
            if rank_mod(prior_powers) < degree:
                break
            if rank_mod(np.stack(powers[: degree + 1], axis=1)) == degree:
                rows = pivot_rows_for_columns(prior_powers)
                relation_coefficients = (inv_mod_matrix(prior_powers[rows, :]) @ powers[degree][rows]) % FIELD_PRIME
                minimal_degree = degree
                break
        if minimal_degree is None or relation_coefficients is None:
            continue

        best_degree = max(best_degree, int(minimal_degree))
        roots = roots_by_field_scan(relation_coefficients)
        best_root_count = max(best_root_count, len(roots))
        for root in roots:
            derivative = derivative_at_relation(relation_coefficients, root)
            if derivative == 0:
                continue
            quotient_coefficients = quotient_by_linear_root(relation_coefficients, root)
            candidate = (
                evaluate_polynomial_in_powers(quotient_coefficients, powers)
                * pow(int(derivative), -1, FIELD_PRIME)
            ) % FIELD_PRIME
            if not np.array_equal(oracle.product(candidate, candidate), candidate % FIELD_PRIME):
                continue
            left_basis, _, left_rank = ideal_basis(oracle, candidate, block_dimension, "left")
            if left_basis is None or left_rank != block_dimension:
                continue
            right_basis, _, right_rank = ideal_basis(oracle, candidate, block_dimension, "right")
            if right_basis is None or right_rank != block_dimension:
                continue
            return candidate % FIELD_PRIME, {
                "random_trials": int(trial + 1),
                "minimal_relation_degree": int(minimal_degree),
                "roots_seen": int(len(roots)),
                "chosen_root": int(root),
                "random_element_sha256": array_digest(element),
                "minimal_relation_coefficients_sha256": array_digest(relation_coefficients),
            }

    raise RuntimeError(
        f"failed to find a primitive corner idempotent for block dimension {block_dimension}; "
        f"best relation degree {best_degree}, best root count {best_root_count}"
    )


def basis_pairing_matrix(
    oracle: MultiplicationOracle,
    corner_idempotent: np.ndarray,
    left_basis: np.ndarray,
    right_basis: np.ndarray,
) -> tuple[np.ndarray, int]:
    dimension = int(left_basis.shape[1])
    matrix = np.zeros((dimension, dimension), dtype=np.int64)
    scalar_failures = 0
    for row in range(dimension):
        for col in range(dimension):
            product = oracle.product(right_basis[:, row], left_basis[:, col])
            scalar = scalar_multiple_of(corner_idempotent, product)
            if scalar is None:
                scalar_failures += 1
                scalar = 0
            matrix[row, col] = int(scalar)
    return matrix % FIELD_PRIME, scalar_failures


def build_block_units(
    oracle: MultiplicationOracle,
    raw_sector: int,
    central_page: np.ndarray,
    block_dimension: int,
    rng: np.random.Generator,
    max_trials: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    corner, primitive_info = find_first_relation(oracle, central_page, block_dimension, rng, max_trials)
    left_basis, left_sources, left_rank = ideal_basis(oracle, corner, block_dimension, "left")
    right_basis, right_sources, right_rank = ideal_basis(oracle, corner, block_dimension, "right")
    if left_basis is None or right_basis is None:
        raise RuntimeError(f"failed to build left/right ideal bases for raw sector {raw_sector}")

    pairing, scalar_failures = basis_pairing_matrix(oracle, corner, left_basis, right_basis)
    pairing_rank = rank_mod(pairing)
    if scalar_failures or pairing_rank != block_dimension:
        raise RuntimeError(
            f"degenerate corner pairing for raw sector {raw_sector}: "
            f"scalar_failures={scalar_failures}, rank={pairing_rank}"
        )
    right_dual_basis = (right_basis @ inv_mod_matrix(pairing).T) % FIELD_PRIME

    bridge_failures = 0
    zero = np.zeros(RELATION_COUNT, dtype=np.int64)
    for row in range(block_dimension):
        for col in range(block_dimension):
            product = oracle.product(right_dual_basis[:, row], left_basis[:, col])
            target = corner if row == col else zero
            if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
                bridge_failures += 1

    units: list[np.ndarray] = []
    for i in range(block_dimension):
        for j in range(block_dimension):
            units.append(oracle.product(left_basis[:, i], right_dual_basis[:, j]))
    matrix_units = np.stack(units, axis=1) % FIELD_PRIME
    diagonal_sum = np.sum(
        matrix_units[:, [i * block_dimension + i for i in range(block_dimension)]],
        axis=1,
    ) % FIELD_PRIME

    info = {
        **primitive_info,
        "raw_sector": int(raw_sector),
        "block_dimension": int(block_dimension),
        "left_ideal_rank": int(left_rank),
        "right_ideal_rank": int(right_rank),
        "left_basis_relation_indices": [int(value) for value in left_sources],
        "right_basis_relation_indices": [int(value) for value in right_sources],
        "corner_pairing_rank": int(pairing_rank),
        "corner_pairing_scalar_failures": int(scalar_failures),
        "bridge_delta_failures": int(bridge_failures),
        "diagonal_sum_equals_central_page": bool(np.array_equal(diagonal_sum, central_page % FIELD_PRIME)),
        "corner_idempotent": vector_digest(corner),
        "matrix_unit_block_sha256": array_digest(matrix_units),
    }
    return matrix_units, corner, left_basis, right_dual_basis, info


def padded_source_indices(rows: Iterable[list[int]]) -> np.ndarray:
    out = np.full((39, MAX_BLOCK_DIMENSION), -2, dtype=np.int64)
    for row_idx, row in enumerate(rows):
        out[row_idx, : len(row)] = np.asarray(row, dtype=np.int64)
    return out


def direct_product_sample(
    oracle: MultiplicationOracle,
    matrix_units: np.ndarray,
    unit_sector: np.ndarray,
    unit_i: np.ndarray,
    unit_j: np.ndarray,
    column_by_key: dict[tuple[int, int, int], int],
    sample_size: int,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    total = int(matrix_units.shape[1])
    zero = np.zeros(RELATION_COUNT, dtype=np.int64)
    failures: list[dict[str, int]] = []
    if sample_size <= 0:
        return {"checked": 0, "failures": [], "failure_count": 0}
    for _ in range(sample_size):
        left = int(rng.integers(0, total))
        right = int(rng.integers(0, total))
        product = oracle.product(matrix_units[:, left], matrix_units[:, right])
        target = zero
        if int(unit_sector[left]) == int(unit_sector[right]) and int(unit_j[left]) == int(unit_i[right]):
            target_col = column_by_key[(int(unit_sector[left]), int(unit_i[left]), int(unit_j[right]))]
            target = matrix_units[:, target_col]
        if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
            failures.append({"left_column": left, "right_column": right})
            if len(failures) >= 8:
                break
    return {"checked": int(sample_size), "failures": failures, "failure_count": len(failures)}


def build_package(
    tensor_npz: Path,
    center_npz: Path,
    out_npz: Path,
    out_json: Path,
    seed: int,
    max_trials: int,
    sample_products: int,
) -> dict[str, Any]:
    tensor = np.load(tensor_npz)
    center = np.load(center_npz)
    triples = np.asarray(tensor["triples"], dtype=np.int64)
    central_pages = np.asarray(center["idempotents_full"], dtype=np.int64) % FIELD_PRIME
    block_dimensions = np.asarray(center["block_dims"], dtype=np.int64)
    identity_indices = np.asarray(center["identity_indices"], dtype=np.int64)
    modulus = int(np.asarray(center["modulus"], dtype=np.int64)[0])
    if modulus != FIELD_PRIME:
        raise ValueError(f"expected field prime {FIELD_PRIME}, got {modulus}")
    if central_pages.shape != (RELATION_COUNT, 39):
        raise ValueError(f"expected 985 x 39 central pages, got {central_pages.shape}")

    oracle = MultiplicationOracle(triples)
    rng = np.random.default_rng(seed)

    matrix_unit_blocks: list[np.ndarray] = []
    corner_blocks: list[np.ndarray] = []
    left_basis_blocks: list[np.ndarray] = []
    right_dual_basis_blocks: list[np.ndarray] = []
    sector_rows: list[dict[str, Any]] = []
    sector_offsets = [0]
    left_offsets = [0]
    unit_sector: list[int] = []
    unit_i: list[int] = []
    unit_j: list[int] = []
    left_basis_sources: list[list[int]] = []
    right_basis_sources: list[list[int]] = []
    primitive_trials = []
    primitive_roots = []
    primitive_degrees = []
    primitive_roots_seen = []

    for raw_sector in range(39):
        dimension = int(block_dimensions[raw_sector])
        units, corner, left_basis, right_dual_basis, info = build_block_units(
            oracle,
            raw_sector,
            central_pages[:, raw_sector],
            dimension,
            rng,
            max_trials,
        )
        start = sector_offsets[-1]
        sector_offsets.append(start + dimension * dimension)
        left_start = left_offsets[-1]
        left_offsets.append(left_start + dimension)
        for i in range(dimension):
            for j in range(dimension):
                unit_sector.append(raw_sector)
                unit_i.append(i)
                unit_j.append(j)
        matrix_unit_blocks.append(units)
        corner_blocks.append(corner)
        left_basis_blocks.append(left_basis)
        right_dual_basis_blocks.append(right_dual_basis)
        left_basis_sources.append(info["left_basis_relation_indices"])
        right_basis_sources.append(info["right_basis_relation_indices"])
        primitive_trials.append(int(info["random_trials"]))
        primitive_roots.append(int(info["chosen_root"]))
        primitive_degrees.append(int(info["minimal_relation_degree"]))
        primitive_roots_seen.append(int(info["roots_seen"]))
        sector_rows.append(
            {
                **info,
                "matrix_unit_column_range": [int(start), int(start + dimension * dimension - 1)],
                "left_basis_column_range": [int(left_start), int(left_start + dimension - 1)],
            }
        )

    matrix_units = np.concatenate(matrix_unit_blocks, axis=1) % FIELD_PRIME
    corner_idempotents = np.stack(corner_blocks, axis=1) % FIELD_PRIME
    left_ideal_basis = np.concatenate(left_basis_blocks, axis=1) % FIELD_PRIME
    right_dual_basis = np.concatenate(right_dual_basis_blocks, axis=1) % FIELD_PRIME
    unit_sector_array = np.asarray(unit_sector, dtype=np.int64)
    unit_i_array = np.asarray(unit_i, dtype=np.int64)
    unit_j_array = np.asarray(unit_j, dtype=np.int64)
    sector_offsets_array = np.asarray(sector_offsets, dtype=np.int64)
    left_offsets_array = np.asarray(left_offsets, dtype=np.int64)
    identity = np.zeros(RELATION_COUNT, dtype=np.int64)
    identity[identity_indices] = 1

    diagonal_columns = [
        int(sector_offsets_array[sector] + i * int(block_dimensions[sector]) + i)
        for sector in range(39)
        for i in range(int(block_dimensions[sector]))
    ]
    global_diagonal_sum = np.sum(matrix_units[:, diagonal_columns], axis=1) % FIELD_PRIME
    unit_count_expected = int(np.sum(block_dimensions * block_dimensions))
    column_by_key = {
        (int(sector), int(i), int(j)): col
        for col, (sector, i, j) in enumerate(zip(unit_sector_array, unit_i_array, unit_j_array))
    }
    sample = direct_product_sample(
        oracle,
        matrix_units,
        unit_sector_array,
        unit_i_array,
        unit_j_array,
        column_by_key,
        sample_products,
        seed + 17,
    )

    checks = {
        "center_page_count_is_39": central_pages.shape[1] == 39,
        "matrix_unit_column_count_is_985": matrix_units.shape == (RELATION_COUNT, 985),
        "sum_block_d_squared_is_985": unit_count_expected == RELATION_COUNT,
        "all_block_diagonal_sums_equal_central_pages": all(
            bool(row["diagonal_sum_equals_central_page"]) for row in sector_rows
        ),
        "bridge_delta_failures_zero": sum(int(row["bridge_delta_failures"]) for row in sector_rows) == 0,
        "corner_pairing_scalar_failures_zero": sum(int(row["corner_pairing_scalar_failures"]) for row in sector_rows)
        == 0,
        "all_left_ideal_ranks_match_block_dimension": all(
            int(row["left_ideal_rank"]) == int(row["block_dimension"]) for row in sector_rows
        ),
        "all_right_ideal_ranks_match_block_dimension": all(
            int(row["right_ideal_rank"]) == int(row["block_dimension"]) for row in sector_rows
        ),
        "global_diagonal_sum_is_A985_unit": bool(np.array_equal(global_diagonal_sum, identity % FIELD_PRIME)),
        "sampled_direct_matrix_unit_products_pass": int(sample["failure_count"]) == 0,
    }
    all_checks_pass = all(checks.values())

    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_npz,
        field_prime=np.array([FIELD_PRIME], dtype=np.int64),
        matrix_units=matrix_units.astype(np.int64),
        unit_sector=unit_sector_array,
        unit_i=unit_i_array,
        unit_j=unit_j_array,
        sector_offsets=sector_offsets_array,
        block_dimensions=block_dimensions.astype(np.int64),
        central_pages=central_pages.astype(np.int64),
        corner_idempotents=corner_idempotents.astype(np.int64),
        left_ideal_basis=left_ideal_basis.astype(np.int64),
        right_dual_basis=right_dual_basis.astype(np.int64),
        left_basis_offsets=left_offsets_array,
        right_dual_basis_offsets=left_offsets_array,
        left_basis_relation_indices=padded_source_indices(left_basis_sources),
        right_basis_relation_indices=padded_source_indices(right_basis_sources),
        primitive_random_trials=np.asarray(primitive_trials, dtype=np.int64),
        primitive_chosen_roots=np.asarray(primitive_roots, dtype=np.int64),
        primitive_minimal_degrees=np.asarray(primitive_degrees, dtype=np.int64),
        primitive_roots_seen=np.asarray(primitive_roots_seen, dtype=np.int64),
        identity_indices=identity_indices.astype(np.int64),
    )

    histogram = Counter(int(value) for value in block_dimensions.tolist())
    report = {
        "schema": "d20.nested_pointer.a985_block_matrix_units.source_drop",
        "status": STATUS_CERTIFIED if all_checks_pass else STATUS_NEEDS_REVIEW,
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "The 39 generated raw-sector central pages of A985 now carry explicit block matrix units "
            "u[s;i,j] in the raw 985-orbital basis over F_1000003."
        ),
        "previous_package": "d20_nested_pointer_a985_orbital_central_idempotents_package",
        "inputs": {
            "t985_tensor": {"path": rel(tensor_npz), "sha256": sha_file(tensor_npz)},
            "raw_orbital_central_pages": {"path": rel(center_npz), "sha256": sha_file(center_npz)},
        },
        "outputs": {
            "matrix_unit_npz": {
                "path": rel(out_npz),
                "sha256": sha_file(out_npz),
                "matrix_units_array": "matrix_units",
                "column_formula": "column = sector_offsets[s] + i * block_dimensions[s] + j",
            },
            "report": {"path": rel(out_json)},
        },
        "construction": {
            "method": (
                "For each central block e_s A985, find a primitive corner idempotent p by a simple root "
                "of a verifier-field minimal relation, build bases of A p and p A, dualize the pAp scalar "
                "pairing, and emit u[s;i,j] = x_i y_j."
            ),
            "matrix_unit_law": (
                "The certificate verifies y_j x_i = delta_ji p in every block; associativity of the raw "
                "T985 algebra then gives u_ij u_kl = delta_jk u_il for all emitted columns."
            ),
            "sector_order_boundary": (
                "The raw sector order is inherited from the separating central-element cache and is not "
                "matched here to legacy sector labels 0..38."
            ),
        },
        "checks": checks,
        "derived": {
            "center_dimension": 39,
            "block_dimensions": [int(value) for value in block_dimensions.tolist()],
            "block_dimension_histogram": {str(key): int(histogram[key]) for key in sorted(histogram)},
            "total_matrix_units": int(matrix_units.shape[1]),
            "left_right_bridge_products_checked": int(sum(int(d) * int(d) for d in block_dimensions.tolist())),
            "sampled_direct_matrix_unit_products": sample,
            "matrix_units_sha256": array_digest(matrix_units),
            "corner_idempotents_sha256": array_digest(corner_idempotents),
            "left_ideal_basis_sha256": array_digest(left_ideal_basis),
            "right_dual_basis_sha256": array_digest(right_dual_basis),
            "central_pages_sha256": array_digest(central_pages),
            "sector_offsets": [int(value) for value in sector_offsets_array.tolist()],
            "identity_indices": [int(value) for value in identity_indices.tolist()],
            "global_diagonal_sum": vector_digest(global_diagonal_sum),
            "sector_rows": sector_rows,
        },
        "next_highest_yield_item": (
            "Match this raw-sector order to the legacy sector labels, then transport legacy sector-local "
            "statements onto the emitted u[s;i,j] coordinates."
        ),
        "all_checks_pass": bool(all_checks_pass),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build raw-orbital A985 block matrix units.")
    parser.add_argument("--tensor", default=str(DEFAULT_TENSOR_NPZ))
    parser.add_argument("--center", default=str(DEFAULT_CENTER_NPZ))
    parser.add_argument("--out-npz", default=str(DEFAULT_OUT_NPZ))
    parser.add_argument("--out-json", default=str(DEFAULT_OUT_JSON))
    parser.add_argument("--seed", type=int, default=20_260_524)
    parser.add_argument("--max-trials", type=int, default=100)
    parser.add_argument("--sample-products", type=int, default=256)
    args = parser.parse_args()

    report = build_package(
        ROOT / args.tensor if not Path(args.tensor).is_absolute() else Path(args.tensor),
        ROOT / args.center if not Path(args.center).is_absolute() else Path(args.center),
        ROOT / args.out_npz if not Path(args.out_npz).is_absolute() else Path(args.out_npz),
        ROOT / args.out_json if not Path(args.out_json).is_absolute() else Path(args.out_json),
        args.seed,
        args.max_trials,
        args.sample_products,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
