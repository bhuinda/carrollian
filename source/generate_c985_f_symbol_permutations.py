from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NPOINTS = 2576
NREL = 985


def h_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_sparse(root: Path):
    z = np.load(root / 'data' / 'tensor_sparse.npz')
    triples = np.array(z['triples'], dtype=np.int64)
    reps = np.array(z['reps'], dtype=np.int64)
    return triples, reps


def smoke(root: Path):
    triples, reps = load_sparse(root)
    rel_path = root / 'data' / 'relation_memberships.npz'
    return {
        'status': 'PASS',
        'script': 'source/generate_c985_f_symbol_permutations.py',
        'requires_relation_memberships': True,
        'relation_memberships_present': rel_path.exists(),
        'relation_memberships_path': 'data/relation_memberships.npz',
        'sparse_tensor_support': int(triples.shape[0]),
        'coefficient_total': int(triples[:,3].sum()),
        'representatives_shape': list(reps.shape),
        'next_output': 'data/c985_f_symbol_permutations.npz',
        'constructs': [
            'left decomposition basis ordering',
            'right decomposition basis ordering',
            'sparse permutation arrays mapping left order to right order',
        ],
    }


def build_pair_to_relation(encoded_pairs: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    pair_to_rel = np.full(NPOINTS * NPOINTS, -1, dtype=np.int32)
    for a in range(NREL):
        pair_to_rel[encoded_pairs[offsets[a]:offsets[a+1]]] = a
    if int(np.count_nonzero(pair_to_rel >= 0)) != NPOINTS * NPOINTS:
        raise AssertionError('relation memberships do not cover Omega x Omega')
    return pair_to_rel


def relation_successors(encoded_pairs: np.ndarray, offsets: np.ndarray, rel: int, x: int) -> np.ndarray:
    lo, hi = int(offsets[rel]), int(offsets[rel+1])
    pairs = encoded_pairs[lo:hi]
    left = pairs // NPOINTS
    right = pairs % NPOINTS
    return np.sort(right[left == int(x)]).astype(np.int32)


def chain_basis(pair_to_rel: np.ndarray, encoded_pairs: np.ndarray, offsets: np.ndarray, a: int, b: int, c: int, e: int, x: int, y: int, chain_cap: int):
    # Chains x --a--> z --b--> w --c--> y, with (x,y) in epsilon=e.
    # Left bracketing decomposes through delta = rel(x,w).
    # Right bracketing decomposes through eta = rel(z,y).
    chains = []
    for z in relation_successors(encoded_pairs, offsets, a, x):
        for w in relation_successors(encoded_pairs, offsets, b, int(z)):
            if int(pair_to_rel[int(w) * NPOINTS + int(y)]) == int(c):
                delta = int(pair_to_rel[int(x) * NPOINTS + int(w)])
                eta = int(pair_to_rel[int(z) * NPOINTS + int(y)])
                code = int(z) * NPOINTS + int(w)
                chains.append((delta, eta, code))
                if len(chains) > chain_cap:
                    raise RuntimeError('chain cap exceeded')
    # left and right are two orderings of the same chain set.
    left = sorted([(d, code) for d, eta, code in chains])
    right = sorted([(eta, code) for d, eta, code in chains])
    right_index = {code: idx for idx, (eta, code) in enumerate(right)}
    perm = np.array([right_index[code] for d, code in left], dtype=np.int64)
    if sorted(perm.tolist()) != list(range(len(perm))):
        raise AssertionError('left-to-right map is not a permutation')
    left_delta = np.array([d for d, code in left], dtype=np.int32)
    right_eta = np.array([eta for eta, code in right], dtype=np.int32)
    left_codes = np.array([code for d, code in left], dtype=np.int64)
    right_codes = np.array([code for eta, code in right], dtype=np.int64)
    if sorted(left_codes.tolist()) != sorted(right_codes.tolist()):
        raise AssertionError('left/right chain inventories differ')
    return left_delta, left_codes, right_eta, right_codes, perm


def generate(root: Path, out_rel: str, sample_limit: int=32, chain_cap: int=100000):
    rel_path = root / 'data' / 'relation_memberships.npz'
    if not rel_path.exists():
        return {
            'status': 'MISSING_RELATION_MEMBERSHIPS',
            'missing': 'data/relation_memberships.npz',
            'run_first': 'python .\\source\\generate_c985_relation_memberships.py --generate-be3 --out .\\data\\relation_memberships.npz',
        }
    triples, reps = load_sparse(root)
    rz = np.load(rel_path)
    encoded_pairs = np.array(rz['encoded_pairs'], dtype=np.int64)
    offsets = np.array(rz['offsets'], dtype=np.int64)
    pair_to_rel = build_pair_to_relation(encoded_pairs, offsets)

    prod = {}
    for a,b,g,p in triples.tolist():
        prod.setdefault((int(a),int(b)), []).append((int(g),int(p)))

    meta = []
    left_delta_chunks = []
    left_code_chunks = []
    right_eta_chunks = []
    right_code_chunks = []
    perm_chunks = []
    sample_offsets = [0]

    count = 0
    # Sample composable triples by using actual nonzero product chains (a*b -> d, d*c -> e).
    for (a,b), ds in prod.items():
        for d, pab in ds[:3]:
            for (dd, c), es in list(prod.items()):
                if dd != d:
                    continue
                for e, pde in es[:3]:
                    x = int(reps[e,2]); y = int(reps[e,3])
                    try:
                        left_delta, left_codes, right_eta, right_codes, perm = chain_basis(
                            pair_to_rel, encoded_pairs, offsets, int(a), int(b), int(c), int(e), x, y, chain_cap
                        )
                    except RuntimeError:
                        continue
                    if len(perm) == 0:
                        continue
                    meta.append((int(a), int(b), int(c), int(e), int(x), int(y), int(len(perm))))
                    left_delta_chunks.append(left_delta)
                    left_code_chunks.append(left_codes)
                    right_eta_chunks.append(right_eta)
                    right_code_chunks.append(right_codes)
                    perm_chunks.append(perm)
                    sample_offsets.append(sample_offsets[-1] + int(len(perm)))
                    count += 1
                    break
                if count >= sample_limit:
                    break
            if count >= sample_limit:
                break
        if count >= sample_limit:
            break

    out = root / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    if meta:
        left_delta_all = np.concatenate(left_delta_chunks).astype(np.int32)
        left_code_all = np.concatenate(left_code_chunks).astype(np.int64)
        right_eta_all = np.concatenate(right_eta_chunks).astype(np.int32)
        right_code_all = np.concatenate(right_code_chunks).astype(np.int64)
        perm_all = np.concatenate(perm_chunks).astype(np.int64)
    else:
        left_delta_all = np.zeros(0, dtype=np.int32)
        left_code_all = np.zeros(0, dtype=np.int64)
        right_eta_all = np.zeros(0, dtype=np.int32)
        right_code_all = np.zeros(0, dtype=np.int64)
        perm_all = np.zeros(0, dtype=np.int64)
    meta_arr = np.array(meta, dtype=np.int64).reshape((-1,7))
    offsets_arr = np.array(sample_offsets, dtype=np.int64)
    np.savez_compressed(
        out,
        sample_meta=meta_arr,
        sample_offsets=offsets_arr,
        left_delta=left_delta_all,
        left_chain_code=left_code_all,
        right_eta=right_eta_all,
        right_chain_code=right_code_all,
        left_to_right_perm=perm_all,
    )
    payload = {
        'status': 'F_SYMBOL_PERMUTATION_SAMPLES_GENERATED',
        'path': str(out),
        'sha256': h_file(out),
        'relation_memberships_sha256': h_file(rel_path),
        'sample_count': int(meta_arr.shape[0]),
        'sample_limit': int(sample_limit),
        'total_basis_vectors_sampled': int(perm_all.shape[0]),
        'chain_cap': int(chain_cap),
        'arrays': {
            'sample_meta': list(meta_arr.shape),
            'sample_offsets': list(offsets_arr.shape),
            'left_delta': list(left_delta_all.shape),
            'left_chain_code': list(left_code_all.shape),
            'right_eta': list(right_eta_all.shape),
            'right_chain_code': list(right_code_all.shape),
            'left_to_right_perm': list(perm_all.shape),
        },
        'meaning': 'For each sampled (alpha,beta,chi,epsilon,x,y), left/right decomposition bases are ordered and left_to_right_perm is the concrete sparse F-symbol permutation array between them.',
        'not_yet_full_inventory': True,
    }
    return payload


def main():
    ap = argparse.ArgumentParser(description='Generate C985 F-symbol left/right basis orderings and sparse permutation samples.')
    ap.add_argument('--out', default='data/c985_f_symbol_permutations.npz')
    ap.add_argument('--sample-limit', type=int, default=32)
    ap.add_argument('--chain-cap', type=int, default=100000)
    ap.add_argument('--smoke', action='store_true')
    args = ap.parse_args()
    if args.smoke:
        print(json.dumps(smoke(ROOT), indent=2, sort_keys=True))
    else:
        print(json.dumps(generate(ROOT, args.out, args.sample_limit, args.chain_cap), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
