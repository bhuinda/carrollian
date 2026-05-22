from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter, deque
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_seed(path: Path) -> dict[str, Any]:
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


def build_label_matrix(encoded: np.ndarray, offsets: np.ndarray, n: int) -> np.ndarray:
    r = offsets.size - 1
    labels = np.empty(n * n, dtype=np.int16)
    for a in range(r):
        labels[encoded[offsets[a] : offsets[a + 1]]] = a
    return labels.reshape(n, n)


def row_keys(M: np.ndarray) -> np.ndarray:
    M = np.ascontiguousarray(M)
    return M.view(np.dtype((np.void, M.dtype.itemsize * M.shape[1]))).reshape(-1)


def signature_matrix(labels: np.ndarray, base: list[int]) -> np.ndarray:
    rows = []
    for b in base:
        rows.append(labels[b, :])
        rows.append(labels[:, b])
    return np.vstack(rows).T.astype(np.int16, copy=False)


def greedy_base(labels: np.ndarray, first_pair: tuple[int, int], max_extra: int = 4) -> list[int]:
    """Pick a deterministic small base whose two-sided relation signatures separate points."""
    n = labels.shape[0]
    base = [int(first_pair[0]), int(first_pair[1])]
    candidates = list(range(n))

    def stats(B: list[int]) -> tuple[int, int]:
        keys = row_keys(signature_matrix(labels, B))
        _, counts = np.unique(keys, return_counts=True)
        return int(counts.max()), int(len(counts))

    # Deterministic greedy: scan all points and minimize max collision, then maximize unique classes.
    for _ in range(max_extra):
        if stats(base)[0] == 1:
            break
        best: tuple[tuple[int, int, int], int] | None = None
        used = set(base)
        for c in candidates:
            if c in used:
                continue
            mx, uniq = stats(base + [c])
            score = (mx, -uniq, c)
            if best is None or score < best[0]:
                best = (score, c)
        if best is None:
            break
        base.append(best[1])
    return base


def reconstruct_action_from_regular_orbital(seed: dict[str, Any], base: list[int] | None = None) -> tuple[np.ndarray, dict[str, Any]]:
    encoded = seed["encoded_pairs"]
    offsets = seed["offsets"]
    n = seed["points"]
    r = offsets.size - 1
    relation_sizes = np.diff(offsets)
    labels = build_label_matrix(encoded, offsets, n)

    max_size = int(relation_sizes.max())
    regular_relations = np.where(relation_sizes == max_size)[0]
    regular_relation = int(regular_relations[0])
    first = int(encoded[offsets[regular_relation]])
    first_pair = (first // n, first % n)

    if base is None:
        # The deterministic greedy usually finds a 4-point base here.  It uses only the supplied
        # orbital partition, not any imported group permutations.
        base = greedy_base(labels, first_pair, max_extra=6)

    full_keys = row_keys(signature_matrix(labels, base))
    src_sort = np.argsort(full_keys)
    full_keys_sorted = full_keys[src_sort]
    full_unique = int(np.unique(full_keys).size)
    if full_unique != n:
        raise ValueError(f"base does not separate points: {full_unique}/{n}")

    # Prefix keys for the added base points.  Given the image of the first two base points,
    # these recover the remaining base images by signature matching.  In this certificate
    # the branch profile is uniformly (2 candidates, 1 valid reconstruction).
    prefix_specs: list[tuple[int, np.void]] = []
    for k in range(2, len(base)):
        key = row_keys(signature_matrix(labels, base[:k])[[base[k]]])[0]
        prefix_specs.append((k, key))

    def candidates_for(prefix_images: list[int], wanted_key: np.void) -> np.ndarray:
        keys = row_keys(signature_matrix(labels, prefix_images))
        return np.where(keys == wanted_key)[0]

    def reconstruct_from_base_images(base_images: list[int]) -> np.ndarray | None:
        keys = row_keys(signature_matrix(labels, base_images))
        order = np.argsort(keys)
        if not np.array_equal(keys[order], full_keys_sorted):
            return None
        perm = np.empty(n, dtype=np.int16)
        perm[src_sort] = order.astype(np.int16)
        if any(int(perm[base[i]]) != int(base_images[i]) for i in range(len(base))):
            return None
        return perm

    perms: list[np.ndarray] = []
    branch_counter: Counter[str] = Counter()
    failures: list[dict[str, Any]] = []
    t0 = time.time()

    for target_index, code in enumerate(encoded[offsets[regular_relation] : offsets[regular_relation + 1]]):
        start_images = [int(code // n), int(code % n)]
        partials: list[list[int]] = [start_images]
        branch_sizes: list[int] = []
        for _k, wanted in prefix_specs:
            next_partials: list[list[int]] = []
            total_candidates = 0
            for partial in partials:
                cand = candidates_for(partial, wanted)
                total_candidates += int(cand.size)
                for w in cand:
                    next_partials.append(partial + [int(w)])
            branch_sizes.append(total_candidates)
            partials = next_partials
        valid: list[np.ndarray] = []
        for images in partials:
            perm = reconstruct_from_base_images(images)
            if perm is not None:
                valid.append(perm)
        branch_counter[str((tuple(branch_sizes), len(valid)))] += 1
        if len(valid) != 1:
            failures.append({"target_index": target_index, "start_images": start_images, "valid": len(valid), "branch_sizes": branch_sizes})
            if len(failures) >= 5:
                break
        else:
            perms.append(valid[0])

    if failures:
        raise ValueError(f"failed to reconstruct unique action from regular orbital: {failures[:3]}")

    P = np.vstack(perms).astype(np.int16, copy=False)
    meta = {
        "regular_relation": regular_relation,
        "regular_relation_size": max_size,
        "regular_relation_count": int(regular_relations.size),
        "base_points": [int(x) for x in base],
        "base_signature_unique_points": full_unique,
        "branch_profile": dict(sorted(branch_counter.items())),
        "reconstruction_seconds": round(time.time() - t0, 6),
    }
    return P, meta


def compose_index(P: np.ndarray, index: dict[bytes, int], i: int, j: int) -> int:
    # P maps prior -> new.  This returns i after j.
    return index[P[i][P[j]].tobytes()]


def closure_size(P: np.ndarray, generator_indices: list[int]) -> int:
    index = {P[i].tobytes(): i for i in range(P.shape[0])}
    seen = {0}
    q: deque[int] = deque([0])
    while q:
        a = q.popleft()
        for g in generator_indices:
            for c in (compose_index(P, index, g, a), compose_index(P, index, a, g)):
                if c not in seen:
                    seen.add(c)
                    q.append(c)
    return len(seen)


def find_generators(P: np.ndarray, candidates: list[int] | None = None) -> tuple[list[int], list[int]]:
    """Greedy deterministic generator extraction.

    The default candidate list is stable and found in the first successful run.  If it still works,
    we avoid repeatedly doing a larger search.  Otherwise we scan sequentially.
    """
    target = P.shape[0]
    preferred = [1229, 1244, 1952, 4517]
    if candidates is None:
        candidates = preferred + [i for i in range(1, min(target, 2000)) if i not in preferred]
    gens: list[int] = []
    sizes: list[int] = []
    current = 1
    for c in candidates:
        trial = gens + [int(c)]
        size = closure_size(P, trial)
        if size > current:
            gens = trial
            sizes.append(size)
            current = size
            if current == target:
                break
    return gens, sizes


def verify_point_orbits(P: np.ndarray) -> list[int]:
    n = P.shape[1]
    used = np.zeros(n, dtype=np.bool_)
    sizes: list[int] = []
    for x in range(n):
        if used[x]:
            continue
        orbit = np.unique(P[:, x])
        used[orbit.astype(np.int64)] = True
        sizes.append(int(orbit.size))
    return sorted(sizes)


def verify_relation_orbits(P: np.ndarray, seed: dict[str, Any]) -> dict[str, Any]:
    encoded = seed["encoded_pairs"]
    offsets = seed["offsets"]
    reps = seed["reps"]
    n = seed["points"]
    r = offsets.size - 1
    bad: list[int] = []
    relation_orbit_sizes: list[int] = []
    for a in range(r):
        x = int(reps[a, 2])
        y = int(reps[a, 3])
        orbit = np.unique(P[:, x].astype(np.int64) * n + P[:, y].astype(np.int64))
        supplied = np.sort(encoded[offsets[a] : offsets[a + 1]])
        relation_orbit_sizes.append(int(orbit.size))
        if not np.array_equal(np.sort(orbit), supplied):
            bad.append(a)
            if len(bad) >= 10:
                break
    return {
        "checked_relations": int(r if not bad else min(r, bad[-1] + 1)),
        "bad_relation_count_first10": len(bad),
        "bad_relation_examples": bad,
        "all_985_relation_orbits_match_supplied_partition": len(bad) == 0,
        "relation_orbit_size_min": int(min(relation_orbit_sizes)) if relation_orbit_sizes else None,
        "relation_orbit_size_max": int(max(relation_orbit_sizes)) if relation_orbit_sizes else None,
    }


def recover_be3_from_orbitals(
    relation_seed: Path,
    out_json: Path | None = None,
    out_generators_npz: Path | None = None,
    save_full_action_npz: Path | None = None,
) -> dict[str, Any]:
    t0 = time.time()
    seed = load_seed(relation_seed)
    P, meta = reconstruct_action_from_regular_orbital(seed)

    id_rows = np.where(np.all(P == np.arange(seed["points"], dtype=np.int16), axis=1))[0].astype(int).tolist()
    point_orbit_sizes = verify_point_orbits(P)
    relation_check = verify_relation_orbits(P, seed)
    gens, closure_steps = find_generators(P)
    generated_order = closure_steps[-1] if closure_steps else 1

    gen_perms = P[np.array(gens, dtype=np.int64)] if gens else np.empty((0, P.shape[1]), dtype=np.int16)
    if out_generators_npz is not None:
        out_generators_npz.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_generators_npz,
            generator_indices=np.array(gens, dtype=np.int32),
            generator_permutations=gen_perms.astype(np.int16, copy=False),
            base_points=np.array(meta["base_points"], dtype=np.int16),
            regular_relation=np.array([meta["regular_relation"]], dtype=np.int32),
        )
    if save_full_action_npz is not None:
        save_full_action_npz.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(save_full_action_npz, permutations=P)

    status_ok = (
        P.shape == (int(seed["group_order"]), int(seed["points"]))
        and len(id_rows) == 1
        and point_orbit_sizes == [144, 192, 384, 512, 576, 768]
        and relation_check["all_985_relation_orbits_match_supplied_partition"]
        and generated_order == int(seed["group_order"])
    )

    result: dict[str, Any] = {
        "schema": "d20.constructor.be3_action_from_orbitals@1",
        "constructor_status": "BE3_ACTION_FROM_ORBITALS_PASS" if status_ok else "BE3_ACTION_FROM_ORBITALS_FAIL",
        "construction_method": "recover group action from a regular ordered-pair orbital using two-sided coherent signatures",
        "input_boundary": "uses supplied ordered-pair orbital partition; still does not construct Be3 from source coorient generators",
        "predicate": "is integral",
        "points": int(seed["points"]),
        "recovered_group_order": int(P.shape[0]),
        "expected_group_order": int(seed["group_order"]),
        "permutation_degree": int(P.shape[1]),
        "identity_rows": id_rows,
        "point_orbit_sizes": point_orbit_sizes,
        "expected_point_orbit_sizes": [144, 192, 384, 512, 576, 768],
        "relation_orbit_verification": relation_check,
        "regular_orbital_reconstruction": meta,
        "generator_indices": [int(x) for x in gens],
        "generator_closure_sizes": [int(x) for x in closure_steps],
        "generators_generate_full_group": bool(generated_order == int(seed["group_order"])),
        "action_sha256": sha_array(P),
        "generator_permutations_sha256": sha_array(gen_perms),
        "saved_generators_npz": str(out_generators_npz.relative_to(ROOT)) if out_generators_npz is not None and out_generators_npz.exists() else None,
        "saved_full_action_npz": str(save_full_action_npz.relative_to(ROOT)) if save_full_action_npz is not None and save_full_action_npz.exists() else None,
        "total_seconds": round(time.time() - t0, 6),
        "remaining_scratch_boundary": [
            "derive this same Be3 action directly from generated G24 plus fixed coorient generators",
            "remove dependence on the supplied ordered-pair orbital partition",
        ],
    }
    body = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["constructor_result_sha256"] = hashlib.sha256(body).hexdigest()

    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Recover the Be3 action from the supplied ordered-pair orbital partition.")
    ap.add_argument("--relation-seed", default="data/raw/relation_memberships.npz")
    ap.add_argument("--out-json", default="generated/be3_action_from_orbitals.json")
    ap.add_argument("--out-generators-npz", default="generated/be3_generators_from_orbitals.npz")
    ap.add_argument("--save-full-action-npz", default=None)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = recover_be3_from_orbitals(
        ROOT / args.relation_seed,
        ROOT / args.out_json if args.out_json else None,
        ROOT / args.out_generators_npz if args.out_generators_npz else None,
        ROOT / args.save_full_action_npz if args.save_full_action_npz else None,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
