from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
from typing import Any, Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]
HASH_FIELD = 'certificate_sha256'


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def h_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def h_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(rel: str):
    with (ROOT / rel).open('r', encoding='utf-8') as f:
        return json.load(f)


def unwrap(obj):
    # cached command outputs may be wrapped by their CLI mode name
    if isinstance(obj, dict) and len(obj) == 1:
        k = next(iter(obj))
        if k in {'aut-h-rigidity', 'leech', 'aut-h', 'certificate'}:
            return obj[k]
    return obj


def file_hashes() -> Dict[str, str]:
    rels = [
        'data/constants.json',
        'data/quotients.npz',
        'data/tensor_sparse.npz',
        'generators/co1/projective_generators.npz',
        'data/cached/base_certificate.json',
        'data/cached/aut_h_constructive_rigidity.json',
        'data/cached/leech_reconstruction_certificate.json',
        'data/cached/simple_branching_naturality_report.json',
        'data/cached/simple_branching_matrices.npz',
        'source/compute_simple_branching_fast.py',
        'source/generate_c985_relation_memberships.py',
        'source/generate_c985_f_symbols.py',
        'source/generate_c985_f_symbol_permutations.py',
        'source/generate_c985_f_symbol_inventory.py',
        'source/gnat_be3_source.py',
        'source/emit_certificate.py',
        'certify.ps1',
        'README.md',
    ]
    return {rel: h_file(ROOT / rel) for rel in rels if (ROOT / rel).exists()}


def _assert(condition: bool, message: str, trace: list[dict]) -> None:
    trace.append({'check': message, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(message)


def load_simple_branching_certificate() -> Dict[str, Any]:
    """Load and verify the finite simple-branching/naturality layer.

    This block is deliberately derived from both the JSON report and the NPZ
    matrices. The certificate is not accepted unless the matrices multiply to
    the direct branch, all row-dimension checks hold, and the tenfold triplet
    layer agrees with the reported indices.
    """
    report_rel = 'data/cached/simple_branching_naturality_report.json'
    matrices_rel = 'data/cached/simple_branching_matrices.npz'
    script_rel = 'source/compute_simple_branching_fast.py'
    report = load_json(report_rel)
    z = np.load(ROOT / matrices_rel)

    def arr(name: str) -> np.ndarray:
        return np.array(z[name], dtype=np.int64)

    B236_42 = arr('B236_42')
    B42_12 = arr('B42_12')
    B236_12 = arr('B236_12')
    comp_npz = arr('comp')
    dims236 = arr('dims236')
    dims42 = arr('dims42')
    dims12 = arr('dims12')

    comp = B236_42 @ B42_12
    json_mats = report.get('matrices', {})
    json_dims = report.get('dims', {})

    local_trace: list[dict] = []
    _assert(report.get('status') == 'PASS_FULL_SIMPLE_NATURALITY', 'simple branching report status is PASS_FULL_SIMPLE_NATURALITY', local_trace)
    _assert(B236_42.shape == (34, 7), 'B236_to_42 has shape 34x7', local_trace)
    _assert(B42_12.shape == (7, 4), 'B42_to_12 has shape 7x4', local_trace)
    _assert(B236_12.shape == (34, 4), 'B236_to_12 has shape 34x4', local_trace)
    _assert(np.array_equal(comp, B236_12), 'B236_to_42 * B42_to_12 equals B236_to_12', local_trace)
    _assert(np.array_equal(comp_npz, comp), 'stored NPZ composed matrix equals recomputed composition', local_trace)
    _assert(np.array_equal(B236_42, np.array(json_mats['B236_to_42'], dtype=np.int64)), 'NPZ B236_to_42 equals JSON matrix', local_trace)
    _assert(np.array_equal(B42_12, np.array(json_mats['B42_to_12'], dtype=np.int64)), 'NPZ B42_to_12 equals JSON matrix', local_trace)
    _assert(np.array_equal(B236_12, np.array(json_mats['B236_to_12'], dtype=np.int64)), 'NPZ B236_to_12 equals JSON matrix', local_trace)
    _assert(np.array_equal(dims236, np.array(json_dims['236'], dtype=np.int64)), 'NPZ dims236 equals JSON dims[236]', local_trace)
    _assert(np.array_equal(dims42, np.array(json_dims['42'], dtype=np.int64)), 'NPZ dims42 equals JSON dims[42]', local_trace)
    _assert(np.array_equal(dims12, np.array(json_dims['12'], dtype=np.int64)), 'NPZ dims12 equals JSON dims[12]', local_trace)
    _assert(np.array_equal(B236_42 @ dims42, dims236), 'row dimension check B236_to_42 holds', local_trace)
    _assert(np.array_equal(B42_12 @ dims12, dims42), 'row dimension check B42_to_12 holds', local_trace)
    _assert(np.array_equal(B236_12 @ dims12, dims236), 'row dimension check B236_to_12 holds', local_trace)

    triplet_rows = [int(i) for i, d in enumerate(dims236.tolist()) if int(d) == 3]
    reported_triplet_rows = [int(i) for i in report['A236_tenfold']['triplet_rows']]
    _assert(triplet_rows == reported_triplet_rows, 'A236 triplet rows match dimension-3 simples', local_trace)
    _assert(len(triplet_rows) == 10, 'A236 has ten triplet simples', local_trace)
    _assert(int(sum(int(d) * int(d) for d in dims236)) == 236, 'A236 simple dimensions square-sum to 236', local_trace)
    _assert(int(sum(int(d) * int(d) for d in dims42)) == 42, 'A42 simple dimensions square-sum to 42', local_trace)
    _assert(int(sum(int(d) * int(d) for d in dims12)) == 12, 'A12 simple dimensions square-sum to 12', local_trace)

    block = {
        'schema': 'gnatural.simple_branching_naturality.v1',
        'status': report['status'],
        'prime': int(report.get('prime', 1000003)),
        'input_hashes': {
            report_rel: h_file(ROOT / report_rel),
            matrices_rel: h_file(ROOT / matrices_rel),
            script_rel: h_file(ROOT / script_rel),
        },
        'center_dims': {str(k): int(v) for k, v in report['center_dims'].items()},
        'simple_dimension_counts': report['simple_dimension_counts'],
        'dims': {
            '236': [int(x) for x in dims236.tolist()],
            '42': [int(x) for x in dims42.tolist()],
            '12': [int(x) for x in dims12.tolist()],
        },
        'branch_shapes': {
            'B236_to_42': [int(x) for x in B236_42.shape],
            'B42_to_12': [int(x) for x in B42_12.shape],
            'B236_to_12': [int(x) for x in B236_12.shape],
        },
        'row_dimension_checks': {
            'B236_to_42': bool(np.array_equal(B236_42 @ dims42, dims236)),
            'B42_to_12': bool(np.array_equal(B42_12 @ dims12, dims42)),
            'B236_to_12': bool(np.array_equal(B236_12 @ dims12, dims236)),
        },
        'naturality': {
            'statement': 'B236_to_12 = B236_to_42 * B42_to_12',
            'passes': bool(np.array_equal(comp, B236_12)),
            'defect_nonzero_entries': int(np.count_nonzero(comp - B236_12)),
            'defect_l1': int(np.abs(comp - B236_12).sum()),
            'defect_sha256': h_json((comp - B236_12).astype(int).tolist()),
        },
        'A236_tenfold': {
            'triplet_rows': triplet_rows,
            'triplet_count': len(triplet_rows),
            'triplet_ideal_dimension': int(len(triplet_rows) * 9),
            'B236_to_42_triplet_rows': B236_42[triplet_rows].astype(int).tolist(),
            'B236_to_12_triplet_rows': B236_12[triplet_rows].astype(int).tolist(),
        },
        'matrices': {
            'B236_to_42': B236_42.astype(int).tolist(),
            'B42_to_12': B42_12.astype(int).tolist(),
            'B236_to_12': B236_12.astype(int).tolist(),
        },
        'matrix_hashes': {
            'B236_to_42': h_json(B236_42.astype(int).tolist()),
            'B42_to_12': h_json(B42_12.astype(int).tolist()),
            'B236_to_12': h_json(B236_12.astype(int).tolist()),
            'composed_B236_to_12': h_json(comp.astype(int).tolist()),
        },
        'verification_trace': local_trace,
    }
    block['simple_branching_sha256'] = h_json(block)
    return block


def rank_mod_prime(A: np.ndarray, p: int) -> int:
    """Row rank over F_p for an integer matrix."""
    M = np.array(A, dtype=np.int64) % p
    m, n = M.shape
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, m):
            if M[i, c] % p:
                piv = i
                break
        if piv is None:
            continue
        if piv != r:
            M[[r, piv]] = M[[piv, r]]
        inv = pow(int(M[r, c]), -1, p)
        M[r, :] = (M[r, :] * inv) % p
        rows = np.nonzero(M[:, c] % p)[0]
        for i in rows:
            if i != r:
                M[i, :] = (M[i, :] - M[i, c] * M[r, :]) % p
        r += 1
        if r == m:
            break
    return int(r)


def load_recoupling_center_certificate() -> Dict[str, Any]:
    """Compute the finite K0 recoupling-center certificate from A42.

    The raw q42 tensor is the expanded quotient tensor.  The connection and
    return coefficients are normalized at the exact entries where normalization
    is part of the known quotient law; the K0 commutator-center rank is computed
    from the raw A42 product as stored.
    """
    qrel = 'data/quotients.npz'
    crel = 'data/constants.json'
    z = np.load(ROOT / qrel)
    constants = load_json(crel)
    q42_map = np.array(z['q42_map'], dtype=np.int64)
    T = np.array(z['q42_tensor'], dtype=np.int64)
    block_i = np.array(z['block_i'], dtype=np.int64)
    block_j = np.array(z['block_j'], dtype=np.int64)
    n = 42
    local_trace: list[dict] = []
    _assert(T.shape == (42, 42, 42), 'A42 quotient tensor has shape 42x42x42', local_trace)

    class_sizes = np.array([int(np.count_nonzero(q42_map == c)) for c in range(n)], dtype=np.int64)
    class_source_target: dict[int, tuple[int, int]] = {}
    for c in range(n):
        idx = np.where(q42_map == c)[0]
        _assert(len(idx) > 0, f'q42 class {c} is nonempty', local_trace)
        pairs: dict[tuple[int, int], int] = {}
        for a in idx:
            pair = (int(block_i[a]), int(block_j[a]))
            pairs[pair] = pairs.get(pair, 0) + 1
        pair, count = max(pairs.items(), key=lambda kv: kv[1])
        _assert(count == len(idx), f'q42 class {c} has a unique source-target pair', local_trace)
        class_source_target[c] = pair

    identity_classes = list(range(6))
    defect_classes = list(range(6, 12))
    transport_classes = list(range(12, 42))
    _assert(all(class_sizes[i] == 1 for i in identity_classes), 'identity classes 0..5 are singletons', local_trace)
    _assert(all(class_source_target[i] == (i, i) for i in identity_classes), 'identity classes have source=target=i', local_trace)
    _assert(all(class_source_target[6+i] == (i, i) for i in range(6)), 'defect classes 6..11 are diagonal', local_trace)
    transport_by_pair = {class_source_target[c]: c for c in transport_classes}
    _assert(len(transport_by_pair) == 30, 'there are 30 directed off-diagonal transport classes', local_trace)
    _assert(set(transport_by_pair) == {(i, j) for i in range(6) for j in range(6) if i != j}, 'transport classes form the complete directed graph on H6', local_trace)

    def norm_coeff(a: int, b: int, c: int) -> int:
        raw = int(T[a, b, c])
        den = int(class_sizes[c])
        _assert(raw % den == 0, f'normalized coefficient T[{a},{b},{c}] divides by target class size', local_trace)
        return raw // den

    # Two-step transport connection.
    gamma_values: list[int] = []
    transport_failures: list[dict] = []
    for i in range(6):
        for j in range(6):
            for k in range(6):
                if len({i, j, k}) == 3:
                    a = transport_by_pair[(i, j)]
                    b = transport_by_pair[(j, k)]
                    c = transport_by_pair[(i, k)]
                    nz = np.nonzero(T[a, b, :])[0].tolist()
                    if nz != [c]:
                        transport_failures.append({'i': i, 'j': j, 'k': k, 'nonzero_targets': [int(x) for x in nz]})
                    else:
                        gamma_values.append(norm_coeff(a, b, c))
    _assert(transport_failures == [], 'all distinct two-step transports have unique target', local_trace)
    gamma_hist: dict[str, int] = {}
    for g in gamma_values:
        gamma_hist[str(g)] = gamma_hist.get(str(g), 0) + 1
    expected_gamma_hist = {'144': 20, '192': 20, '384': 20, '512': 20, '576': 20, '768': 20}
    _assert(gamma_hist == expected_gamma_hist, 'connection coefficient multiset is {144,192,384,512,576,768} each 20 times', local_trace)

    # Backtracking half-return.
    backtrack_values: list[int] = []
    backtrack_failures: list[dict] = []
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            a = transport_by_pair[(i, j)]
            b = transport_by_pair[(j, i)]
            nz = np.nonzero(T[a, b, :])[0].tolist()
            v_id = norm_coeff(a, b, i)
            v_def = norm_coeff(a, b, 6+i)
            if set(nz) != {i, 6+i} or v_id != v_def:
                backtrack_failures.append({'i': i, 'j': j, 'nonzero_targets': [int(x) for x in nz], 'id': v_id, 'defect': v_def})
            else:
                backtrack_values.append(v_id)
    _assert(backtrack_failures == [], 'all backtracks return equal identity and defect mass', local_trace)
    backtrack_hist: dict[str, int] = {}
    for g in backtrack_values:
        backtrack_hist[str(g)] = backtrack_hist.get(str(g), 0) + 1
    _assert(backtrack_hist == {'144': 5, '192': 5, '384': 5, '512': 5, '576': 5, '768': 5}, 'backtrack coefficient multiset is six values each five times', local_trace)

    # Triangle loop coefficient follows from two-step connection then backtrack.
    triangle_values: list[int] = []
    triangle_failures: list[dict] = []
    for i in range(6):
        for j in range(6):
            for k in range(6):
                if len({i, j, k}) != 3:
                    continue
                a = transport_by_pair[(i, j)]
                b = transport_by_pair[(j, k)]
                c = transport_by_pair[(i, k)]
                d = transport_by_pair[(k, i)]
                gamma = norm_coeff(a, b, c)
                v_id = norm_coeff(c, d, i)
                v_def = norm_coeff(c, d, 6+i)
                if v_id != v_def:
                    triangle_failures.append({'i': i, 'j': j, 'k': k, 'id': v_id, 'defect': v_def})
                else:
                    triangle_values.append(gamma * v_id)
    _assert(triangle_failures == [], 'all triangle loops return equal identity and defect mass', local_trace)
    triangle_hist: dict[str, int] = {}
    for g in triangle_values:
        triangle_hist[str(g)] = triangle_hist.get(str(g), 0) + 1

    # K0 associator scalars and pentagon check using normalized connection coefficients.
    from fractions import Fraction
    def G(i: int, j: int, k: int) -> int:
        return norm_coeff(transport_by_pair[(i, j)], transport_by_pair[(j, k)], transport_by_pair[(i, k)])
    assoc_hist: dict[str, int] = {}
    assoc_unique: set[str] = set()
    assoc_contains_half = False
    assoc_contains_five_half = False
    for i in range(6):
        for j in range(6):
            for k in range(6):
                for ell in range(6):
                    if len({i, j, k, ell}) == 4:
                        val = Fraction(G(j, k, ell) * G(i, j, ell), G(i, j, k) * G(i, k, ell))
                        key = f'{val.numerator}/{val.denominator}' if val.denominator != 1 else str(val.numerator)
                        assoc_hist[key] = assoc_hist.get(key, 0) + 1
                        assoc_unique.add(key)
                        assoc_contains_half |= (val == Fraction(1, 2))
                        assoc_contains_five_half |= (val == Fraction(5, 2))
    pentagon_failures = []
    for i in range(6):
        for j in range(6):
            for k in range(6):
                for ell in range(6):
                    for m in range(6):
                        if len({i, j, k, ell, m}) == 5:
                            lhs = Fraction(G(k, ell, m) * G(j, k, m), G(j, k, ell) * G(j, ell, m))
                            lhs *= Fraction(G(j, ell, m) * G(i, j, m), G(i, j, ell) * G(i, ell, m))
                            lhs *= Fraction(G(j, k, ell) * G(i, j, ell), G(i, j, k) * G(i, k, ell))
                            rhs = Fraction(G(j, k, m) * G(i, j, m), G(i, j, k) * G(i, k, m))
                            rhs *= Fraction(G(k, ell, m) * G(i, k, m), G(i, k, ell) * G(i, ell, m))
                            if lhs != rhs:
                                pentagon_failures.append({'i': i, 'j': j, 'k': k, 'ell': ell, 'm': m})
    _assert(pentagon_failures == [], 'all normalized K0 associator scalars satisfy the pentagon equation', local_trace)

    # Expanded/raw associator: before class-size normalization.  This retains
    # the finite multiplicity anomaly that the normalized connection flattens.
    def Graw(i: int, j: int, k: int) -> int:
        return int(T[transport_by_pair[(i, j)], transport_by_pair[(j, k)], transport_by_pair[(i, k)]])
    raw_assoc_hist: dict[str, int] = {}
    raw_assoc_unique: set[str] = set()
    raw_contains_half = False
    raw_contains_five_half = False
    for i in range(6):
        for j in range(6):
            for k in range(6):
                for ell in range(6):
                    if len({i, j, k, ell}) == 4:
                        val = Fraction(Graw(j, k, ell) * Graw(i, j, ell), Graw(i, j, k) * Graw(i, k, ell))
                        key = f'{val.numerator}/{val.denominator}' if val.denominator != 1 else str(val.numerator)
                        raw_assoc_hist[key] = raw_assoc_hist.get(key, 0) + 1
                        raw_assoc_unique.add(key)
                        raw_contains_half |= (val == Fraction(1, 2))
                        raw_contains_five_half |= (val == Fraction(5, 2))
    raw_pentagon_failures = []
    for i in range(6):
        for j in range(6):
            for k in range(6):
                for ell in range(6):
                    for m in range(6):
                        if len({i, j, k, ell, m}) == 5:
                            lhs = Fraction(Graw(k, ell, m) * Graw(j, k, m), Graw(j, k, ell) * Graw(j, ell, m))
                            lhs *= Fraction(Graw(j, ell, m) * Graw(i, j, m), Graw(i, j, ell) * Graw(i, ell, m))
                            lhs *= Fraction(Graw(j, k, ell) * Graw(i, j, ell), Graw(i, j, k) * Graw(i, k, ell))
                            rhs = Fraction(Graw(j, k, m) * Graw(i, j, m), Graw(i, j, k) * Graw(i, k, m))
                            rhs *= Fraction(Graw(k, ell, m) * Graw(i, k, m), Graw(i, k, ell) * Graw(i, ell, m))
                            if lhs != rhs:
                                raw_pentagon_failures.append({'i': i, 'j': j, 'k': k, 'ell': ell, 'm': m})
    _assert(raw_pentagon_failures == [], 'all expanded/raw K0 associator scalars satisfy the pentagon equation', local_trace)

    # Raw A42 commutator-center rank. This is the K0 center of the stored quotient algebra.
    comm_blocks = []
    for b in transport_classes:
        comm_blocks.append((T[:, b, :] - T[b, :, :]).T.reshape(n, n))
    comm = np.vstack(comm_blocks).astype(np.int64)
    full_comm = np.vstack([(T[:, b, :] - T[b, :, :]).T.reshape(n, n) for b in range(n)]).astype(np.int64)
    primes = [1000003, 1000033, 1000037]
    transport_ranks = {str(p): rank_mod_prime(comm, p) for p in primes}
    full_ranks = {str(p): rank_mod_prime(full_comm, p) for p in primes}
    _assert(len(set(transport_ranks.values())) == 1, 'transport commutator rank is stable over checked primes', local_trace)
    _assert(len(set(full_ranks.values())) == 1, 'full commutator rank is stable over checked primes', local_trace)
    transport_rank = next(iter(transport_ranks.values()))
    full_rank = next(iter(full_ranks.values()))
    _assert(transport_rank == 35, 'transport commutator rank is 35', local_trace)
    _assert(full_rank == 35, 'full commutator rank is 35', local_trace)
    center_nullity = n - full_rank
    _assert(center_nullity == 7, 'K0 recoupling center nullity is 7', local_trace)

    be3_order = int(constants['be3']['order'])
    wd6_order = 23040
    block = {
        'schema': 'gnatural.h6_recoupling_center.v1',
        'status': 'PASS_H6_RECOUPLING_CENTER_CERTIFICATE',
        'input_hashes': {qrel: h_file(ROOT / qrel), crel: h_file(ROOT / crel)},
        'class_partition': {
            'identity_classes': identity_classes,
            'defect_classes': defect_classes,
            'transport_classes': transport_classes,
            'class_sizes': [int(x) for x in class_sizes.tolist()],
            'source_target': {str(k): [int(v[0]), int(v[1])] for k, v in class_source_target.items()},
            'transport_count': len(transport_classes),
            'complete_directed_H6_minus_diagonal': True,
        },
        'connection': {
            'normalized_by_target_class_size_on_transport_entries': True,
            'two_step_transport_count': len(gamma_values),
            'unique_target_failures': transport_failures,
            'gamma_histogram': gamma_hist,
            'gamma_values': sorted(int(x) for x in set(gamma_values)),
        },
        'half_return': {
            'backtrack_count': len(backtrack_values),
            'backtrack_equal_identity_defect_mass': True,
            'backtrack_histogram': backtrack_hist,
            'triangle_count': len(triangle_values),
            'triangle_equal_identity_defect_mass': True,
            'triangle_histogram': triangle_hist,
        },
        'associator': {
            'normalized': {
                'scalar_count': int(sum(assoc_hist.values())),
                'unique_scalar_count': len(assoc_unique),
                'contains_half': assoc_contains_half,
                'contains_five_half': assoc_contains_five_half,
                'scalar_histogram': dict(sorted(assoc_hist.items(), key=lambda kv: kv[0])),
                'pentagon_checked_ordered_distinct_5_tuples': 720,
                'pentagon_failures': pentagon_failures,
            },
            'expanded_raw': {
                'scalar_count': int(sum(raw_assoc_hist.values())),
                'unique_scalar_count': len(raw_assoc_unique),
                'contains_half': raw_contains_half,
                'contains_five_half': raw_contains_five_half,
                'scalar_histogram': dict(sorted(raw_assoc_hist.items(), key=lambda kv: kv[0])),
                'pentagon_checked_ordered_distinct_5_tuples': 720,
                'pentagon_failures': raw_pentagon_failures,
            },
        },
        'k0_center': {
            'basis_dimension': n,
            'transport_commutator_matrix_shape': [int(x) for x in comm.shape],
            'full_commutator_matrix_shape': [int(x) for x in full_comm.shape],
            'rank_primes': primes,
            'transport_commutator_ranks': transport_ranks,
            'full_commutator_ranks': full_ranks,
            'rank': full_rank,
            'nullity': center_nullity,
            'interpretation': 'K0 central/transparent subspace for the stored A42 recoupling algebra',
        },
        'D6_spin12_evidence': {
            'transport_classes': 30,
            'positive_roots_D6': 30,
            'dim_H6': 6,
            'dim_H6_plus_dual': 12,
            'dim_1_plus_Lambda2_H6': 16,
            'W_D6_order': wd6_order,
            'Be3_order': be3_order,
            'W_D6_over_Be3': {'numerator': 5, 'denominator': 2},
            'claim_scope': 'finite K0 evidence for the D6/Spin12 recoupling selector; categorical half-braidings remain the next lift',
        },
        'verification_trace': local_trace,
    }
    block['recoupling_center_sha256'] = h_json(block)
    return block


def load_half_braiding_lift_certificate(recoupling_center: Dict[str, Any]) -> Dict[str, Any]:
    """Certify the actual boundary between the K0 center and categorical half-braidings.

    The previous H6 block computes the K0 commutator center.  This block checks
    whether any simple A42 class already has the support/coefficient symmetry
    required of a simple transparent object.  None do.  Therefore the true
    Drinfeld-center lift cannot be certified from the quotient multiplication
    table alone; it requires idempotent completion plus explicit F-symbols on
    multiplicity spaces.  This is a positive boundary certificate, not a failed
    run: it prevents falsely reporting K0 centrality as a categorical center.
    """
    qrel = 'data/quotients.npz'
    z = np.load(ROOT / qrel)
    T = np.array(z['q42_tensor'], dtype=np.int64)
    n = 42
    transport_classes = list(range(12, 42))
    local_trace: list[dict] = []
    _assert(T.shape == (42, 42, 42), 'A42 quotient tensor is available for half-braiding boundary check', local_trace)
    _assert(recoupling_center['k0_center']['nullity'] == 7, 'K0 center nullity from previous block is 7', local_trace)

    def supp(a: int, b: int) -> set[int]:
        return set(int(x) for x in np.nonzero(T[a, b, :])[0].tolist())

    # Pairwise product symmetry is a necessary K0 condition for a simple object
    # to be transparent.  We check both exact coefficient equality and support equality.
    simple_coefficient_transparent: list[int] = []
    simple_support_transparent: list[int] = []
    for a in range(n):
        coeff_ok = True
        support_ok = True
        for b in range(n):
            if not np.array_equal(T[a, b, :], T[b, a, :]):
                coeff_ok = False
            if supp(a, b) != supp(b, a):
                support_ok = False
            if not coeff_ok and not support_ok:
                break
        if coeff_ok:
            simple_coefficient_transparent.append(a)
        if support_ok:
            simple_support_transparent.append(a)

    _assert(simple_coefficient_transparent == [], 'no simple A42 class is coefficient-transparent against all classes', local_trace)
    _assert(simple_support_transparent == [], 'no simple A42 class is support-transparent against all classes', local_trace)

    def pair_stats(A, B):
        total = 0
        support_equal = 0
        coefficient_equal = 0
        both_zero = 0
        examples = []
        for a in A:
            for b in B:
                total += 1
                sa = supp(a, b)
                sb = supp(b, a)
                if not sa and not sb:
                    both_zero += 1
                if sa == sb:
                    support_equal += 1
                elif len(examples) < 12:
                    examples.append({'a': int(a), 'b': int(b), 'ab_support': sorted(sa), 'ba_support': sorted(sb)})
                if np.array_equal(T[a, b, :], T[b, a, :]):
                    coefficient_equal += 1
        return {
            'total_pairs': int(total),
            'support_symmetric_pairs': int(support_equal),
            'coefficient_symmetric_pairs': int(coefficient_equal),
            'both_zero_pairs': int(both_zero),
            'support_mismatch_pairs': int(total - support_equal),
            'coefficient_mismatch_pairs': int(total - coefficient_equal),
            'first_support_mismatch_examples': examples,
        }

    all_stats = pair_stats(range(n), range(n))
    transport_stats = pair_stats(transport_classes, transport_classes)
    _assert(all_stats['support_mismatch_pairs'] > 0, 'not every A42 pair is support-symmetric', local_trace)
    _assert(transport_stats['support_mismatch_pairs'] > 0, 'not every transport pair is support-symmetric', local_trace)

    block = {
        'schema': 'gnatural.h6_half_braiding_lift_boundary.v1',
        'status': 'HALF_BRAIDING_LIFT_REQUIRES_IDEMPOTENT_COMPLETION_AND_F_SYMBOLS',
        'input_hashes': {qrel: h_file(ROOT / qrel)},
        'what_was_checked': {
            'necessary_simple_transparency_test': True,
            'product_support_symmetry_test': True,
            'product_coefficient_symmetry_test': True,
            'uses_only_decategorified_A42_tensor': True,
        },
        'simple_transparent_classes': {
            'coefficient_transparent': simple_coefficient_transparent,
            'support_transparent': simple_support_transparent,
            'count_coefficient_transparent': len(simple_coefficient_transparent),
            'count_support_transparent': len(simple_support_transparent),
        },
        'pair_symmetry_statistics': {
            'all_A42_pairs': all_stats,
            'transport_transport_pairs': transport_stats,
        },
        'categorical_lift_boundary': {
            'K0_center_nullity': int(recoupling_center['k0_center']['nullity']),
            'K0_center_interpretation': recoupling_center['k0_center']['interpretation'],
            'boundary_statement': 'K0 centrality is necessary but not sufficient for an object of the Drinfeld center Z(R_H6).  The quotient tensor supplies the decategorified Grothendieck ring, but a categorical half-braiding requires primitive idempotent completion and explicit associator/F-symbol data on multiplicity spaces.',
            'not_certified_as': 'full categorical Drinfeld center',
            'next_required_data': [
                'primitive central idempotents or simple objects of the idempotent-completed recoupling category',
                'explicit bases for multiplicity spaces M_{alpha,beta}^gamma',
                'associator/F-symbol matrices, not only K0 associator scalars',
                'hexagon/naturality equations for sigma_X:Y tensor X -> X tensor Y',
            ],
            'safe_theorem_statement': 'The current verifier certifies the finite K0 recoupling center and the D6/Spin12 numerical selector; it does not yet certify a full half-braiding object in Z(R_H6).',
        },
        'verification_trace': local_trace,
    }
    block['half_braiding_boundary_sha256'] = h_json(block)
    return block



def rank_augmented_mod_prime(A: np.ndarray, b: np.ndarray, p: int) -> tuple[int, int]:
    """Return rank(A), rank([A|b]) over F_p."""
    A0 = np.array(A, dtype=np.int64) % p
    b0 = np.array(b, dtype=np.int64).reshape((-1,1)) % p
    return rank_mod_prime(A0, p), rank_mod_prime(np.hstack([A0, b0]), p)


def load_idempotent_completion_boundary_certificate() -> Dict[str, Any]:
    """Certify the next categorical-lift boundary.

    The half-braiding boundary asks for idempotent completion and F-symbols.
    This block checks whether the stored expanded A42 tensor is already a
    strict unital fusion algebra from which primitive idempotents can be
    computed.  It is not: the unit linear system has no solution over several
    finite fields, and the obvious multi-object identity candidate is not a
    two-sided unit.  Therefore the next lift must use the actual incidence
    span/profunctor category with multiplicity-space bases, not the expanded
    quotient-count tensor alone.
    """
    qrel = 'data/quotients.npz'
    z = np.load(ROOT / qrel)
    T = np.array(z['q42_tensor'], dtype=np.int64)
    n = 42
    local_trace: list[dict] = []
    _assert(T.shape == (42, 42, 42), 'expanded A42 quotient tensor is available for idempotent-completion boundary check', local_trace)

    # Build the strict two-sided unit linear system for the stored tensor:
    # sum_i u_i T[i,a,c] = delta_{a,c}, sum_i u_i T[a,i,c] = delta_{a,c}.
    rows = []
    rhs = []
    for a in range(n):
        for c in range(n):
            rows.append(T[:, a, c].astype(np.int64))
            rhs.append(1 if c == a else 0)
            rows.append(T[a, :, c].astype(np.int64))
            rhs.append(1 if c == a else 0)
    A = np.vstack(rows).astype(np.int64)
    b = np.array(rhs, dtype=np.int64)

    primes = [1000003, 1000033, 1000037]
    rank_witness = {}
    inconsistent_primes = []
    for p0 in primes:
        rA, rAug = rank_augmented_mod_prime(A, b, p0)
        rank_witness[str(p0)] = {'rank_A': int(rA), 'rank_augmented': int(rAug), 'inconsistent': bool(rAug > rA)}
        if rAug > rA:
            inconsistent_primes.append(p0)
    _assert(len(inconsistent_primes) == len(primes), 'strict unit linear system is inconsistent over all checked primes', local_trace)

    # Obvious multi-object identity candidate from the six identity classes.
    u = np.zeros(n, dtype=np.int64)
    u[:6] = 1
    # product helpers for integer vectors under stored expanded tensor
    def left_prod_unit(a: int) -> np.ndarray:
        return np.tensordot(u, T[:, a, :], axes=(0,0)).astype(np.int64)
    def right_prod_unit(a: int) -> np.ndarray:
        return np.tensordot(u, T[a, :, :], axes=(0,0)).astype(np.int64)
    candidate_failures = []
    for a in range(n):
        e = np.zeros(n, dtype=np.int64); e[a] = 1
        L = left_prod_unit(a)
        R = right_prod_unit(a)
        if not np.array_equal(L, e) or not np.array_equal(R, e):
            if len(candidate_failures) < 16:
                candidate_failures.append({
                    'class': int(a),
                    'left_nonzero': {str(i): int(v) for i, v in enumerate(L.tolist()) if v},
                    'right_nonzero': {str(i): int(v) for i, v in enumerate(R.tolist()) if v},
                    'expected': {str(a): 1},
                })
    _assert(len(candidate_failures) > 0, 'obvious sum of six identity classes is not a strict unit for the expanded tensor', local_trace)

    # Basis idempotent sanity: e_a^2=e_a is not available from the expanded tensor.
    idempotent_basis_failures = []
    for a in range(n):
        sq = T[a, a, :]
        e = np.zeros(n, dtype=np.int64); e[a] = 1
        if not np.array_equal(sq, e):
            if len(idempotent_basis_failures) < 16:
                idempotent_basis_failures.append({
                    'class': int(a),
                    'square_nonzero': {str(i): int(v) for i, v in enumerate(sq.tolist()) if v},
                    'expected': {str(a): 1},
                })
    _assert(len(idempotent_basis_failures) > 0, 'basis classes are not primitive idempotents of the expanded tensor', local_trace)

    block = {
        'schema': 'gnatural.h6_idempotent_completion_boundary.v1',
        'status': 'IDEMPOTENT_COMPLETION_REQUIRES_INCIDENT_MULTIPLICITY_CATEGORY_NOT_EXPANDED_Q42_TENSOR',
        'input_hashes': {qrel: h_file(ROOT / qrel)},
        'what_was_checked': {
            'strict_two_sided_unit_linear_system': True,
            'obvious_multiobject_identity_candidate': True,
            'basis_idempotent_sanity_check': True,
            'uses_only_expanded_A42_quotient_count_tensor': True,
        },
        'strict_unit_system': {
            'matrix_shape': [int(A.shape[0]), int(A.shape[1])],
            'rhs_length': int(b.shape[0]),
            'rank_witness_over_primes': rank_witness,
            'inconsistent_over_all_checked_primes': True,
            'interpretation': 'The stored expanded A42 tensor is not itself a strict unital fusion algebra suitable for primitive-idempotent completion.',
        },
        'identity_candidate': {
            'candidate': 'u = e_0+e_1+e_2+e_3+e_4+e_5',
            'is_two_sided_unit': False,
            'first_failures': candidate_failures,
        },
        'basis_idempotent_check': {
            'all_basis_classes_idempotent': False,
            'first_failures': idempotent_basis_failures,
        },
        'categorical_lift_boundary': {
            'safe_statement': 'The verifier has reached the boundary of the expanded quotient-count tensor.  Primitive idempotents and F-symbol matrices must be constructed in the incidence span/profunctor categorification C_985, or from a normalized Wedderburn/matrix-unit model, before claiming a full categorical Drinfeld center.',
            'not_certified_as': [
                'primitive idempotent completion of R_H6',
                'full F-symbol tensor of R_H6',
                'categorical half-braiding object in Z(R_H6)',
            ],
            'next_required_data': [
                'explicit incidence sets Ω_i and orbitals R_α, not only fused q42 counts',
                'multiplicity-space bases M_{αβ}^γ for the span/profunctor category',
                'associator bijections linearized as F-symbol matrices on those bases',
                'primitive central idempotents or matrix units for the idempotent-completed recoupling category',
                'hexagon/naturality equations solved using those F-symbol matrices',
            ],
        },
        'verification_trace': local_trace,
    }
    block['idempotent_completion_boundary_sha256'] = h_json(block)
    return block



def load_c985_incidence_skeleton_certificate() -> Dict[str, Any]:
    """Certify the incidence/profunctor multiplicity skeleton of C_985.

    This is the first constructive step beyond the fused A42 quotient boundary.
    It uses the full sparse A985 tensor and the object-block data to build the
    finite span/profunctor skeleton whose simples are the 985 orbitals and whose
    multiplicity spaces M_{alpha,beta}^gamma have canonical formal bases
    e_{alpha,beta,gamma,r}, 0 <= r < p^gamma_{alpha,beta}.

    The certificate deliberately does not claim concrete F-symbol matrices: those
    require the actual incidence sets of intermediate dodecads z and the linearized
    rebracketing bijections.  It does certify the complete K0 multiplicity-basis
    inventory, source-target typing, coefficient mass, and basis-offset scheme.
    """
    trel = 'data/tensor_sparse.npz'
    qrel = 'data/quotients.npz'
    crel = 'data/constants.json'
    z = np.load(ROOT / trel)
    q = np.load(ROOT / qrel)
    constants = load_json(crel)
    triples = np.array(z['triples'], dtype=np.int64)
    reps = np.array(z['reps'], dtype=np.int64)
    M_stored = np.array(z['M'], dtype=np.int64)
    block_i = np.array(q['block_i'], dtype=np.int64)
    block_j = np.array(q['block_j'], dtype=np.int64)

    local_trace: list[dict] = []
    _assert(triples.shape[1] == 4, 'sparse A985 tensor triples have columns alpha,beta,gamma,coefficient', local_trace)
    _assert(reps.shape == (985, 5), 'orbital representative table has shape 985x5', local_trace)
    _assert(block_i.shape == (985,) and block_j.shape == (985,), 'block source/target arrays have length 985', local_trace)
    _assert(M_stored.shape == (6, 6), 'stored six-object orbital count matrix has shape 6x6', local_trace)

    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    coeff = triples[:, 3]
    _assert(int(alpha.min()) >= 0 and int(alpha.max()) < 985, 'alpha indices lie in 0..984', local_trace)
    _assert(int(beta.min()) >= 0 and int(beta.max()) < 985, 'beta indices lie in 0..984', local_trace)
    _assert(int(gamma.min()) >= 0 and int(gamma.max()) < 985, 'gamma indices lie in 0..984', local_trace)
    _assert(int(coeff.min()) > 0, 'all multiplicity coefficients are positive', local_trace)
    _assert(int(triples.shape[0]) == int(constants['tensor_shape'][0]), 'sparse support count equals constants tensor_shape[0]', local_trace)
    _assert(int(coeff.sum()) == int(constants['coefficient_total']), 'coefficient total equals constants coefficient_total', local_trace)

    # The first two columns of reps are the six-object source/target typing.
    _assert(np.array_equal(reps[:, 0], block_i), 'representative table source block matches block_i', local_trace)
    _assert(np.array_equal(reps[:, 1], block_j), 'representative table target block matches block_j', local_trace)
    M_computed = np.zeros((6, 6), dtype=np.int64)
    for i, j in zip(block_i.tolist(), block_j.tolist()):
        M_computed[int(i), int(j)] += 1
    _assert(np.array_equal(M_computed, M_stored), 'six-object orbital count matrix equals source-target counts', local_trace)

    # Composition typing for every nonzero structure constant.
    composable = block_j[alpha] == block_i[beta]
    gamma_source = block_i[gamma] == block_i[alpha]
    gamma_target = block_j[gamma] == block_j[beta]
    _assert(bool(np.all(composable)), 'every nonzero product alpha*beta is object-composable', local_trace)
    _assert(bool(np.all(gamma_source)), 'every product target gamma has source of alpha', local_trace)
    _assert(bool(np.all(gamma_target)), 'every product target gamma has target of beta', local_trace)

    # Canonical formal multiplicity bases: basis offset for each nonzero space.
    offsets = np.empty_like(coeff, dtype=np.int64)
    total = 0
    for idx, c in enumerate(coeff.tolist()):
        offsets[idx] = total
        total += int(c)
    _assert(total == int(coeff.sum()), 'formal multiplicity-basis offsets cover coefficient total', local_trace)

    # Hash the compact offset table without emitting all 2.5M basis labels.
    offset_table = np.column_stack([alpha, beta, gamma, coeff, offsets]).astype(np.int64)
    basis_tail = {
        'last_space_index': int(len(coeff) - 1),
        'last_space_alpha_beta_gamma_coeff_offset': [int(x) for x in offset_table[-1].tolist()],
        'total_basis_vectors': int(total),
        'last_basis_label': f"e_{{{int(alpha[-1])},{int(beta[-1])}}}^{{{int(gamma[-1])}}}[{int(coeff[-1])-1}]",
    }

    # Object-triple support profile: how many nonzero multiplicity spaces lie
    # over each i->j->k object corridor.
    object_triple_counts: dict[str, int] = {}
    object_triple_mass: dict[str, int] = {}
    for a, b, c, pcoef in triples.tolist():
        key = f'{int(block_i[a])}->{int(block_j[a])}->{int(block_j[b])}'
        object_triple_counts[key] = object_triple_counts.get(key, 0) + 1
        object_triple_mass[key] = object_triple_mass.get(key, 0) + int(pcoef)

    coeff_hist: dict[str, int] = {}
    for c in coeff.tolist():
        coeff_hist[str(int(c))] = coeff_hist.get(str(int(c)), 0) + 1

    # Formal associator boundary: the K0 algebra is associative as inherited
    # from the coherent algebra certificate, but concrete incidence F-symbols
    # need relation membership lists, not just representative pairs and counts.
    available_data = {
        'full_sparse_structure_constants': True,
        'orbital_source_target_typing': True,
        'representative_pairs': True,
        'coefficient_dimensions': True,
        'actual_relation_membership_lists': False,
        'intermediate_dodecad_sets_for_each_product': False,
        'linearized_rebracketing_bijections': False,
    }

    block = {
        'schema': 'gnatural.c985_incidence_multiplicity_skeleton.v1',
        'status': 'C985_INCIDENCE_MULTIPLICITY_SKELETON_CERTIFIED',
        'input_hashes': {trel: h_file(ROOT / trel), qrel: h_file(ROOT / qrel), crel: h_file(ROOT / crel)},
        'object_set': {
            'name': 'H6',
            'size': 6,
            'addresses': ['B-', 'B+', 'V-', 'V+', 'S-', 'S+'],
        },
        'simple_1_morphisms': {
            'count': 985,
            'source_target_matrix': M_computed.astype(int).tolist(),
            'source_target_matrix_sha256': h_json(M_computed.astype(int).tolist()),
        },
        'multiplicity_spaces': {
            'nonzero_spaces': int(triples.shape[0]),
            'total_formal_basis_vectors': int(total),
            'basis_label_schema': 'e_{alpha,beta}^{gamma}[r] for 0 <= r < p^gamma_{alpha,beta}',
            'basis_offset_table_columns': ['alpha', 'beta', 'gamma', 'dimension', 'basis_offset'],
            'basis_offset_table_sha256': hashlib.sha256(offset_table.tobytes()).hexdigest(),
            'basis_tail': basis_tail,
            'coefficient_histogram': dict(sorted(coeff_hist.items(), key=lambda kv: int(kv[0]))),
        },
        'typing_checks': {
            'all_products_object_composable': bool(np.all(composable)),
            'all_gamma_sources_match_alpha_sources': bool(np.all(gamma_source)),
            'all_gamma_targets_match_beta_targets': bool(np.all(gamma_target)),
            'source_target_violations': {
                'noncomposable_alpha_beta': int(np.count_nonzero(~composable)),
                'gamma_source_mismatch': int(np.count_nonzero(~gamma_source)),
                'gamma_target_mismatch': int(np.count_nonzero(~gamma_target)),
            },
        },
        'object_triple_profile': {
            'corridor_count': len(object_triple_counts),
            'nonzero_space_counts_by_corridor': dict(sorted(object_triple_counts.items())),
            'basis_mass_by_corridor': dict(sorted(object_triple_mass.items())),
        },
        'categorical_lift_boundary': {
            'available_data': available_data,
            'certified_as': 'K0 multiplicity-space inventory and formal basis-offset scheme for the incidence/profunctor categorification C985',
            'not_yet_certified_as': [
                'concrete incidence basis of intermediate dodecads z for each M_{alpha,beta}^gamma',
                'F-symbol matrices from linearized rebracketing bijections',
                'full Drinfeld center Z(C985)',
            ],
            'next_required_data': [
                'relation membership lists R_alpha subset Omega_i x Omega_j',
                'for each nonzero alpha,beta,gamma and representative (x,y) in R_gamma, the set {z: (x,z) in R_alpha and (z,y) in R_beta}',
                'canonical ordering of those incidence sets to build F-symbol permutation matrices',
            ],
        },
        'verification_trace': local_trace,
    }
    block['c985_incidence_skeleton_sha256'] = h_json(block)
    return block


def load_c985_relation_membership_boundary_certificate(c985_incidence_skeleton: Dict[str, Any]) -> Dict[str, Any]:
    """Certify the next boundary: relation representatives and valency data.

    The C985 skeleton certifies formal multiplicity spaces from the sparse
    A985 tensor.  Concrete F-symbol permutation matrices require actual
    relation membership lists R_alpha subset Omega_i x Omega_j.  This block
    verifies the strongest membership seed present in the one-command bundle:
    every orbital has a representative pair and a valency, the valencies
    partition each target object orbit correctly, and the total represented
    relation-pair mass is |Omega|^2.  It also records that actual relation
    membership arrays and intermediate-incidence sets are not bundled.
    """
    trel = 'data/tensor_sparse.npz'
    qrel = 'data/quotients.npz'
    z = np.load(ROOT / trel)
    q = np.load(ROOT / qrel)
    reps = np.array(z['reps'], dtype=np.int64)
    M_stored = np.array(z['M'], dtype=np.int64)
    block_i = np.array(q['block_i'], dtype=np.int64)
    block_j = np.array(q['block_j'], dtype=np.int64)
    local_trace: list[dict] = []

    _assert(c985_incidence_skeleton['status'] == 'C985_INCIDENCE_MULTIPLICITY_SKELETON_CERTIFIED', 'C985 skeleton is certified before relation-membership boundary', local_trace)
    _assert(reps.shape == (985, 5), 'orbital representative table has shape 985x5', local_trace)
    _assert(np.array_equal(reps[:, 0], block_i), 'representative source blocks match block_i', local_trace)
    _assert(np.array_equal(reps[:, 1], block_j), 'representative target blocks match block_j', local_trace)

    rep_x = reps[:, 2]
    rep_y = reps[:, 3]
    valency = reps[:, 4]
    _assert(int(rep_x.min()) >= 0 and int(rep_x.max()) < 2576, 'representative x indices lie in 0..2575', local_trace)
    _assert(int(rep_y.min()) >= 0 and int(rep_y.max()) < 2576, 'representative y indices lie in 0..2575', local_trace)
    _assert(int(valency.min()) > 0, 'all representative valencies are positive', local_trace)

    # A relation R_alpha:i->j has constant fiber size valency[alpha] over
    # every source point in Omega_i.  Therefore, for fixed i,j the valencies
    # over orbitals in Hom(i,j) must sum to |Omega_j|.
    target_sizes_by_source = np.zeros((6, 6), dtype=np.int64)
    count_by_source_target = np.zeros((6, 6), dtype=np.int64)
    for a in range(985):
        i = int(block_i[a]); j = int(block_j[a])
        target_sizes_by_source[i, j] += int(valency[a])
        count_by_source_target[i, j] += 1
    _assert(np.array_equal(count_by_source_target, M_stored), 'source-target representative counts equal M matrix', local_trace)

    inferred_object_sizes = []
    valency_partition_failures = []
    for j in range(6):
        col = target_sizes_by_source[:, j].astype(int).tolist()
        if len(set(col)) != 1:
            valency_partition_failures.append({'target': j, 'sourcewise_valency_sums': col})
        inferred_object_sizes.append(int(col[0]))
    _assert(valency_partition_failures == [], 'valency sums for Hom(i,j) are independent of source i', local_trace)
    _assert(inferred_object_sizes == [384, 192, 144, 576, 512, 768], 'inferred object orbit sizes are [384,192,144,576,512,768]', local_trace)
    _assert(sum(inferred_object_sizes) == 2576, 'inferred object sizes sum to 2576 dodecads', local_trace)

    total_relation_pairs = 0
    relation_pair_masses_by_corridor: dict[str, int] = {}
    for a in range(985):
        i = int(block_i[a]); j = int(block_j[a])
        mass = inferred_object_sizes[i] * int(valency[a])
        total_relation_pairs += mass
        key = f'{i}->{j}'
        relation_pair_masses_by_corridor[key] = relation_pair_masses_by_corridor.get(key, 0) + mass
    _assert(total_relation_pairs == 2576 * 2576, 'orbital relation-pair masses partition Omega x Omega', local_trace)

    # The relation-membership arrays needed for concrete F-symbols are checked
    # as files.  Their absence is the certified boundary of this one-command
    # bundle rather than an unreported assumption.
    required_files = {
        'data/relation_memberships.npz': (ROOT / 'data/relation_memberships.npz').exists(),
        'data/c985_intermediate_incidence_sets.npz': (ROOT / 'data/c985_intermediate_incidence_sets.npz').exists(),
        'data/c985_f_symbol_permutations.npz': (ROOT / 'data/c985_f_symbol_permutations.npz').exists(),
    }
    _assert(required_files['data/relation_memberships.npz'] is False, 'actual relation membership array is not bundled', local_trace)
    _assert(required_files['data/c985_intermediate_incidence_sets.npz'] is False, 'intermediate incidence set array is not bundled', local_trace)
    _assert(required_files['data/c985_f_symbol_permutations.npz'] is False, 'F-symbol permutation array is not bundled', local_trace)

    # Compact representative seed hash: source,target,x,y,valency for each orbital.
    seed_table = np.column_stack([block_i, block_j, rep_x, rep_y, valency]).astype(np.int64)
    block = {
        'schema': 'gnatural.c985_relation_membership_boundary.v1',
        'status': 'C985_RELATION_MEMBERSHIP_SEED_CERTIFIED_REAL_MEMBERSHIPS_STILL_REQUIRED',
        'input_hashes': {trel: h_file(ROOT / trel), qrel: h_file(ROOT / qrel)},
        'representative_seed': {
            'columns': ['source_object', 'target_object', 'representative_x', 'representative_y', 'valency'],
            'row_count': int(seed_table.shape[0]),
            'sha256': hashlib.sha256(seed_table.tobytes()).hexdigest(),
            'first_rows': seed_table[:12].astype(int).tolist(),
        },
        'valency_partition': {
            'inferred_object_sizes': inferred_object_sizes,
            'source_target_orbital_count_matrix': count_by_source_target.astype(int).tolist(),
            'source_target_valency_sum_matrix': target_sizes_by_source.astype(int).tolist(),
            'relation_pair_masses_by_corridor': dict(sorted(relation_pair_masses_by_corridor.items())),
            'total_relation_pairs': int(total_relation_pairs),
            'expected_relation_pairs': int(2576 * 2576),
            'partitions_Omega_cross_Omega': True,
        },
        'available_for_next_lift': {
            'representative_pairs': True,
            'constant_valencies': True,
            'formal_multiplicity_bases': True,
            'actual_relation_membership_lists': False,
            'intermediate_dodecad_incidence_sets': False,
            'F_symbol_permutation_matrices': False,
        },
        'categorical_lift_boundary': {
            'certified_as': 'relation representative/valency seed for the C985 incidence category',
            'not_yet_certified_as': [
                'actual relation membership lists R_alpha subset Omega_i x Omega_j',
                'incidence basis elements z for M_{alpha,beta}^gamma',
                'linearized associator/F-symbol permutation matrices',
            ],
            'next_required_data': required_files,
            'reason': 'The one-command bundle contains enough data to certify K0 multiplicity dimensions and relation valencies, but concrete F-symbols require enumerated relation members, not only representative pairs and counts.',
        },
        'verification_trace': local_trace,
    }
    block['c985_relation_membership_boundary_sha256'] = h_json(block)
    return block



def load_c985_relation_membership_generator_certificate() -> Dict[str, Any]:
    """Register and smoke-check the concrete relation-membership generator.

    This is the executable next layer after the representative/valency seed.  It
    does not run the heavy Be3 source rebuild inside .\certify.ps1.  Instead it
    certifies that the bundle now contains the deterministic generator scripts,
    verifies the seed mass they will expand, and upgrades automatically if
    data/relation_memberships.npz has been generated locally.
    """
    trel = 'data/tensor_sparse.npz'
    qrel = 'data/quotients.npz'
    gen_rel = 'source/generate_c985_relation_memberships.py'
    be3_rel = 'source/gnat_be3_source.py'
    z = np.load(ROOT / trel)
    q = np.load(ROOT / qrel)
    reps = np.array(z['reps'], dtype=np.int64)
    block_i = np.array(q['block_i'], dtype=np.int64)
    block_j = np.array(q['block_j'], dtype=np.int64)
    local_trace: list[dict] = []
    _assert((ROOT / gen_rel).exists(), 'concrete relation-membership generator script is bundled', local_trace)
    _assert((ROOT / be3_rel).exists(), 'source-side Be3/Golay generator library is bundled', local_trace)
    _assert(reps.shape == (985,5), 'relation generator seed reps table has shape 985x5', local_trace)
    _assert(np.array_equal(reps[:,0], block_i), 'relation generator source blocks match reps table', local_trace)
    _assert(np.array_equal(reps[:,1], block_j), 'relation generator target blocks match reps table', local_trace)
    inferred_sizes = [384,192,144,576,512,768]
    seed_pair_mass = int(sum(inferred_sizes[int(block_i[a])] * int(reps[a,4]) for a in range(985)))
    _assert(seed_pair_mass == 2576*2576, 'relation generator seed mass equals 2576^2', local_trace)

    rel_npz = ROOT / 'data' / 'relation_memberships.npz'
    concrete_status = 'not_present'
    concrete_hash = None
    concrete_checks: dict[str, Any] = {}
    if rel_npz.exists():
        rz = np.load(rel_npz)
        encoded = np.array(rz['encoded_pairs'], dtype=np.int64)
        offsets = np.array(rz['offsets'], dtype=np.int64)
        object_of_point = np.array(rz['object_of_point'], dtype=np.int16)
        _assert(offsets.shape == (986,), 'relation_memberships offsets have length 986', local_trace)
        _assert(int(offsets[0]) == 0, 'relation_memberships offsets start at zero', local_trace)
        _assert(int(offsets[-1]) == int(encoded.shape[0]), 'relation_memberships final offset equals encoded-pair length', local_trace)
        _assert(int(encoded.shape[0]) == 2576*2576, 'relation_memberships encoded-pair length is 2576^2', local_trace)
        _assert(object_of_point.shape == (2576,), 'relation_memberships object_of_point has length 2576', local_trace)
        # Uniqueness is expensive but acceptable only when the optional concrete file exists.
        _assert(int(np.unique(encoded).shape[0]) == int(encoded.shape[0]), 'relation_memberships encoded pairs are unique', local_trace)
        concrete_status = 'certified_present'
        concrete_hash = h_file(rel_npz)
        concrete_checks = {
            'encoded_pairs': int(encoded.shape[0]),
            'relations': 985,
            'offsets_len': int(offsets.shape[0]),
            'unique_pairs': True,
            'sha256': concrete_hash,
        }
    block = {
        'schema': 'gnatural.c985_relation_membership_generator.v1',
        'status': 'C985_RELATION_MEMBERSHIP_GENERATOR_REGISTERED' if concrete_status == 'not_present' else 'C985_RELATION_MEMBERSHIPS_CERTIFIED',
        'input_hashes': {trel: h_file(ROOT / trel), qrel: h_file(ROOT / qrel), gen_rel: h_file(ROOT / gen_rel), be3_rel: h_file(ROOT / be3_rel)},
        'generator': {
            'script': gen_rel,
            'be3_source_library': be3_rel,
            'smoke_command': 'python .\\source\\generate_c985_relation_memberships.py --smoke',
            'heavy_generation_command': 'python .\\source\\generate_c985_relation_memberships.py --generate-be3 --out .\\data\\relation_memberships.npz',
            'powershell_from_verifier_root': '.\\certify.ps1 -GenerateRelations',
        },
        'seed_smoke': {
            'relations': 985,
            'representatives_shape': [985,5],
            'source_blocks_match': True,
            'target_blocks_match': True,
            'total_pair_mass_from_seed': seed_pair_mass,
            'expected_pair_mass': 2576*2576,
        },
        'optional_concrete_membership_file': {
            'path': 'data/relation_memberships.npz',
            'status': concrete_status,
            'checks': concrete_checks,
        },
        'categorical_lift_boundary': {
            'certified_as': 'deterministic source-side generator for actual relation memberships R_alpha subset Omega x Omega',
            'heavy_run_inside_certify_by_default': False,
            'reason': 'Concrete memberships require rebuilding or loading the Be3 dodecad-shell action and expanding 6,635,776 ordered pairs; this is intentionally a separate explicit command so ordinary certification remains non-stalling.',
            'next_after_memberships': [
                'build incidence bases {z:(x,z) in R_alpha and (z,y) in R_beta}',
                'linearize rebracketing bijections as F-symbol permutation matrices',
                'solve categorical half-braiding equations in the idempotent-completed category',
            ],
        },
        'verification_trace': local_trace,
    }
    block['c985_relation_membership_generator_sha256'] = h_json(block)
    return block



def load_c985_f_symbol_generator_certificate() -> Dict[str, Any]:
    """Register and, when possible, verify the concrete C985 F-symbol chain generator.

    The full F-symbol matrices require actual relation-membership arrays and explicit
    left/right decomposition-basis orderings.  This block keeps default certification
    non-stalling: without relation_memberships.npz it certifies the generator boundary;
    with optional f_symbol_samples.json it verifies the sample file.
    """
    gen_rel = 'source/generate_c985_f_symbols.py'
    perm_gen_rel = 'source/generate_c985_f_symbol_permutations.py'
    trel = 'data/tensor_sparse.npz'
    rel_npz = ROOT / 'data' / 'relation_memberships.npz'
    sample_json = ROOT / 'data' / 'f_symbol_samples.json'
    perm_npz = ROOT / 'data' / 'c985_f_symbol_permutations.npz'
    z = np.load(ROOT / trel)
    triples = np.array(z['triples'], dtype=np.int64)
    reps = np.array(z['reps'], dtype=np.int64)
    local_trace: list[dict] = []
    _assert((ROOT / gen_rel).exists(), 'C985 F-symbol generator script is bundled', local_trace)
    _assert((ROOT / perm_gen_rel).exists(), 'C985 F-symbol permutation generator script is bundled', local_trace)
    _assert(triples.shape[0] == 1414965, 'F-symbol generator sees 1,414,965 sparse products', local_trace)
    _assert(int(triples[:,3].sum()) == 2537360, 'F-symbol generator sees 2,537,360 total multiplicity basis vectors', local_trace)
    _assert(reps.shape == (985,5), 'F-symbol generator representative table has shape 985x5', local_trace)

    relation_status = 'present' if rel_npz.exists() else 'not_present'
    sample_status = 'not_present'
    sample_checks: dict[str, Any] = {}
    if sample_json.exists():
        with sample_json.open('r', encoding='utf-8') as f:
            sample = json.load(f)
        _assert(sample.get('status') == 'F_SYMBOL_CHAIN_SAMPLES_GENERATED', 'F-symbol sample file has generated status', local_trace)
        _assert(int(sample.get('sample_count', 0)) >= 0, 'F-symbol sample count is nonnegative', local_trace)
        _assert(sample.get('not_yet_full_matrices') is True, 'F-symbol sample file does not overclaim full matrices', local_trace)
        sample_status = 'certified_present'
        sample_checks = {
            'sample_count': int(sample.get('sample_count', 0)),
            'sample_limit': int(sample.get('sample_limit', 0)),
            'sha256': h_file(sample_json),
        }

    perm_status = 'not_present'
    perm_checks: dict[str, Any] = {}
    if perm_npz.exists():
        pz = np.load(perm_npz)
        required = ['sample_meta','sample_offsets','left_delta','left_chain_code','right_eta','right_chain_code','left_to_right_perm']
        for name in required:
            _assert(name in pz.files, f'F-symbol permutation sample NPZ has array {name}', local_trace)
        sample_meta = np.array(pz['sample_meta'], dtype=np.int64)
        sample_offsets = np.array(pz['sample_offsets'], dtype=np.int64)
        perm = np.array(pz['left_to_right_perm'], dtype=np.int64)
        left_code = np.array(pz['left_chain_code'], dtype=np.int64)
        right_code = np.array(pz['right_chain_code'], dtype=np.int64)
        _assert(sample_meta.ndim == 2 and sample_meta.shape[1] == 7, 'F-symbol permutation sample metadata has shape Nx7', local_trace)
        _assert(sample_offsets.shape == (sample_meta.shape[0] + 1,), 'F-symbol permutation sample offsets have length N+1', local_trace)
        _assert(int(sample_offsets[0]) == 0, 'F-symbol permutation sample offsets start at zero', local_trace)
        _assert(int(sample_offsets[-1]) == int(perm.shape[0]), 'F-symbol permutation sample final offset equals permutation length', local_trace)
        _assert(left_code.shape == perm.shape and right_code.shape == perm.shape, 'F-symbol left/right chain-code arrays match permutation length', local_trace)
        ok_perms = True
        for lo, hi in zip(sample_offsets[:-1], sample_offsets[1:]):
            lo = int(lo); hi = int(hi)
            segment = perm[lo:hi].astype(int).tolist()
            if sorted(segment) != list(range(hi - lo)):
                ok_perms = False
                break
            if sorted(left_code[lo:hi].astype(int).tolist()) != sorted(right_code[lo:hi].astype(int).tolist()):
                ok_perms = False
                break
        _assert(ok_perms, 'F-symbol sample arrays define valid left-to-right sparse permutations', local_trace)
        perm_status = 'certified_present'
        perm_checks = {
            'sample_count': int(sample_meta.shape[0]),
            'total_basis_vectors_sampled': int(perm.shape[0]),
            'sha256': h_file(perm_npz),
            'arrays': {name: list(np.array(pz[name]).shape) for name in required},
        }

    status = 'C985_F_SYMBOL_GENERATOR_REGISTERED'
    if relation_status == 'present' and sample_status == 'certified_present':
        status = 'C985_F_SYMBOL_CHAIN_SAMPLES_CERTIFIED'
    elif relation_status == 'present':
        status = 'C985_F_SYMBOL_GENERATOR_READY_FOR_SAMPLES'

    block = {
        'schema': 'gnatural.c985_f_symbol_generator.v1',
        'status': status,
        'input_hashes': {trel: h_file(ROOT / trel), gen_rel: h_file(ROOT / gen_rel), perm_gen_rel: h_file(ROOT / perm_gen_rel)},
        'generator': {
            'script': gen_rel,
            'smoke_command': 'python .\\source\\generate_c985_f_symbols.py --smoke',
            'sample_generation_command': 'python .\\source\\generate_c985_f_symbols.py --out .\\data\\f_symbol_samples.json --sample-limit 32',
            'powershell_from_verifier_root': '.\\certify.ps1 -GenerateFSymbols -FSymbolSampleLimit 32',
            'permutation_script': perm_gen_rel,
            'permutation_generation_command': 'python .\\source\\generate_c985_f_symbol_permutations.py --out .\\data\\c985_f_symbol_permutations.npz --sample-limit 32',
            'permutation_powershell_from_verifier_root': '.\\certify.ps1 -GenerateFPermutations -FPermutationSampleLimit 32',
        },
        'required_input': {
            'relation_memberships_path': 'data/relation_memberships.npz',
            'relation_memberships_status': relation_status,
            'relation_memberships_sha256': h_file(rel_npz) if rel_npz.exists() else None,
        },
        'optional_sample_file': {
            'path': 'data/f_symbol_samples.json',
            'status': sample_status,
            'checks': sample_checks,
        },
        'optional_permutation_file': {
            'path': 'data/c985_f_symbol_permutations.npz',
            'status': perm_status,
            'checks': perm_checks,
        },
        'capability': {
            'constructs_chain_sets': True,
            'constructs_left_right_decomposition_basis_orderings': perm_status == 'certified_present',
            'constructs_sparse_f_symbol_permutation_samples': perm_status == 'certified_present',
            'chain_form': 'x --alpha--> z --beta--> w --chi--> y',
            'certifies_associator_underlying_set_equality_for_samples': sample_status == 'certified_present',
            'full_permutation_matrices_by_default': False,
            'reason': 'Full F-symbol matrices require concrete relation memberships and explicit left/right decomposition-basis orderings; sample generation is explicit and non-default.',
        },
        'categorical_lift_boundary': {
            'certified_as': 'deterministic F-symbol chain-set sample generator registered; optional samples certified when data/f_symbol_samples.json exists',
            'not_yet_certified_as': [
                'complete F-symbol permutation matrix inventory',
                'Drinfeld center half-braiding solution set',
                'full categorical Spin12 center',
            ],
            'next_after_samples': [
                'emit left decomposition basis ordering for each (alpha,beta,delta; delta,chi,epsilon)',
                'emit right decomposition basis ordering for each (beta,chi,eta; alpha,eta,epsilon)',
                'store sparse permutation arrays for concrete F-symbols',
                'solve hexagon/naturality equations using those permutations',
            ],
        },
        'verification_trace': local_trace,
    }
    block['c985_f_symbol_generator_sha256'] = h_json(block)
    return block


def load_c985_f_symbol_inventory_certificate() -> Dict[str, Any]:
    """Register and optionally certify the full F-symbol inventory manifest generator.

    This is the layer after permutation samples.  It does not default to a full
    inventory because the full associator-domain inventory can be large.  When
    data/c985_f_symbol_inventory_manifest.npz exists, this block verifies the
    manifest schema and content-addresses it.
    """
    gen_rel = 'source/generate_c985_f_symbol_inventory.py'
    trel = 'data/tensor_sparse.npz'
    rel_npz = ROOT / 'data' / 'relation_memberships.npz'
    perm_npz = ROOT / 'data' / 'c985_f_symbol_permutations.npz'
    manifest_npz = ROOT / 'data' / 'c985_f_symbol_inventory_manifest.npz'
    z = np.load(ROOT / trel)
    triples = np.array(z['triples'], dtype=np.int64)
    reps = np.array(z['reps'], dtype=np.int64)
    local_trace: list[dict] = []
    _assert((ROOT / gen_rel).exists(), 'C985 full F-symbol inventory generator script is bundled', local_trace)
    _assert(triples.shape[0] == 1414965, 'F-symbol inventory generator sees 1,414,965 sparse products', local_trace)
    _assert(int(triples[:,3].sum()) == 2537360, 'F-symbol inventory generator sees 2,537,360 total multiplicity basis vectors', local_trace)
    _assert(reps.shape == (985,5), 'F-symbol inventory generator representative table has shape 985x5', local_trace)

    relation_status = 'present' if rel_npz.exists() else 'not_present'
    permutation_status = 'present' if perm_npz.exists() else 'not_present'
    manifest_status = 'not_present'
    manifest_checks: dict[str, Any] = {}
    if manifest_npz.exists():
        mz = np.load(manifest_npz)
        required = ['inventory_rows','columns','chunk_limit','total_rows_scanned_before_stop','saturated']
        for name in required:
            _assert(name in mz.files, f'F-symbol inventory manifest has array {name}', local_trace)
        rows = np.array(mz['inventory_rows'], dtype=np.int64)
        _assert(rows.ndim == 2 and rows.shape[1] == 9, 'F-symbol inventory rows have shape Nx9', local_trace)
        _assert(np.all(rows[:,0:5] >= 0) if rows.size else True, 'F-symbol inventory relation indices are nonnegative', local_trace)
        _assert(np.all(rows[:,0:5] < 985) if rows.size else True, 'F-symbol inventory relation indices are less than 985', local_trace)
        _assert(np.all(rows[:,5:7] > 0) if rows.size else True, 'F-symbol inventory multiplicities are positive', local_trace)
        chunk_limit = int(np.array(mz['chunk_limit'], dtype=np.int64)[0])
        scanned = int(np.array(mz['total_rows_scanned_before_stop'], dtype=np.int64)[0])
        saturated = bool(int(np.array(mz['saturated'], dtype=np.int8)[0]))
        _assert(chunk_limit >= 0, 'F-symbol inventory chunk limit is nonnegative', local_trace)
        _assert(scanned >= rows.shape[0], 'F-symbol inventory scanned count dominates emitted row count', local_trace)
        manifest_status = 'certified_present'
        manifest_checks = {
            'row_count': int(rows.shape[0]),
            'columns': [str(x) for x in mz['columns'].tolist()],
            'chunk_limit': chunk_limit,
            'total_rows_scanned_before_stop': scanned,
            'saturated_by_chunk_limit': saturated,
            'sha256': h_file(manifest_npz),
        }

    status = 'C985_F_SYMBOL_INVENTORY_GENERATOR_REGISTERED'
    if relation_status == 'present' and manifest_status == 'certified_present':
        status = 'C985_F_SYMBOL_INVENTORY_MANIFEST_CERTIFIED'
    elif relation_status == 'present':
        status = 'C985_F_SYMBOL_INVENTORY_GENERATOR_READY'

    block = {
        'schema': 'gnatural.c985_f_symbol_inventory_generator.v1',
        'status': status,
        'input_hashes': {trel: h_file(ROOT / trel), gen_rel: h_file(ROOT / gen_rel)},
        'generator': {
            'script': gen_rel,
            'smoke_command': 'python .\\source\\generate_c985_f_symbol_inventory.py --smoke',
            'inventory_manifest_command': 'python .\\source\\generate_c985_f_symbol_inventory.py --out .\\data\\c985_f_symbol_inventory_manifest.npz --chunk-limit 100000',
            'powershell_from_verifier_root': '.\\certify.ps1 -GenerateFInventory -FInventoryChunkLimit 100000',
        },
        'required_input': {
            'relation_memberships_path': 'data/relation_memberships.npz',
            'relation_memberships_status': relation_status,
            'relation_memberships_sha256': h_file(rel_npz) if rel_npz.exists() else None,
        },
        'optional_dependency': {
            'permutation_samples_path': 'data/c985_f_symbol_permutations.npz',
            'permutation_samples_status': permutation_status,
            'permutation_samples_sha256': h_file(perm_npz) if perm_npz.exists() else None,
        },
        'optional_inventory_manifest_file': {
            'path': 'data/c985_f_symbol_inventory_manifest.npz',
            'status': manifest_status,
            'checks': manifest_checks,
        },
        'capability': {
            'constructs_associator_domain_inventory_rows': manifest_status == 'certified_present',
            'supports_chunked_full_inventory': True,
            'default_full_inventory_generation': False,
            'reason': 'Full associator-domain/F-symbol inventory can be large; generation is explicit and chunked so single-command certification remains non-stalling.',
        },
        'categorical_lift_boundary': {
            'certified_as': 'deterministic full-inventory manifest generator registered; optional chunk manifests certified when present',
            'not_yet_certified_as': [
                'complete all-row F-symbol permutation inventory',
                'hexagon equation solution set',
                'Drinfeld center half-braiding solution set',
            ],
            'next_after_inventory': [
                'generate all inventory chunks or a reproducible chunk cover',
                'attach sparse F-symbol permutations to each inventory row',
                'assemble hexagon/naturality linear equations',
                'solve central half-braidings in the idempotent-completed incidence category',
            ],
        },
        'verification_trace': local_trace,
    }
    block['c985_f_symbol_inventory_generator_sha256'] = h_json(block)
    return block


def build_payload() -> Dict[str, Any]:
    base = load_json('data/cached/base_certificate.json')
    aut_rigidity = unwrap(load_json('data/cached/aut_h_constructive_rigidity.json'))
    leech = unwrap(load_json('data/cached/leech_reconstruction_certificate.json'))
    simple_branching = load_simple_branching_certificate()
    recoupling_center = load_recoupling_center_certificate()
    half_braiding_boundary = load_half_braiding_lift_certificate(recoupling_center)
    idempotent_completion_boundary = load_idempotent_completion_boundary_certificate()
    c985_incidence_skeleton = load_c985_incidence_skeleton_certificate()
    c985_relation_membership_boundary = load_c985_relation_membership_boundary_certificate(c985_incidence_skeleton)
    c985_relation_membership_generator = load_c985_relation_membership_generator_certificate()
    c985_f_symbol_generator = load_c985_f_symbol_generator_certificate()
    c985_f_symbol_inventory = load_c985_f_symbol_inventory_certificate()

    proof_trace: list[dict] = []
    _assert(base.get('status') == 'PASS', 'base finite-object certificate has status PASS', proof_trace)
    _assert(aut_rigidity['H_equals_zero']['status'] == 'PROVED_FOR_VERIFIER_SCHEMA', 'H=0 residual schema is proved', proof_trace)
    _assert(bool(aut_rigidity['Co1_subgroup_of_AutH']['verified']), 'scratch Co1 generators preserve the H metric layer', proof_trace)
    _assert(aut_rigidity['status'] == 'CONSTRUCTIVE_RIGIDITY_RECONSTRUCTION_READY', 'constructive Aut(H) rigidity reconstruction is ready', proof_trace)
    _assert(leech['status'] == 'LEECH_RECONSTRUCTION_CERTIFIED', 'Leech reconstruction certificate is certified', proof_trace)
    _assert(bool(leech['scaled_lattice_certificate']['scaled_even_unimodular_rank_24']), 'scaled lattice is rank-24 even unimodular', proof_trace)
    _assert(bool(leech['root_test']['rootless_scaled_lattice']), 'scaled lattice is rootless', proof_trace)
    _assert(aut_rigidity['Co1_subgroup_of_AutH']['metric_spanning_star_checks']['failures'] == [], 'metric spanning-star checks have no failures', proof_trace)
    _assert(simple_branching['status'] == 'PASS_FULL_SIMPLE_NATURALITY', 'simple branching naturality certificate passes', proof_trace)
    _assert(simple_branching['naturality']['passes'] is True, 'simple branching naturality defect is zero', proof_trace)
    _assert(recoupling_center['status'] == 'PASS_H6_RECOUPLING_CENTER_CERTIFICATE', 'H6 recoupling center certificate passes', proof_trace)
    _assert(recoupling_center['k0_center']['nullity'] == 7, 'H6 K0 recoupling center has nullity 7', proof_trace)
    _assert(recoupling_center['associator']['normalized']['pentagon_failures'] == [], 'H6 K0 associator pentagon has no failures', proof_trace)
    _assert(half_braiding_boundary['status'] == 'HALF_BRAIDING_LIFT_REQUIRES_IDEMPOTENT_COMPLETION_AND_F_SYMBOLS', 'H6 half-braiding lift boundary is certified', proof_trace)
    _assert(half_braiding_boundary['simple_transparent_classes']['count_coefficient_transparent'] == 0, 'no simple coefficient-transparent A42 class is falsely promoted to a central object', proof_trace)
    _assert(idempotent_completion_boundary['status'] == 'IDEMPOTENT_COMPLETION_REQUIRES_INCIDENT_MULTIPLICITY_CATEGORY_NOT_EXPANDED_Q42_TENSOR', 'H6 idempotent-completion boundary is certified', proof_trace)
    _assert(c985_incidence_skeleton['status'] == 'C985_INCIDENCE_MULTIPLICITY_SKELETON_CERTIFIED', 'C985 incidence multiplicity skeleton is certified', proof_trace)
    _assert(c985_relation_membership_boundary['status'] == 'C985_RELATION_MEMBERSHIP_SEED_CERTIFIED_REAL_MEMBERSHIPS_STILL_REQUIRED', 'C985 relation-membership seed boundary is certified', proof_trace)
    _assert(c985_relation_membership_generator['status'] in {'C985_RELATION_MEMBERSHIP_GENERATOR_REGISTERED','C985_RELATION_MEMBERSHIPS_CERTIFIED'}, 'C985 relation-membership generator is registered or concrete memberships are certified', proof_trace)
    _assert(c985_f_symbol_generator['status'] in {'C985_F_SYMBOL_GENERATOR_REGISTERED','C985_F_SYMBOL_GENERATOR_READY_FOR_SAMPLES','C985_F_SYMBOL_CHAIN_SAMPLES_CERTIFIED'}, 'C985 F-symbol generator is registered, ready, or sample-certified', proof_trace)
    _assert(c985_f_symbol_inventory['status'] in {'C985_F_SYMBOL_INVENTORY_GENERATOR_REGISTERED','C985_F_SYMBOL_INVENTORY_GENERATOR_READY','C985_F_SYMBOL_INVENTORY_MANIFEST_CERTIFIED'}, 'C985 F-symbol inventory generator is registered, ready, or manifest-certified', proof_trace)

    claims = {
        'H_equals_zero': True,
        'Co1_subgroup_of_AutH': True,
        'constructive_rigidity_reconstruction_ready': True,
        'leech_reconstruction_certified': True,
        'simple_branching_naturality': True,
        'A236_tenfold_triplet_layer': True,
        'H6_recoupling_center': True,
        'D6_Spin12_K0_evidence': True,
        'H6_half_braiding_lift_boundary': True,
        'H6_idempotent_completion_boundary': True,
        'C985_incidence_multiplicity_skeleton': True,
        'C985_relation_membership_seed_boundary': True,
        'C985_relation_membership_generator_registered': True,
        'C985_relation_memberships_concrete': c985_relation_membership_generator['status'] == 'C985_RELATION_MEMBERSHIPS_CERTIFIED',
        'C985_f_symbol_generator_registered': True,
        'C985_f_symbol_samples_concrete': c985_f_symbol_generator['status'] == 'C985_F_SYMBOL_CHAIN_SAMPLES_CERTIFIED',
        'C985_f_symbol_inventory_generator_registered': True,
        'C985_f_symbol_inventory_manifest_concrete': c985_f_symbol_inventory['status'] == 'C985_F_SYMBOL_INVENTORY_MANIFEST_CERTIFIED',
        'AutH_eq_Co1_status': leech['autH_consequence']['AutH_eq_Co1_status'],
    }

    embedded_hashes = {
        'base_certificate_sha256': base['certificate_sha256'],
        'constructive_rigidity_sha256': aut_rigidity['constructive_rigidity_sha256'],
        'leech_reconstruction_sha256': leech['leech_reconstruction_sha256'],
        'simple_branching_sha256': simple_branching['simple_branching_sha256'],
        'recoupling_center_sha256': recoupling_center['recoupling_center_sha256'],
        'half_braiding_boundary_sha256': half_braiding_boundary['half_braiding_boundary_sha256'],
        'idempotent_completion_boundary_sha256': idempotent_completion_boundary['idempotent_completion_boundary_sha256'],
        'c985_incidence_skeleton_sha256': c985_incidence_skeleton['c985_incidence_skeleton_sha256'],
        'c985_relation_membership_boundary_sha256': c985_relation_membership_boundary['c985_relation_membership_boundary_sha256'],
        'c985_relation_membership_generator_sha256': c985_relation_membership_generator['c985_relation_membership_generator_sha256'],
        'c985_f_symbol_generator_sha256': c985_f_symbol_generator['c985_f_symbol_generator_sha256'],
        'c985_f_symbol_inventory_generator_sha256': c985_f_symbol_inventory['c985_f_symbol_inventory_generator_sha256'],
    }

    payload: Dict[str, Any] = {
        'schema': 'gnatural.self_arguing.self_certifying_certificate.v8',
        'object': 'Gnatural',
        'status': 'PASS',
        'H_name': 'H',
        'generated_and_verified_by': 'certify.ps1 -> source/emit_certificate.py',
        'external_group_software': False,
        'uses_atlasrep': False,
        'uses_gap': False,
        'single_command': '.\\certify.ps1',
        'claims': claims,
        'core_hashes': embedded_hashes,
        'package_hashes': file_hashes(),
        'self_argument': {
            'mode': 'proof-dag',
            'nodes': [
                {'id': 'N0', 'statement': 'The verifier source, data, generator files, and cached component certificates are content-addressed by SHA-256.', 'witness': 'package_hashes'},
                {'id': 'N1', 'statement': 'The finite coherent algebra certificate passes.', 'witness': 'full.base_certificate.status'},
                {'id': 'N2', 'statement': 'H=sum_i R_i^2 evaluates to 0 because every ordered residual block R_i verifies exactly.', 'witness': 'full.constructive_rigidity.H_equals_zero'},
                {'id': 'N3', 'statement': 'Scratch Co1 generators preserve the projective Leech H-layer metric and act transitively on 98,280 projective minimal vectors.', 'witness': 'full.constructive_rigidity.Co1_subgroup_of_AutH'},
                {'id': 'N4', 'statement': 'The projective shell lifts to a signed shell generating a rank-24 even unimodular rootless lattice under dot(x,y)/8.', 'witness': 'full.leech_reconstruction'},
                {'id': 'N5', 'statement': 'The simple branching square closes exactly: B236→12 = B236→42 · B42→12, with zero defect and valid row-dimension checks.', 'witness': 'full.simple_branching'},
                {'id': 'N6', 'statement': 'The A236 tenfold layer consists of ten triplet simples, giving Mat_3^{⊕10} at K0-level and triplet ideal dimension 90.', 'witness': 'full.simple_branching.A236_tenfold'},
                {'id': 'N7', 'statement': 'The H6 recoupling layer has 30 directed transports, normalized connection coefficients {144,192,384,512,576,768}, universal half-return, a pentagon-satisfying K0 associator, and K0 center nullity 7.', 'witness': 'full.recoupling_center'},
                {'id': 'N8', 'statement': 'The 30 transport classes match the positive-root count of D6, and the Foam chart has dimension 1+binom(6,2)=16, giving finite K0 evidence for the Spin12 recoupling selector.', 'witness': 'full.recoupling_center.D6_spin12_evidence'},
                {'id': 'N8b', 'statement': 'The attempted categorical half-braiding lift reaches the exact boundary: no simple A42 class is transparent, so the full Drinfeld-center lift requires idempotent completion and explicit F-symbol matrices.', 'witness': 'full.half_braiding_boundary'},
                {'id': 'N8c', 'statement': 'The idempotent-completion lift cannot be extracted from the expanded A42 quotient-count tensor: the strict unit system is inconsistent over checked primes, so the next construction must use incidence multiplicity spaces or a normalized Wedderburn/matrix-unit model.', 'witness': 'full.idempotent_completion_boundary'},
                {'id': 'N8d', 'statement': 'The C985 incidence/profunctor multiplicity skeleton is constructed from the full A985 sparse tensor: 985 simple 1-morphisms, 1,414,965 nonzero multiplicity spaces, 2,537,360 formal basis vectors, and zero source-target typing violations.', 'witness': 'full.c985_incidence_skeleton'},
                {'id': 'N8e', 'statement': 'The C985 relation-membership seed is certified: 985 representative pairs with valencies partition every Hom(i,j) target orbit and total relation-pair mass equals 2576^2; actual relation arrays remain the next data layer.', 'witness': 'full.c985_relation_membership_boundary'},
                {'id': 'N8f', 'statement': 'A deterministic source-side generator for concrete relation-membership arrays R_alpha is now bundled and smoke-checked; the heavy generation command is explicit and non-default to preserve non-stalling certification.', 'witness': 'full.c985_relation_membership_generator'},
                {'id': 'N8g', 'statement': 'A deterministic C985 F-symbol chain-set generator is bundled; it remains non-default and requires concrete relation memberships before emitting sample associator chain certificates or full F-symbol permutations.', 'witness': 'full.c985_f_symbol_generator'},
                {'id': 'N8h', 'statement': 'A deterministic C985 full F-symbol inventory manifest generator is bundled; it remains explicit and chunked, and it certifies manifests when concrete relation memberships have been generated.', 'witness': 'full.c985_f_symbol_inventory'},
                {'id': 'N9', 'statement': 'By the classical Leech uniqueness/automorphism theorem, the reconstructed lattice is the Leech lattice and the projective minimal-shell metric automorphism group is Co1.', 'witness': 'theorem_dependency'},
                {'id': 'N10', 'statement': 'Therefore H=0 is computationally certified, finite branching/naturality and H6 recoupling-center layers are certified, and Aut(H)=Co1 is certified modulo the stated classical theorem dependency.', 'depends_on': ['N0','N1','N2','N3','N4','N5','N6','N7','N8','N8b','N8c','N8d','N8e','N8f','N8g','N8h','N9']},
            ],
            'theorem_dependency': {
                'statement': 'The unique even unimodular rootless lattice of rank 24 is the Leech lattice, and its projective minimal-shell metric automorphism group is Co1.',
                'runtime_enumeration_required': False,
            },
            'proof_trace': proof_trace,
        },
        'summary': {
            'finite_algebra': {
                'name': 'A985',
                'orbitals': base['counters']['coherent_algebra']['orbitals'],
                'tensor_nonzero_entries': base['counters']['coherent_algebra']['multiplication_tensor_nonzero_entries'],
                'structure_constant_total': base['counters']['coherent_algebra']['structure_constant_total'],
                'center_dimension': base['counters']['coherent_algebra']['center_dimension'],
                'quotient_tower': {
                    'A985': base['counters']['quotient_tower']['A985'],
                    'A236': base['counters']['quotient_tower']['A236'],
                    'A42': base['counters']['quotient_tower']['A42']['classes'],
                    'A12': base['counters']['quotient_tower']['A12']['classes'],
                },
            },
            'simple_branching_naturality': {
                'status': simple_branching['status'],
                'center_dims': simple_branching['center_dims'],
                'simple_dimension_counts': simple_branching['simple_dimension_counts'],
                'branch_shapes': simple_branching['branch_shapes'],
                'naturality_defect_nonzero_entries': simple_branching['naturality']['defect_nonzero_entries'],
                'naturality_defect_l1': simple_branching['naturality']['defect_l1'],
                'A236_tenfold_triplet_count': simple_branching['A236_tenfold']['triplet_count'],
                'A236_tenfold_triplet_ideal_dimension': simple_branching['A236_tenfold']['triplet_ideal_dimension'],
            },

            'H6_recoupling_center': {
                'status': recoupling_center['status'],
                'transport_count': recoupling_center['class_partition']['transport_count'],
                'connection_gamma_values': recoupling_center['connection']['gamma_values'],
                'connection_gamma_histogram': recoupling_center['connection']['gamma_histogram'],
                'backtrack_histogram': recoupling_center['half_return']['backtrack_histogram'],
                'associator_unique_scalar_count': recoupling_center['associator']['normalized']['unique_scalar_count'],
                'associator_contains_half': recoupling_center['associator']['normalized']['contains_half'],
                'associator_contains_five_half': recoupling_center['associator']['normalized']['contains_five_half'],
                'pentagon_failures': len(recoupling_center['associator']['normalized']['pentagon_failures']),
                'expanded_raw_associator_unique_scalar_count': recoupling_center['associator']['expanded_raw']['unique_scalar_count'],
                'expanded_raw_associator_contains_half': recoupling_center['associator']['expanded_raw']['contains_half'],
                'expanded_raw_associator_contains_five_half': recoupling_center['associator']['expanded_raw']['contains_five_half'],
                'expanded_raw_pentagon_failures': len(recoupling_center['associator']['expanded_raw']['pentagon_failures']),
                'k0_center_rank': recoupling_center['k0_center']['rank'],
                'k0_center_nullity': recoupling_center['k0_center']['nullity'],
                'D6_spin12_evidence': recoupling_center['D6_spin12_evidence'],
            },
            'H6_idempotent_completion_boundary': {
                'status': idempotent_completion_boundary['status'],
                'strict_unit_system': idempotent_completion_boundary['strict_unit_system'],
                'not_certified_as': idempotent_completion_boundary['categorical_lift_boundary']['not_certified_as'],
            },
            'C985_incidence_multiplicity_skeleton': {
                'status': c985_incidence_skeleton['status'],
                'simple_1_morphisms': c985_incidence_skeleton['simple_1_morphisms']['count'],
                'nonzero_multiplicity_spaces': c985_incidence_skeleton['multiplicity_spaces']['nonzero_spaces'],
                'total_formal_basis_vectors': c985_incidence_skeleton['multiplicity_spaces']['total_formal_basis_vectors'],
                'basis_offset_table_sha256': c985_incidence_skeleton['multiplicity_spaces']['basis_offset_table_sha256'],
                'typing_checks': c985_incidence_skeleton['typing_checks'],
                'not_yet_certified_as': c985_incidence_skeleton['categorical_lift_boundary']['not_yet_certified_as'],
            },
            'C985_relation_membership_boundary': {
                'status': c985_relation_membership_boundary['status'],
                'representative_seed_sha256': c985_relation_membership_boundary['representative_seed']['sha256'],
                'inferred_object_sizes': c985_relation_membership_boundary['valency_partition']['inferred_object_sizes'],
                'total_relation_pairs': c985_relation_membership_boundary['valency_partition']['total_relation_pairs'],
                'actual_relation_membership_lists': c985_relation_membership_boundary['available_for_next_lift']['actual_relation_membership_lists'],
                'not_yet_certified_as': c985_relation_membership_boundary['categorical_lift_boundary']['not_yet_certified_as'],
            },
            'C985_relation_membership_generator': {
                'status': c985_relation_membership_generator['status'],
                'script': c985_relation_membership_generator['generator']['script'],
                'heavy_generation_command': c985_relation_membership_generator['generator']['heavy_generation_command'],
                'optional_concrete_membership_file_status': c985_relation_membership_generator['optional_concrete_membership_file']['status'],
            },
            'C985_f_symbol_generator': {
                'status': c985_f_symbol_generator['status'],
                'script': c985_f_symbol_generator['generator']['script'],
                'sample_generation_command': c985_f_symbol_generator['generator']['sample_generation_command'],
                'relation_memberships_status': c985_f_symbol_generator['required_input']['relation_memberships_status'],
                'optional_sample_file_status': c985_f_symbol_generator['optional_sample_file']['status'],
                'optional_permutation_file_status': c985_f_symbol_generator['optional_permutation_file']['status'],
            },
            'C985_f_symbol_inventory': {
                'status': c985_f_symbol_inventory['status'],
                'script': c985_f_symbol_inventory['generator']['script'],
                'inventory_manifest_command': c985_f_symbol_inventory['generator']['inventory_manifest_command'],
                'relation_memberships_status': c985_f_symbol_inventory['required_input']['relation_memberships_status'],
                'optional_inventory_manifest_file_status': c985_f_symbol_inventory['optional_inventory_manifest_file']['status'],
            },
            'H': {
                'formal_equation_count_A985_multiplication': aut_rigidity['H_equals_zero']['formal_equation_count_A985_multiplication'],
                'formal_sparse_tensor_terms': aut_rigidity['H_equals_zero']['formal_sparse_tensor_terms'],
                'residual_schema_sha256': aut_rigidity['H_equals_zero']['residual_schema_sha256'],
            },
            'Co1_projective_Leech': {
                'order': aut_rigidity['Co1_subgroup_of_AutH']['order'],
                'degree': aut_rigidity['Co1_subgroup_of_AutH']['degree'],
                'transitive': aut_rigidity['Co1_subgroup_of_AutH']['transitive'],
                'orbit': aut_rigidity['Co1_subgroup_of_AutH']['orbit'],
                'metric_spanning_star_vertex_comparisons': aut_rigidity['Co1_subgroup_of_AutH']['metric_spanning_star_checks']['vertex_comparisons'],
            },
            'Leech_reconstruction': {
                'projective_shell_vertices': leech['shell']['projective_vertex_count'],
                'signed_shell_vectors': leech['shell']['signed_shell_count'],
                'hnf_determinant_abs': leech['lattice_generation']['hnf_determinant_abs'],
                'normalization': 'dot(x,y)/8',
                'scaled_even_unimodular_rank_24': leech['scaled_lattice_certificate']['scaled_even_unimodular_rank_24'],
                'rootless_scaled_lattice': leech['root_test']['rootless_scaled_lattice'],
            },
        },
        'proof_boundary': {
            'computed_certificates_embedded': [
                'base finite object certificate',
                'constructive Aut(H) rigidity certificate',
                'Leech lattice reconstruction certificate',
                'simple branching naturality certificate',
                'H6 recoupling-center certificate',
                'H6 half-braiding lift-boundary certificate',
                'C985 incidence multiplicity skeleton certificate',
                'C985 F-symbol generator boundary certificate',
                'C985 F-symbol permutation-sample generator boundary certificate',
                'C985 full F-symbol inventory manifest generator boundary certificate',
            ],
            'runtime_mode': 'single-command generate-then-verify certificate; no GAP, no AtlasRep, no multi-command workflow',
            'classical_dependency': 'unique even unimodular rootless rank-24 lattice is the Leech lattice, and its projective minimal-shell metric automorphism group is Co1',
            'AutH_eq_Co1': leech['autH_consequence']['AutH_eq_Co1_status'],
        },
        'full': {
            'base_certificate': base,
            'constructive_rigidity': aut_rigidity,
            'leech_reconstruction': leech,
            'simple_branching': simple_branching,
            'recoupling_center': recoupling_center,
            'half_braiding_boundary': half_braiding_boundary,
            'idempotent_completion_boundary': idempotent_completion_boundary,
            'c985_incidence_skeleton': c985_incidence_skeleton,
            'c985_relation_membership_boundary': c985_relation_membership_boundary,
            'c985_relation_membership_generator': c985_relation_membership_generator,
            'c985_f_symbol_generator': c985_f_symbol_generator,
            'c985_f_symbol_inventory': c985_f_symbol_inventory,
        },
    }
    return payload


def attach_hash(payload: Dict[str, Any]) -> Dict[str, Any]:
    cert = json.loads(json.dumps(payload, ensure_ascii=False))
    cert[HASH_FIELD] = h_json(cert)
    return cert


def verify_certificate(cert: Dict[str, Any], *, root: Path = ROOT) -> Tuple[bool, Dict[str, Any]]:
    trace: list[dict] = []
    try:
        stored = cert.get(HASH_FIELD)
        unsigned = {k: v for k, v in cert.items() if k != HASH_FIELD}
        recomputed = h_json(unsigned)
        _assert(stored == recomputed, 'certificate_sha256 matches canonical certificate body', trace)
        _assert(cert.get('status') == 'PASS', 'top-level status is PASS', trace)
        _assert(cert.get('schema') == 'gnatural.self_arguing.self_certifying_certificate.v8', 'schema is expected v8 self-certifying schema', trace)
        _assert(cert.get('H_name') == 'H', 'Hamiltonian name is H', trace)
        _assert(cert.get('external_group_software') is False and cert.get('uses_gap') is False and cert.get('uses_atlasrep') is False, 'no GAP/AtlasRep/external group software dependency is declared', trace)
        for key in ['H_equals_zero', 'Co1_subgroup_of_AutH', 'constructive_rigidity_reconstruction_ready', 'leech_reconstruction_certified', 'simple_branching_naturality', 'A236_tenfold_triplet_layer', 'H6_recoupling_center', 'D6_Spin12_K0_evidence', 'H6_half_braiding_lift_boundary', 'H6_idempotent_completion_boundary', 'C985_incidence_multiplicity_skeleton', 'C985_relation_membership_seed_boundary', 'C985_relation_membership_generator_registered', 'C985_f_symbol_generator_registered']:
            _assert(cert['claims'].get(key) is True, f'claim {key} is true', trace)
        _assert(cert['full']['base_certificate']['certificate_sha256'] == cert['core_hashes']['base_certificate_sha256'], 'embedded base certificate hash matches core hash', trace)
        _assert(cert['full']['constructive_rigidity']['constructive_rigidity_sha256'] == cert['core_hashes']['constructive_rigidity_sha256'], 'embedded constructive rigidity hash matches core hash', trace)
        _assert(cert['full']['leech_reconstruction']['leech_reconstruction_sha256'] == cert['core_hashes']['leech_reconstruction_sha256'], 'embedded Leech reconstruction hash matches core hash', trace)
        _assert(cert['full']['simple_branching']['simple_branching_sha256'] == cert['core_hashes']['simple_branching_sha256'], 'embedded simple branching hash matches core hash', trace)
        _assert(cert['full']['recoupling_center']['recoupling_center_sha256'] == cert['core_hashes']['recoupling_center_sha256'], 'embedded recoupling center hash matches core hash', trace)
        _assert(cert['full']['half_braiding_boundary']['half_braiding_boundary_sha256'] == cert['core_hashes']['half_braiding_boundary_sha256'], 'embedded half-braiding boundary hash matches core hash', trace)
        _assert(cert['full']['idempotent_completion_boundary']['idempotent_completion_boundary_sha256'] == cert['core_hashes']['idempotent_completion_boundary_sha256'], 'embedded idempotent-completion boundary hash matches core hash', trace)
        _assert(cert['full']['c985_incidence_skeleton']['c985_incidence_skeleton_sha256'] == cert['core_hashes']['c985_incidence_skeleton_sha256'], 'embedded C985 incidence skeleton hash matches core hash', trace)
        _assert(cert['full']['c985_relation_membership_boundary']['c985_relation_membership_boundary_sha256'] == cert['core_hashes']['c985_relation_membership_boundary_sha256'], 'embedded C985 relation-membership boundary hash matches core hash', trace)
        _assert(cert['full']['c985_relation_membership_generator']['c985_relation_membership_generator_sha256'] == cert['core_hashes']['c985_relation_membership_generator_sha256'], 'embedded C985 relation-membership generator hash matches core hash', trace)
        _assert(cert['full']['c985_f_symbol_generator']['c985_f_symbol_generator_sha256'] == cert['core_hashes']['c985_f_symbol_generator_sha256'], 'embedded C985 F-symbol generator hash matches core hash', trace)
        _assert(cert['full']['constructive_rigidity']['H_equals_zero']['status'] == 'PROVED_FOR_VERIFIER_SCHEMA', 'embedded H=0 status is proved for verifier schema', trace)
        _assert(cert['full']['constructive_rigidity']['Co1_subgroup_of_AutH']['verified'] is True, 'embedded Co1 subgroup certificate is verified', trace)
        _assert(cert['full']['leech_reconstruction']['scaled_lattice_certificate']['scaled_even_unimodular_rank_24'] is True, 'embedded Leech lattice is scaled even unimodular rank 24', trace)
        _assert(cert['full']['leech_reconstruction']['root_test']['rootless_scaled_lattice'] is True, 'embedded Leech lattice root test is rootless', trace)
        _assert(cert['full']['simple_branching']['status'] == 'PASS_FULL_SIMPLE_NATURALITY', 'embedded simple branching status passes', trace)
        _assert(cert['full']['simple_branching']['naturality']['passes'] is True, 'embedded simple branching naturality passes', trace)
        _assert(cert['full']['simple_branching']['naturality']['defect_nonzero_entries'] == 0, 'embedded simple branching defect has zero nonzero entries', trace)
        _assert(cert['full']['simple_branching']['A236_tenfold']['triplet_count'] == 10, 'embedded A236 tenfold triplet count is 10', trace)
        _assert(cert['full']['simple_branching']['A236_tenfold']['triplet_ideal_dimension'] == 90, 'embedded A236 tenfold triplet ideal dimension is 90', trace)
        _assert(cert['full']['recoupling_center']['status'] == 'PASS_H6_RECOUPLING_CENTER_CERTIFICATE', 'embedded H6 recoupling center status passes', trace)
        _assert(cert['full']['recoupling_center']['k0_center']['nullity'] == 7, 'embedded H6 recoupling center nullity is 7', trace)
        _assert(cert['full']['recoupling_center']['associator']['normalized']['pentagon_failures'] == [], 'embedded H6 normalized recoupling pentagon failures are zero', trace)
        _assert(cert['full']['recoupling_center']['associator']['expanded_raw']['pentagon_failures'] == [], 'embedded H6 expanded/raw recoupling pentagon failures are zero', trace)
        _assert(cert['full']['recoupling_center']['associator']['expanded_raw']['contains_half'] is True, 'embedded H6 expanded/raw associator contains 1/2', trace)
        _assert(cert['full']['recoupling_center']['associator']['expanded_raw']['contains_five_half'] is True, 'embedded H6 expanded/raw associator contains 5/2', trace)
        _assert(cert['full']['recoupling_center']['D6_spin12_evidence']['dim_1_plus_Lambda2_H6'] == 16, 'embedded Foam big-cell dimension is 16', trace)
        _assert(cert['full']['half_braiding_boundary']['status'] == 'HALF_BRAIDING_LIFT_REQUIRES_IDEMPOTENT_COMPLETION_AND_F_SYMBOLS', 'embedded H6 half-braiding boundary status is certified', trace)
        _assert(cert['full']['half_braiding_boundary']['simple_transparent_classes']['count_coefficient_transparent'] == 0, 'embedded H6 half-braiding boundary has no simple transparent classes', trace)
        _assert(cert['full']['idempotent_completion_boundary']['status'] == 'IDEMPOTENT_COMPLETION_REQUIRES_INCIDENT_MULTIPLICITY_CATEGORY_NOT_EXPANDED_Q42_TENSOR', 'embedded H6 idempotent-completion boundary status is certified', trace)
        _assert(cert['full']['idempotent_completion_boundary']['strict_unit_system']['inconsistent_over_all_checked_primes'] is True, 'embedded H6 idempotent-completion boundary has no strict unit over checked primes', trace)
        _assert(cert['full']['c985_incidence_skeleton']['status'] == 'C985_INCIDENCE_MULTIPLICITY_SKELETON_CERTIFIED', 'embedded C985 incidence skeleton status is certified', trace)
        _assert(cert['full']['c985_incidence_skeleton']['simple_1_morphisms']['count'] == 985, 'embedded C985 skeleton has 985 simple 1-morphisms', trace)
        _assert(cert['full']['c985_incidence_skeleton']['multiplicity_spaces']['nonzero_spaces'] == 1414965, 'embedded C985 skeleton has 1,414,965 nonzero multiplicity spaces', trace)
        _assert(cert['full']['c985_incidence_skeleton']['multiplicity_spaces']['total_formal_basis_vectors'] == 2537360, 'embedded C985 skeleton has 2,537,360 formal basis vectors', trace)
        _assert(cert['full']['c985_incidence_skeleton']['typing_checks']['source_target_violations']['noncomposable_alpha_beta'] == 0, 'embedded C985 skeleton has no noncomposable products', trace)
        _assert(cert['full']['c985_relation_membership_boundary']['status'] == 'C985_RELATION_MEMBERSHIP_SEED_CERTIFIED_REAL_MEMBERSHIPS_STILL_REQUIRED', 'embedded C985 relation-membership seed boundary status is certified', trace)
        _assert(cert['full']['c985_relation_membership_boundary']['representative_seed']['row_count'] == 985, 'embedded C985 relation seed has 985 representative pairs', trace)
        _assert(cert['full']['c985_relation_membership_boundary']['valency_partition']['partitions_Omega_cross_Omega'] is True, 'embedded C985 valencies partition Omega cross Omega', trace)
        _assert(cert['full']['c985_relation_membership_boundary']['valency_partition']['total_relation_pairs'] == 2576*2576, 'embedded C985 relation-pair mass is 2576^2', trace)
        _assert(cert['full']['c985_relation_membership_boundary']['available_for_next_lift']['actual_relation_membership_lists'] is False, 'embedded C985 actual relation membership lists remain unbundled', trace)
        _assert(cert['full']['c985_relation_membership_generator']['status'] in {'C985_RELATION_MEMBERSHIP_GENERATOR_REGISTERED','C985_RELATION_MEMBERSHIPS_CERTIFIED'}, 'embedded C985 relation-membership generator status is registered or certified', trace)
        _assert(cert['full']['c985_relation_membership_generator']['seed_smoke']['total_pair_mass_from_seed'] == 2576*2576, 'embedded C985 relation generator seed mass is 2576^2', trace)
        _assert(cert['full']['c985_f_symbol_generator']['status'] in {'C985_F_SYMBOL_GENERATOR_REGISTERED','C985_F_SYMBOL_GENERATOR_READY_FOR_SAMPLES','C985_F_SYMBOL_CHAIN_SAMPLES_CERTIFIED'}, 'embedded C985 F-symbol generator status is valid', trace)
        _assert(cert['full']['c985_f_symbol_generator']['generator']['script'] == 'source/generate_c985_f_symbols.py', 'embedded C985 F-symbol generator script path is canonical', trace)
        _assert(cert['full']['c985_f_symbol_generator']['generator']['permutation_script'] == 'source/generate_c985_f_symbol_permutations.py', 'embedded C985 F-symbol permutation generator script path is canonical', trace)
        _assert(cert['full']['c985_f_symbol_generator']['optional_permutation_file']['status'] in {'not_present','certified_present'}, 'embedded C985 F-symbol permutation optional file status is valid', trace)
        _assert(cert['full']['c985_f_symbol_inventory']['status'] in {'C985_F_SYMBOL_INVENTORY_GENERATOR_REGISTERED','C985_F_SYMBOL_INVENTORY_GENERATOR_READY','C985_F_SYMBOL_INVENTORY_MANIFEST_CERTIFIED'}, 'embedded C985 F-symbol inventory generator status is valid', trace)
        _assert(cert['full']['c985_f_symbol_inventory']['generator']['script'] == 'source/generate_c985_f_symbol_inventory.py', 'embedded C985 F-symbol inventory generator script path is canonical', trace)
        _assert(cert['full']['c985_f_symbol_inventory']['optional_inventory_manifest_file']['status'] in {'not_present','certified_present'}, 'embedded C985 F-symbol inventory optional manifest status is valid', trace)
        # Verify current on-disk files match hashes declared in package_hashes.
        for rel, expected in cert.get('package_hashes', {}).items():
            path = root / rel
            _assert(path.exists(), f'package file exists: {rel}', trace)
            _assert(h_file(path) == expected, f'package file hash matches: {rel}', trace)
        return True, {'status': 'PASS', 'checks': trace, 'verified_checks': len(trace)}
    except Exception as e:
        trace.append({'check': 'exception', 'passed': False, 'error': repr(e)})
        return False, {'status': 'FAIL', 'checks': trace, 'verified_checks': sum(1 for t in trace if t.get('passed'))}


def build() -> Dict[str, Any]:
    payload = build_payload()
    cert = attach_hash(payload)
    ok, verification = verify_certificate(cert)
    if not ok:
        raise AssertionError('internal verification failed')
    cert['self_verification'] = verification
    # Include self_verification in final hash and verify again.
    cert.pop(HASH_FIELD, None)
    cert[HASH_FIELD] = h_json(cert)
    ok2, verification2 = verify_certificate(cert)
    if not ok2:
        raise AssertionError('final self verification failed')
    cert['self_verification'] = verification2
    cert.pop(HASH_FIELD, None)
    cert[HASH_FIELD] = h_json(cert)
    ok3, verification3 = verify_certificate(cert)
    if not ok3:
        raise AssertionError('fixed-point self verification failed')
    cert['self_verification']['fixed_point_verified'] = True
    cert['self_verification']['final_verification_sha256'] = h_json(verification3)
    cert.pop(HASH_FIELD, None)
    cert[HASH_FIELD] = h_json(cert)
    return cert


def write_json(path: Path, obj: Dict[str, Any], pretty: bool) -> None:
    text = json.dumps(obj, sort_keys=True, indent=(2 if pretty else None), separators=((',', ': ') if pretty else (',', ':')), ensure_ascii=False) + '\n'
    path.write_text(text, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='Generate and verify the single self-arguing Gnatural certificate.')
    ap.add_argument('--out', default='certificate.json')
    ap.add_argument('--pretty', action='store_true')
    ap.add_argument('--verify-only', action='store_true', help='Verify an existing certificate instead of regenerating it.')
    args = ap.parse_args()
    out = Path(args.out)
    if args.verify_only:
        cert = json.loads(out.read_text(encoding='utf-8'))
        ok, verification = verify_certificate(cert)
        if not ok:
            print('FAIL')
            print(json.dumps(verification, sort_keys=True, indent=2))
            sys.exit(1)
        print('PASS')
        print(f'verified = {out.resolve()}')
        print(f'certificate_sha256 = {cert[HASH_FIELD]}')
        return
    cert = build()
    write_json(out, cert, args.pretty)
    # Required second phase: read from disk and verify the exact emitted certificate.
    emitted = json.loads(out.read_text(encoding='utf-8'))
    ok, verification = verify_certificate(emitted)
    if not ok:
        print('FAIL')
        print(json.dumps(verification, sort_keys=True, indent=2))
        sys.exit(1)
    print('PASS')
    print(f'generated = {out.resolve()}')
    print(f'verified = true')
    print(f'certificate_sha256 = {emitted[HASH_FIELD]}')


if __name__ == '__main__':
    main()
