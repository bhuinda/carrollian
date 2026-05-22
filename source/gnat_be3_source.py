from __future__ import annotations
from itertools import product, permutations
from collections import deque
from pathlib import Path
import json

EXPECTED_CODE_SIZE = 4096
EXPECTED_DODECADS = 2576
EXPECTED_BE3_ORDER = 9216
EXPECTED_ORBITALS = 985
EXPECTED_OBJECT_ORBIT_SIZES = sorted([384, 192, 144, 576, 512, 768])

SEXTET = [
    (0,1,2,3),
    (4,5,6,7),
    (8,9,12,13),
    (10,11,14,15),
    (16,17,22,23),
    (18,19,20,21),
]
PAIR_BLOCKS = [(0,3),(1,4),(2,5)]

def wt(x: int) -> int:
    return int(x.bit_count())

def mask_from_one_based(S) -> int:
    x = 0
    for i in S:
        x |= 1 << (i-1)
    return x

def span_int(gens, nbits=24):
    S = {0}
    for g in gens:
        S |= {x ^ g for x in list(S)}
    return sorted(S)

def h8_codewords_8bit():
    pts = list(product([0,1], repeat=3))
    gens = []
    gens.append(sum(1 << i for i,_ in enumerate(pts)))
    for j in range(3):
        m = 0
        for i,p in enumerate(pts):
            if p[j]:
                m |= 1 << i
        gens.append(m)
    return span_int(gens, 8), gens

def lift8(block_word: int, block: int) -> int:
    return block_word << (8*block)

def row_reduce_basis(codewords):
    basis = []
    pivots = []
    for x in codewords:
        y = x
        for b,p in zip(basis, pivots):
            if (y >> p) & 1:
                y ^= b
        if y:
            p = y.bit_length() - 1
            for idx,b in enumerate(basis):
                if (b >> p) & 1:
                    basis[idx] ^= y
            insert = 0
            while insert < len(pivots) and pivots[insert] > p:
                insert += 1
            basis.insert(insert, y)
            pivots.insert(insert, p)
    return basis

def dot_mod2(x: int, y: int) -> int:
    return (x & y).bit_count() & 1

def neighbor(codewords, v):
    sub = [c for c in codewords if dot_mod2(c,v)==0]
    basis = row_reduce_basis(sub) + [v]
    return span_int(basis, 24)

def build_g24_ints():
    H8,_ = h8_codewords_8bit()
    gens = []
    for block in range(3):
        for h in row_reduce_basis(H8):
            gens.append(lift8(h, block))
    C = span_int(gens, 24)
    v1 = mask_from_one_based({2,4,9,10,12,13,14,16,17,18,20,22})
    v2 = mask_from_one_based({3,4,9,13,15,16,19,20})
    v3 = mask_from_one_based({2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23})
    history = []
    for v in (v1,v2,v3):
        history.append(sum(1 for c in C if wt(c)==4))
        C = neighbor(C, v)
    history.append(sum(1 for c in C if wt(c)==4))
    if history != [42,18,6,0]:
        raise AssertionError(f'root history mismatch: {history}')
    if len(C) != EXPECTED_CODE_SIZE:
        raise AssertionError(f'code size mismatch: {len(C)}')
    return sorted(C)

def build_dodecad_shell():
    C = build_g24_ints()
    dodecads = sorted([c for c in C if wt(c) == 12])
    if len(dodecads) != EXPECTED_DODECADS:
        raise AssertionError(f'dodecad count mismatch: {len(dodecads)}')
    return dodecads

def apply_coord_perm(mask: int, perm_old_to_new) -> int:
    y = 0
    x = mask
    while x:
        lsb = x & -x
        old = lsb.bit_length() - 1
        y |= 1 << perm_old_to_new[old]
        x ^= lsb
    return y

def sextet_pair_maps():
    maps = []
    for pair_perm in permutations(range(3)):
        for flips in product([0,1], repeat=3):
            m = [None]*6
            for a, target_pair_index in enumerate(pair_perm):
                src_pair = PAIR_BLOCKS[a]
                dst_pair = PAIR_BLOCKS[target_pair_index]
                if flips[a] == 0:
                    m[src_pair[0]] = dst_pair[0]
                    m[src_pair[1]] = dst_pair[1]
                else:
                    m[src_pair[0]] = dst_pair[1]
                    m[src_pair[1]] = dst_pair[0]
            maps.append(tuple(m))
    return maps

def _basis_candidate_tables(codewords, basis):
    by_weight = {}
    for c in codewords:
        by_weight.setdefault(wt(c), []).append(c)
    return [by_weight[wt(b)] for b in basis]

def enumerate_code_preserving_sextet_perms(codewords, max_count=None):
    Cset = set(codewords)
    basis = row_reduce_basis(codewords)
    if len(basis) != 12:
        raise AssertionError(f'expected 12-dimensional code basis, got {len(basis)}')
    base_candidates = _basis_candidate_tables(codewords, basis)
    coord_order = [i for tetrad in SEXTET for i in tetrad]
    tetrad_of = {}
    for ti,T in enumerate(SEXTET):
        for c in T:
            tetrad_of[c] = ti
    results = []
    def filtered(cands, old, new):
        bit_old = 1 << old
        bit_new = 1 << new
        out = []
        for b, cand_list in zip(basis, cands):
            want = bool(b & bit_old)
            if want:
                sub = [d for d in cand_list if d & bit_new]
            else:
                sub = [d for d in cand_list if not (d & bit_new)]
            if not sub:
                return None
            out.append(sub)
        return out
    for tetrad_map in sextet_pair_maps():
        target_allowed = {old_t: list(SEXTET[tetrad_map[old_t]]) for old_t in range(6)}
        used = set()
        perm = [-1]*24
        def backtrack(pos, cands):
            if max_count is not None and len(results) >= max_count:
                return
            if pos == 24:
                p = tuple(perm)
                for b in basis:
                    if apply_coord_perm(b, p) not in Cset:
                        return
                results.append(p)
                return
            old = coord_order[pos]
            t = tetrad_of[old]
            for new in target_allowed[t]:
                if new in used:
                    continue
                nc = filtered(cands, old, new)
                if nc is None:
                    continue
                perm[old] = new
                used.add(new)
                backtrack(pos+1, nc)
                used.remove(new)
                perm[old] = -1
        backtrack(0, base_candidates)
    return results

def induced_dodecad_permutation(coord_perm, dodecads, index):
    return [index[apply_coord_perm(d, coord_perm)] for d in dodecads]

def compose(p, q):
    return tuple(p[i] for i in q)

def identity(n):
    return tuple(range(n))

def generated_group(perms, n, cap=None):
    e = identity(n)
    seen = {e}
    dq = deque([e])
    gens = [tuple(g) for g in perms]
    while dq:
        h = dq.popleft()
        for g in gens:
            gh = compose(g,h)
            if gh not in seen:
                seen.add(gh); dq.append(gh)
                if cap and len(seen) > cap:
                    raise RuntimeError(f'group exceeded cap {cap}')
    return list(seen)

def extract_generators(point_perms, n=EXPECTED_DODECADS, target_order=EXPECTED_BE3_ORDER):
    gens = []
    closure = {identity(n)}
    for p in point_perms:
        tp = tuple(p)
        if tp in closure:
            continue
        trial = set(generated_group(gens + [tp], n, cap=target_order))
        if len(trial) > len(closure):
            gens.append(tp)
            closure = trial
            if len(closure) == target_order:
                break
    if len(closure) != target_order:
        raise AssertionError(f'generator extraction produced order {len(closure)} not {target_order}')
    return [list(g) for g in gens]

def generate_be3_generators(data_dir: Path, write=True):
    codewords = build_g24_ints()
    dodecads = sorted([c for c in codewords if wt(c)==12])
    index = {d:i for i,d in enumerate(dodecads)}
    coord_perms = enumerate_code_preserving_sextet_perms(codewords)
    if len(coord_perms) != EXPECTED_BE3_ORDER:
        raise AssertionError(f'coordinate Be3 count mismatch: {len(coord_perms)}')
    point_perms = [induced_dodecad_permutation(p, dodecads, index) for p in coord_perms]
    unique_point_perms = list({tuple(p):p for p in point_perms}.values())
    if len(unique_point_perms) != EXPECTED_BE3_ORDER:
        raise AssertionError(f'point Be3 count mismatch: {len(unique_point_perms)}')
    gens = extract_generators(unique_point_perms)
    group = generated_group(gens, EXPECTED_DODECADS, cap=EXPECTED_BE3_ORDER)
    if len(group) != EXPECTED_BE3_ORDER:
        raise AssertionError(f'generated point group order mismatch: {len(group)}')
    payload = {
        'points': EXPECTED_DODECADS,
        'description': 'Generated Be3 dodecad-shell permutations on the sorted weight-12 Golay shell.',
        'generators': gens,
    }
    if write:
        source_dir = data_dir / 'source'
        source_dir.mkdir(parents=True, exist_ok=True)
        with (source_dir / 'be3_generators.json').open('w', encoding='utf-8') as f:
            json.dump(payload, f)
    return payload

def load_or_generate_be3_generators(data_dir: Path, generate=False):
    path = data_dir / 'source' / 'be3_generators.json'
    if path.exists():
        with path.open('r', encoding='utf-8') as f:
            payload = json.load(f)
    elif generate:
        payload = generate_be3_generators(data_dir, write=True)
    else:
        raise FileNotFoundError('Missing data/source/be3_generators.json. Re-run with --generate-be3 to build it from source.')
    n = int(payload.get('points', EXPECTED_DODECADS))
    gens = [tuple(int(x) for x in g) for g in payload['generators']]
    if n != EXPECTED_DODECADS:
        raise AssertionError(f'expected {EXPECTED_DODECADS} points, got {n}')
    return gens, path
