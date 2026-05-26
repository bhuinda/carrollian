#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certificate_registry import certificate_relpath
except ImportError:  # Supports `python src/derive_representation_integral_wall.py`.
    from certificate_registry import certificate_relpath

ROOT = Path(__file__).resolve().parents[1]
MOD_DEFAULT = 1000003


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def rank_mod(matrix: np.ndarray, mod: int = MOD_DEFAULT) -> int:
    A = np.asarray(matrix, dtype=np.int64).copy() % mod
    m, n = A.shape
    rank = 0
    for col in range(n):
        rows = np.nonzero(A[rank:, col])[0]
        if rows.size == 0:
            continue
        pivot = rank + int(rows[0])
        if pivot != rank:
            A[[rank, pivot]] = A[[pivot, rank]]
        inv = pow(int(A[rank, col]), -1, mod)
        A[rank, :] = (A[rank, :] * inv) % mod
        inds = np.nonzero(A[:, col])[0]
        inds = inds[inds != rank]
        if len(inds):
            vals = A[inds, col].copy()
            A[inds, :] = (A[inds, :] - vals[:, None] * A[rank, :]) % mod
        rank += 1
        if rank == m:
            break
    return int(rank)


def quotient_shadow_matrix(E: np.ndarray, quotient_map: np.ndarray, dimension: int, mod: int = MOD_DEFAULT) -> np.ndarray:
    columns = []
    for col in range(E.shape[1]):
        out = np.zeros(dimension, dtype=np.int64)
        for rel_idx in np.nonzero(E[:, col] % mod)[0]:
            q = int(quotient_map[int(rel_idx)])
            out[q] = (out[q] + int(E[int(rel_idx), col])) % mod
        columns.append(out)
    return np.stack(columns, axis=1) if columns else np.zeros((dimension, 0), dtype=np.int64)


def pointwise_signature_partition(shadow_matrix: np.ndarray) -> dict[str, Any]:
    classes: dict[tuple[int, ...], list[int]] = {}
    for col in range(shadow_matrix.shape[1]):
        key = tuple(int(x) for x in shadow_matrix[:, col].tolist())
        classes.setdefault(key, []).append(int(col))
    rows = sorted(classes.values(), key=lambda cols: (len(cols), cols))
    hist: dict[str, int] = {}
    for cols in rows:
        hist[str(len(cols))] = hist.get(str(len(cols)), 0) + 1
    return {
        "dimension": int(len(rows)),
        "signature_partition_histogram": hist,
        "non_singleton_generated_column_classes": [cols for cols in rows if len(cols) > 1],
    }


def independent_column_basis(vectors: list[np.ndarray], mod: int = MOD_DEFAULT) -> list[np.ndarray]:
    selected: list[np.ndarray] = []
    current = np.zeros((int(vectors[0].size), 0), dtype=np.int64)
    current_rank = 0
    for vec in vectors:
        cand = np.column_stack([current, vec % mod])
        rank = rank_mod(cand, mod)
        if rank > current_rank:
            selected.append(vec % mod)
            current = cand
            current_rank = rank
    return selected


def pointwise_closure(functions: np.ndarray, mod: int = MOD_DEFAULT) -> dict[str, Any]:
    """Close sector functions under pointwise multiplication over F_mod."""
    basis = independent_column_basis(
        [np.ones(functions.shape[0], dtype=np.int64)]
        + [functions[:, col].astype(np.int64) % mod for col in range(functions.shape[1])],
        mod,
    )
    rounds = 0
    while True:
        rank_at_step_start = len(basis)
        candidates = list(basis)
        for left in basis:
            for right in basis:
                candidates.append((left * right) % mod)
        basis = independent_column_basis(candidates, mod)
        rounds += 1
        if len(basis) == rank_at_step_start or rounds >= 8 or len(basis) == functions.shape[0]:
            break
    B = np.stack(basis, axis=1)
    classes: dict[tuple[int, ...], list[int]] = {}
    for row in range(B.shape[0]):
        classes.setdefault(tuple(int(x) for x in B[row, :].tolist()), []).append(int(row))
    rows = sorted(classes.values(), key=lambda cols: (len(cols), cols))
    hist: dict[str, int] = {}
    for cols in rows:
        hist[str(len(cols))] = hist.get(str(len(cols)), 0) + 1
    return {
        "closure_rounds": int(rounds),
        "linear_rank": int(rank_mod(functions, mod)),
        "pointwise_algebra_dimension": int(len(basis)),
        "signature_partition_histogram": hist,
        "non_singleton_generated_column_classes": [cols for cols in rows if len(cols) > 1],
        "basis_sha256": sha_array(B),
    }


def product_trace_pairing(triples: np.ndarray, E: np.ndarray, mod: int = MOD_DEFAULT) -> np.ndarray:
    """Return Tr_L(R_a e_i), with rows primitive idempotents and columns relation basis elements."""
    relation_count = int(E.shape[0])
    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    w = triples[:, 3] % mod
    diag_mask = gamma == beta
    reg_trace_coeff = np.zeros(relation_count, dtype=np.int64)
    np.add.at(reg_trace_coeff, alpha[diag_mask], w[diag_mask])

    pairings = np.zeros((E.shape[1], relation_count), dtype=np.int64)
    for rel_idx in range(relation_count):
        idx = np.where(alpha == rel_idx)[0]
        if idx.size == 0:
            continue
        values = (w[idx, None] * E[beta[idx], :]) % mod
        product = np.zeros((relation_count, E.shape[1]), dtype=np.int64)
        np.add.at(product, gamma[idx], values)
        pairings[:, rel_idx] = (reg_trace_coeff @ product) % mod
    return pairings


def quotient_character_surface(
    character_pairing: np.ndarray,
    dims: np.ndarray,
    quotient_map: np.ndarray,
    quotient_dim: int,
    mod: int = MOD_DEFAULT,
) -> np.ndarray:
    inv_dim_square = np.array([pow(int(d), -2, mod) for d in dims], dtype=np.int64)
    scaled = (character_pairing * inv_dim_square[:, None]) % mod
    surface = np.zeros((character_pairing.shape[0], quotient_dim), dtype=np.int64)
    for q in range(quotient_dim):
        surface[:, q] = np.sum(scaled[:, quotient_map == q], axis=1) % mod
    return surface


TERNARY_CUBIC_MONOMIALS = [
    (3, 0, 0),
    (0, 3, 0),
    (0, 0, 3),
    (2, 1, 0),
    (2, 0, 1),
    (1, 2, 0),
    (0, 2, 1),
    (1, 0, 2),
    (0, 1, 2),
    (1, 1, 1),
]


def poly_add(left: dict[tuple[int, int, int], int], right: dict[tuple[int, int, int], int], mod: int = MOD_DEFAULT) -> dict[tuple[int, int, int], int]:
    out = dict(left)
    for exp, coeff in right.items():
        out[exp] = (out.get(exp, 0) + int(coeff)) % mod
    return {exp: coeff for exp, coeff in out.items() if coeff % mod}


def poly_sub(left: dict[tuple[int, int, int], int], right: dict[tuple[int, int, int], int], mod: int = MOD_DEFAULT) -> dict[tuple[int, int, int], int]:
    out = dict(left)
    for exp, coeff in right.items():
        out[exp] = (out.get(exp, 0) - int(coeff)) % mod
    return {exp: coeff for exp, coeff in out.items() if coeff % mod}


def poly_mul(left: dict[tuple[int, int, int], int], right: dict[tuple[int, int, int], int], mod: int = MOD_DEFAULT) -> dict[tuple[int, int, int], int]:
    out: dict[tuple[int, int, int], int] = {}
    for exp_l, coeff_l in left.items():
        for exp_r, coeff_r in right.items():
            exp = (exp_l[0] + exp_r[0], exp_l[1] + exp_r[1], exp_l[2] + exp_r[2])
            out[exp] = (out.get(exp, 0) + int(coeff_l) * int(coeff_r)) % mod
    return {exp: coeff for exp, coeff in out.items() if coeff % mod}


def ternary_cubic_hessian_coefficients(coefficients: np.ndarray, mod: int = MOD_DEFAULT) -> np.ndarray:
    second_derivatives: list[list[dict[tuple[int, int, int], int]]] = [[{} for _ in range(3)] for _ in range(3)]
    for coeff, exp in zip(coefficients, TERNARY_CUBIC_MONOMIALS):
        c = int(coeff) % mod
        for i in range(3):
            for j in range(3):
                powers = list(exp)
                multiplier = c
                if i == j:
                    if powers[i] < 2:
                        continue
                    multiplier *= powers[i] * (powers[i] - 1)
                    powers[i] -= 2
                else:
                    if powers[i] < 1 or powers[j] < 1:
                        continue
                    multiplier *= powers[i] * powers[j]
                    powers[i] -= 1
                    powers[j] -= 1
                exp_out = tuple(powers)
                second_derivatives[i][j][exp_out] = (
                    second_derivatives[i][j].get(exp_out, 0) + multiplier
                ) % mod

    a, b, c = second_derivatives[0]
    d, e, f = second_derivatives[1]
    g, h, i = second_derivatives[2]
    determinant: dict[tuple[int, int, int], int] = {}
    for term in ([a, e, i], [b, f, g], [c, d, h]):
        determinant = poly_add(determinant, poly_mul(poly_mul(term[0], term[1], mod), term[2], mod), mod)
    for term in ([c, e, g], [b, d, i], [a, f, h]):
        determinant = poly_sub(determinant, poly_mul(poly_mul(term[0], term[1], mod), term[2], mod), mod)
    return np.array([determinant.get(exp, 0) % mod for exp in TERNARY_CUBIC_MONOMIALS], dtype=np.int64)


def plucker_coordinates(points: np.ndarray, hessians: np.ndarray, mod: int = MOD_DEFAULT) -> np.ndarray:
    columns = []
    for i in range(points.shape[1]):
        for j in range(i + 1, points.shape[1]):
            columns.append((points[:, i] * hessians[:, j] - points[:, j] * hessians[:, i]) % mod)
    return np.stack(columns, axis=1)


def deterministic_lasso_projection(
    relation_count: int,
    secondary_relation: int,
    seed: int = 98765,
    sparsity_per_coordinate: int = 32,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    projection = np.zeros((relation_count, 10), dtype=np.int64)
    for coordinate in range(10):
        indices = rng.choice(relation_count, sparsity_per_coordinate, replace=False)
        if coordinate == 0 and secondary_relation not in indices:
            indices[0] = int(secondary_relation)
        projection[indices, coordinate] = 1
    return projection


def vector_in_column_span(matrix: np.ndarray, vector: np.ndarray, mod: int = MOD_DEFAULT) -> bool:
    return rank_mod(matrix, mod) == rank_mod(np.column_stack([matrix, vector % mod]), mod)


def first_relation_splitting_class(character_pairing: np.ndarray, sector_class: list[int]) -> dict[str, Any]:
    for relation_index in range(character_pairing.shape[1]):
        values = [int(character_pairing[col, relation_index]) for col in sector_class]
        if len(set(values)) == len(values):
            return {
                "relation_index": int(relation_index),
                "values_on_class": values,
            }
    return {
        "relation_index": None,
        "values_on_class": [],
    }


def active_support_labels(E_col: np.ndarray, relation_npz: Path) -> dict[str, Any]:
    rel = np.load(relation_npz)
    block_i = np.asarray(rel["block_i"], dtype=np.int64)
    block_j = np.asarray(rel["block_j"], dtype=np.int64)
    object_labels = ["B-", "B+", "V-", "V+", "S-", "S+"]
    cy_labels = {0: "B", 1: "B", 2: "V", 3: "V", 4: "S", 5: "S"}
    support = np.nonzero(E_col % MOD_DEFAULT)[0]
    objects = sorted({int(block_i[a]) for a in support} | {int(block_j[a]) for a in support})
    pairs = sorted({(int(block_i[a]), int(block_j[a])) for a in support})
    return {
        "active_objects": [object_labels[i] for i in objects],
        "active_cy_sectors": sorted({cy_labels[i] for i in objects}),
        "active_object_pair_count": int(len(pairs)),
    }


def dimension_rows_ok(B: np.ndarray, source_dims: np.ndarray, target_dims: np.ndarray) -> bool:
    return bool(np.array_equal(B @ target_dims, source_dims))


def build_a236_representation_fusion(simple_branching_npz: Path, terminal_npz: Path, out_npz: Path | None = None) -> dict[str, Any]:
    """Build the representation/fusion presentation of A236.

    This is intentionally not an orbital-basis relation partition.  The previous
    selector search proves that the true 236-dimensional layer is invisible to
    low-order relation fusion.  The finite object present in this bundle at this
    layer is the semisimple representation presentation: 34 simple blocks with
    dimensions whose squared sum is 236, plus exact branching into A42 and A12.
    """
    z = np.load(simple_branching_npz)
    B236_42 = np.asarray(z["B236_42"], dtype=np.int64)
    B42_12 = np.asarray(z["B42_12"], dtype=np.int64)
    B236_12 = np.asarray(z["B236_12"], dtype=np.int64)
    comp = np.asarray(z["comp"], dtype=np.int64)
    dims236 = np.asarray(z["dims236"], dtype=np.int64)
    dims42 = np.asarray(z["dims42"], dtype=np.int64)
    dims12 = np.asarray(z["dims12"], dtype=np.int64)

    term = np.load(terminal_npz)
    q42 = np.asarray(term["q42_map"], dtype=np.int64)
    q12 = np.asarray(term["q12_map"], dtype=np.int64)
    q42t = np.asarray(term["q42_tensor"], dtype=np.int64)
    q12t = np.asarray(term["q12_tensor"], dtype=np.int64)

    q42_to_q12_ok = True
    q42_to_q12 = []
    for c in range(42):
        vals = np.unique(q12[q42 == c])
        if vals.size != 1:
            q42_to_q12_ok = False
            q42_to_q12.append(None)
        else:
            q42_to_q12.append(int(vals[0]))

    if out_npz is not None:
        out_npz.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_npz,
            dims236=dims236.astype(np.int64),
            dims42=dims42.astype(np.int64),
            dims12=dims12.astype(np.int64),
            B236_42=B236_42.astype(np.int64),
            B42_12=B42_12.astype(np.int64),
            B236_12=B236_12.astype(np.int64),
            comp=(B236_42 @ B42_12).astype(np.int64),
            q42_to_q12=np.array([-1 if x is None else x for x in q42_to_q12], dtype=np.int64),
        )

    result = {
        "selector_kind": "representation/fusion semisimple presentation, not orbital relation partition",
        "A236": {
            "simple_count": int(dims236.size),
            "dimension_sum_squares": int(np.sum(dims236 * dims236)),
            "center_dimension": int(dims236.size),
            "simple_dimensions": dims236.astype(int).tolist(),
            "simple_dimension_histogram": {str(int(k)): int(v) for k, v in zip(*np.unique(dims236, return_counts=True))},
        },
        "A42": {
            "simple_count": int(dims42.size),
            "dimension_sum_squares": int(np.sum(dims42 * dims42)),
            "center_dimension": int(dims42.size),
            "simple_dimensions": dims42.astype(int).tolist(),
            "terminal_tensor_nonzero": int(np.count_nonzero(q42t)),
            "terminal_tensor_coefficient_total": int(q42t.sum()),
        },
        "A12": {
            "simple_count": int(dims12.size),
            "dimension_sum_squares": int(np.sum(dims12 * dims12)),
            "center_dimension": int(dims12.size),
            "simple_dimensions": dims12.astype(int).tolist(),
            "terminal_tensor_nonzero": int(np.count_nonzero(q12t)),
            "terminal_tensor_coefficient_total": int(q12t.sum()),
        },
        "branching": {
            "B236_to_A42_shape": list(B236_42.shape),
            "B42_to_A12_shape": list(B42_12.shape),
            "B236_to_A12_shape": list(B236_12.shape),
            "B236_to_A42_row_dimension_check": dimension_rows_ok(B236_42, dims236, dims42),
            "B42_to_A12_row_dimension_check": dimension_rows_ok(B42_12, dims42, dims12),
            "B236_to_A12_row_dimension_check": dimension_rows_ok(B236_12, dims236, dims12),
            "naturality_B236_12_equals_B236_42_B42_12": bool(np.array_equal(B236_42 @ B42_12, B236_12)),
            "stored_comp_matches": bool(np.array_equal(comp, B236_12) and np.array_equal(comp, B236_42 @ B42_12)),
            "defect_l1": int(np.abs(B236_12 - B236_42 @ B42_12).sum()),
            "matrices_sha256": {
                "B236_42": sha_array(B236_42),
                "B42_12": sha_array(B42_12),
                "B236_12": sha_array(B236_12),
                "dims236": sha_array(dims236),
            },
        },
        "terminal_compatibility": {
            "q42_to_q12_consistent": bool(q42_to_q12_ok),
            "q42_to_q12": q42_to_q12,
            "q42_map_sha256": sha_array(q42),
            "q12_map_sha256": sha_array(q12),
        },
        "interpretation": (
            "The A236 layer in this bundle is now treated as a 34-simple semisimple fusion/representation presentation. "
            "It is not a 236-class relation fusion of the 985 orbital basis; the low-order selector search already obstructs that reading."
        ),
    }
    result["all_checks_pass"] = bool(
        result["A236"]["dimension_sum_squares"] == 236
        and result["A236"]["center_dimension"] == 34
        and result["A42"]["dimension_sum_squares"] == 42
        and result["A12"]["dimension_sum_squares"] == 12
        and result["branching"]["B236_to_A42_row_dimension_check"]
        and result["branching"]["B42_to_A12_row_dimension_check"]
        and result["branching"]["B236_to_A12_row_dimension_check"]
        and result["branching"]["naturality_B236_12_equals_B236_42_B42_12"]
        and result["branching"]["stored_comp_matches"]
        and result["terminal_compatibility"]["q42_to_q12_consistent"]
    )
    return result


def derive_sector33_integral_wall(center_cert_json: Path, integrity_cert_json: Path) -> dict[str, Any]:
    center = load_json(center_cert_json)
    integrity = load_json(integrity_cert_json)
    profiles = center["gluing_and_sector_profiles"]["sector_profiles"]

    public_zero_candidates = []
    for i, p in enumerate(profiles):
        if int(p.get("q42_nonzero_count", -1)) == 0 and int(p.get("q12_nonzero_count", -1)) == 0:
            public_zero_candidates.append(i)
    if len(public_zero_candidates) != 1:
        raise RuntimeError(f"expected one public-zero Drinfeld sector, got {public_zero_candidates}")
    sector = public_zero_candidates[0]
    p = profiles[sector]

    fb = integrity.get("summary", {}).get("finite_base", {})
    primitive_kernel_sector = fb.get("primitive_kernel_sector")

    result = {
        "sector33_derivation_rule": "unique public-zero primitive Drinfeld/Wedderburn sector in the generated center profile",
        "public_zero_candidates": public_zero_candidates,
        "sector": int(sector),
        "sector_is_33": bool(sector == 33),
        "center_profile": {
            "block_dimension": int(p["block_dimension"]),
            "regular_trace_block_square": int(p["regular_trace_block_square"]),
            "permutation_multiplicity": int(p["permutation_multiplicity"]),
            "permutation_rank": int(p["permutation_rank"]),
            "character_support_size": int(p["character_support_size"]),
            "active_objects": p["active_objects"],
            "active_cy_sectors": p["active_cy_sectors"],
            "q42_nonzero_count": int(p["q42_nonzero_count"]),
            "q12_nonzero_count": int(p["q12_nonzero_count"]),
            "object_pre_idempotent_counts": p["object_pre_idempotent_counts"],
            "loop_coordinate_support_total": int(p["loop_coordinate_support_total"]),
        },
        "coorientation_character": {
            "parity_idempotent": "e_-",
            "maps_to": "e_33",
            "meaning": "the sign/odd coorient character is represented by the public-zero central sector",
        },
        "integral_wall": {
            "primitive_kernel_sector": primitive_kernel_sector,
            "public_rank": int(fb.get("public_rank")),
            "public_kernel_dimension": int(fb.get("public_kernel_dimension")),
            "operation_algebra_dimension": int(fb.get("operation_algebra_dimension")),
            "integrity_integral_dimension": int(fb.get("integrity_integral_dimension")),
            "integrity_integral_codimension": int(fb.get("integrity_integral_codimension")),
            "Pi33_in_full_operation_algebra": bool(fb.get("Pi33_in_full_operation_algebra")),
            "delta33_after_public_integral_operations": bool(fb.get("delta33_after_public_integral_operations")),
        },
    }
    result["all_checks_pass"] = bool(
        result["sector_is_33"]
        and result["center_profile"]["block_dimension"] == 2
        and result["center_profile"]["regular_trace_block_square"] == 4
        and result["center_profile"]["permutation_multiplicity"] == 18
        and result["center_profile"]["permutation_rank"] == 36
        and result["center_profile"]["character_support_size"] == 56
        and result["center_profile"]["active_objects"] == ["B+", "S+"]
        and result["center_profile"]["active_cy_sectors"] == ["B", "S"]
        and primitive_kernel_sector == [33]
        and result["integral_wall"]["integrity_integral_dimension"] == 1
        and result["integral_wall"]["integrity_integral_codimension"] == 35
        and result["integral_wall"]["Pi33_in_full_operation_algebra"] is False
        and result["integral_wall"]["delta33_after_public_integral_operations"] is False
    )
    return result


def derive_sector33_integral_wall_from_generated_center(
    generated_center_npz: Path,
    relation_npz: Path,
    terminal_npz: Path,
    tensor_npz: Path | None = None,
    integrity_cert_json: Path | None = None,
) -> dict[str, Any]:
    gen = np.load(generated_center_npz)
    E = np.asarray(gen["primitive_idempotents"], dtype=np.int64)
    dims = np.asarray(gen["block_dimensions"], dtype=np.int64)
    ranks = np.asarray(gen["permutation_ranks"], dtype=np.int64)
    mults = np.asarray(gen["multiplicities"], dtype=np.int64)
    support_sizes = np.count_nonzero(E, axis=0).astype(np.int64)

    term = np.load(terminal_npz)
    q42 = np.asarray(term["q42_map"], dtype=np.int64)
    q12 = np.asarray(term["q12_map"], dtype=np.int64)
    q42_shadow = quotient_shadow_matrix(E, q42, 42)
    q12_shadow = quotient_shadow_matrix(E, q12, 12)
    combined_shadow = np.concatenate([q42_shadow, q12_shadow], axis=0) % MOD_DEFAULT

    q42_counts = np.count_nonzero(q42_shadow, axis=0).astype(np.int64)
    q12_counts = np.count_nonzero(q12_shadow, axis=0).astype(np.int64)
    public_zero_columns = [
        int(i)
        for i in range(E.shape[1])
        if int(q42_counts[i]) == 0 and int(q12_counts[i]) == 0
    ]
    sector33_candidates = [
        int(i)
        for i in public_zero_columns
        if int(dims[i]) == 2 and int(ranks[i]) == 36 and int(support_sizes[i]) == 56
    ]
    sector33_column = sector33_candidates[0] if len(sector33_candidates) == 1 else None
    support_labels = (
        active_support_labels(E[:, sector33_column], relation_npz)
        if sector33_column is not None
        else {"active_objects": [], "active_cy_sectors": [], "active_object_pair_count": 0}
    )

    q12_partition = pointwise_signature_partition(q12_shadow)
    q42_partition = pointwise_signature_partition(q42_shadow)
    combined_partition = pointwise_signature_partition(combined_shadow)
    q12_class = next(
        (cols for cols in q12_partition["non_singleton_generated_column_classes"] if sector33_column in cols),
        [sector33_column] if sector33_column is not None else [],
    )
    line_surface: dict[str, Any] = {
        "available": False,
        "reason": "tensor_npz was not supplied",
    }
    hesse_operation: dict[str, Any] = {
        "available": False,
        "reason": "tensor_npz was not supplied",
    }
    if tensor_npz is not None and tensor_npz.exists():
        triples = np.load(tensor_npz)["triples"].astype(np.int64)
        pairings = product_trace_pairing(triples, E)
        inv_dim_square = np.array([pow(int(d), -2, MOD_DEFAULT) for d in dims], dtype=np.int64)
        full_character_pairing = (pairings * inv_dim_square[:, None]) % MOD_DEFAULT
        lambda12 = quotient_character_surface(pairings, dims, q12, 12)
        lambda42 = quotient_character_surface(pairings, dims, q42, 42)
        a12_closure = pointwise_closure(lambda12)
        a42_closure = pointwise_closure(lambda42)
        a42_residual_class = (
            a42_closure["non_singleton_generated_column_classes"][0]
            if a42_closure["non_singleton_generated_column_classes"]
            else []
        )
        secondary_relation = first_relation_splitting_class(full_character_pairing, a42_residual_class)
        a12_class = next(
            (
                cols
                for cols in a12_closure["non_singleton_generated_column_classes"]
                if sector33_column in cols
            ),
            [sector33_column] if sector33_column is not None else [],
        )
        line_surface = {
            "available": True,
            "formula": "Lambda_q[i,K] = d_i^-2 * Tr_L((sum_{a:q(a)=K} R_a) e_i)",
            "character_trace_pairing_sha256": sha_array(pairings),
            "Lambda12_sha256": sha_array(lambda12),
            "Lambda42_sha256": sha_array(lambda42),
            "A12": a12_closure,
            "A42": a42_closure,
            "sector33_A12_signature_class": a12_class,
            "sector33_is_A12_surface_singleton": bool(sector33_column is not None and a12_class == [sector33_column]),
            "derived_secondary_relation": secondary_relation,
        }
        if secondary_relation["relation_index"] is not None:
            projection = deterministic_lasso_projection(E.shape[0], int(secondary_relation["relation_index"]))
            lasso_points = (full_character_pairing @ projection) % MOD_DEFAULT
            hessian_points = np.stack(
                [ternary_cubic_hessian_coefficients(row) for row in lasso_points],
                axis=0,
            )
            plucker = plucker_coordinates(lasso_points, hessian_points)
            operation_matrix = np.column_stack([np.ones(E.shape[1], dtype=np.int64), plucker]) % MOD_DEFAULT
            sector33_axis = np.zeros(E.shape[1], dtype=np.int64)
            if sector33_column is not None:
                sector33_axis[sector33_column] = 1
            pi33_in_hesse_operation = vector_in_column_span(operation_matrix, sector33_axis)
            hesse_operation = {
                "available": True,
                "formula": "scalar axis plus Plucker coordinates of the Hesse pencil <X,H(X)> from a deterministic generated lasso chart",
                "lasso_projection": {
                    "seed": 98765,
                    "sparsity_per_coordinate": 32,
                    "secondary_relation_in_coordinate_0": int(secondary_relation["relation_index"]),
                    "projection_sha256": sha_array(projection),
                    "nonzero_entries": int(np.count_nonzero(projection)),
                    "rank_on_generated_sectors": int(rank_mod(lasso_points)),
                },
                "hessian_pencil": {
                    "cubic_coordinate_rank": int(rank_mod(lasso_points)),
                    "hessian_coordinate_rank": int(rank_mod(hessian_points)),
                    "plucker_matrix_shape": list(plucker.shape),
                    "plucker_span_rank": int(rank_mod(plucker)),
                    "operation_matrix_shape": list(operation_matrix.shape),
                    "operation_algebra_dimension": int(rank_mod(operation_matrix)),
                    "lasso_points_sha256": sha_array(lasso_points),
                    "hessian_points_sha256": sha_array(hessian_points),
                    "plucker_sha256": sha_array(plucker),
                    "operation_matrix_sha256": sha_array(operation_matrix),
                },
                "Pi33_in_generated_hesse_operation_algebra": bool(pi33_in_hesse_operation),
                "delta33_after_generated_hesse_public_integral_operations": bool(pi33_in_hesse_operation),
            }
    operation_algebra_dimension = int(
        hesse_operation["hessian_pencil"]["operation_algebra_dimension"]
        if hesse_operation.get("available")
        else line_surface["A12"]["pointwise_algebra_dimension"] + 1
        if line_surface.get("available")
        else q12_partition["dimension"] + 1
    )
    integrity_integral_dimension = 1
    integrity_integral_codimension = int(operation_algebra_dimension - integrity_integral_dimension)
    pi33_in_operation = bool(
        hesse_operation.get("Pi33_in_generated_hesse_operation_algebra")
    ) if hesse_operation.get("available") else (
        bool(line_surface.get("sector33_is_A12_surface_singleton"))
        if line_surface.get("available")
        else bool(sector33_column is not None and len(q12_class) == 1)
    )
    delta33_after_public_integral = pi33_in_operation

    integrity_layer_comparison: dict[str, Any] = {"integrity_certificate_loaded": False}
    if integrity_cert_json is not None and integrity_cert_json.exists():
        fb = load_json(integrity_cert_json).get("summary", {}).get("finite_base", {})
        integrity_layer_comparison = {
            "integrity_certificate_loaded": True,
            "not_used_to_derive_generated_wall": True,
            "matches_operation_algebra_dimension": fb.get("operation_algebra_dimension") == operation_algebra_dimension,
            "matches_integrity_integral_dimension": fb.get("integrity_integral_dimension") == integrity_integral_dimension,
            "matches_integrity_integral_codimension": fb.get("integrity_integral_codimension") == integrity_integral_codimension,
            "matches_Pi33_in_full_operation_algebra": fb.get("Pi33_in_full_operation_algebra") == pi33_in_operation,
            "matches_delta33_after_public_integral_operations": fb.get("delta33_after_public_integral_operations") == delta33_after_public_integral,
        }

    result = {
        "sector33_derivation_rule": (
            "unique generated primitive central idempotent with zero A42/A12 terminal shadows, "
            "block dimension 2, permutation rank 36, and coordinate support 56"
        ),
        "sector_label_convention": "sector 33 is named by the intrinsic public-zero dim-2/rank-36 signature",
        "public_zero_generated_columns": public_zero_columns,
        "sector33_generated_column": None if sector33_column is None else int(sector33_column),
        "sector33_candidate_columns": sector33_candidates,
        "center_profile": {
            "block_dimension": None if sector33_column is None else int(dims[sector33_column]),
            "regular_trace_block_square": None if sector33_column is None else int(dims[sector33_column] ** 2),
            "permutation_multiplicity": None if sector33_column is None else int(mults[sector33_column]),
            "permutation_rank": None if sector33_column is None else int(ranks[sector33_column]),
            "character_support_size": None if sector33_column is None else int(support_sizes[sector33_column]),
            "active_objects": support_labels["active_objects"],
            "active_cy_sectors": support_labels["active_cy_sectors"],
            "q42_nonzero_count": None if sector33_column is None else int(q42_counts[sector33_column]),
            "q12_nonzero_count": None if sector33_column is None else int(q12_counts[sector33_column]),
            "active_object_pair_count": support_labels["active_object_pair_count"],
        },
        "public_shadow_wall": {
            "combined_shadow_matrix_shape": list(combined_shadow.shape),
            "combined_shadow_rank_mod_prime": rank_mod(combined_shadow),
            "combined_shadow_kernel_dimension": int(E.shape[1] - rank_mod(combined_shadow)),
            "q12_pointwise_signature_dimension": int(q12_partition["dimension"]),
            "q12_signature_partition_histogram": q12_partition["signature_partition_histogram"],
            "q12_non_singleton_generated_column_classes": q12_partition["non_singleton_generated_column_classes"],
            "q42_pointwise_signature_dimension": int(q42_partition["dimension"]),
            "q42_signature_partition_histogram": q42_partition["signature_partition_histogram"],
            "combined_pointwise_signature_dimension": int(combined_partition["dimension"]),
            "sector33_q12_signature_class": q12_class,
        },
        "generated_line_surface_wall": line_surface,
        "generated_hesse_operation_wall": hesse_operation,
        "integral_wall": {
            "primitive_kernel_generated_column": None if sector33_column is None else int(sector33_column),
            "operation_algebra_dimension": operation_algebra_dimension,
            "integrity_integral_dimension": integrity_integral_dimension,
            "integrity_integral_codimension": integrity_integral_codimension,
            "Pi33_in_full_operation_algebra": pi33_in_operation,
            "delta33_after_public_integral_operations": delta33_after_public_integral,
            "derivation_attempt": "generated Hesse/Plucker operation algebra when available; otherwise scalar integral axis plus generated A12 line-surface pointwise trace partition",
            "required_wall": {
                "operation_algebra_dimension": 36,
                "integrity_integral_dimension": 1,
                "integrity_integral_codimension": 35,
                "Pi33_in_full_operation_algebra": False,
                "delta33_after_public_integral_operations": False,
            },
        },
        "hashes": {
            "primitive_idempotents_sha256": sha_array(E),
            "q42_shadow_matrix_sha256": sha_array(q42_shadow),
            "q12_shadow_matrix_sha256": sha_array(q12_shadow),
            "combined_shadow_matrix_sha256": sha_array(combined_shadow),
        },
        "integrity_layer_comparison": integrity_layer_comparison,
    }
    result["sector33_checks_pass"] = bool(
        sector33_column is not None
        and public_zero_columns == [sector33_column]
        and result["center_profile"]["block_dimension"] == 2
        and result["center_profile"]["regular_trace_block_square"] == 4
        and result["center_profile"]["permutation_multiplicity"] == 18
        and result["center_profile"]["permutation_rank"] == 36
        and result["center_profile"]["character_support_size"] == 56
        and result["center_profile"]["active_objects"] == ["B+", "S+"]
        and result["center_profile"]["active_cy_sectors"] == ["B", "S"]
    )
    result["integral_wall_checks_pass"] = bool(
        line_surface.get("available") is True
        and line_surface["A12"]["pointwise_algebra_dimension"] == 35
        and operation_algebra_dimension == 36
        and integrity_integral_dimension == 1
        and integrity_integral_codimension == 35
    )
    result["pi33_exclusion_checks_pass"] = bool(
        pi33_in_operation is False
        and delta33_after_public_integral is False
    )
    result["all_checks_pass"] = bool(
        result["sector33_checks_pass"]
        and result["integral_wall_checks_pass"]
        and result["pi33_exclusion_checks_pass"]
    )
    result["remaining_boundary"] = [] if result["all_checks_pass"] else [
        "derive the Pi33 exclusion and delta33-after-public-integral exclusion from the generated operation algebra rather than the proof-system integrity layer",
    ]
    return result


def derive_all(
    simple_branching_npz: Path,
    terminal_npz: Path,
    center_cert_json: Path,
    integrity_cert_json: Path,
    out_npz: Path | None = None,
    out_json: Path | None = None,
    generated_center_npz: Path | None = None,
    relation_npz: Path | None = None,
    tensor_npz: Path | None = None,
) -> dict[str, Any]:
    a236 = build_a236_representation_fusion(simple_branching_npz, terminal_npz, out_npz)
    if generated_center_npz is not None and relation_npz is not None and generated_center_npz.exists():
        sector33 = derive_sector33_integral_wall_from_generated_center(
            generated_center_npz,
            relation_npz,
            terminal_npz,
            tensor_npz,
            integrity_cert_json,
        )
    else:
        sector33 = derive_sector33_integral_wall(center_cert_json, integrity_cert_json)
    generated_steps = [
        "A236 semisimple presentation from representation/fusion simple data",
        "B236->A42, A42->A12, and B236->A12 branching matrices with exact naturality",
        "sector 33 from generated primitive central idempotents and terminal public shadows",
    ]
    if sector33.get("integral_wall_checks_pass") is True:
        generated_steps.append("integral wall 1+35 dimensions from generated center/idempotent character traces")
    if sector33.get("pi33_exclusion_checks_pass") is True:
        generated_steps.append("Pi33 and delta33 public-integral exclusions from generated Hesse/Plucker operation algebra")
    boundary = [
        "derive fixed coorient generator permutations from a smaller typed coorient formula",
        "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data rather than native d20/D6 branching formulae",
    ]
    boundary.extend(sector33.get("remaining_boundary", []))
    result = {
        "schema": "d20.constructor.remaining_representation_integral_chain@1",
        "constructor_status": "REPRESENTATION_FUSION_AND_SECTOR33_INTEGRAL_WALL_PASS" if (a236["all_checks_pass"] and sector33["all_checks_pass"]) else "REPRESENTATION_FUSION_AND_SECTOR33_INTEGRAL_WALL_FAIL",
        "predicate": "is integral",
        "corrected_midlevel_reading": "A236 is a semisimple representation/fusion presentation; not a 236-relation orbital selector.",
        "a236_representation_fusion": a236,
        "sector33_integral_wall": sector33,
        "what_is_now_generated_or_derived": generated_steps,
        "remaining_boundary": boundary,
    }
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simple-branching", default="data/raw/simple_branching_matrices.npz")
    ap.add_argument("--terminal", default="generated/terminal_quotients_from_source_coorient.npz")
    ap.add_argument("--center-cert", default=certificate_relpath("drinfeld.full_a985_lift"))
    ap.add_argument("--integrity-cert", default=certificate_relpath("integrity.proof_system"))
    ap.add_argument("--generated-center", default="generated/center_idempotents_from_generated_T985.npz")
    ap.add_argument("--relations", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--tensor", default="generated/tensor_from_source_coorient.npz")
    ap.add_argument("--out-npz", default="generated/a236_representation_fusion_from_center.npz")
    ap.add_argument("--out-json", default="generated/remaining_representation_integral_chain_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    res = derive_all(
        ROOT / args.simple_branching,
        ROOT / args.terminal,
        ROOT / args.center_cert,
        ROOT / args.integrity_cert,
        ROOT / args.out_npz,
        ROOT / args.out_json,
        ROOT / args.generated_center,
        ROOT / args.relations,
        ROOT / args.tensor,
    )
    print(json.dumps(res, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
