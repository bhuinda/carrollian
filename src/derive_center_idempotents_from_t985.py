#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certificate_registry import certificate_relpath
except ImportError:  # Supports `python src/derive_center_idempotents_from_t985.py`.
    from certificate_registry import certificate_relpath

ROOT = Path(__file__).resolve().parents[1]
MOD_DEFAULT = 1000003
NREL = 985


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def derive_identity_relations_from_relation_body(relation_npz: Path) -> list[int]:
    rel = np.load(relation_npz)
    encoded = rel["encoded_pairs"].astype(np.int64)
    offsets = rel["offsets"].astype(np.int64)
    object_of_point = rel["object_of_point"].astype(np.int64)
    block_i = rel["block_i"].astype(np.int64)
    block_j = rel["block_j"].astype(np.int64)
    point_count = int(object_of_point.size)
    object_count = int(max(object_of_point.max(), block_i.max(), block_j.max()) + 1)
    object_sizes = np.bincount(object_of_point, minlength=object_count)

    identities: list[int] = []
    for obj in range(object_count):
        matches: list[int] = []
        for rel_idx in np.nonzero((block_i == obj) & (block_j == obj))[0]:
            seg = encoded[int(offsets[rel_idx]) : int(offsets[rel_idx + 1])]
            rows = seg // point_count
            cols = seg % point_count
            if (
                int(seg.size) == int(object_sizes[obj])
                and bool(np.array_equal(rows, cols))
                and bool(np.all(object_of_point[rows] == obj))
            ):
                matches.append(int(rel_idx))
        if len(matches) != 1:
            raise RuntimeError(f"expected one identity relation for object {obj}, got {matches}")
        identities.append(matches[0])
    return identities


def rref_nullspace(A: np.ndarray, mod: int) -> tuple[np.ndarray, int, list[int]]:
    """Return a column basis for ker(A) over F_mod, with RREF rank."""
    A = np.asarray(A, dtype=np.int64).copy() % mod
    m, n = A.shape
    rank = 0
    pivots: list[int] = []
    pivot_set: set[int] = set()
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
        pivots.append(col)
        pivot_set.add(col)
        rank += 1
        if rank == m:
            break
    free = [j for j in range(n) if j not in pivot_set]
    X = np.zeros((n, len(free)), dtype=np.int64)
    for idx, f in enumerate(free):
        X[f, idx] = 1
    if free:
        for row, col in enumerate(pivots):
            X[col, :] = (-A[row, free]) % mod
    return X, rank, pivots


def rank_mod(A: np.ndarray, mod: int) -> int:
    A = np.asarray(A, dtype=np.int64).copy() % mod
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
    return rank


def inv_mod_matrix(A: np.ndarray, mod: int) -> np.ndarray:
    A = np.asarray(A, dtype=np.int64).copy() % mod
    n = A.shape[0]
    if A.shape != (n, n):
        raise ValueError(f"expected square matrix, got {A.shape}")
    Aug = np.concatenate([A, np.eye(n, dtype=np.int64)], axis=1)
    rank = 0
    for col in range(n):
        rows = np.nonzero(Aug[rank:, col])[0]
        if rows.size == 0:
            raise ValueError("singular matrix over verifier field")
        pivot = rank + int(rows[0])
        if pivot != rank:
            Aug[[rank, pivot]] = Aug[[pivot, rank]]
        inv = pow(int(Aug[rank, col]), -1, mod)
        Aug[rank, :] = (Aug[rank, :] * inv) % mod
        inds = np.nonzero(Aug[:, col])[0]
        inds = inds[inds != rank]
        if len(inds):
            vals = Aug[inds, col].copy()
            Aug[inds, :] = (Aug[inds, :] - vals[:, None] * Aug[rank, :]) % mod
        rank += 1
    return Aug[:, n:]


def build_random_commutator(triples: np.ndarray, coeff: np.ndarray, mod: int) -> np.ndarray:
    """Build [?, c] matrix for central unknown x against random c=sum coeff_i R_i."""
    a = triples[:, 0]
    b = triples[:, 1]
    g = triples[:, 2]
    w = triples[:, 3] % mod
    C = np.zeros((NREL, NREL), dtype=np.int64)
    np.add.at(C, (g, a), (coeff[b] * w) % mod)
    np.add.at(C, (g, b), -(coeff[a] * w) % mod)
    return C % mod


def product(triples: np.ndarray, u: np.ndarray, v: np.ndarray, mod: int) -> np.ndarray:
    a = triples[:, 0]
    b = triples[:, 1]
    g = triples[:, 2]
    w = triples[:, 3] % mod
    vals = (((u[a] * v[b]) % mod) * w) % mod
    out = np.zeros(NREL, dtype=np.int64)
    np.add.at(out, g, vals)
    return out % mod


def verify_central_basis(triples: np.ndarray, B: np.ndarray, mod: int) -> bool:
    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    w = (triples[:, 3] % mod).astype(np.int64)
    by_alpha = [np.where(alpha == i)[0] for i in range(NREL)]
    by_beta = [np.where(beta == i)[0] for i in range(NREL)]
    k = B.shape[1]
    for i in range(NREL):
        L = np.zeros((NREL, k), dtype=np.int64)
        R = np.zeros((NREL, k), dtype=np.int64)
        idx = by_beta[i]
        if len(idx):
            vals = (w[idx, None] * B[alpha[idx], :]) % mod
            np.add.at(L, gamma[idx], vals)
        idx = by_alpha[i]
        if len(idx):
            vals = (w[idx, None] * B[beta[idx], :]) % mod
            np.add.at(R, gamma[idx], vals)
        if np.any((L - R) % mod):
            return False
    return True


def find_pivot_rows(B: np.ndarray, mod: int) -> list[int]:
    rows: list[int] = []
    mat: list[list[int]] = []
    rank = 0
    for i in range(B.shape[0]):
        cand = np.array(mat + [B[i].astype(int).tolist()], dtype=np.int64) if mat else B[i:i + 1]
        rr = rank_mod(cand, mod)
        if rr > rank:
            rows.append(i)
            mat = cand.astype(int).tolist()
            rank = rr
            if rank == B.shape[1]:
                break
    if rank != B.shape[1]:
        raise RuntimeError("failed to select full-rank row chart for central basis")
    return rows


def factor_linear_roots(coeff: np.ndarray, mod: int) -> tuple[list[int], list[tuple[int, int]]]:
    """For z^d=sum c_i z^i, scan F_mod for roots of x^d-sum c_i x^i."""
    degree = int(coeff.size)
    roots: list[int] = []
    chunk = 100_000
    coeff_mod = np.asarray(coeff, dtype=np.int64) % mod
    for start in range(0, mod, chunk):
        xs = np.arange(start, min(start + chunk, mod), dtype=np.int64)
        vals = np.ones_like(xs, dtype=np.int64)
        for ci in coeff_mod[::-1]:
            vals = (vals * xs - int(ci)) % mod
        roots.extend(int(x) for x in xs[vals == 0])
    if len(roots) == degree and len(set(roots)) == degree:
        factor_degrees = [(1, 1)] * degree
    else:
        remaining = max(degree - len(roots), 0)
        factor_degrees = [(1, 1)] * len(roots)
        if remaining:
            factor_degrees.append((remaining, 1))
    return roots, factor_degrees


def derive_center_idempotents(
    tensor_npz: Path,
    center_cert_json: Path | None,
    relation_npz: Path,
    terminal_npz: Path,
    out_npz: Path | None = None,
    out_json: Path | None = None,
    mod: int = MOD_DEFAULT,
    seed: int = 124,
) -> dict[str, Any]:
    triples = np.load(tensor_npz)["triples"].astype(np.int64)
    identity_relations = derive_identity_relations_from_relation_body(relation_npz)
    identity_comparison: dict[str, Any] = {"center_certificate_loaded": False}
    if center_cert_json is not None and center_cert_json.exists():
        center_cert = json.loads(center_cert_json.read_text(encoding="utf-8"))
        prior_identity_relations = center_cert["full_A985_idempotent_validation"]["identity_relations_by_object"]
        identity_comparison = {
            "center_certificate_loaded": True,
            "matches_center_certificate_identity_rows": bool(identity_relations == prior_identity_relations),
            "center_certificate_identity_relations_by_object": [int(x) for x in prior_identity_relations],
        }

    rng = np.random.default_rng(seed)
    B = np.eye(NREL, dtype=np.int64)
    centralizer_dims: list[int] = []
    random_hashes: list[str] = []
    for _ in range(16):
        c = rng.integers(0, mod, size=NREL, dtype=np.int64)
        random_hashes.append(sha_array(c))
        C = build_random_commutator(triples, c, mod)
        A = (C @ B) % mod
        X, rank, _ = rref_nullspace(A, mod)
        B = (B @ X) % mod
        centralizer_dims.append(int(B.shape[1]))
        if B.shape[1] == 39:
            break
    center_dim = int(B.shape[1])
    centrality_verified = verify_central_basis(triples, B, mod) if center_dim == 39 else False

    rows = find_pivot_rows(B, mod)
    row_chart = B[rows, :]
    row_chart_inv = inv_mod_matrix(row_chart, mod)

    def coords(v: np.ndarray) -> np.ndarray:
        return (row_chart_inv @ (v[rows] % mod)) % mod

    unit = np.zeros(NREL, dtype=np.int64)
    unit[np.array(identity_relations, dtype=np.int64)] = 1
    unit_coords = coords(unit)

    # Choose a generic central element whose powers span the generated center.
    power_rank = 0
    generic_coeff = None
    generic_element = None
    powers = None
    power_coords = None
    minimal_coeff = None
    roots: list[int] = []
    factor_degrees: list[tuple[int, int]] = []
    for _ in range(32):
        c = rng.integers(0, mod, size=center_dim, dtype=np.int64)
        z = (B @ c) % mod
        local_powers: list[np.ndarray] = []
        local_coords: list[np.ndarray] = []
        v = unit.copy()
        for _k in range(center_dim + 1):
            local_powers.append(v)
            local_coords.append(coords(v))
            v = product(triples, v, z, mod)
        Cmat = np.stack(local_coords[:center_dim], axis=1)
        pr = rank_mod(Cmat, mod)
        if pr > power_rank:
            power_rank = pr
        if pr == center_dim:
            inv = inv_mod_matrix(Cmat, mod)
            minimal_coeff = (inv @ local_coords[center_dim]) % mod
            roots, factor_degrees = factor_linear_roots(minimal_coeff, mod)
            generic_coeff = c
            generic_element = z
            powers = local_powers
            power_coords = local_coords
            if len(roots) == center_dim and len(set(roots)) == center_dim:
                break
    if generic_coeff is None or generic_element is None or powers is None or minimal_coeff is None:
        raise RuntimeError("failed to find generic central element")

    # Materialize primitive idempotents if the generic center element splits into distinct verifier-field roots.
    primitive_idempotents = np.zeros((NREL, 0), dtype=np.int64)
    idempotents_materialized = False
    idempotent_sum_is_unit = False
    idempotent_self_product_failures: list[int] = []
    if len(roots) == center_dim and len(set(roots)) == center_dim:
        cols: list[np.ndarray] = []
        for lam in roots:
            poly = np.array([1], dtype=object)
            denom = 1
            for mu in roots:
                if mu == lam:
                    continue
                nxt = np.zeros(len(poly) + 1, dtype=object)
                nxt[:-1] += (-mu) * poly
                nxt[1:] += poly
                poly = nxt % mod
                denom = (denom * ((lam - mu) % mod)) % mod
            inv_denom = pow(int(denom), -1, mod)
            coeffs = np.array([(int(a) * inv_denom) % mod for a in poly], dtype=np.int64)
            e = np.zeros(NREL, dtype=np.int64)
            for k, ak in enumerate(coeffs):
                if int(ak):
                    e = (e + int(ak) * powers[k]) % mod
            cols.append(e)
        primitive_idempotents = np.stack(cols, axis=1)
        idempotents_materialized = True
        idempotent_sum_is_unit = bool(np.array_equal(primitive_idempotents.sum(axis=1) % mod, unit % mod))
        for i in range(center_dim):
            ee = product(triples, primitive_idempotents[:, i], primitive_idempotents[:, i], mod)
            if not np.array_equal(ee, primitive_idempotents[:, i] % mod):
                idempotent_self_product_failures.append(i)
                if len(idempotent_self_product_failures) >= 8:
                    break

    # Intrinsic invariants of generated primitive central idempotents.
    traces = []
    block_dims = []
    permutation_ranks = []
    multiplicities = []
    q42_counts = []
    q12_counts = []
    q42_shadow_columns: list[np.ndarray] = []
    q12_shadow_columns: list[np.ndarray] = []
    active_object_pairs = []
    sector33_candidates = []
    if idempotents_materialized:
        rel = np.load(relation_npz)
        encoded = rel["encoded_pairs"].astype(np.int64)
        offsets = rel["offsets"].astype(np.int64)
        block_i = rel["block_i"].astype(np.int64)
        block_j = rel["block_j"].astype(np.int64)
        relation_trace = np.zeros(NREL, dtype=np.int64)
        for a in range(NREL):
            seg = encoded[int(offsets[a]):int(offsets[a + 1])]
            relation_trace[a] = int(np.count_nonzero((seg // 2576) == (seg % 2576)))
        qz = np.load(terminal_npz)
        q42 = qz["q42_map"].astype(np.int64)
        q12 = qz["q12_map"].astype(np.int64)
        # regular trace basis: coefficient of R_beta in R_alpha R_beta, summed over beta.
        gamma = triples[:, 2]
        beta = triples[:, 1]
        alpha = triples[:, 0]
        w = triples[:, 3] % mod
        diag_mask = gamma == beta
        reg_trace_coeff = np.zeros(NREL, dtype=np.int64)
        np.add.at(reg_trace_coeff, alpha[diag_mask], w[diag_mask])
        for j in range(center_dim):
            e = primitive_idempotents[:, j]
            reg_trace = int((reg_trace_coeff @ e) % mod)
            rank_perm = int((relation_trace @ e) % mod)
            traces.append(reg_trace)
            d = int(round(reg_trace ** 0.5)) if reg_trace >= 0 else -1
            block_dims.append(d if d * d == reg_trace else -1)
            permutation_ranks.append(rank_perm)
            multiplicities.append(rank_perm // d if d > 0 and rank_perm % d == 0 else -1)
            q42_shadow = np.bincount(q42, weights=e, minlength=42).astype(object)
            q12_shadow = np.bincount(q12, weights=e, minlength=12).astype(object)
            q42_shadow = np.array([int(x) % mod for x in q42_shadow], dtype=np.int64)
            q12_shadow = np.array([int(x) % mod for x in q12_shadow], dtype=np.int64)
            q42n = int(np.count_nonzero(q42_shadow))
            q12n = int(np.count_nonzero(q12_shadow))
            q42_shadow_columns.append(q42_shadow)
            q12_shadow_columns.append(q12_shadow)
            q42_counts.append(q42n)
            q12_counts.append(q12n)
            support = np.nonzero(e)[0]
            pairs = sorted({(int(block_i[a]), int(block_j[a])) for a in support})
            active_object_pairs.append(pairs)
            if d == 2 and rank_perm == 36 and q42n == 0 and q12n == 0:
                sector33_candidates.append(j)

    result: dict[str, Any] = {
        "schema": "d20.constructor.center_idempotents_from_generated_T985@1",
        "constructor_status": "CENTER_IDEMPOTENTS_FROM_GENERATED_T985_PASS" if (center_dim == 39 and centrality_verified and idempotents_materialized and idempotent_sum_is_unit and not idempotent_self_product_failures) else "CENTER_IDEMPOTENTS_FROM_GENERATED_T985_BOUNDARY",
        "field_prime": int(mod),
        "source_tensor": str(tensor_npz.relative_to(ROOT) if tensor_npz.is_relative_to(ROOT) else tensor_npz),
        "center_basis": {
            "centralizer_intersection_dims": centralizer_dims,
            "dimension": center_dim,
            "centrality_verified_against_all_985_basis_relations": bool(centrality_verified),
            "basis_sha256": sha_array(B),
            "row_chart_pivots": [int(x) for x in rows],
            "row_chart_inverse_sha256": sha_array(row_chart_inv),
            "random_commutator_coeff_hashes": random_hashes,
        },
        "generated_unit": {
            "identity_relation_source": "relation body diagonal identity rows",
            "identity_relations_by_object": [int(x) for x in identity_relations],
            "identity_relations_sha256": sha_array(np.array(identity_relations, dtype=np.int64)),
            "comparison": identity_comparison,
        },
        "generic_center_element": {
            "power_rank": int(power_rank),
            "power_basis_full_rank": bool(power_rank == center_dim),
            "coeff_sha256": sha_array(generic_coeff),
            "element_sha256": sha_array(generic_element),
            "minimal_relation_coefficients_sha256": sha_array(minimal_coeff),
            "factor_degrees": [[int(a), int(b)] for a, b in factor_degrees],
            "linear_root_count": int(len(roots)),
            "distinct_root_count": int(len(set(roots))),
            "roots_sha256": sha_array(np.array(roots, dtype=np.int64)),
        },
        "primitive_central_idempotents": {
            "materialized": bool(idempotents_materialized),
            "count": int(primitive_idempotents.shape[1]),
            "matrix_shape": list(primitive_idempotents.shape),
            "matrix_sha256": sha_array(primitive_idempotents),
            "sum_is_A985_unit": bool(idempotent_sum_is_unit),
            "self_product_failures_first": [int(x) for x in idempotent_self_product_failures],
            "self_products_checked": int(primitive_idempotents.shape[1]) if idempotents_materialized and not idempotent_self_product_failures else int(len(idempotent_self_product_failures)),
        },
        "intrinsic_sector_invariants": {
            "regular_trace_values": [int(x) for x in traces],
            "block_dimensions": [int(x) for x in block_dims],
            "block_dimension_histogram": {str(int(k)): int(v) for k, v in zip(*np.unique(np.array(block_dims, dtype=np.int64), return_counts=True))} if block_dims else {},
            "permutation_ranks": [int(x) for x in permutation_ranks],
            "multiplicities": [int(x) for x in multiplicities],
            "q42_shadow_nonzero_counts": [int(x) for x in q42_counts],
            "q12_shadow_nonzero_counts": [int(x) for x in q12_counts],
            "q42_shadow_matrix_sha256": sha_array(np.stack(q42_shadow_columns, axis=1)) if q42_shadow_columns else None,
            "q12_shadow_matrix_sha256": sha_array(np.stack(q12_shadow_columns, axis=1)) if q12_shadow_columns else None,
            "public_zero_dim2_rank36_candidates_by_generated_column": [int(x) for x in sector33_candidates],
        },
        "remaining_boundary": [
            "derive the named coorient generator formula rather than storing fixed coorient generator permutations",
            "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data; generated primitive idempotent coordinates alone do not determine the native A236 branching matrices",
        ],
    }
    result["all_checks_pass"] = bool(result["constructor_status"] == "CENTER_IDEMPOTENTS_FROM_GENERATED_T985_PASS")
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})

    if out_npz is not None:
        out_npz.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_npz,
            center_basis=B.astype(np.int64),
            primitive_idempotents=primitive_idempotents.astype(np.int64),
            generic_center_coeff=generic_coeff.astype(np.int64),
            generic_center_element=generic_element.astype(np.int64),
            minimal_relation_coefficients=minimal_coeff.astype(np.int64),
            roots=np.array(roots, dtype=np.int64),
            row_chart_pivots=np.array(rows, dtype=np.int64),
            row_chart_inverse=row_chart_inv.astype(np.int64),
            regular_trace_values=np.array(traces, dtype=np.int64),
            block_dimensions=np.array(block_dims, dtype=np.int64),
            permutation_ranks=np.array(permutation_ranks, dtype=np.int64),
            multiplicities=np.array(multiplicities, dtype=np.int64),
            q42_shadow_nonzero_counts=np.array(q42_counts, dtype=np.int64),
            q12_shadow_nonzero_counts=np.array(q12_counts, dtype=np.int64),
            q42_shadow_matrix=np.stack(q42_shadow_columns, axis=1).astype(np.int64) if q42_shadow_columns else np.zeros((42, 0), dtype=np.int64),
            q12_shadow_matrix=np.stack(q12_shadow_columns, axis=1).astype(np.int64) if q12_shadow_columns else np.zeros((12, 0), dtype=np.int64),
            identity_relations_by_object=np.array(identity_relations, dtype=np.int64),
        )
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tensor", default="generated/tensor_from_source_coorient.npz")
    ap.add_argument("--center-cert", default="")
    ap.add_argument("--relations", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--terminal", default="generated/terminal_quotients_from_source_coorient.npz")
    ap.add_argument("--out-npz", default="generated/center_idempotents_from_generated_T985.npz")
    ap.add_argument("--out-json", default="generated/center_idempotents_from_generated_T985_report.json")
    ap.add_argument("--prime", type=int, default=MOD_DEFAULT)
    ap.add_argument("--seed", type=int, default=124)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive_center_idempotents(
        ROOT / args.tensor,
        ROOT / args.center_cert if args.center_cert else None,
        ROOT / args.relations,
        ROOT / args.terminal,
        ROOT / args.out_npz,
        ROOT / args.out_json,
        args.prime,
        args.seed,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
