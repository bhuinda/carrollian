from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any

import numpy as np

from .derive_lifted_coorient_generators_formula import build_label_matrix, signature_keys, reconstruct_perm_from_base_images, sha_array

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_GROUP_ORDER = 9216
EXPECTED_RELATIONS = 985
EXPECTED_POINTS = 2576

def sha_json(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def choose_canonical_base(labels: np.ndarray, max_size: int = 4) -> list[int]:
    base: list[int] = []
    n = labels.shape[0]
    current_unique = 1
    remaining = set(range(n))
    while current_unique < n and len(base) < max_size:
        best = None
        best_unique = -1
        for cand in range(n):
            if cand in remaining:
                u = int(np.unique(signature_keys(labels, base + [cand])).size)
                if u > best_unique:
                    best_unique = u
                    best = cand
        if best is None:
            break
        base.append(int(best))
        remaining.remove(int(best))
        current_unique = best_unique
    return base

def derive(relation_npz: Path, generator_npz: Path, out_formula_json: Path, out_json: Path) -> dict[str, Any]:
    rel = np.load(relation_npz)
    encoded = np.asarray(rel["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(rel["offsets"], dtype=np.int64)
    n = int(np.asarray(rel["points"]).reshape(-1)[0])
    labels = build_label_matrix(encoded, offsets, n)
    gens = np.asarray(np.load(generator_npz)["generator_permutations"], dtype=np.int16)
    base = choose_canonical_base(labels, 4)
    unique_count = int(np.unique(signature_keys(labels, base)).size)
    base_images = gens[:, base].astype(int).tolist()
    # Reconstruct and verify all generators from the canonical marker.
    reconstructed = np.vstack([reconstruct_perm_from_base_images(labels, base, row) for row in base_images]).astype(np.int16)
    matches = bool(np.array_equal(reconstructed, gens))
    formula = {
        "schema": "d20.coorient.lift.canonical_marker_formula@1",
        "d6_marker": "marked D6 Coxeter-polarity d20 selector; canonical separating base chosen greedily by two-sided coherent relation signatures",
        "formula": "Choose the lexicographically first greedy base maximizing two-sided coherent-signature separation at each step. For each lifted coorient generator, store only its images on that canonical base; the full permutation is the unique coherent-signature lift preserving all 985 relation labels.",
        "base_selection": "greedy max unique two-sided relation signatures, lexicographic tie-break",
        "base_points": base,
        "generator_base_images": base_images,
        "expected_closure_order": EXPECTED_GROUP_ORDER,
        "expected_pair_orbitals": EXPECTED_RELATIONS,
    }
    out_formula_json.parent.mkdir(parents=True, exist_ok=True)
    out_formula_json.write_text(json.dumps(formula, indent=2, sort_keys=True), encoding="utf-8")
    result = {
        "schema": "d20.constructor.coorient_canonical_marker@1",
        "constructor_status": "COORIENT_CANONICAL_MARKER_PASS" if matches and unique_count == n else "COORIENT_CANONICAL_MARKER_FAIL",
        "predicate": "is integral",
        "base_points": base,
        "base_size": len(base),
        "signature_unique_points": unique_count,
        "point_count": n,
        "base_separates_points": bool(unique_count == n),
        "generator_base_images": base_images,
        "seed_size_integers": len(base) + sum(len(row) for row in base_images),
        "full_generator_size_integers": int(gens.size),
        "compression_ratio": float(gens.size / (len(base) + sum(len(row) for row in base_images))),
        "reconstruction_matches_generator_array": matches,
        "generator_sha256": sha_array(gens),
        "reconstructed_sha256": sha_array(reconstructed),
        "formula_json": str(out_formula_json.relative_to(ROOT)),
    }
    result["all_checks_pass"] = bool(matches and unique_count == n)
    result["constructor_result_sha256"] = sha_json({k:v for k,v in result.items() if k != "constructor_result_sha256"})
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--relation", default="generated/relation_memberships_from_lifted_coorient_formula.npz")
    ap.add_argument("--generators", default="generated/lifted_coorient_generators_from_formula.npz")
    ap.add_argument("--out-formula", default="data/coorient/lifted_coorient_canonical_marker_formula.json")
    ap.add_argument("--out-json", default="generated/coorient_canonical_marker_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive(ROOT/args.relation, ROOT/args.generators, ROOT/args.out_formula, ROOT/args.out_json)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))

if __name__ == "__main__":
    main()
