#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap
import argparse, hashlib, json
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, Iterable
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NREL = 985
P_DEFAULT = 1000003

try:
    from .certify_io import raw_tensor_relpath
except ImportError:  # Supports `python src/solve_half_braiding.py`.
    from certify_io import raw_tensor_relpath


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def h_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def h_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_blocks():
    rel = np.load(ROOT / 'data/raw/relation_memberships.npz')
    bi = np.asarray(rel['block_i'], dtype=np.int64)
    bj = np.asarray(rel['block_j'], dtype=np.int64)
    loops = [np.where((bi == i) & (bj == i))[0].astype(np.int64) for i in range(6)]
    unknowns = []
    col_of = {}
    for i, L in enumerate(loops):
        for a in L.tolist():
            col_of[(i, int(a))] = len(unknowns)
            unknowns.append((i, int(a)))
    return bi, bj, loops, unknowns, col_of


def build_pair_terms():
    triples = np.asarray(np.load(ROOT / raw_tensor_relpath())['triples'], dtype=np.int64)
    pair_terms: dict[tuple[int,int], list[tuple[int,int]]] = defaultdict(list)
    for a, b, c, v in triples.tolist():
        pair_terms[(int(a), int(b))].append((int(c), int(v)))
    return triples, pair_terms


def half_braiding_rows(alpha_ids: Iterable[int], p: int, bi, bj, loops, col_of, pair_terms):
    """Yield sparse rows for z_src(alpha)*alpha = alpha*z_tgt(alpha).

    Unknowns are closed-loop coefficients z_i in Hom(i,i), one family per object.
    A row is a dict col->coefficient modulo p for one output relation gamma.
    """
    for alpha in alpha_ids:
        alpha = int(alpha)
        i = int(bi[alpha]); j = int(bj[alpha])
        eqs: dict[int, dict[int,int]] = defaultdict(dict)
        for a in loops[i].tolist():
            col = col_of[(i, int(a))]
            for gamma, v in pair_terms.get((int(a), alpha), []):
                d = eqs[int(gamma)]
                d[col] = (d.get(col, 0) + int(v)) % p
        for b in loops[j].tolist():
            col = col_of[(j, int(b))]
            for gamma, v in pair_terms.get((alpha, int(b)), []):
                d = eqs[int(gamma)]
                d[col] = (d.get(col, 0) - int(v)) % p
        for row in eqs.values():
            row = {c: (v % p) for c, v in row.items() if v % p}
            if row:
                yield row


def sparse_rank_and_basis(rows: Iterable[dict[int,int]], nvars: int, p: int, keep_basis: bool = False):
    pivots: dict[int, dict[int,int]] = {}
    raw_rows = 0
    nonzero_rows = 0
    for row in rows:
        raw_rows += 1
        row = {int(c): int(v) % p for c, v in row.items() if int(v) % p}
        if not row:
            continue
        while row:
            pc = min(row)
            coeff = row[pc] % p
            if coeff == 0:
                del row[pc]
                continue
            if pc in pivots:
                prow = pivots[pc]
                factor = coeff
                for c, v in prow.items():
                    nv = (row.get(c, 0) - factor * v) % p
                    if nv:
                        row[c] = nv
                    elif c in row:
                        del row[c]
            else:
                inv = pow(coeff, -1, p)
                row = {c: (v * inv) % p for c, v in row.items() if (v * inv) % p}
                pivots[pc] = row
                nonzero_rows += 1
                break
    pivot_cols = sorted(pivots)
    free_cols = [c for c in range(nvars) if c not in set(pivot_cols)]
    basis_hash = None
    basis_shape = [nvars, len(free_cols)]
    if keep_basis:
        B = np.zeros((nvars, len(free_cols)), dtype=np.int64)
        for j, fc in enumerate(free_cols):
            B[fc, j] = 1
            for pc in pivot_cols:
                row = pivots[pc]
                if fc in row:
                    B[pc, j] = (-row[fc]) % p
        basis_hash = h_array(B)
    pivot_items = []
    for pc in pivot_cols:
        row = pivots[pc]
        pivot_items.append((pc, tuple(sorted(row.items()))))
    reducer_hash = hashlib.sha256(repr(pivot_items).encode('utf-8')).hexdigest()
    return {
        'raw_rows_seen': int(raw_rows),
        'rank': int(len(pivot_cols)),
        'nullity': int(nvars - len(pivot_cols)),
        'pivot_count': int(len(pivot_cols)),
        'free_count': int(len(free_cols)),
        'pivot_columns_sha256': h_array(np.asarray(pivot_cols, dtype=np.int64)),
        'free_columns_sha256': h_array(np.asarray(free_cols, dtype=np.int64)),
        'reducer_sha256': reducer_hash,
        'nullspace_basis_shape': basis_shape,
        'nullspace_basis_sha256': basis_hash,
    }


def solve(sample_relations: int | None, full: bool, p: int, keep_basis: bool) -> Dict[str, Any]:
    bi, bj, loops, unknowns, col_of = load_blocks()
    triples, pair_terms = build_pair_terms()
    nvars = len(unknowns)
    ids = list(range(NREL if full else int(sample_relations or 128)))
    rows_iter = half_braiding_rows(ids, p, bi, bj, loops, col_of, pair_terms)
    rr = sparse_rank_and_basis(rows_iter, nvars, p, keep_basis=keep_basis)
    loop_counts = [int(len(x)) for x in loops]
    relation_count_matrix = np.zeros((6,6), dtype=np.int64)
    for i,j in zip(bi,bj):
        relation_count_matrix[int(i), int(j)] += 1
    mode = 'full' if full else 'prefix_sample'
    result = {
        'schema': 'gnatural.c985.half_braiding_solver.source_drop',
        'status': 'HALF_BRAIDING_SOLVER_FULL_SOLVED' if full else 'HALF_BRAIDING_SOLVER_REGISTERED_PREFIX_SAMPLE',
        'field': {'prime': int(p)},
        'equation': 'For every simple relation alpha:i->j, solve z_i * alpha = alpha * z_j with z_i in Hom(i,i).',
        'mode': mode,
        'sample_relations': None if full else int(sample_relations or 128),
        'relations_used': int(len(ids)),
        'unknown_family': {
            'description': 'closed-loop coefficients z_i over all six object blocks',
            'unknown_count': int(nvars),
            'unknown_count_by_object': loop_counts,
            'unknown_order_sha256': hashlib.sha256(repr(unknowns).encode('utf-8')).hexdigest(),
        },
        'input_shape': {
            'relations': NREL,
            'tensor_support_rows': int(triples.shape[0]),
            'relation_count_matrix': relation_count_matrix.astype(int).tolist(),
        },
        'linear_system': rr,
        'complete_or_sampled': 'complete' if full else 'sampled',
        'claim_boundary': 'A full run is an exact finite-field Grothendieck half-braiding solve. The default certificate only registers and smoke-checks the solver unless --full is used.',
        'verified_claims': [
            'The half-braiding solver constructs the finite linear equations z_src(alpha)*alpha = alpha*z_tgt(alpha).',
            'Unknowns are closed-loop coefficients over the six diagonal Hom(i,i) sectors.',
            'The prefix-sample mode checks the solver pipeline without claiming a complete Drinfeld-center solve.',
        ],
    }
    result['c985_half_braiding_solver_sha256'] = h_json(result)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/derived/half_braiding_solver.json')
    ap.add_argument('--sample-relations', type=int, default=128)
    ap.add_argument('--prime', type=int, default=P_DEFAULT)
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--basis', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    res = solve(args.sample_relations, args.full, args.prime, args.basis)
    out = Path(args.out)
    if not out.is_absolute(): out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        if args.pretty: json.dump(res, f, indent=2, sort_keys=True)
        else: json.dump(res, f, sort_keys=True, separators=(',', ':'))
        f.write('\n')
    print('HALF_BRAIDING_SOLVER', res['status'])
    print('rows =', res['linear_system']['raw_rows_seen'])
    print('rank =', res['linear_system']['rank'])
    print('nullity =', res['linear_system']['nullity'])
    print('sha256 =', res['c985_half_braiding_solver_sha256'])
    print('written =', out)

if __name__ == '__main__':
    main()
