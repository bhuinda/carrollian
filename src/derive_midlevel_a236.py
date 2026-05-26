from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
P = 1000003


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def rank_mod_numpy(A: np.ndarray, p: int = P) -> int:
    """Dense row rank over F_p using vectorized numpy elimination.

    This is intentionally dependency-light: numpy only.  The intended matrix here
    is at most 55,696 x 236, so the check is finite and quick on a normal dev box.
    """
    A = np.asarray(A, dtype=np.int64).copy() % p
    m, n = A.shape
    r = 0
    for c in range(n):
        nz = np.flatnonzero(A[r:, c] % p)
        if nz.size == 0:
            continue
        piv = r + int(nz[0])
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), p - 2, p)
        A[r, c:] = (A[r, c:] * inv) % p
        rows = np.flatnonzero(A[:, c] % p)
        rows = rows[rows != r]
        if rows.size:
            fac = A[rows, c].copy() % p
            A[rows, c:] = (A[rows, c:] - fac[:, None] * A[r, c:]) % p
        r += 1
        if r == n:
            break
    return int(r)


def center_rank_for_local_tensor(local_triples: np.ndarray, n: int, p: int = P) -> dict[str, Any]:
    """Compute center dimension of an n-dimensional algebra from sparse constants.

    Equation for x=sum_i x_i e_i:
        x e_j = e_j x for every basis element e_j.
    For every (a,b,c,w), add +w to row (b,c), column a, and -w to row (a,c), column b.
    """
    A = np.zeros((n * n, n), dtype=np.int64)
    for a, b, c, w in local_triples.astype(np.int64, copy=False):
        A[int(b) * n + int(c), int(a)] = (A[int(b) * n + int(c), int(a)] + int(w)) % p
        A[int(a) * n + int(c), int(b)] = (A[int(a) * n + int(c), int(b)] - int(w)) % p
    rank = rank_mod_numpy(A, p)
    return {
        'field_prime': int(p),
        'commutator_matrix_shape': [int(A.shape[0]), int(A.shape[1])],
        'commutator_matrix_nonzero': int(np.count_nonzero(A)),
        'commutator_matrix_sha256': sha_array(A),
        'center_rank': int(n - rank),
        'commutator_rank': int(rank),
    }


def derive_midlevel_a236(
    relation_npz: Path,
    tensor_npz: Path,
    selector_json: Path,
    out_npz: Path | None = None,
    compare_constants_json: Path | None = None,
    check_center: bool = True,
) -> dict[str, Any]:
    rel = np.load(relation_npz)
    block_i = np.asarray(rel['block_i'], dtype=np.int16)
    block_j = np.asarray(rel['block_j'], dtype=np.int16)
    offsets = np.asarray(rel['offsets'], dtype=np.int64)
    reps = np.asarray(rel['reps'], dtype=np.int32)
    selector = load_json(selector_json)
    object_to_sector = np.asarray(selector['object_to_sector'], dtype=np.int16)
    sector_names = selector.get('sector_names', ['B', 'V', 'S'])
    spin_sector = int(selector.get('midlevel_candidate_sector', 2))

    rel_sizes = np.diff(offsets).astype(np.int64)
    ternary_i = object_to_sector[block_i]
    ternary_j = object_to_sector[block_j]
    relation_count_matrix = np.zeros((3, 3), dtype=np.int64)
    pair_mass_matrix = np.zeros((3, 3), dtype=np.int64)
    for a in range(offsets.size - 1):
        s = int(ternary_i[a]); t = int(ternary_j[a])
        relation_count_matrix[s, t] += 1
        pair_mass_matrix[s, t] += int(rel_sizes[a])

    candidate = np.where((ternary_i == spin_sector) & (ternary_j == spin_sector))[0].astype(np.int32)
    prior_to_local = np.full(offsets.size - 1, -1, dtype=np.int32)
    prior_to_local[candidate] = np.arange(candidate.size, dtype=np.int32)

    T = np.load(tensor_npz)
    triples = np.asarray(T['triples'], dtype=np.int64)
    ab_candidate = (prior_to_local[triples[:, 0]] >= 0) & (prior_to_local[triples[:, 1]] >= 0)
    abc_candidate = ab_candidate & (prior_to_local[triples[:, 2]] >= 0)
    outside = ab_candidate & (prior_to_local[triples[:, 2]] < 0)

    local_triples = np.empty((int(np.count_nonzero(abc_candidate)), 4), dtype=np.int32)
    local_triples[:, 0] = prior_to_local[triples[abc_candidate, 0]]
    local_triples[:, 1] = prior_to_local[triples[abc_candidate, 1]]
    local_triples[:, 2] = prior_to_local[triples[abc_candidate, 2]]
    local_triples[:, 3] = triples[abc_candidate, 3].astype(np.int32)

    object_block_counts: dict[str, int] = {}
    for i in range(6):
        for j in range(6):
            m = np.count_nonzero((block_i[candidate] == i) & (block_j[candidate] == j))
            if m:
                object_block_counts[f'{i}->{j}'] = int(m)

    if out_npz is not None:
        out_npz.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            out_npz,
            candidate_relation_ids=candidate,
            local_triples=local_triples,
            relation_count_matrix=relation_count_matrix,
            pair_mass_matrix=pair_mass_matrix,
            prior_to_local=prior_to_local,
            reps=reps[candidate],
            block_i=block_i[candidate],
            block_j=block_j[candidate],
        )

    center = None
    if check_center:
        center = center_rank_for_local_tensor(local_triples.astype(np.int64), int(candidate.size), P)

    expected: dict[str, Any] = {}
    if compare_constants_json is not None and compare_constants_json.exists():
        constants = load_json(compare_constants_json)
        expected = constants.get('A236', {})

    expected_center = expected.get('center_dim')
    expected_dim = expected.get('dimension')
    center_matches_expected = None
    if center is not None and expected_center is not None:
        center_matches_expected = bool(center['center_rank'] == int(expected_center))

    dim_matches_expected = expected_dim is not None and int(candidate.size) == int(expected_dim)
    closure_ok = bool(np.count_nonzero(outside) == 0 and int(triples[outside, 3].sum()) == 0)

    if center is None:
        status = 'MIDLEVEL_A236_CANDIDATE_DERIVED_CENTER_UNCHECKED'
    elif dim_matches_expected and closure_ok and center_matches_expected:
        status = 'MIDLEVEL_A236_PASS'
    else:
        status = 'MIDLEVEL_A236_SELECTOR_STILL_MISSING'

    result: dict[str, Any] = {
        'schema': 'd20.constructor.midlevel_a236_boundary@1',
        'constructor_status': status,
        'predicate': 'is integral',
        'construction_method': 'derive the natural level-2 S->S clopen block from generated relation data and generated T985, then test whether it is the certified A236 algebra',
        'relation_npz': str(relation_npz.relative_to(ROOT)) if relation_npz.is_relative_to(ROOT) else str(relation_npz),
        'tensor_npz': str(tensor_npz.relative_to(ROOT)) if tensor_npz.is_relative_to(ROOT) else str(tensor_npz),
        'selector_json': str(selector_json.relative_to(ROOT)) if selector_json.is_relative_to(ROOT) else str(selector_json),
        'sector_names': sector_names,
        'candidate_sector': int(spin_sector),
        'candidate_sector_name': str(sector_names[spin_sector]) if spin_sector < len(sector_names) else str(spin_sector),
        'level2_relation_count_matrix': relation_count_matrix.astype(int).tolist(),
        'level2_pair_mass_matrix': pair_mass_matrix.astype(int).tolist(),
        'candidate_relation_count': int(candidate.size),
        'candidate_relation_ids_sha256': sha_array(candidate),
        'candidate_object_block_counts': object_block_counts,
        'closure': {
            'closed_under_generated_T985': closure_ok,
            'outside_support_rows': int(np.count_nonzero(outside)),
            'outside_coefficient_total': int(triples[outside, 3].sum()),
            'local_support_rows': int(local_triples.shape[0]),
            'local_coefficient_total': int(local_triples[:, 3].sum()),
            'local_tensor_sha256': sha_array(local_triples),
        },
        'expected_A236_certificate': expected,
        'dimension_matches_expected_A236': bool(dim_matches_expected),
        'center_check': center,
        'center_matches_expected_A236': center_matches_expected,
        'conclusion': None,
        'remaining_boundary': None,
    }

    if status == 'MIDLEVEL_A236_SELECTOR_STILL_MISSING':
        result['conclusion'] = (
            'The natural S->S clopen block has the correct dimension 236 and is closed under T985, '
            'but its computed center dimension does not match the certified A236 center dimension. '
            'Therefore certified A236 is not merely the terminal S->S block; it requires an additional midlevel selector/fusion law.'
        )
        result['remaining_boundary'] = [
            'derive the true A985->A236 midlevel selector/fusion law',
            'derive simple branching matrices from that generated A236 algebra',
            'derive sector 33 and the integral wall from generated center/idempotent data',
        ]
    elif status == 'MIDLEVEL_A236_PASS':
        result['conclusion'] = 'The generated candidate block matches the certified A236 dimension and center dimension.'
        result['remaining_boundary'] = [
            'derive simple branching matrices from generated A236',
            'derive sector 33 and the integral wall from generated center/idempotent data',
        ]
    else:
        result['conclusion'] = 'The natural midlevel candidate was generated; center comparison was skipped.'

    result['constructor_result_sha256'] = hashlib.sha256(
        json.dumps({k: v for k, v in result.items() if k != 'constructor_result_sha256'}, sort_keys=True, separators=(',', ':')).encode('utf-8')
    ).hexdigest()
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--relation-seed', default='generated/relation_memberships_from_source_coorient_aligned.npz')
    ap.add_argument('--tensor', default='generated/tensor_from_source_coorient.npz')
    ap.add_argument('--selector', default='data/quotient/terminal_quotient_selector.json')
    ap.add_argument('--out-npz', default='generated/a236_candidate_from_source_coorient.npz')
    ap.add_argument('--out-json', default='generated/a236_candidate_from_source_coorient_report.json')
    ap.add_argument('--skip-center', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    result = derive_midlevel_a236(
        ROOT / args.relation_seed,
        ROOT / args.tensor,
        ROOT / args.selector,
        ROOT / args.out_npz,
        ROOT / 'data/raw/constants.json',
        not args.skip_center,
    )
    out = ROOT / args.out_json
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True), encoding='utf-8')
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == '__main__':
    main()
