from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np

from .certify_constructor import stable_constructor_sha_json
from .generate_source import source_constructor_certificate

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OBJECT_SIZES_BY_LABEL = [384, 192, 144, 576, 512, 768]
EXPECTED_SORTED_OBJECT_SIZES = sorted(EXPECTED_OBJECT_SIZES_BY_LABEL)
EXPECTED_GROUP_ORDER = 9216
EXPECTED_RELATIONS = 985
EXPECTED_POINTS = 2576


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def validate_permutation_rows(gens: np.ndarray, n: int) -> None:
    target = np.arange(n, dtype=np.int64)
    for i, g in enumerate(gens):
        if g.shape != (n,):
            raise ValueError(f"generator {i} has shape {g.shape}, expected {(n,)}")
        if not np.array_equal(np.sort(g.astype(np.int64)), target):
            raise ValueError(f"generator {i} is not a permutation of 0..{n-1}")


def invert_perm(p: np.ndarray) -> np.ndarray:
    inv = np.empty_like(p)
    inv[p] = np.arange(p.size, dtype=p.dtype)
    return inv


def close_group(generators: np.ndarray) -> tuple[np.ndarray, list[int]]:
    n = generators.shape[1]
    idp = np.arange(n, dtype=np.int16)
    gen_list: list[np.ndarray] = []
    for g in generators.astype(np.int16, copy=False):
        gen_list.append(g)
        gen_list.append(invert_perm(g))
    seen: dict[bytes, int] = {idp.tobytes(): 0}
    perms: list[np.ndarray] = [idp]
    q: deque[np.ndarray] = deque([idp])
    closure_sizes: list[int] = []
    while q:
        p = q.popleft()
        for g in gen_list:
            c = g[p]
            b = c.tobytes()
            if b not in seen:
                seen[b] = len(perms)
                cp = c.copy()
                perms.append(cp)
                q.append(cp)
        # keep a tiny progress fingerprint without printing
        if len(closure_sizes) == 0 or len(perms) >= closure_sizes[-1] * 2:
            closure_sizes.append(len(perms))
    return np.vstack(perms).astype(np.int16, copy=False), closure_sizes


def point_orbits(P: np.ndarray) -> tuple[np.ndarray, list[list[int]], list[int]]:
    n = P.shape[1]
    used = np.zeros(n, dtype=np.bool_)
    raw_orbits: list[np.ndarray] = []
    for x in range(n):
        if used[x]:
            continue
        orb = np.unique(P[:, x]).astype(np.int32)
        used[orb.astype(np.int64)] = True
        raw_orbits.append(orb)
    sizes = sorted(int(o.size) for o in raw_orbits)
    object_of_point = np.empty(n, dtype=np.int16)
    size_to_label = {size: label for label, size in enumerate(EXPECTED_OBJECT_SIZES_BY_LABEL)}
    for orb in raw_orbits:
        size = int(orb.size)
        label = size_to_label.get(size)
        if label is None:
            # Fallback for nonstandard actions: deterministic by increasing orbit minimum.
            label = len(size_to_label)
            size_to_label[size] = label
        object_of_point[orb.astype(np.int64)] = int(label)
    return object_of_point, [o.astype(int).tolist() for o in raw_orbits], sizes


def pair_orbits(P: np.ndarray, object_of_point: np.ndarray) -> dict[str, Any]:
    n = P.shape[1]
    N = n * n
    visited = np.zeros(N, dtype=np.bool_)
    encoded_segments: list[np.ndarray] = []
    reps: list[tuple[int, int, int, int, int]] = []
    block_i: list[int] = []
    block_j: list[int] = []
    t0 = time.time()
    while True:
        remaining = np.flatnonzero(~visited)
        if remaining.size == 0:
            break
        rep_code = int(remaining[0])
        x = rep_code // n
        y = rep_code % n
        orbit = np.unique(P[:, x].astype(np.int64) * n + P[:, y].astype(np.int64))
        visited[orbit] = True
        a = len(encoded_segments)
        bi = int(object_of_point[x])
        bj = int(object_of_point[y])
        encoded_segments.append(orbit.astype(np.int64, copy=False))
        block_i.append(bi)
        block_j.append(bj)
        reps.append((bi, bj, int(x), int(y), int(orbit.size)))
    offsets = np.zeros(len(encoded_segments) + 1, dtype=np.int64)
    pos = 0
    for i, seg in enumerate(encoded_segments):
        offsets[i] = pos
        pos += int(seg.size)
    offsets[len(encoded_segments)] = pos
    encoded = np.concatenate(encoded_segments).astype(np.int64, copy=False)
    return {
        "encoded_pairs": encoded,
        "offsets": offsets,
        "reps": np.array(reps, dtype=np.int32),
        "block_i": np.array(block_i, dtype=np.int16),
        "block_j": np.array(block_j, dtype=np.int16),
        "orbit_count": len(encoded_segments),
        "pair_orbit_seconds": round(time.time() - t0, 6),
    }


def save_relation_memberships(path: Path, rel: dict[str, Any], object_of_point: np.ndarray, group_order: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        encoded_pairs=rel["encoded_pairs"].astype(np.int64, copy=False),
        offsets=rel["offsets"].astype(np.int64, copy=False),
        object_of_point=object_of_point.astype(np.int16, copy=False),
        reps=rel["reps"].astype(np.int32, copy=False),
        block_i=rel["block_i"].astype(np.int16, copy=False),
        block_j=rel["block_j"].astype(np.int16, copy=False),
        points=np.array([object_of_point.size], dtype=np.int64),
        group_order=np.array([group_order], dtype=np.int64),
    )


def segment_hashes(encoded: np.ndarray, offsets: np.ndarray) -> list[str]:
    out: list[str] = []
    for i in range(offsets.size - 1):
        seg = encoded[int(offsets[i]):int(offsets[i + 1])]
        out.append(hashlib.sha256(np.ascontiguousarray(seg).tobytes()).hexdigest())
    return out


def align_to_supplied(generated: dict[str, Any], supplied_npz: Path) -> dict[str, Any]:
    z = np.load(supplied_npz)
    sup_encoded = np.asarray(z["encoded_pairs"], dtype=np.int64)
    sup_offsets = np.asarray(z["offsets"], dtype=np.int64)
    sup_object = np.asarray(z["object_of_point"], dtype=np.int16)
    sup_reps = np.asarray(z["reps"], dtype=np.int32)
    sup_bi = np.asarray(z["block_i"], dtype=np.int16)
    sup_bj = np.asarray(z["block_j"], dtype=np.int16)

    gen_hash = segment_hashes(generated["encoded_pairs"], generated["offsets"])
    sup_hash = segment_hashes(sup_encoded, sup_offsets)
    sup_lookup = {h: i for i, h in enumerate(sup_hash)}
    gen_to_sup = np.array([sup_lookup.get(h, -1) for h in gen_hash], dtype=np.int32)
    all_match = bool(np.all(gen_to_sup >= 0) and len(set(gen_to_sup.astype(int).tolist())) == len(gen_hash))

    aligned: dict[str, Any] | None = None
    if all_match:
        inverse = np.empty_like(gen_to_sup)
        for gen_i, sup_i in enumerate(gen_to_sup):
            inverse[int(sup_i)] = int(gen_i)
        enc_parts = []
        offsets = np.zeros(len(inverse) + 1, dtype=np.int64)
        pos = 0
        for sup_i, gen_i in enumerate(inverse):
            lo = int(generated["offsets"][gen_i]); hi = int(generated["offsets"][gen_i + 1])
            seg = generated["encoded_pairs"][lo:hi]
            enc_parts.append(seg)
            offsets[sup_i] = pos
            pos += int(seg.size)
        offsets[len(inverse)] = pos
        aligned = {
            "encoded_pairs": np.concatenate(enc_parts).astype(np.int64, copy=False),
            "offsets": offsets,
            # Use generated representative data in supplied relation order.
            "reps": generated["reps"][inverse].astype(np.int32, copy=False),
            "block_i": generated["block_i"][inverse].astype(np.int16, copy=False),
            "block_j": generated["block_j"][inverse].astype(np.int16, copy=False),
        }

    return {
        "all_generated_relation_sets_match_supplied": all_match,
        "matched_relation_count": int(np.count_nonzero(gen_to_sup >= 0)),
        "generated_relation_count": int(len(gen_hash)),
        "supplied_relation_count": int(len(sup_hash)),
        "generated_to_supplied_relation_map": gen_to_sup.astype(int).tolist(),
        "object_labels_match_supplied": None,  # filled by caller
        "supplied_object_of_point": sup_object,
        "supplied_reps": sup_reps,
        "supplied_block_i": sup_bi,
        "supplied_block_j": sup_bj,
        "aligned": aligned,
    }


def construct_be3_from_source_coorient(
    coorient_npz: Path,
    out_json: Path | None = None,
    out_relation_npz: Path | None = None,
    out_aligned_relation_npz: Path | None = None,
    compare_relation_npz: Path | None = None,
) -> dict[str, Any]:
    t0 = time.time()
    source_cert = source_constructor_certificate()
    if not source_cert["dodecad_shell"]["count_pass"]:
        raise ValueError("source constructor did not produce 2576 dodecads")

    z = np.load(coorient_npz)
    gens = np.asarray(z["generator_permutations"], dtype=np.int16)
    validate_permutation_rows(gens, EXPECTED_POINTS)
    t_close = time.time()
    P, closure_trace = close_group(gens)
    close_seconds = time.time() - t_close
    object_of_point, orbit_list, orbit_sizes = point_orbits(P)

    t_pair = time.time()
    rel = pair_orbits(P, object_of_point)
    pair_seconds = time.time() - t_pair

    if out_relation_npz is not None:
        save_relation_memberships(out_relation_npz, rel, object_of_point, int(P.shape[0]))

    comparison: dict[str, Any] = {}
    if compare_relation_npz is not None and compare_relation_npz.exists():
        cmp = align_to_supplied(rel, compare_relation_npz)
        cmp["object_labels_match_supplied"] = bool(np.array_equal(object_of_point, cmp.pop("supplied_object_of_point")))
        # Remove arrays from JSON-facing comparison.
        cmp.pop("supplied_reps", None)
        cmp.pop("supplied_block_i", None)
        cmp.pop("supplied_block_j", None)
        aligned = cmp.pop("aligned", None)
        if aligned is not None and out_aligned_relation_npz is not None:
            save_relation_memberships(out_aligned_relation_npz, aligned, object_of_point, int(P.shape[0]))
            cmp["saved_aligned_relation_npz"] = str(out_aligned_relation_npz.relative_to(ROOT))
            cmp["aligned_encoded_pairs_sha256"] = sha_array(aligned["encoded_pairs"])
        comparison = cmp

    status_ok = (
        P.shape == (EXPECTED_GROUP_ORDER, EXPECTED_POINTS)
        and orbit_sizes == EXPECTED_SORTED_OBJECT_SIZES
        and int(rel["orbit_count"]) == EXPECTED_RELATIONS
        and int(rel["encoded_pairs"].size) == EXPECTED_POINTS * EXPECTED_POINTS
        and (not comparison or comparison.get("all_generated_relation_sets_match_supplied") is True)
    )

    result: dict[str, Any] = {
        "schema": "d20.constructor.source_coorient_to_be3_orbitals@1",
        "constructor_status": "SOURCE_COORIENT_TO_BE3_ORBITALS_PASS" if status_ok else "SOURCE_COORIENT_TO_BE3_ORBITALS_FAIL",
        "construction_method": "generate G24 dodecads from H8^3, apply fixed coorient dodecad-action generators, close Be3, compute point and ordered-pair orbits",
        "input_boundary": "uses fixed coorient generator permutations on the generated 2576 dodecads; does not derive those coorient generators from a smaller formula",
        "predicate": "is integral",
        "source": {
            "source_constructor_status": source_cert["constructor_status"],
            "root_sequence": source_cert["neighbors"]["root_sequence"],
            "dodecad_count": source_cert["dodecad_shell"]["count"],
            "dodecad_words_sha256": source_cert["dodecad_shell"]["dodecad_words_sha256"],
        },
        "coorient_seed": {
            "path": str(coorient_npz.relative_to(ROOT)) if coorient_npz.is_relative_to(ROOT) else str(coorient_npz),
            "generator_count": int(gens.shape[0]),
            "degree": int(gens.shape[1]),
            "generator_permutations_sha256": sha_array(gens),
        },
        "be3_action": {
            "group_order": int(P.shape[0]),
            "expected_group_order": EXPECTED_GROUP_ORDER,
            "degree": int(P.shape[1]),
            "closure_trace_last_values": [int(x) for x in closure_trace[-10:]],
            "action_sha256": sha_array(P),
            "close_seconds": round(close_seconds, 6),
        },
        "point_orbits": {
            "sizes_sorted": orbit_sizes,
            "expected_sizes_sorted": EXPECTED_SORTED_OBJECT_SIZES,
            "sizes_by_integral_label": [int(np.count_nonzero(object_of_point == i)) for i in range(6)],
            "orbit_minima_and_sizes": [[int(min(o)), int(len(o))] for o in orbit_list],
            "object_of_point_sha256": sha_array(object_of_point),
        },
        "ordered_pair_orbits": {
            "relation_count": int(rel["orbit_count"]),
            "expected_relation_count": EXPECTED_RELATIONS,
            "encoded_pair_count": int(rel["encoded_pairs"].size),
            "expected_encoded_pair_count": EXPECTED_POINTS * EXPECTED_POINTS,
            "relation_size_min": int(np.diff(rel["offsets"]).min()),
            "relation_size_max": int(np.diff(rel["offsets"]).max()),
            "encoded_pairs_sha256": sha_array(rel["encoded_pairs"]),
            "offsets_sha256": sha_array(rel["offsets"]),
            "pair_seconds": round(pair_seconds, 6),
            "saved_relation_npz": str(out_relation_npz.relative_to(ROOT)) if out_relation_npz is not None and out_relation_npz.exists() else None,
        },
        "comparison_to_supplied_raw": comparison,
        "remaining_boundary": [
            "derive the fixed coorient generator permutations from a smaller typed coorient formula rather than storing them as seed data"
        ],
        "total_seconds": round(time.time() - t0, 6),
    }
    result["constructor_result_sha256"] = stable_constructor_sha_json(result)
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Construct Be3 orbitals from source dodecads plus fixed coorient action generators.")
    ap.add_argument("--coorient", default="data/coorient/be3_coorient_generators.npz")
    ap.add_argument("--out-json", default="generated/source_coorient_to_be3_orbitals.json")
    ap.add_argument("--out-relation-npz", default="generated/relation_memberships_from_source_coorient.npz")
    ap.add_argument("--out-aligned-relation-npz", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--compare", default="data/raw/relation_memberships.npz")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = construct_be3_from_source_coorient(
        ROOT / args.coorient,
        ROOT / args.out_json if args.out_json else None,
        ROOT / args.out_relation_npz if args.out_relation_npz else None,
        ROOT / args.out_aligned_relation_npz if args.out_aligned_relation_npz else None,
        ROOT / args.compare if args.compare else None,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
