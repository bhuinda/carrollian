from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .build_be3_from_coorient import close_group, point_orbits, pair_orbits, save_relation_memberships

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_GROUP_ORDER = 9216
EXPECTED_POINTS = 2576
EXPECTED_RELATIONS = 985
EXPECTED_OBJECT_SIZES = [384, 192, 144, 576, 512, 768]


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def build_label_matrix(encoded: np.ndarray, offsets: np.ndarray, n: int) -> np.ndarray:
    labels = np.empty(n * n, dtype=np.int16)
    for a in range(offsets.size - 1):
        labels[encoded[int(offsets[a]):int(offsets[a + 1])]] = a
    return labels.reshape(n, n)


def signature_keys(labels: np.ndarray, base: list[int]) -> np.ndarray:
    rows = []
    for b in base:
        rows.append(labels[b, :])
        rows.append(labels[:, b])
    S = np.vstack(rows).T.astype(np.int16, copy=False)
    return np.ascontiguousarray(S).view(np.dtype((np.void, S.dtype.itemsize * S.shape[1]))).reshape(-1)


def reconstruct_perm_from_base_images(labels: np.ndarray, base: list[int], images: list[int]) -> np.ndarray:
    if len(base) != len(images):
        raise ValueError("base and images must have equal length")
    src_keys = signature_keys(labels, base)
    dst_keys = signature_keys(labels, images)
    src_order = np.argsort(src_keys)
    dst_order = np.argsort(dst_keys)
    if not np.array_equal(src_keys[src_order], dst_keys[dst_order]):
        raise ValueError("base-image formula does not preserve coherent signatures")
    perm = np.empty(labels.shape[0], dtype=np.int16)
    perm[src_order] = dst_order.astype(np.int16)
    for b, im in zip(base, images):
        if int(perm[b]) != int(im):
            raise ValueError(f"base image mismatch at {b}: got {int(perm[b])}, expected {im}")
    return perm


def derive_formula(
    relation_npz: Path,
    formula_json: Path,
    compare_generators_npz: Path | None,
    out_generators_npz: Path,
    out_relation_npz: Path,
    out_json: Path,
) -> dict[str, Any]:
    rel = np.load(relation_npz)
    encoded = np.asarray(rel["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(rel["offsets"], dtype=np.int64)
    object_seed = np.asarray(rel["object_of_point"], dtype=np.int16)
    n = int(np.asarray(rel["points"]).reshape(-1)[0])
    labels = build_label_matrix(encoded, offsets, n)

    formula = json.loads(formula_json.read_text(encoding="utf-8"))
    base = [int(x) for x in formula["base_points"]]
    base_images = [[int(y) for y in row] for row in formula["generator_base_images"]]

    # The base is adequate exactly when the two-sided coherent signatures separate all dodecads.
    base_unique = int(np.unique(signature_keys(labels, base)).size)
    gens = np.vstack([reconstruct_perm_from_base_images(labels, base, row) for row in base_images]).astype(np.int16)

    comparison: dict[str, Any] = {}
    if compare_generators_npz is not None and compare_generators_npz.exists():
        prior = np.asarray(np.load(compare_generators_npz)["generator_permutations"], dtype=np.int16)
        comparison = {
            "matches_previous_full_generator_permutations": bool(np.array_equal(gens, prior)),
            "previous_generator_sha256": sha_array(prior),
        }

    P, closure_trace = close_group(gens)
    object_of_point, orbit_list, orbit_sizes = point_orbits(P)
    pair = pair_orbits(P, object_of_point)
    save_relation_memberships(out_relation_npz, pair, object_of_point, int(P.shape[0]))
    out_generators_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_generators_npz,
        generator_permutations=gens.astype(np.int16),
        base_points=np.array(base, dtype=np.int16),
        generator_base_images=np.array(base_images, dtype=np.int16),
        formula_source=np.array(["two-sided coherent-signature lift over marked D6/d20 relation labels"]),
    )

    result = {
        "schema": "d20.constructor.lifted_coorient_generators.formula@1",
        "constructor_status": "LIFTED_COORIENT_GENERATORS_FORMULA_PASS",
        "predicate": "is integral",
        "formula": {
            "name": "two-sided coherent-signature lift",
            "base_points": base,
            "generator_base_images": base_images,
            "seed_size_integers": len(base) + sum(len(x) for x in base_images),
            "full_seed_size_integers": int(gens.size),
            "compression_ratio": float(gens.size / (len(base) + sum(len(x) for x in base_images))),
            "d6_marker": formula.get("d6_marker"),
            "interpretation": "A lifted coorient generator is the unique permutation preserving all 985 coherent relations and sending the separating base to the listed base-image tuple.",
        },
        "signature_base": {
            "base_signature_unique_points": base_unique,
            "point_count": n,
            "base_separates_points": bool(base_unique == n),
        },
        "derived_generators": {
            "shape": list(gens.shape),
            "generator_permutations_sha256": sha_array(gens),
            **comparison,
        },
        "closed_action": {
            "group_order": int(P.shape[0]),
            "degree": int(P.shape[1]),
            "closure_trace_last_values": [int(x) for x in closure_trace[-10:]],
            "action_sha256": sha_array(P),
        },
        "point_orbits": {
            "sizes_by_integral_label": [int(np.count_nonzero(object_of_point == i)) for i in range(6)],
            "sizes_sorted": sorted(int(x) for x in orbit_sizes),
            "expected_sizes_sorted": sorted(EXPECTED_OBJECT_SIZES),
            "object_labels_match_relation_input": bool(np.array_equal(object_of_point, object_seed)),
        },
        "ordered_pair_orbits": {
            "relation_count": int(pair["orbit_count"]),
            "expected_relation_count": EXPECTED_RELATIONS,
            "encoded_pair_count": int(pair["encoded_pairs"].size),
            "encoded_pairs_sha256": sha_array(pair["encoded_pairs"]),
            "offsets_sha256": sha_array(pair["offsets"]),
        },
        "outputs": {
            "generators_npz": str(out_generators_npz.relative_to(ROOT)),
            "relation_npz": str(out_relation_npz.relative_to(ROOT)),
        },
    }
    result["all_checks_pass"] = bool(
        base_unique == n
        and P.shape == (EXPECTED_GROUP_ORDER, EXPECTED_POINTS)
        and sorted(orbit_sizes) == sorted(EXPECTED_OBJECT_SIZES)
        and int(pair["orbit_count"]) == EXPECTED_RELATIONS
        and comparison.get("matches_previous_full_generator_permutations", True) is True
    )
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--relation", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--formula", default="data/coorient/lifted_coorient_signature_formula.json")
    ap.add_argument("--compare", default="data/coorient/be3_coorient_generators.npz")
    ap.add_argument("--out-generators", default="generated/lifted_coorient_generators_from_formula.npz")
    ap.add_argument("--out-relation", default="generated/relation_memberships_from_lifted_coorient_formula.npz")
    ap.add_argument("--out-json", default="generated/lifted_coorient_generators_formula_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive_formula(
        ROOT / args.relation,
        ROOT / args.formula,
        ROOT / args.compare if args.compare else None,
        ROOT / args.out_generators,
        ROOT / args.out_relation,
        ROOT / args.out_json,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
