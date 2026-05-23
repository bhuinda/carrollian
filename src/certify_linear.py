from __future__ import annotations

import numpy as np


def rank_mod(mat: np.ndarray, p: int) -> int:
    """Row rank over F_p for small dense integer matrices."""
    A = np.asarray(mat, dtype=np.int64) % p
    m, n = A.shape
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, m):
            if int(A[i, c]) % p:
                piv = i
                break
        if piv is None:
            continue
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), -1, p)
        A[r, :] = (A[r, :] * inv) % p
        nz = np.nonzero(A[:, c])[0]
        for i in nz:
            if i != r:
                A[i, :] = (A[i, :] - A[i, c] * A[r, :]) % p
        r += 1
        if r == m:
            break
    return int(r)


def rref_nullspace_mod(mat: np.ndarray, p: int) -> tuple[np.ndarray, list[int]]:
    """Return a row-reduced nullspace basis for mat*x=0 over F_p.

    Basis vectors are returned as columns in an (n,d) array. The pivot list is
    the list of pivot columns of the row-reduced constraint matrix.
    """
    A = np.asarray(mat, dtype=np.int64) % p
    m, n = A.shape
    r = 0
    pivots: list[int] = []
    for c in range(n):
        piv = None
        for i in range(r, m):
            if int(A[i, c]) % p:
                piv = i
                break
        if piv is None:
            continue
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), -1, p)
        A[r, :] = (A[r, :] * inv) % p
        for i in range(m):
            if i != r and int(A[i, c]) % p:
                A[i, :] = (A[i, :] - int(A[i, c]) * A[r, :]) % p
        pivots.append(c)
        r += 1
        if r == m:
            break
    free = [c for c in range(n) if c not in set(pivots)]
    B = np.zeros((n, len(free)), dtype=np.int64)
    for j, fc in enumerate(free):
        B[fc, j] = 1
        for row, pc in enumerate(pivots):
            B[pc, j] = (-A[row, fc]) % p
    return B % p, pivots


def independent_row_indices_mod(B: np.ndarray, p: int) -> list[int]:
    """Choose row indices so B[rows,:] is invertible over F_p."""
    B = np.asarray(B, dtype=np.int64) % p
    n, d = B.shape
    if d == 0:
        return []
    rows: list[int] = []
    cur = np.zeros((0, d), dtype=np.int64)
    rk = 0
    for i in range(n):
        trial = np.vstack([cur, B[i:i+1, :]])
        nrk = rank_mod(trial, p)
        if nrk > rk:
            rows.append(i)
            cur = trial
            rk = nrk
            if rk == d:
                break
    if rk != d:
        raise AssertionError('failed to find independent center-basis row minor')
    return rows


def solve_square_mod(A: np.ndarray, b: np.ndarray, p: int) -> np.ndarray:
    """Solve A x = b for nonsingular square A over F_p."""
    A = np.asarray(A, dtype=np.int64) % p
    b = np.asarray(b, dtype=np.int64).reshape(-1, 1) % p
    n = A.shape[0]
    aug = np.hstack([A.copy(), b])
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, n):
            if int(aug[i, c]) % p:
                piv = i
                break
        if piv is None:
            raise AssertionError('singular solve matrix over finite field')
        if piv != r:
            aug[[r, piv]] = aug[[piv, r]]
        inv = pow(int(aug[r, c]), -1, p)
        aug[r, :] = (aug[r, :] * inv) % p
        for i in range(n):
            if i != r and int(aug[i, c]) % p:
                aug[i, :] = (aug[i, :] - int(aug[i, c]) * aug[r, :]) % p
        r += 1
    return aug[:, -1] % p


def multiply_vectors_by_tensor_mod(u: np.ndarray, v: np.ndarray, T: np.ndarray, p: int) -> np.ndarray:
    """Product vector w_k = sum_ab u_a v_b T_abk over F_p.

    Uses Python integer accumulation to avoid int64 overflow when coefficients
    are already reduced modulo a large prime.
    """
    uu = [int(x) % p for x in np.asarray(u).reshape(-1)]
    vv = [int(x) % p for x in np.asarray(v).reshape(-1)]
    TT = np.asarray(T, dtype=np.int64)
    out = [0] * TT.shape[2]
    for a, ua in enumerate(uu):
        if ua == 0:
            continue
        for b, vb in enumerate(vv):
            if vb == 0:
                continue
            uv = (ua * vb) % p
            row = TT[a, b]
            for k, coef in enumerate(row):
                cc = int(coef) % p
                if cc:
                    out[k] = (out[k] + uv * cc) % p
    return np.asarray(out, dtype=np.int64)


def pivot_columns_for_full_row_rank_matrix(mat: np.ndarray, p: int) -> list[int]:
    """Deterministic left-to-right pivot columns over F_p."""
    A = np.asarray(mat, dtype=np.int64).copy() % p
    m, n = A.shape
    r = 0
    pivots: list[int] = []
    for c in range(n):
        piv = None
        for i in range(r, m):
            if int(A[i, c]) % p:
                piv = i
                break
        if piv is None:
            continue
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), -1, p)
        A[r, :] = (A[r, :] * inv) % p
        nz = np.nonzero(A[:, c])[0]
        for i in nz:
            if i != r:
                A[i, :] = (A[i, :] - A[i, c] * A[r, :]) % p
        pivots.append(int(c))
        r += 1
        if r == m:
            break
    if r != m:
        raise AssertionError(f'projection block is not full row rank: rank={r}, rows={m}')
    return pivots


def inverse_mod_square(mat: np.ndarray, p: int) -> np.ndarray:
    """Inverse of a square matrix over F_p by deterministic Gauss-Jordan."""
    B = np.asarray(mat, dtype=np.int64).copy() % p
    m, n = B.shape
    if m != n:
        raise AssertionError('matrix inverse requested for non-square matrix')
    A = np.concatenate([B, np.eye(m, dtype=np.int64)], axis=1) % p
    r = 0
    for c in range(m):
        piv = None
        for i in range(r, m):
            if int(A[i, c]) % p:
                piv = i
                break
        if piv is None:
            raise AssertionError('singular pivot block in tube projection section')
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), -1, p)
        A[r, :] = (A[r, :] * inv) % p
        nz = np.nonzero(A[:, c])[0]
        for i in nz:
            if i != r:
                A[i, :] = (A[i, :] - A[i, c] * A[r, :]) % p
        r += 1
    return A[:, m:]
