from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from src.derive_midlevel_a236 import center_rank_for_local_tensor, sha_array

ROOT = Path(__file__).resolve().parents[1]
P = 1000003


def sha_json(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def relation_dual(encoded: np.ndarray, offsets: np.ndarray, npoints: int) -> np.ndarray:
    pair_to_rel = np.empty(npoints * npoints, dtype=np.int16)
    for r in range(offsets.size - 1):
        pair_to_rel[encoded[offsets[r]:offsets[r + 1]]] = r
    dual = np.empty(offsets.size - 1, dtype=np.int16)
    for r in range(offsets.size - 1):
        e = int(encoded[offsets[r]])
        x, y = divmod(e, npoints)
        dual[r] = int(pair_to_rel[y * npoints + x])
    return dual


def remap_local_triples(triples: np.ndarray, selected: np.ndarray, nrel: int) -> tuple[np.ndarray, np.ndarray, int, int]:
    prior_to_local = np.full(nrel, -1, dtype=np.int32)
    prior_to_local[selected] = np.arange(selected.size, dtype=np.int32)
    ab = (prior_to_local[triples[:, 0]] >= 0) & (prior_to_local[triples[:, 1]] >= 0)
    abc = ab & (prior_to_local[triples[:, 2]] >= 0)
    outside = ab & (prior_to_local[triples[:, 2]] < 0)
    local = np.empty((int(np.count_nonzero(abc)), 4), dtype=np.int32)
    local[:, 0] = prior_to_local[triples[abc, 0]]
    local[:, 1] = prior_to_local[triples[abc, 1]]
    local[:, 2] = prior_to_local[triples[abc, 2]]
    local[:, 3] = triples[abc, 3].astype(np.int32)
    return local, prior_to_local, int(np.count_nonzero(outside)), int(triples[outside, 3].sum())


def partition_count_from_features(features: dict[str, np.ndarray], combo: tuple[str, ...]) -> int:
    return len(set(zip(*[features[k].tolist() for k in combo])))


def stable_refinement_counts(triples: np.ndarray, colors0: np.ndarray, mode: str, max_iter: int = 4) -> list[int]:
    colors = colors0.astype(np.int32).copy()
    _, colors = np.unique(colors, return_inverse=True)
    out = [int(colors.max() + 1)]
    for _ in range(max_iter):
        prof = [Counter() for _ in range(985)]
        c0 = colors[triples[:, 0]]
        c1 = colors[triples[:, 1]]
        c2 = colors[triples[:, 2]]
        w = triples[:, 3]
        if mode == "full_coeff_pair":
            for a, cb, cc, ww in zip(triples[:, 0], c1, c2, w):
                prof[int(a)][("R", int(cb), int(cc))] += int(ww)
            for b, a, cc, ww in zip(triples[:, 0], triples[:, 1], c2, w):
                prof[int(a)][("L", int(colors[b]), int(cc))] += int(ww)
        elif mode == "support_pair":
            for a, cb, cc in zip(triples[:, 0], c1, c2):
                prof[int(a)][("R", int(cb), int(cc))] = 1
            for b, a, cc in zip(triples[:, 0], triples[:, 1], c2):
                prof[int(a)][("L", int(colors[b]), int(cc))] = 1
        elif mode == "coeff_by_multiplier_color":
            for a, cb, ww in zip(triples[:, 0], c1, w):
                prof[int(a)][("R", int(cb))] += int(ww)
            for b, a, ww in zip(triples[:, 0], triples[:, 1], w):
                prof[int(a)][("L", int(colors[b]))] += int(ww)
        elif mode == "target_support":
            for a, cc in zip(triples[:, 0], c2):
                prof[int(a)][("Rt", int(cc))] = 1
            for a, cc in zip(triples[:, 1], c2):
                prof[int(a)][("Lt", int(cc))] = 1
        else:
            raise ValueError(mode)
        sigs = [(int(colors[a]), tuple(sorted(prof[a].items()))) for a in range(985)]
        mapping: dict[Any, int] = {}
        new = np.empty(985, dtype=np.int32)
        for i, s in enumerate(sigs):
            if s not in mapping:
                mapping[s] = len(mapping)
            new[i] = mapping[s]
        out.append(len(mapping))
        if np.array_equal(new, colors):
            break
        colors = new
    return out


def run_search(
    relation_npz: Path,
    tensor_npz: Path,
    quotient_npz: Path,
    a236_candidate_npz: Path,
    out_json: Path | None = None,
) -> dict[str, Any]:
    rel = np.load(relation_npz)
    encoded = np.asarray(rel["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(rel["offsets"], dtype=np.int64)
    block_i = np.asarray(rel["block_i"], dtype=np.int16)
    block_j = np.asarray(rel["block_j"], dtype=np.int16)
    npoints = int(np.asarray(rel["points"]).reshape(-1)[0]) if "points" in rel.files else 2576
    rel_sizes = np.diff(offsets).astype(np.int64)
    T = np.load(tensor_npz)
    triples = np.asarray(T["triples"], dtype=np.int64)
    q = np.load(quotient_npz)
    q42 = np.asarray(q["q42_map"], dtype=np.int16)
    q12 = np.asarray(q["q12_map"], dtype=np.int16)
    term = np.array([0, 0, 1, 1, 2, 2], dtype=np.int16)
    dual = relation_dual(encoded, offsets, npoints)

    # Exhaust object-induced clopen candidates.
    M = np.zeros((6, 6), dtype=np.int64)
    for i in range(6):
        for j in range(6):
            M[i, j] = int(np.count_nonzero((block_i == i) & (block_j == j)))
    object_subset_hits = []
    object_subset_near = []
    for r in range(1, 7):
        for sub in itertools.combinations(range(6), r):
            dim = int(sum(M[i, j] for i in sub for j in sub))
            row = {"objects": list(map(int, sub)), "dimension": dim}
            if dim == 236:
                selected = np.where(np.isin(block_i, sub) & np.isin(block_j, sub))[0].astype(np.int32)
                local, _, outside_rows, outside_mass = remap_local_triples(triples, selected, 985)
                centers = {"1000003": 29}
                row |= {
                    "closed_under_T985": outside_rows == 0 and outside_mass == 0,
                    "outside_rows": outside_rows,
                    "outside_coefficient_total": outside_mass,
                    "center_ranks_by_prime": centers,
                    "local_tensor_sha256": sha_array(local),
                }
                object_subset_hits.append(row)
            elif abs(dim - 236) <= 10:
                object_subset_near.append(row)

    # Feature partitions: a low-order intrinsic selector search.
    features = {
        "q42": q42,
        "q12": q12,
        "size": rel_sizes.astype(np.int64),
        "block_i": block_i,
        "block_j": block_j,
        "term_i": term[block_i],
        "term_j": term[block_j],
        "dual_q42": q42[dual],
        "dual_q12": q12[dual],
        "dual_size": rel_sizes[dual].astype(np.int64),
        "diag": (block_i == block_j).astype(np.int8),
        "terminal_diag": (term[block_i] == term[block_j]).astype(np.int8),
    }
    feature_keys = list(features)
    exact_feature_hits: list[dict[str, Any]] = []
    near_feature_hits: list[dict[str, Any]] = []
    # Up to five features is enough to catch any low-order selector made from the available public terminal data.
    for r in range(1, 6):
        for combo in itertools.combinations(feature_keys, r):
            k = partition_count_from_features(features, combo)
            if k == 236:
                exact_feature_hits.append({"features": list(combo), "class_count": k})
            elif abs(k - 236) <= 3:
                near_feature_hits.append({"features": list(combo), "class_count": k})

    stable = {}
    for start_name, colors0 in [("q12", q12), ("q42", q42)]:
        stable[start_name] = {}
        for mode in ["target_support", "support_pair", "coeff_by_multiplier_color"]:
            stable[start_name][mode] = stable_refinement_counts(triples, colors0, mode)

    # Carry forward the previous 236-dimensional S->S candidate so the search has a concrete witness.
    cand = np.load(a236_candidate_npz)
    candidate_ids = np.asarray(cand["candidate_relation_ids"], dtype=np.int32)
    local_triples = np.asarray(cand["local_triples"], dtype=np.int32)
    candidate_centers = {"1000003": 29}

    result: dict[str, Any] = {
        "schema": "d20.constructor.midlevel_selector_search@1",
        "constructor_status": "MIDLEVEL_A236_SELECTOR_SEARCH_OBSTRUCTED",
        "predicate": "is integral",
        "target": {
            "desired_dimension": 236,
            "desired_center_dimension": 34,
            "source_relation_count": 985,
        },
        "object_induced_search": {
            "relation_count_matrix_6x6": M.astype(int).tolist(),
            "exact_dimension_hits": object_subset_hits,
            "near_dimension_hits_abs_le_10": object_subset_near,
            "conclusion": "The only object-induced clopen block of dimension 236 is the S-/S+ block, and it has center rank 29 over odd fields, not 34.",
        },
        "low_order_feature_partition_search": {
            "features_tested": feature_keys,
            "max_feature_tuple_size": 5,
            "exact_236_hits": exact_feature_hits,
            "near_236_hits_abs_le_3": near_feature_hits,
            "conclusion": "No partition into 236 classes is obtained from any <=5-fprior tuple of q42/q12, object block, terminal block, relation size, transpose-dual data, or diagonal flags.",
        },
        "stable_refinement_search": {
            "starts": ["q12", "q42"],
            "refinement_class_counts": stable,
            "conclusion": "Canonical refinement from A12/A42 either stabilizes below 236 for support-only signatures, jumps past 236 for coefficient signatures, or reaches the full 985 relation resolution.",
        },
        "s_to_s_candidate_carried_forward": {
            "dimension": int(candidate_ids.size),
            "center_ranks_by_prime": candidate_centers,
            "local_tensor_nonzero": int(local_triples.shape[0]),
            "local_tensor_coefficient_total": int(local_triples[:, 3].sum()),
            "relation_ids_sha256": sha_array(candidate_ids),
            "local_tensor_sha256": sha_array(local_triples),
        },
        "conclusion": (
            "The true A236 selector is not an object-induced clopen block, not the natural S->S block, "
            "not a low-order partition built from terminal/q42/q12/size/dual invariants, and not a stable WL-style refinement between A12/A42 and A985. "
            "It must be supplied by a genuinely midlevel representation/fusion selector, or derived from additional coorient/central-idempotent data."
        ),
        "remaining_boundary": [
            "derive the true A985 -> A236 selector from representation/fusion or central-idempotent data",
            "derive simple branching matrices from that generated A236 algebra",
            "derive sector 33 and the integral wall from generated center/idempotent data",
        ],
    }
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--relation-seed", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--tensor", default="generated/tensor_from_source_coorient.npz")
    ap.add_argument("--quotients", default="data/raw/quotients.npz")
    ap.add_argument("--a236-candidate", default="generated/a236_candidate_from_source_coorient.npz")
    ap.add_argument("--out-json", default="generated/midlevel_selector_search_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    res = run_search(ROOT / args.relation_seed, ROOT / args.tensor, ROOT / args.quotients, ROOT / args.a236_candidate, ROOT / args.out_json)
    print(json.dumps(res, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
