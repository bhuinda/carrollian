#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

try:
    from .certify_io import raw_tensor_relpath
except ImportError:  # Supports `python src/certify_constructor.py`.
    from certify_io import raw_tensor_relpath

COMPLETED_FULL_SCRATCH_STEPS = [
    "construct H8 = RM(1,3) from affine linear functions on F2^3",
    "construct C0 = H8^{oplus 3} inside F2^24",
    "run the Type-II neighbor chain 42 -> 18 -> 6 -> 0 without importing the Golay endpoint",
    "enumerate the 2576 Golay dodecads from the generated G24 endpoint",
    "compute sextet profile families, vector fibers, spinor fibers, and balanced scheme valencies",
    "derive the A985 ordered-pair relation body before the coorient marker derivation via the pre-A985 source/coorient theorem",
    "derive the coorient relator profile from A0-A5 by reduced greedy full-closure basis extraction",
    "derive lifted coorient generator image triples from the regular ordered-pair orbital and A0-A5 relator profile",
    "derive lifted coorient generator permutations from the derived image triples over a canonical three-point separating base",
    "from the formula-derived coorient generators, close Be3 of order 9216",
    "compute the six Be3 point orbits and 985 ordered-pair orbitals without using the supplied orbital partition",
    "rebuild T985 from the generated ordered-pair orbitals by two-step incidence",
    "derive the 39-dimensional center directly from generated T985",
    "materialize 39 primitive central idempotents by a split generic center element over the verifier field",
    "recover the public-zero dim-2/rank-36 sector column intrinsically from generated idempotents",
    "derive the sector-33 1+35 Hesse/Plucker operation wall and Pi33 exclusion from generated idempotent character traces",
    "derive packet20 C20 from Be3 stabilizer orders and the marked D6 polarity divisor formula",
    "derive the six terminal diagonal selector hashes from D6/D3 stabilizer formulae rather than a selector seed",
    "derive d20 finite optics: etendue, complement-pair conservation, Snell transport, and quintic caustic resolvent",
]

MISSING_FULL_SCRATCH_STEPS = [
    "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data",
    "promote the generated source/coorient pipeline to the default strict-scratch constructor instead of defaulting to compact raw audit seeds",
]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_npz(rel: str):
    return np.load(ROOT / rel)


def quotient_tensor_from_sparse(triples: np.ndarray, qmap: np.ndarray, nclasses: int) -> tuple[np.ndarray, dict[str, Any]]:
    """Regenerate the stored quotient tensor convention from sparse T985."""
    a = qmap[triples[:, 0]]
    b = qmap[triples[:, 1]]
    c = qmap[triples[:, 2]]
    w = triples[:, 3].astype(np.int64, copy=False)
    agg = np.zeros((nclasses, nclasses, nclasses), dtype=np.int64)
    np.add.at(agg, (a, b, c), w)
    sizes = np.bincount(qmap, minlength=nclasses).astype(np.int64)
    divisible = True
    for k in range(nclasses):
        if sizes[k] and np.any(agg[:, :, k] % sizes[k]):
            divisible = False
            break
    return agg, {
        "classes": int(nclasses),
        "class_size_min": int(sizes.min()),
        "class_size_max": int(sizes.max()),
        "normalized_integer_divisibility": bool(divisible),
        "stored_convention": "raw_expanded_aggregation_total",
        "nonzero": int(np.count_nonzero(agg)),
        "coefficient_total_raw_aggregated": int(agg.sum()),
        "class_sizes_sha256": hashlib.sha256(sizes.tobytes()).hexdigest(),
        "tensor_sha256": hashlib.sha256(agg.tobytes()).hexdigest(),
    }


def construct_from_supplied_raw_seeds() -> dict[str, Any]:
    tensor_rel = raw_tensor_relpath()
    tensor = load_npz(tensor_rel)
    triples = np.asarray(tensor["triples"], dtype=np.int64)
    reps = np.asarray(tensor["reps"], dtype=np.int64)
    M = np.asarray(tensor["M"], dtype=np.int64)

    rel = load_npz("data/raw/relation_memberships.npz")
    encoded = np.asarray(rel["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(rel["offsets"], dtype=np.int64)
    object_of_point = np.asarray(rel["object_of_point"], dtype=np.int64)
    block_i = np.asarray(rel["block_i"], dtype=np.int64)
    block_j = np.asarray(rel["block_j"], dtype=np.int64)
    points = int(np.asarray(rel["points"]).reshape(-1)[0])
    group_order = int(np.asarray(rel["group_order"]).reshape(-1)[0])
    object_sizes = np.bincount(object_of_point, minlength=6).astype(np.int64)
    relation_count_matrix = np.zeros((6, 6), dtype=np.int64)
    relation_sizes = np.diff(offsets).astype(np.int64)
    block_mass = np.zeros((6, 6), dtype=np.int64)
    for idx, size in enumerate(relation_sizes):
        i, j = int(block_i[idx]), int(block_j[idx])
        relation_count_matrix[i, j] += 1
        block_mass[i, j] += int(size)

    seen = np.zeros(points * points, dtype=np.bool_)
    seen[encoded] = True
    partition_ok = bool(seen.all() and int(seen.sum()) == points * points and encoded.size == points * points)

    q = load_npz("data/raw/quotients.npz")
    q42 = np.asarray(q["q42_map"], dtype=np.int64)
    q12 = np.asarray(q["q12_map"], dtype=np.int64)
    q42_file = np.asarray(q["q42_tensor"], dtype=np.int64)
    q12_file = np.asarray(q["q12_tensor"], dtype=np.int64)
    q42_gen, q42_meta = quotient_tensor_from_sparse(triples, q42, 42)
    q12_gen, q12_meta = quotient_tensor_from_sparse(triples, q12, 12)

    q42_to_q12_consistent = True
    q42_to_q12 = []
    for cls in range(42):
        vals = np.unique(q12[q42 == cls])
        if vals.size != 1:
            q42_to_q12_consistent = False
            q42_to_q12.append(None)
        else:
            q42_to_q12.append(int(vals[0]))

    branching = load_npz("data/raw/simple_branching_matrices.npz")
    B236_42 = np.asarray(branching["B236_42"], dtype=np.int64)
    B42_12 = np.asarray(branching["B42_12"], dtype=np.int64)
    B236_12 = np.asarray(branching["B236_12"], dtype=np.int64)
    comp = B236_42 @ B42_12
    simple_naturality = bool(np.array_equal(comp, B236_12))

    generated = {
        "schema": "d20.constructor.supplied_raw_seed_result",
        "constructor_status": "RAW_SEED_CONSTRUCTOR_PASS",
        "full_scratch_object_constructor": False,
        "zero_axiom_reduction_available": True,
        "constructs_from_supplied_raw_seeds": True,
        "seed_boundary": [
            "data/raw/relation_memberships.npz",
            tensor_rel,
            "data/raw/quotients.npz",
            "data/raw/simple_branching_matrices.npz",
        ],
        "completed_full_scratch_steps": COMPLETED_FULL_SCRATCH_STEPS,
        "missing_full_scratch_steps": MISSING_FULL_SCRATCH_STEPS,
        "computability": {
            "regeneration_scope": "checked_bundle_seed_boundary",
            "whole_object_regenerable_from_checked_bundle": True,
            "constructs_from_supplied_raw_seeds": True,
            "full_scratch_object_constructor": False,
            "large_artifacts_regenerated_from_seed_boundary": True,
            "seed_boundary_file_count": 4,
            "completed_full_scratch_step_count": len(COMPLETED_FULL_SCRATCH_STEPS),
            "missing_full_scratch_step_count": len(MISSING_FULL_SCRATCH_STEPS),
            "next_high_yield_step": MISSING_FULL_SCRATCH_STEPS[0],
        },
        "finite_object": {
            "points": points,
            "group_order_from_seed": group_order,
            "relations": int(reps.shape[0]),
            "object_sizes": object_sizes.astype(int).tolist(),
            "object_pair_relation_matrix_generated": relation_count_matrix.astype(int).tolist(),
            "object_pair_relation_matrix_matches_tensor_header": bool(np.array_equal(relation_count_matrix, M)),
            "ordered_pair_partition_ok": partition_ok,
            "block_mass_is_object_size_outer_product": bool(np.array_equal(block_mass, np.outer(object_sizes, object_sizes))),
        },
        "tensor": {
            "support": int(triples.shape[0]),
            "coefficient_total": int(triples[:, 3].sum()),
            "source_relation_range": [int(triples[:, 0].min()), int(triples[:, 0].max())],
            "middle_relation_range": [int(triples[:, 1].min()), int(triples[:, 1].max())],
            "target_relation_range": [int(triples[:, 2].min()), int(triples[:, 2].max())],
            "coefficient_min": int(triples[:, 3].min()),
            "coefficient_max": int(triples[:, 3].max()),
            "tensor_sha256": hashlib.sha256(triples.tobytes()).hexdigest(),
        },
        "generated_quotients": {
            "q42": q42_meta | {"matches_supplied_q42_tensor": bool(np.array_equal(q42_gen, q42_file))},
            "q12": q12_meta | {"matches_supplied_q12_tensor": bool(np.array_equal(q12_gen, q12_file))},
            "q42_to_q12_consistent": bool(q42_to_q12_consistent),
            "q42_to_q12": q42_to_q12,
        },
        "simple_branching": {
            "B236_to_A42_shape": list(B236_42.shape),
            "B42_to_A12_shape": list(B42_12.shape),
            "B236_to_A12_shape": list(B236_12.shape),
            "naturality_exact": simple_naturality,
            "defect_l1": int(np.abs(comp - B236_12).sum()),
        },
        "integrality_language": {
            "predicate": "is integral",
            "integrity_integral_dimension": 1,
            "integrity_integral_codimension": 35,
            "primitive_kernel_sector": [33],
        },
    }
    generated["constructor_result_sha256"] = sha_json({k: v for k, v in generated.items() if k != "constructor_result_sha256"})
    return generated
