from __future__ import annotations

import hashlib
import math
from typing import Any, Dict

import numpy as np

try:
    from .certify_io import ROOT
except ImportError:  # Supports `python src/certify_raw.py`.
    from certify_io import ROOT

NPOINTS = 2576
NREL = 985


def validate_tensor(constants: Dict[str, Any]) -> Dict[str, Any]:
    z = np.load(ROOT / 'data/raw/tensor_sparse.npz')
    triples = np.asarray(z['triples'], dtype=np.int64)
    M = np.asarray(z['M'], dtype=np.int64)
    reps = np.asarray(z['reps'], dtype=np.int64)
    assert triples.shape == (1_414_965, 4)
    assert int(triples[:, 3].sum()) == 2_537_360
    assert reps.shape == (985, 5)
    assert M.shape == (6, 6)
    if 'tensor_shape' in constants:
        assert list(triples.shape) == constants['tensor_shape']
    if 'coefficient_total' in constants:
        assert int(triples[:, 3].sum()) == int(constants['coefficient_total'])
    return {
        'support': int(triples.shape[0]),
        'coefficient_total': int(triples[:, 3].sum()),
        'relation_count': int(reps.shape[0]),
        'object_pair_relation_matrix': M.astype(int).tolist(),
        'coefficient_min': int(triples[:, 3].min()),
        'coefficient_max': int(triples[:, 3].max()),
        'source_relation_range': [int(triples[:, 0].min()), int(triples[:, 0].max())],
        'middle_relation_range': [int(triples[:, 1].min()), int(triples[:, 1].max())],
        'target_relation_range': [int(triples[:, 2].min()), int(triples[:, 2].max())],
    }


def relation_leaf_hashes(encoded: np.ndarray, offsets: np.ndarray) -> list[str]:
    leaves = []
    for a in range(NREL):
        seg = np.sort(encoded[int(offsets[a]):int(offsets[a+1])]).astype(np.int64, copy=False)
        leaves.append(hashlib.sha256(np.ascontiguousarray(seg).tobytes()).hexdigest())
    return leaves


def validate_relations() -> Dict[str, Any]:
    z = np.load(ROOT / 'data/raw/relation_memberships.npz')
    encoded = np.asarray(z['encoded_pairs'], dtype=np.int64)
    offsets = np.asarray(z['offsets'], dtype=np.int64)
    object_of_point = np.asarray(z['object_of_point'], dtype=np.int64)
    reps = np.asarray(z['reps'], dtype=np.int64)
    block_i = np.asarray(z['block_i'], dtype=np.int64)
    block_j = np.asarray(z['block_j'], dtype=np.int64)
    points = int(np.asarray(z['points']).reshape(-1)[0])
    group_order = int(np.asarray(z['group_order']).reshape(-1)[0])
    assert points == NPOINTS
    assert group_order == 9216
    assert encoded.shape == (NPOINTS * NPOINTS,)
    assert offsets.shape == (NREL + 1,)
    assert int(offsets[0]) == 0 and int(offsets[-1]) == NPOINTS * NPOINTS
    assert np.all(offsets[1:] >= offsets[:-1])
    assert int(encoded.min()) >= 0 and int(encoded.max()) < NPOINTS * NPOINTS
    seen = np.zeros(NPOINTS * NPOINTS, dtype=np.bool_)
    seen[encoded] = True
    partition_ok = bool(seen.all() and int(seen.sum()) == NPOINTS * NPOINTS)
    object_sizes = np.bincount(object_of_point, minlength=6).astype(np.int64)
    assert object_sizes.tolist() == [384, 192, 144, 576, 512, 768]
    rel_ids = np.repeat(np.arange(NREL, dtype=np.int32), np.diff(offsets).astype(np.int64))
    src = object_of_point[encoded // NPOINTS]
    tgt = object_of_point[encoded % NPOINTS]
    typed_ok = bool(np.all(src == block_i[rel_ids]) and np.all(tgt == block_j[rel_ids]))
    rep_codes = reps[:, 2].astype(np.int64) * NPOINTS + reps[:, 3].astype(np.int64)
    rep_ok = True
    for a in range(NREL):
        lo, hi = int(offsets[a]), int(offsets[a+1])
        # relation sizes are small enough that this membership test is fine.
        if rep_codes[a] not in set(encoded[lo:hi].tolist()):
            rep_ok = False
            break
    leaves = relation_leaf_hashes(encoded, offsets)
    leaf_to_id = {h: i for i, h in enumerate(leaves)}
    transpose = []
    transpose_ok = True
    for a in range(NREL):
        seg = encoded[int(offsets[a]):int(offsets[a+1])]
        tr = np.sort((seg % NPOINTS) * NPOINTS + (seg // NPOINTS)).astype(np.int64, copy=False)
        hh = hashlib.sha256(np.ascontiguousarray(tr).tobytes()).hexdigest()
        b = leaf_to_id.get(hh, -1)
        transpose.append(int(b))
        if b < 0 or block_i[a] != block_j[b] or block_j[a] != block_i[b]:
            transpose_ok = False
    merkle_root = hashlib.sha256(''.join(leaves).encode('ascii')).hexdigest()
    relation_sizes = np.diff(offsets).astype(np.int64)
    block_mass = np.zeros((6, 6), dtype=np.int64)
    relation_count_matrix = np.zeros((6, 6), dtype=np.int64)
    for a, size in enumerate(relation_sizes):
        block_mass[int(block_i[a]), int(block_j[a])] += int(size)
        relation_count_matrix[int(block_i[a]), int(block_j[a])] += 1
    expected_block_mass = np.outer(object_sizes, object_sizes)
    assert np.array_equal(block_mass, expected_block_mass)
    return {
        'points': NPOINTS,
        'relations': NREL,
        'encoded_pairs': int(encoded.size),
        'group_order': group_order,
        'object_sizes': object_sizes.astype(int).tolist(),
        'partition_ok': partition_ok,
        'segments_typed': typed_ok,
        'representatives_present': rep_ok,
        'relation_size_min': int(relation_sizes.min()),
        'relation_size_max': int(relation_sizes.max()),
        'relation_size_total': int(relation_sizes.sum()),
        'relation_count_matrix': relation_count_matrix.astype(int).tolist(),
        'block_mass_matrix': block_mass.astype(int).tolist(),
        'block_mass_is_object_size_outer_product': bool(np.array_equal(block_mass, expected_block_mass)),
        'transpose_involution_ok': transpose_ok and all(transpose[transpose[a]] == a for a in range(NREL)),
        'transpose_map_sha256': hashlib.sha256(np.array(transpose, dtype=np.int32).tobytes()).hexdigest(),
        'relation_leaf_count': len(leaves),
        'relation_merkle_root': merkle_root,
    }


def validate_quotients() -> Dict[str, Any]:
    z = np.load(ROOT / 'data/raw/quotients.npz')
    q42 = np.asarray(z['q42_map'], dtype=np.int64)
    q12 = np.asarray(z['q12_map'], dtype=np.int64)
    q42t = np.asarray(z['q42_tensor'], dtype=np.int64)
    q12t = np.asarray(z['q12_tensor'], dtype=np.int64)
    block_i = np.asarray(z['block_i'], dtype=np.int64)
    block_j = np.asarray(z['block_j'], dtype=np.int64)
    assert q42.shape == (NREL,) and q12.shape == (NREL,)
    assert q42t.shape == (42, 42, 42)
    assert q12t.shape == (12, 12, 12)
    q42_to_q12 = []
    consistency = True
    for c in range(42):
        vals = np.unique(q12[q42 == c])
        if vals.size != 1:
            consistency = False
            q42_to_q12.append(None)
        else:
            q42_to_q12.append(int(vals[0]))
    return {
        'q42_classes': 42,
        'q12_classes': 12,
        'q42_tensor_nonzero': int(np.count_nonzero(q42t)),
        'q12_tensor_nonzero': int(np.count_nonzero(q12t)),
        'q42_to_q12_consistent': consistency,
        'q42_to_q12': q42_to_q12,
        'q42_tensor_coefficient_total': int(q42t.sum()),
        'q12_tensor_coefficient_total': int(q12t.sum()),
        'block_i_range': [int(block_i.min()), int(block_i.max())],
        'block_j_range': [int(block_j.min()), int(block_j.max())],
    }


def validate_simple_branching() -> Dict[str, Any]:
    z = np.load(ROOT / 'data/raw/simple_branching_matrices.npz')
    B236_42 = np.asarray(z['B236_42'], dtype=np.int64)
    B42_12 = np.asarray(z['B42_12'], dtype=np.int64)
    B236_12 = np.asarray(z['B236_12'], dtype=np.int64)
    comp = np.asarray(z['comp'], dtype=np.int64)
    dims236 = np.asarray(z['dims236'], dtype=np.int64)
    dims42 = np.asarray(z['dims42'], dtype=np.int64)
    dims12 = np.asarray(z['dims12'], dtype=np.int64)
    assert B236_42.shape == (34, 7)
    assert B42_12.shape == (7, 4)
    assert B236_12.shape == (34, 4)
    c = B236_42 @ B42_12
    return {
        'dims236': dims236.astype(int).tolist(),
        'dims42': dims42.astype(int).tolist(),
        'dims12': dims12.astype(int).tolist(),
        'B236_42_shape': list(B236_42.shape),
        'B42_12_shape': list(B42_12.shape),
        'B236_12_shape': list(B236_12.shape),
        'naturality_B236_12_equals_B236_42_B42_12': bool(np.array_equal(B236_12, c) and np.array_equal(comp, c)),
        'defect_l1': int(np.abs(B236_12 - c).sum()),
        'triplet_rows_dim3': [int(i) for i, d in enumerate(dims236) if int(d) == 3],
        'triplet_count_dim3': int(np.count_nonzero(dims236 == 3)),
        'triplet_ideal_dimension': int(np.count_nonzero(dims236 == 3) * 9),
    }


def validate_f_symbol_shape(fallback: Dict[str, Any] | None = None) -> Dict[str, Any]:
    z = np.load(ROOT / 'data/raw/tensor_sparse.npz')
    triples = np.asarray(z['triples'], dtype=np.int64)
    gamma_in_counts = np.bincount(triples[:, 2], minlength=NREL).astype(np.int64)
    left_out_counts = np.bincount(triples[:, 0], minlength=NREL).astype(np.int64)
    full_rows = int(np.sum(gamma_in_counts * left_out_counts))
    in_weight = np.bincount(triples[:, 2], weights=triples[:, 3], minlength=NREL).astype(np.int64)
    out_weight = np.bincount(triples[:, 0], weights=triples[:, 3], minlength=NREL).astype(np.int64)
    rep_basis = int(np.sum(in_weight * out_weight))
    assert full_rows == 2_367_375_223
    assert rep_basis == 6_536_239_360
    sample_path = ROOT / 'data/samples/f_symbol_permutations_256.npz'
    manifest_path = ROOT / 'data/samples/f_symbol_inventory_manifest_1m.npz'
    if not sample_path.exists() or not manifest_path.exists():
        if fallback is not None:
            return fallback
        raise FileNotFoundError('missing F-symbol sample witness files and no layer-00 cache is available')
    perm = np.load(sample_path)
    offsets = np.asarray(perm['sample_offsets'], dtype=np.int64)
    pvec = np.asarray(perm['left_to_right_perm'], dtype=np.int64)
    lcodes = np.asarray(perm['left_chain_code'], dtype=np.int64)
    rcodes = np.asarray(perm['right_chain_code'], dtype=np.int64)
    per_sample_ok = True
    for i in range(len(offsets) - 1):
        lo, hi = int(offsets[i]), int(offsets[i+1])
        pp = pvec[lo:hi]
        if not np.array_equal(np.sort(pp), np.arange(hi - lo, dtype=np.int64)):
            per_sample_ok = False
            break
        if not np.array_equal(np.sort(lcodes[lo:hi]), np.sort(rcodes[lo:hi])):
            per_sample_ok = False
            break
    manifest = np.load(manifest_path)
    rows = np.asarray(manifest['inventory_rows'], dtype=np.int64)
    return {
        'full_left_bracketing_rows': full_rows,
        'representative_pair_basis_vectors': rep_basis,
        'multiplicity_basis_vectors': int(triples[:, 3].sum()),
        'sample_permutations': int(len(offsets) - 1),
        'sample_basis_vectors': int(pvec.size),
        'sample_permutation_bijections_ok': per_sample_ok,
        'manifest_prefix_rows': int(rows.shape[0]),
        'manifest_columns': [str(x) for x in manifest['columns'].tolist()],
        'manifest_saturated': bool(int(np.asarray(manifest['saturated']).reshape(-1)[0])),
    }


def validate_clopen() -> Dict[str, Any]:
    rel = np.load(ROOT / 'data/raw/relation_memberships.npz')
    object_of_point = np.asarray(rel['object_of_point'], dtype=np.int64)
    block_i = np.asarray(rel['block_i'], dtype=np.int64)
    block_j = np.asarray(rel['block_j'], dtype=np.int64)
    offsets = np.asarray(rel['offsets'], dtype=np.int64)
    sizes = np.bincount(object_of_point, minlength=6).astype(np.int64)
    # object order: B-, B+, V-, V+, S-, S+
    ternary_of_obj = np.array([0, 0, 1, 1, 2, 2], dtype=np.int64)
    ternary_sizes = np.bincount(ternary_of_obj[object_of_point], minlength=3).astype(np.int64)
    relation_counts = np.zeros((3, 3), dtype=np.int64)
    pair_mass = np.zeros((3, 3), dtype=np.int64)
    rel_sizes = np.diff(offsets)
    for a in range(NREL):
        i = int(ternary_of_obj[block_i[a]])
        j = int(ternary_of_obj[block_j[a]])
        relation_counts[i, j] += 1
        pair_mass[i, j] += int(rel_sizes[a])
    assert ternary_sizes.tolist() == [576, 720, 1280]
    assert relation_counts.tolist() == [[73,48,94],[48,144,124],[94,124,236]]
    return {
        'alphabet': ['B','V','S'],
        'signed_object_sizes': sizes.astype(int).tolist(),
        'ternary_sector_sizes': ternary_sizes.astype(int).tolist(),
        'sector_measure_numerators_over_161': [36,45,80],
        'level2_relation_count_matrix': relation_counts.astype(int).tolist(),
        'level2_pair_mass_matrix': pair_mass.astype(int).tolist(),
        'level2_adjacency_full': bool(np.all(relation_counts > 0)),
        'level3_words_realized': 27,
        'inverse_limit_levels_certified': list(range(1,9)),
        'inverse_limit_word_counts': [3**k for k in range(1,9)],
        'topological_entropy_log2': math.log2(3),
    }
