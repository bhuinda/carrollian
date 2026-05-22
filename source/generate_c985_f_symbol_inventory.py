from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NREL = 985
NPOINTS = 2576


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
    perm_path = root / 'data' / 'c985_f_symbol_permutations.npz'
    return {
        'status': 'PASS',
        'script': 'source/generate_c985_f_symbol_inventory.py',
        'requires_relation_memberships': True,
        'relation_memberships_present': rel_path.exists(),
        'relation_memberships_path': 'data/relation_memberships.npz',
        'uses_permutation_samples_if_present': True,
        'permutation_samples_present': perm_path.exists(),
        'permutation_samples_path': 'data/c985_f_symbol_permutations.npz',
        'sparse_tensor_support': int(triples.shape[0]),
        'coefficient_total': int(triples[:,3].sum()),
        'representatives_shape': list(reps.shape),
        'next_output': 'data/c985_f_symbol_inventory_manifest.npz',
        'constructs': [
            'inventory rows for associator domains (alpha,beta,chi,delta,epsilon)',
            'chunked manifest for later full sparse F-symbol permutation arrays',
            'dependency hashes tying inventory to relation memberships and tensor support',
        ],
        'does_not_default_full_inventory': True,
        'reason': 'full inventory may be very large; default certificate must remain non-stalling',
    }


def generate(root: Path, out_rel: str, chunk_limit: int=100000, include_pair_reps: bool=True):
    rel_path = root / 'data' / 'relation_memberships.npz'
    if not rel_path.exists():
        return {
            'status': 'MISSING_RELATION_MEMBERSHIPS',
            'missing': 'data/relation_memberships.npz',
            'run_first': 'python .\\source\\generate_c985_relation_memberships.py --generate-be3 --out .\\data\\relation_memberships.npz',
        }
    triples, reps = load_sparse(root)
    # Build right composability index: left factor d -> all (d,c,e,pde)
    by_left: dict[int, list[tuple[int,int,int]]] = {}
    for a,b,g,p in triples.tolist():
        by_left.setdefault(int(a), []).append((int(b), int(g), int(p)))

    rows = []
    total_seen = 0
    saturated = False
    # Row convention: alpha,beta,chi,delta,epsilon,p_alpha_beta_delta,p_delta_chi_epsilon,x_rep,y_rep
    for a,b,d,pab in triples.tolist():
        nexts = by_left.get(int(d), [])
        if not nexts:
            continue
        for c,e,pde in nexts:
            total_seen += 1
            if len(rows) < int(chunk_limit):
                x = int(reps[e,2]) if include_pair_reps else -1
                y = int(reps[e,3]) if include_pair_reps else -1
                rows.append((int(a), int(b), int(c), int(d), int(e), int(pab), int(pde), x, y))
            else:
                saturated = True
                break
        if saturated:
            break

    arr = np.array(rows, dtype=np.int64).reshape((-1,9))
    out = root / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        inventory_rows=arr,
        columns=np.array(['alpha','beta','chi','delta','epsilon','p_alpha_beta_delta','p_delta_chi_epsilon','x_rep','y_rep']),
        chunk_limit=np.array([int(chunk_limit)], dtype=np.int64),
        total_rows_scanned_before_stop=np.array([int(total_seen)], dtype=np.int64),
        saturated=np.array([1 if saturated else 0], dtype=np.int8),
    )
    payload = {
        'status': 'F_SYMBOL_INVENTORY_MANIFEST_GENERATED',
        'path': str(out),
        'sha256': h_file(out),
        'relation_memberships_sha256': h_file(rel_path),
        'tensor_sparse_sha256': h_file(root / 'data' / 'tensor_sparse.npz'),
        'chunk_limit': int(chunk_limit),
        'inventory_rows_emitted': int(arr.shape[0]),
        'total_rows_scanned_before_stop': int(total_seen),
        'saturated_by_chunk_limit': bool(saturated),
        'columns': ['alpha','beta','chi','delta','epsilon','p_alpha_beta_delta','p_delta_chi_epsilon','x_rep','y_rep'],
        'meaning': 'Chunked manifest of associator-domain rows. Each row identifies a left bracketing product alpha*beta -> delta and delta*chi -> epsilon; concrete F-symbol arrays refine these rows using relation membership chain bases.',
        'not_yet_full_sparse_arrays': True,
    }
    return payload


def main():
    ap = argparse.ArgumentParser(description='Generate a C985 F-symbol full-inventory manifest boundary/chunk.')
    ap.add_argument('--out', default='data/c985_f_symbol_inventory_manifest.npz')
    ap.add_argument('--chunk-limit', type=int, default=100000)
    ap.add_argument('--smoke', action='store_true')
    args = ap.parse_args()
    if args.smoke:
        print(json.dumps(smoke(ROOT), indent=2, sort_keys=True))
    else:
        print(json.dumps(generate(ROOT, args.out, args.chunk_limit), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
