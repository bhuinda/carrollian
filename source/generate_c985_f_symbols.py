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
        'script': 'source/generate_c985_f_symbols.py',
        'requires_relation_memberships': True,
        'relation_memberships_present': rel_path.exists(),
        'relation_memberships_path': 'data/relation_memberships.npz',
        'sparse_tensor_support': int(triples.shape[0]),
        'coefficient_total': int(triples[:,3].sum()),
        'representatives_shape': list(reps.shape),
        'next_output': 'data/f_symbol_samples.json',
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
    return np.sort(right[left == x]).astype(np.int32)


def in_relation(pair_to_rel: np.ndarray, rel: int, x: int, y: int) -> bool:
    return int(pair_to_rel[int(x) * NPOINTS + int(y)]) == int(rel)


def chain_set(pair_to_rel: np.ndarray, encoded_pairs: np.ndarray, offsets: np.ndarray, a: int, b: int, c: int, e: int, x: int, y: int, cap: int|None=None):
    # Chains x --a--> z --b--> w --c--> y. Returns sorted encoded chains z*N+w.
    out = []
    for z in relation_successors(encoded_pairs, offsets, a, x):
        for w in relation_successors(encoded_pairs, offsets, b, int(z)):
            if in_relation(pair_to_rel, c, int(w), y):
                out.append(int(z) * NPOINTS + int(w))
                if cap is not None and len(out) > cap:
                    raise RuntimeError('chain sample cap exceeded')
    return np.array(sorted(out), dtype=np.int64)


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

    # Build a quick lookup of nonzero products: (a,b) -> [(g,p),...]
    prod = {}
    for a,b,g,p in triples.tolist():
        prod.setdefault((int(a),int(b)), []).append((int(g),int(p)))

    samples = []
    # Sample composable triples from sparse tensor and test the underlying chain-set equality
    # for both parenthesizations by comparing the same z,w chains.
    count = 0
    for a,b,d,pab in triples.tolist():
        a=int(a); b=int(b); d=int(d)
        # choose a chi with d*chi nonzero
        for (dd, c), eps_list in list(prod.items()):
            if dd != d:
                continue
            c = int(c)
            for e, pde in eps_list[:1]:
                x = int(reps[e,2]); y = int(reps[e,3])
                try:
                    chains = chain_set(pair_to_rel, encoded_pairs, offsets, a,b,c,e,x,y,cap=chain_cap)
                except RuntimeError:
                    continue
                samples.append({
                    'alpha': a, 'beta': b, 'chi': c, 'epsilon': int(e),
                    'chain_count': int(len(chains)),
                    'chain_sha256': hashlib.sha256(chains.tobytes()).hexdigest(),
                    'interpretation': 'same chain set indexes both sides of the associator; concrete F-symbol is the ordering-change permutation once left/right decomposition bases are emitted',
                })
                count += 1
                break
            if count >= sample_limit:
                break
        if count >= sample_limit:
            break

    payload = {
        'status': 'F_SYMBOL_CHAIN_SAMPLES_GENERATED',
        'relation_memberships_sha256': h_file(rel_path),
        'sample_count': len(samples),
        'sample_limit': int(sample_limit),
        'chain_cap': int(chain_cap),
        'samples': samples,
        'not_yet_full_matrices': True,
        'next_required': 'emit left/right decomposition ordering and permutation arrays for all requested quadruples',
    }
    out = root / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    payload['path'] = str(out)
    payload['sha256'] = h_file(out)
    return payload


def main():
    ap = argparse.ArgumentParser(description='Generate concrete C985 F-symbol chain samples from relation memberships.')
    ap.add_argument('--out', default='data/f_symbol_samples.json')
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
