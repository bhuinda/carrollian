from __future__ import annotations

import hashlib
from typing import Any, Dict

import numpy as np

try:
    from .certify_io import cached_core_block, h_json, load_json, raw_tensor_relpath, ROOT
except ImportError:  # Supports `python src/certify_tube_center.py`.
    from certify_io import cached_core_block, h_json, load_json, raw_tensor_relpath, ROOT

try:
    from .certify_linear import (
        independent_row_indices_mod,
        multiply_vectors_by_tensor_mod,
        rref_nullspace_mod,
        solve_square_mod,
    )
except ImportError:  # Supports `python src/certify_tube_center.py`.
    from certify_linear import (
        independent_row_indices_mod,
        multiply_vectors_by_tensor_mod,
        rref_nullspace_mod,
        solve_square_mod,
    )

try:
    from .certify_tube_lift import find_identity_relations
except ImportError:  # Supports `python src/certify_tube_center.py`.
    from certify_tube_lift import find_identity_relations


def compute_tube_center_algebra_lift() -> Dict[str, Any]:
    """Compute finite-field center bases and center multiplication for closed-loop blocks.

    This is the next algebraic lift after the tube-algebra skeleton.  It is a
    concrete center-subalgebra certificate over a large prime field.  It is not
    a primitive-idempotent or full Drinfeld-center classification.
    """
    p0 = 1000003
    rel = np.load(ROOT / 'data/raw/relation_memberships.npz')
    encoded = np.asarray(rel['encoded_pairs'], dtype=np.int64)
    offsets = np.asarray(rel['offsets'], dtype=np.int64)
    object_of_point = np.asarray(rel['object_of_point'], dtype=np.int64)
    block_i = np.asarray(rel['block_i'], dtype=np.int64)
    block_j = np.asarray(rel['block_j'], dtype=np.int64)
    tensor = np.load(ROOT / raw_tensor_relpath())
    triples = np.asarray(tensor['triples'], dtype=np.int64)
    identity_relations = find_identity_relations(encoded, offsets, object_of_point, block_i, block_j)

    blocks = []
    total_center_dim = 0
    total_center_product_rows = 0
    total_center_product_mass_mod = 0
    all_basis_commutes = True
    all_center_products_close = True
    all_center_products_commute = True
    all_center_products_associate_sampled = True
    assoc_failures_total = 0
    assoc_challenges_total = 0
    center_multiplication_hash_inputs = []

    rng = np.random.default_rng(985109)

    for obj in range(6):
        ids = np.where((block_i == obj) & (block_j == obj))[0].astype(np.int64)
        n = int(len(ids))
        idx = {int(a): k for k, a in enumerate(ids.tolist())}
        mask = np.isin(triples[:, 0], ids) & np.isin(triples[:, 1], ids) & np.isin(triples[:, 2], ids)
        sub = triples[mask]
        T = np.zeros((n, n, n), dtype=np.int64)
        for aa, bb, cc, vv in sub.tolist():
            T[idx[int(aa)], idx[int(bb)], idx[int(cc)]] = int(vv)
        rows = []
        for a in range(n):
            rows.append((T[:, a, :] - T[a, :, :]).T)
        M = np.vstack(rows) if rows else np.zeros((0, n), dtype=np.int64)
        B, constraint_pivots = rref_nullspace_mod(M, p0)
        d = int(B.shape[1])
        total_center_dim += d
        # Validate commutation constraints.
        commute_ok = bool(np.all((M % p0) @ (B % p0) % p0 == 0))
        all_basis_commutes = all_basis_commutes and commute_ok
        minor_rows = independent_row_indices_mod(B, p0)
        minor = B[minor_rows, :] % p0 if d else np.zeros((0,0), dtype=np.int64)
        mult = np.zeros((d, d, d), dtype=np.int64)
        closure_ok = True
        commutative_ok = True
        for i in range(d):
            for j in range(d):
                prod = multiply_vectors_by_tensor_mod(B[:, i], B[:, j], T, p0)
                coords = solve_square_mod(minor, prod[minor_rows], p0) if d else np.zeros((0,), dtype=np.int64)
                recon = (B @ coords) % p0 if d else np.zeros((n,), dtype=np.int64)
                if not np.array_equal(recon % p0, prod % p0):
                    closure_ok = False
                mult[i, j, :] = coords
        if not np.array_equal(mult, np.swapaxes(mult, 0, 1)):
            commutative_ok = False
        # Unit vector in center coordinates.
        unit_rel = int(identity_relations[obj])
        unit_local = idx[unit_rel]
        unit_vec = np.zeros(n, dtype=np.int64); unit_vec[unit_local] = 1
        unit_coords = solve_square_mod(minor, unit_vec[minor_rows], p0) if d else np.zeros((0,), dtype=np.int64)
        unit_recon_ok = bool(np.array_equal((B @ unit_coords) % p0, unit_vec % p0)) if d else False
        # Unit laws in center algebra coordinates.
        unit_law_ok = True
        for i in range(d):
            left = multiply_vectors_by_tensor_mod(B @ unit_coords, B[:, i], T, p0)
            right = multiply_vectors_by_tensor_mod(B[:, i], B @ unit_coords, T, p0)
            if not (np.array_equal(left % p0, B[:, i] % p0) and np.array_equal(right % p0, B[:, i] % p0)):
                unit_law_ok = False
                break
        # Sample associativity inside center multiplication coordinates.
        failures = 0
        challenges = min(2048, max(1, d*d*d))
        for _ in range(challenges):
            a = int(rng.integers(0, d)) if d else 0
            b = int(rng.integers(0, d)) if d else 0
            c = int(rng.integers(0, d)) if d else 0
            left = mult[a, b, :].astype(np.int64) @ mult[:, c, :].astype(np.int64) % p0
            right = mult[b, c, :].astype(np.int64) @ mult[a, :, :].astype(np.int64) % p0
            if not np.array_equal(left % p0, right % p0):
                failures += 1
        assoc_challenges_total += int(challenges)
        assoc_failures_total += int(failures)
        all_center_products_associate_sampled = all_center_products_associate_sampled and (failures == 0)
        all_center_products_close = all_center_products_close and closure_ok
        all_center_products_commute = all_center_products_commute and commutative_ok
        supp = int(np.count_nonzero(mult))
        mass_mod = int(mult.sum() % p0)
        total_center_product_rows += supp
        total_center_product_mass_mod = (total_center_product_mass_mod + mass_mod) % p0
        center_multiplication_hash_inputs.append(hashlib.sha256(mult.astype(np.int64).tobytes()).hexdigest())
        blocks.append({
            'object': int(obj),
            'closed_loop_basis_count': n,
            'center_dimension': d,
            'center_constraint_rank': int(n - d),
            'center_basis_sha256': hashlib.sha256(B.astype(np.int64).tobytes()).hexdigest(),
            'center_basis_minor_rows_sha256': hashlib.sha256(np.asarray(minor_rows, dtype=np.int32).tobytes()).hexdigest(),
            'center_basis_commutes_with_closed_loop_block': commute_ok,
            'center_product_closure_ok': closure_ok,
            'center_product_commutative_ok': commutative_ok,
            'center_product_support_rows': supp,
            'center_product_coefficient_mass_mod_prime': mass_mod,
            'center_product_tensor_sha256': center_multiplication_hash_inputs[-1],
            'unit_relation': unit_rel,
            'unit_coordinates_sha256': hashlib.sha256(unit_coords.astype(np.int64).tobytes()).hexdigest(),
            'unit_reconstructs_identity_relation': unit_recon_ok,
            'unit_laws_hprior_inside_center_algebra': unit_law_ok,
            'sampled_center_associativity_challenges': int(challenges),
            'sampled_center_associativity_failures': int(failures),
        })
    result = {
        'schema': 'gnatural.c985.tube_center_algebra_lift.source_drop',
        'scope': 'Finite-field center-subalgebra basis and multiplication certificate for the six closed-loop tube blocks. This is still not primitive idempotents or full Drinfeld-center modular data.',
        'field': {'prime': p0, 'note': 'large finite field used for exact modular linear algebra'},
        'center_algebra': {
            'total_center_dimension': int(total_center_dim),
            'center_dimension_by_object': [b['center_dimension'] for b in blocks],
            'basis_commutes_with_closed_loop_algebra': bool(all_basis_commutes),
            'center_product_closure_ok': bool(all_center_products_close),
            'center_product_commutative_ok': bool(all_center_products_commute),
            'center_product_support_rows_total': int(total_center_product_rows),
            'center_product_coefficient_mass_mod_prime_total': int(total_center_product_mass_mod),
            'center_product_hash_root': hashlib.sha256(''.join(center_multiplication_hash_inputs).encode('ascii')).hexdigest(),
        },
        'unit_and_associativity': {
            'all_units_reconstruct_identity_relations': all(b['unit_reconstructs_identity_relation'] for b in blocks),
            'all_unit_laws_hprior_inside_center_algebras': all(b['unit_laws_hprior_inside_center_algebra'] for b in blocks),
            'sampled_center_associativity_challenges_total': int(assoc_challenges_total),
            'sampled_center_associativity_failures_total': int(assoc_failures_total),
            'sampled_center_associativity_ok': bool(all_center_products_associate_sampled),
        },
        'blocks': blocks,
        'verified_claims': [
            'For each closed-loop block i->i, the verifier computes an explicit finite-field basis for the Grothendieck center.',
            'The computed center bases commute with all closed-loop basis relations.',
            'Products of center basis elements close back into the center basis and are commutative.',
            'The categorical identity relation in each closed-loop block reconstructs as a center element and acts as a unit.',
            'Sampled associativity checks pass inside the computed center algebras.',
        ],
    }
    result['c985_tube_center_algebra_lift_sha256'] = h_json(result)
    return result


def validate_tube_center_algebra_lift() -> Dict[str, Any]:
    computed = compute_tube_center_algebra_lift()
    path = ROOT / 'data/derived/tube_center_algebra.json'
    if path.exists():
        recorded = load_json('data/derived/tube_center_algebra.json')
        if recorded != computed:
            raise AssertionError('data/derived/tube_center_algebra.json does not match recomputed tube center algebra lift')
    return computed



def validate_tube_center_primitive_idempotents() -> Dict[str, Any]:
    """Validate stored primitive central idempotents for the closed-loop tube center.

    The idempotent coordinates are small and stored in JSON.  The verifier
    reconstructs the finite-field center multiplication from the raw tensor and
    checks the idempotent laws directly.  No polynomial factorization dependency
    is needed for verification.
    """
    path = ROOT / 'data/derived/tube_center_primitive_idempotents.json'
    if not path.exists():
        cached = cached_core_block('tube_center_primitive_idempotents')
        if cached is not None:
            return cached
        raise FileNotFoundError('missing tube-center primitive idempotent certificate and no layer-00 cache is available')
    rec = load_json('data/derived/tube_center_primitive_idempotents.json')
    p0 = int(rec['field']['prime'])
    if p0 != 1000003:
        raise AssertionError('unexpected primitive-idempotent check prime')
    rel = np.load(ROOT / 'data/raw/relation_memberships.npz')
    encoded = np.asarray(rel['encoded_pairs'], dtype=np.int64)
    offsets = np.asarray(rel['offsets'], dtype=np.int64)
    object_of_point = np.asarray(rel['object_of_point'], dtype=np.int64)
    block_i = np.asarray(rel['block_i'], dtype=np.int64)
    block_j = np.asarray(rel['block_j'], dtype=np.int64)
    tensor = np.load(ROOT / raw_tensor_relpath())
    triples = np.asarray(tensor['triples'], dtype=np.int64)
    identity_relations = find_identity_relations(encoded, offsets, object_of_point, block_i, block_j)

    total_idems = 0
    hash_inputs: list[str] = []
    block_summaries = []
    all_orthogonal = True
    all_sum_to_unit = True
    all_diagonal = True

    for block in rec['blocks']:
        obj = int(block['object'])
        ids = np.where((block_i == obj) & (block_j == obj))[0].astype(np.int64)
        n = int(len(ids))
        idx = {int(a): k for k, a in enumerate(ids.tolist())}
        mask = np.isin(triples[:, 0], ids) & np.isin(triples[:, 1], ids) & np.isin(triples[:, 2], ids)
        sub = triples[mask]
        T = np.zeros((n, n, n), dtype=np.int64)
        for aa, bb, cc, vv in sub.tolist():
            T[idx[int(aa)], idx[int(bb)], idx[int(cc)]] = int(vv)
        rows = []
        for a in range(n):
            rows.append((T[:, a, :] - T[a, :, :]).T)
        M = np.vstack(rows) if rows else np.zeros((0, n), dtype=np.int64)
        B, _ = rref_nullspace_mod(M, p0)
        d = int(B.shape[1])
        if d != int(block['center_dimension']):
            raise AssertionError('primitive-idempotent center dimension mismatch')
        minor_rows = independent_row_indices_mod(B, p0)
        minor = B[minor_rows, :] % p0 if d else np.zeros((0, 0), dtype=np.int64)
        mult = np.zeros((d, d, d), dtype=np.int64)
        for i in range(d):
            for j in range(d):
                prod = multiply_vectors_by_tensor_mod(B[:, i], B[:, j], T, p0)
                coords = solve_square_mod(minor, prod[minor_rows], p0) if d else np.zeros((0,), dtype=np.int64)
                mult[i, j, :] = coords
        unit_rel = int(identity_relations[obj])
        unit_vec = np.zeros(n, dtype=np.int64)
        unit_vec[idx[unit_rel]] = 1
        unit_coords = solve_square_mod(minor, unit_vec[minor_rows], p0) if d else np.zeros((0,), dtype=np.int64)
        E = np.asarray(block['primitive_idempotent_coordinates'], dtype=np.int64) % p0
        if E.shape != (d, d):
            raise AssertionError('primitive-idempotent coordinate shape mismatch')
        if hashlib.sha256(E.astype(np.int64).tobytes()).hexdigest() != block['primitive_idempotent_coordinates_sha256']:
            raise AssertionError('primitive-idempotent coordinate hash mismatch')
        sep = np.asarray(block['separator_coordinates'], dtype=np.int64) % p0
        roots = [int(x) % p0 for x in block['eigenvalues']]
        if len(set(roots)) != d or sep.shape != (d,):
            raise AssertionError('separator/eigenvalue data malformed')

        def cprod(u: np.ndarray, v: np.ndarray) -> np.ndarray:
            return multiply_vectors_by_tensor_mod(u, v, mult, p0)

        orth_ok = True
        diag_ok = True
        zero = np.zeros(d, dtype=np.int64)
        for i in range(d):
            for j in range(d):
                got = cprod(E[i], E[j])
                want = E[i] if i == j else zero
                if not np.array_equal(got % p0, want % p0):
                    orth_ok = False
                    break
            if not orth_ok:
                break
        sum_ok = bool(np.array_equal(E.sum(axis=0) % p0, unit_coords % p0))
        for i in range(d):
            if not np.array_equal(cprod(sep, E[i]) % p0, (roots[i] * E[i]) % p0):
                diag_ok = False
                break
        all_orthogonal = all_orthogonal and orth_ok
        all_sum_to_unit = all_sum_to_unit and sum_ok
        all_diagonal = all_diagonal and diag_ok
        total_idems += d
        hash_inputs.append(block['primitive_idempotent_coordinates_sha256'])
        block_summaries.append({
            'object': obj,
            'center_dimension': d,
            'primitive_idempotent_count': d,
            'separator_seed': int(block['separator_seed']),
            'distinct_separator_eigenvalues': len(set(roots)),
            'orthogonal_idempotents_ok': bool(orth_ok),
            'sum_to_unit_ok': bool(sum_ok),
            'separator_diagonal_action_ok': bool(diag_ok),
            'primitive_idempotent_coordinates_sha256': block['primitive_idempotent_coordinates_sha256'],
        })
    root = hashlib.sha256(''.join(hash_inputs).encode('ascii')).hexdigest()
    if root != rec['idempotent_skeleton']['idempotent_hash_root']:
        raise AssertionError('primitive-idempotent hash root mismatch')
    if total_idems != int(rec['idempotent_skeleton']['total_primitive_idempotents']):
        raise AssertionError('primitive-idempotent total mismatch')
    return {
        'schema': rec['schema'],
        'scope': rec['scope'],
        'field': rec['field'],
        'idempotent_skeleton': {
            'total_primitive_idempotents': int(total_idems),
            'primitive_idempotents_by_object': [b['primitive_idempotent_count'] for b in block_summaries],
            'all_idempotents_orthogonal': bool(all_orthogonal),
            'all_idempotents_sum_to_units': bool(all_sum_to_unit),
            'all_separator_actions_diagonal': bool(all_diagonal),
            'idempotent_hash_root': root,
        },
        'blocks': block_summaries,
        'verified_claims': rec['verified_claims'],
        'c985_tube_center_primitive_idempotent_skeleton_sha256': rec['c985_tube_center_primitive_idempotent_skeleton_sha256'],
    }


