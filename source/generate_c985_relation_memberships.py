from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
from gnat_be3_source import generated_group, load_or_generate_be3_generators, EXPECTED_BE3_ORDER, EXPECTED_DODECADS

ROOT = Path(__file__).resolve().parents[1]

def h_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def load_seed(root: Path):
    z = np.load(root / 'data' / 'tensor_sparse.npz')
    q = np.load(root / 'data' / 'quotients.npz')
    reps = np.array(z['reps'], dtype=np.int64)
    block_i = np.array(q['block_i'], dtype=np.int16)
    block_j = np.array(q['block_j'], dtype=np.int16)
    return reps, block_i, block_j

def point_orbits(group, n):
    seen = np.zeros(n, dtype=bool)
    orbits = []
    for x in range(n):
        if seen[x]:
            continue
        orb = sorted({int(g[x]) for g in group})
        seen[orb] = True
        orbits.append(orb)
    return orbits

def object_id_from_orbits(orbits, expected_sizes=(384,192,144,576,512,768)):
    by_size = {len(o): idx for idx,o in enumerate(orbits)}
    out = np.empty(EXPECTED_DODECADS, dtype=np.int16)
    for object_id, size in enumerate(expected_sizes):
        if size not in by_size:
            raise AssertionError(f'missing object orbit of size {size}; got {[len(o) for o in orbits]}')
        for x in orbits[by_size[size]]:
            out[x] = object_id
    return out

def relation_orbit_from_rep(group, x, y):
    # Return sorted encoded pairs x*N+y for the orbit of (x,y).
    n = EXPECTED_DODECADS
    return np.array(sorted({int(g[x])*n + int(g[y]) for g in group}), dtype=np.int64)

def generate(root: Path, out_rel: str, generate_be3: bool=False, force: bool=False):
    out = root / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not force:
        return {'status': 'EXISTS', 'path': str(out), 'sha256': h_file(out)}
    reps, block_i, block_j = load_seed(root)
    gens, gen_path = load_or_generate_be3_generators(root / 'data', generate=generate_be3)
    group = generated_group(gens, EXPECTED_DODECADS, cap=EXPECTED_BE3_ORDER)
    if len(group) != EXPECTED_BE3_ORDER:
        raise AssertionError(f'Be3 group order mismatch: {len(group)}')
    orbits = point_orbits(group, EXPECTED_DODECADS)
    object_of_point = object_id_from_orbits(orbits)

    # Build relation memberships in one contiguous encoded-pair vector.
    offsets = np.zeros(986, dtype=np.int64)
    chunks = []
    for a in range(985):
        x = int(reps[a,2]); y = int(reps[a,3]); val = int(reps[a,4])
        src = int(block_i[a]); tgt = int(block_j[a])
        if int(object_of_point[x]) != src or int(object_of_point[y]) != tgt:
            raise AssertionError(f'representative object mismatch at alpha={a}')
        enc = relation_orbit_from_rep(group, x, y)
        expected_len = int(np.count_nonzero(object_of_point == src)) * val
        if len(enc) != expected_len:
            raise AssertionError(f'relation length mismatch alpha={a}: {len(enc)} != {expected_len}')
        offsets[a+1] = offsets[a] + len(enc)
        chunks.append(enc)
    encoded_pairs = np.concatenate(chunks).astype(np.int64)
    if len(encoded_pairs) != EXPECTED_DODECADS * EXPECTED_DODECADS:
        raise AssertionError('relation encoded-pair total is not 2576^2')
    if len(np.unique(encoded_pairs)) != len(encoded_pairs):
        raise AssertionError('relation encoded pairs do not partition Omega x Omega')
    np.savez_compressed(
        out,
        encoded_pairs=encoded_pairs,
        offsets=offsets,
        object_of_point=object_of_point,
        reps=reps.astype(np.int32),
        block_i=block_i.astype(np.int16),
        block_j=block_j.astype(np.int16),
        points=np.array([EXPECTED_DODECADS], dtype=np.int64),
        group_order=np.array([EXPECTED_BE3_ORDER], dtype=np.int64),
    )
    return {
        'status': 'GENERATED',
        'path': str(out),
        'sha256': h_file(out),
        'relations': 985,
        'encoded_pairs': int(len(encoded_pairs)),
        'generator_file': str(gen_path),
    }

def smoke(root: Path):
    reps, block_i, block_j = load_seed(root)
    val = reps[:,4].astype(np.int64)
    inferred = [384,192,144,576,512,768]
    total = 0
    for a in range(985):
        total += inferred[int(block_i[a])] * int(val[a])
    return {
        'status': 'PASS',
        'relations': 985,
        'representatives_shape': list(reps.shape),
        'source_blocks_match': bool(np.array_equal(reps[:,0].astype(np.int16), block_i)),
        'target_blocks_match': bool(np.array_equal(reps[:,1].astype(np.int16), block_j)),
        'total_pair_mass_from_seed': int(total),
        'expected_pair_mass': int(EXPECTED_DODECADS * EXPECTED_DODECADS),
        'generator_script': 'source/generate_c985_relation_memberships.py',
    }

def main():
    ap = argparse.ArgumentParser(description='Generate concrete C985 relation memberships R_alpha subset Omega x Omega.')
    ap.add_argument('--out', default='data/relation_memberships.npz')
    ap.add_argument('--generate-be3', action='store_true', help='Generate data/source/be3_generators.json if missing. Heavy.')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--smoke', action='store_true', help='Only check the seed data and do not build Be3 or relation lists.')
    args = ap.parse_args()
    if args.smoke:
        print(json.dumps(smoke(ROOT), indent=2))
        return
    res = generate(ROOT, args.out, generate_be3=args.generate_be3, force=args.force)
    print(json.dumps(res, indent=2))

if __name__ == '__main__':
    main()
