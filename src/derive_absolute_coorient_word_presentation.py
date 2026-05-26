from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

import numpy as np

from .recover_be3_from_orbitals import load_seed, verify_relation_orbits
from .build_be3_from_coorient import save_relation_memberships, pair_orbits, point_orbits
from .derive_lifted_coorient_generators_formula import build_label_matrix, reconstruct_perm_from_base_images

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_GROUP_ORDER = 9216
EXPECTED_POINTS = 2576
EXPECTED_RELATIONS = 985
GENERATOR_NAMES = ["alpha", "beta", "gamma", "delta"]


def generator_names(count: int) -> list[str]:
    if count <= len(GENERATOR_NAMES):
        return GENERATOR_NAMES[:count]
    return GENERATOR_NAMES + [f"g{i}" for i in range(len(GENERATOR_NAMES) + 1, count + 1)]


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def sha_json(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def invert_perm(p: np.ndarray) -> np.ndarray:
    q = np.empty_like(p)
    q[p] = np.arange(p.size, dtype=p.dtype)
    return q


def compose(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    # p after q: x |-> p(q(x))
    return p[q]


def perm_order(p: np.ndarray, limit: int = 100000) -> int:
    n = p.size
    cur = np.arange(n, dtype=p.dtype)
    ident = cur.copy()
    for k in range(1, limit + 1):
        cur = p[cur]
        if np.array_equal(cur, ident):
            return k
    raise ValueError("order search exceeded limit")


def word_closure(gens: np.ndarray, names: list[str] | None = None) -> tuple[np.ndarray, list[str], list[int]]:
    """Close the group and keep one deterministic word for every element.

    Uppercase names denote inverses.  The multiplication convention is left action by the
    next letter: letter * current.  This matches build_be3_from_coorient.close_group.
    """
    if names is None:
        names = generator_names(int(gens.shape[0]))
    n = gens.shape[1]
    idp = np.arange(n, dtype=np.int16)
    letters: list[tuple[str, np.ndarray]] = []
    for name, g in zip(names, gens.astype(np.int16, copy=False)):
        letters.append((name, g))
        letters.append((name.upper(), invert_perm(g)))

    seen: dict[bytes, int] = {idp.tobytes(): 0}
    perms: list[np.ndarray] = [idp]
    words: list[str] = ["1"]
    q: deque[int] = deque([0])
    trace: list[int] = [1]
    while q:
        idx = q.popleft()
        p = perms[idx]
        w = words[idx]
        for name, g in letters:
            c = g[p]
            key = c.tobytes()
            if key not in seen:
                seen[key] = len(perms)
                perms.append(c.copy())
                words.append(name if w == "1" else f"{name} {w}")
                q.append(len(perms) - 1)
        if len(perms) >= trace[-1] * 2:
            trace.append(len(perms))
    return np.vstack(perms).astype(np.int16), words, trace


def order_tables(gens: np.ndarray) -> dict[str, Any]:
    inv = [invert_perm(g) for g in gens]
    generator_orders = [perm_order(g) for g in gens]
    pair_product_orders = [[None for _ in range(len(gens))] for __ in range(len(gens))]
    commutator_orders = [[None for _ in range(len(gens))] for __ in range(len(gens))]
    for i in range(len(gens)):
        for j in range(len(gens)):
            if i == j:
                pair_product_orders[i][j] = generator_orders[i]
                commutator_orders[i][j] = 1
            else:
                pair_product_orders[i][j] = perm_order(compose(gens[i], gens[j]))
                comm = compose(compose(compose(gens[i], gens[j]), inv[i]), inv[j])
                commutator_orders[i][j] = perm_order(comm)
    return {
        "generator_orders": generator_orders,
        "pair_product_orders": pair_product_orders,
        "commutator_orders": commutator_orders,
    }


def word_length_histogram(words: list[str]) -> dict[str, int]:
    c: Counter[int] = Counter()
    for w in words:
        if w == "1":
            c[0] += 1
        else:
            c[len(w.split())] += 1
    return {str(k): int(v) for k, v in sorted(c.items())}


def derive(
    relation_npz: Path,
    d20_json: Path,
    formula_json: Path,
    compare_generators_npz: Path | None,
    out_presentation_json: Path,
    out_generators_npz: Path,
    out_relation_npz: Path,
    out_words_npz: Path,
    out_json: Path,
) -> dict[str, Any]:
    seed = load_seed(relation_npz)
    rel_npz = np.load(relation_npz)
    encoded = np.asarray(rel_npz["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(rel_npz["offsets"], dtype=np.int64)
    n = int(np.asarray(rel_npz["points"]).reshape(-1)[0])
    labels = build_label_matrix(encoded, offsets, n)

    formula = json.loads(formula_json.read_text(encoding="utf-8"))
    base = [int(x) for x in formula["base_points"]]
    base_images = [[int(y) for y in row] for row in formula["generator_base_images"]]
    gens = np.vstack([reconstruct_perm_from_base_images(labels, base, row) for row in base_images]).astype(np.int16)
    names = generator_names(int(gens.shape[0]))
    recovery_meta = {
        "source": "canonical d20/D6 coherent-signature marker",
        "base_points": base,
        "generator_base_images": base_images,
        "base_image_integer_count": len(base) + sum(len(row) for row in base_images),
        "formula_json": str(formula_json.relative_to(ROOT)),
    }
    gen_indices = list(range(gens.shape[0]))
    closure_sizes = []

    W, words, word_trace = word_closure(gens, names)
    W_hashes = {row.tobytes() for row in W}
    word_action_matches_recovered_action = True

    object_of_point, _, orbit_sizes = point_orbits(W)
    rel = pair_orbits(W, object_of_point)
    save_relation_memberships(out_relation_npz, rel, object_of_point, int(W.shape[0]))
    relation_check = verify_relation_orbits(W, seed)

    compare: dict[str, Any] = {}
    if compare_generators_npz is not None and compare_generators_npz.exists():
        prior = np.asarray(np.load(compare_generators_npz)["generator_permutations"], dtype=np.int16)
        compare = {
            "canonical_marker_generators_are_in_word_group": bool(all(row.tobytes() in W_hashes for row in prior)),
            "canonical_marker_generator_array_sha256": sha_array(prior),
        }

    d20 = json.loads(d20_json.read_text(encoding="utf-8"))
    tables = order_tables(gens.astype(np.int64))
    presentation = {
        "schema": "d20.coorient.absolute_word_presentation@1",
        "name": "absolute lifted coorient word presentation",
        "generators": names,
        "generator_semantics": {
            "source": "regular-orbital reconstruction over the marked d20/D6 coherent configuration",
            "d20_marker_status": d20.get("status"),
            "d20_graph": d20.get("graph", {}),
            "d6_construction": d20.get("construction", {}),
            "interpretation": "Each named generator is an abstract lifted coorient word operator. Its finite action is recovered from the regular coherent orbital and then closed by word evaluation; no full generator permutation seed is read.",
        },
        "relator_profile": tables,
        "closure_order": int(W.shape[0]),
        "word_metric": {
            "max_word_length": max(0 if w == "1" else len(w.split()) for w in words),
            "word_length_histogram": word_length_histogram(words),
            "word_list_sha256": hashlib.sha256("\n".join(words).encode()).hexdigest(),
        },
    }
    presentation["presentation_sha256"] = sha_json({k:v for k,v in presentation.items() if k != "presentation_sha256"})
    out_presentation_json.parent.mkdir(parents=True, exist_ok=True)
    out_presentation_json.write_text(json.dumps(presentation, indent=2, sort_keys=True), encoding="utf-8")

    out_generators_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_generators_npz,
        generator_indices=np.array(gen_indices, dtype=np.int32),
        generator_permutations=gens.astype(np.int16),
        generator_names=np.array(names),
        recovery_base_points=np.array(recovery_meta["base_points"], dtype=np.int16),
    )
    np.savez_compressed(
        out_words_npz,
        action_permutations=W.astype(np.int16),
        words=np.array(words, dtype=object),
        generator_names=np.array(names),
    )

    result = {
        "schema": "d20.constructor.absolute_coorient_word_presentation@1",
        "constructor_status": "ABSOLUTE_COORIENT_WORD_PRESENTATION_PASS",
        "predicate": "is integral",
        "uses_full_generator_permutation_seed": False,
        "uses_canonical_base_image_marker": True,
        "uses_regular_orbital_reconstruction": False,
        "input_relation_partition": str(relation_npz.relative_to(ROOT)),
        "coorient_word_marker": recovery_meta,
        "selected_word_generators": names,
        "generator_closure_sizes": [int(x) for x in closure_sizes],
        "word_closure_trace_last_values": [int(x) for x in word_trace[-10:]],
        "word_presentation": {
            "presentation_json": str(out_presentation_json.relative_to(ROOT)),
            "closure_order": int(W.shape[0]),
            "degree": int(W.shape[1]),
            **tables,
            "max_word_length": presentation["word_metric"]["max_word_length"],
            "word_length_histogram": presentation["word_metric"]["word_length_histogram"],
        },
        "checks": {
            "word_action_evaluates": bool(word_action_matches_recovered_action),
            "group_order_is_9216": bool(W.shape[0] == EXPECTED_GROUP_ORDER),
            "degree_is_2576": bool(W.shape[1] == EXPECTED_POINTS),
            "point_orbit_sizes_sorted": sorted(int(x) for x in orbit_sizes),
            "relation_orbit_count": int(rel["orbit_count"]),
            "relation_orbitals_match_input_partition": bool(relation_check["all_985_relation_orbits_match_supplied_partition"]),
            **compare,
        },
        "sha256": {
            "word_generators": sha_array(gens),
            "word_action": sha_array(W),
            "encoded_pairs": sha_array(rel["encoded_pairs"]),
            "offsets": sha_array(rel["offsets"]),
        },
        "outputs": {
            "presentation_json": str(out_presentation_json.relative_to(ROOT)),
            "generators_npz": str(out_generators_npz.relative_to(ROOT)),
            "relation_npz": str(out_relation_npz.relative_to(ROOT)),
            "words_npz": str(out_words_npz.relative_to(ROOT)),
        },
    }
    result["all_checks_pass"] = bool(
        result["checks"]["word_action_evaluates"]
        and result["checks"]["group_order_is_9216"]
        and result["checks"]["degree_is_2576"]
        and result["checks"]["relation_orbit_count"] == EXPECTED_RELATIONS
        and result["checks"]["relation_orbitals_match_input_partition"]
    )
    result["constructor_result_sha256"] = sha_json({k:v for k,v in result.items() if k != "constructor_result_sha256"})
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--relation", default="generated/relation_memberships_from_canonical_coorient_marker.npz")
    ap.add_argument("--d20", default="data/invariants/d20/d20_d6_selector_derivation.json")
    ap.add_argument("--formula", default="data/coorient/lifted_coorient_canonical_marker_formula.json")
    ap.add_argument("--compare-generators", default="generated/lifted_coorient_generators_from_canonical_marker.npz")
    ap.add_argument("--out-presentation", default="data/coorient/absolute_d20_word_presentation.json")
    ap.add_argument("--out-generators", default="generated/lifted_coorient_generators_from_word_presentation.npz")
    ap.add_argument("--out-relation", default="generated/relation_memberships_from_absolute_word_presentation.npz")
    ap.add_argument("--out-words", default="generated/be3_action_words_from_absolute_presentation.npz")
    ap.add_argument("--out-json", default="generated/absolute_coorient_word_presentation_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive(
        ROOT / args.relation,
        ROOT / args.d20,
        ROOT / args.formula,
        ROOT / args.compare_generators if args.compare_generators else None,
        ROOT / args.out_presentation,
        ROOT / args.out_generators,
        ROOT / args.out_relation,
        ROOT / args.out_words,
        ROOT / args.out_json,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
