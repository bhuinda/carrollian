from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import csr_matrix

ROOT = Path(__file__).resolve().parents[1]


def sha_bytes(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_relation_seed(path: Path) -> dict[str, Any]:
    z = np.load(path)
    return {
        "encoded_pairs": np.asarray(z["encoded_pairs"], dtype=np.int64),
        "offsets": np.asarray(z["offsets"], dtype=np.int64),
        "object_of_point": np.asarray(z["object_of_point"], dtype=np.int16),
        "reps": np.asarray(z["reps"], dtype=np.int32),
        "block_i": np.asarray(z["block_i"], dtype=np.int16),
        "block_j": np.asarray(z["block_j"], dtype=np.int16),
        "points": int(np.asarray(z["points"]).reshape(-1)[0]),
        "group_order": int(np.asarray(z["group_order"]).reshape(-1)[0]),
    }


def build_label_matrix(encoded: np.ndarray, offsets: np.ndarray, n: int, relation_count: int) -> np.ndarray:
    labels = np.empty(n * n, dtype=np.int16)
    for a in range(relation_count):
        labels[encoded[offsets[a] : offsets[a + 1]]] = a
    return labels.reshape(n, n)


def build_relation_matrices(encoded: np.ndarray, offsets: np.ndarray, n: int, relation_count: int) -> list[csr_matrix]:
    mats: list[csr_matrix] = []
    for a in range(relation_count):
        e = encoded[offsets[a] : offsets[a + 1]]
        rows = e // n
        cols = e % n
        data = np.ones(e.size, dtype=np.int8)
        mats.append(csr_matrix((data, (rows, cols)), shape=(n, n), dtype=np.int16))
    return mats


def compute_tensor_from_orbitals(
    relation_seed: Path,
    out_npz: Path | None = None,
    compare_npz: Path | None = None,
    sample_limit: int | None = None,
    progress: bool = False,
) -> dict[str, Any]:
    """Rebuild T985 from an ordered-pair orbital partition.

    This uses the coherent-configuration representative formula.  For each target
    orbital gamma, choose one representative pair (x,y) in R_gamma and count

        p^gamma_{alpha,beta} = #{z : (x,z) in R_alpha and (z,y) in R_beta}.

    That is exactly the two-step incidence definition, but it is O(|R|*|X|)
    rather than multiplying all relation matrices.
    """
    t0 = time.time()
    seed = load_relation_seed(relation_seed)
    encoded = seed["encoded_pairs"]
    offsets = seed["offsets"]
    n = seed["points"]
    r = offsets.size - 1
    block_i = seed["block_i"]
    block_j = seed["block_j"]

    if encoded.size != n * n:
        raise ValueError(f"encoded pair partition has {encoded.size}, expected {n*n}")

    labels = build_label_matrix(encoded, offsets, n, r)
    prep_time = time.time() - t0

    gammas = range(r) if sample_limit is None else range(min(sample_limit, r))
    triples: list[tuple[int, int, int, int]] = []
    t1 = time.time()
    block_mismatch = 0
    for count, g in enumerate(gammas, start=1):
        e = int(encoded[offsets[g]])
        x = e // n
        y = e % n
        alpha = labels[x, :].astype(np.int64, copy=False)
        beta = labels[:, y].astype(np.int64, copy=False)
        keys = alpha * r + beta
        hist = np.bincount(keys, minlength=r * r)
        nz = np.nonzero(hist)[0]
        gi = int(block_i[g])
        gj = int(block_j[g])
        for key in nz:
            a = int(key // r)
            b = int(key % r)
            coeff = int(hist[key])
            if coeff == 0:
                continue
            if int(block_i[a]) != gi or int(block_j[a]) != int(block_i[b]) or int(block_j[b]) != gj:
                block_mismatch += 1
            triples.append((a, b, int(g), coeff))
        if progress and (count % 100 == 0):
            print(json.dumps({"gammas": count, "triples": len(triples), "elapsed": round(time.time()-t1, 3)}), flush=True)

    triples_arr = np.array(triples, dtype=np.int32)
    if triples_arr.size:
        order = np.lexsort((triples_arr[:, 2], triples_arr[:, 1], triples_arr[:, 0]))
        triples_arr = triples_arr[order]
    else:
        triples_arr = triples_arr.reshape(0, 4)

    if out_npz is not None:
        out_npz.parent.mkdir(parents=True, exist_ok=True)
        M = np.zeros((6, 6), dtype=np.int64)
        for a in range(r):
            M[int(block_i[a]), int(block_j[a])] += 1
        np.savez(out_npz, triples=triples_arr, M=M, reps=seed["reps"])

    comparison: dict[str, Any] = {}
    if compare_npz is not None and compare_npz.exists():
        z = np.load(compare_npz)
        supplied = np.asarray(z["triples"], dtype=np.int32)
        supplied_order = np.lexsort((supplied[:, 2], supplied[:, 1], supplied[:, 0]))
        supplied = supplied[supplied_order]
        comparison = {
            "supplied_triples": int(supplied.shape[0]),
            "supplied_coefficient_total": int(supplied[:, 3].sum()),
            "supplied_sha256": sha_bytes(supplied),
            "matches_supplied_tensor": bool(np.array_equal(triples_arr, supplied)) if sample_limit is None else None,
        }
        if sample_limit is not None:
            mask = supplied[:, 2] < min(sample_limit, r)
            sub = supplied[mask]
            comparison["sample_supplied_restricted_triples"] = int(sub.shape[0])
            comparison["sample_matches_supplied_restriction"] = bool(np.array_equal(triples_arr, sub))

    coeff_total = int(triples_arr[:, 3].sum()) if triples_arr.size else 0
    source_name = str(relation_seed)
    if "source_coorient" in source_name:
        method = "representative two-step incidence over source+coorient generated ordered-pair orbitals"
        boundary = "uses generated relation membership from fixed coorient generators; compare_npz is used only for equality checking when supplied"
    else:
        method = "representative two-step incidence over supplied ordered-pair orbitals"
        boundary = "uses supplied ordered-pair orbital partition; does not construct Be3 from coorient generators"

    result = {
        "schema": "d20.constructor.orbitals_to_tensor@1",
        "constructor_status": "ORBITALS_TO_TENSOR_PASS" if block_mismatch == 0 else "ORBITALS_TO_TENSOR_BLOCK_FAILURE",
        "construction_method": method,
        "input_boundary": boundary,
        "predicate": "is integral",
        "points": int(n),
        "relations": int(r),
        "group_order_from_orbital_seed": int(seed["group_order"]),
        "ordered_pair_partition_size": int(encoded.size),
        "target_orbitals_processed": int(min(sample_limit, r) if sample_limit is not None else r),
        "tensor_support": int(triples_arr.shape[0]),
        "coefficient_total": coeff_total,
        "block_mismatches": int(block_mismatch),
        "tensor_sha256": sha_bytes(triples_arr),
        "prep_seconds": round(prep_time, 6),
        "compute_seconds": round(time.time() - t1, 6),
        "total_seconds": round(time.time() - t0, 6),
        "comparison": comparison,
        "output_npz": str(out_npz.relative_to(ROOT)) if out_npz is not None and out_npz.exists() else None,
    }
    body = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["constructor_result_sha256"] = hashlib.sha256(body).hexdigest()
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Rebuild the A985 multiplication tensor from supplied ordered-pair orbitals by two-step incidence.")
    ap.add_argument("--relation-seed", default="data/raw/relation_memberships.npz")
    ap.add_argument("--compare", default="data/raw/tensor_sparse.npz")
    ap.add_argument("--out-npz", default="generated/tensor_from_orbitals.npz")
    ap.add_argument("--out-json", default="generated/orbitals_to_tensor_report.json")
    ap.add_argument("--sample-limit", type=int, default=None)
    ap.add_argument("--progress", action="store_true")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    result = compute_tensor_from_orbitals(
        ROOT / args.relation_seed,
        ROOT / args.out_npz if args.out_npz else None,
        ROOT / args.compare if args.compare else None,
        args.sample_limit,
        args.progress,
    )
    out_json = ROOT / args.out_json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
