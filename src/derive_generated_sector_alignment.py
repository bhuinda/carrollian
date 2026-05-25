#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certificate_registry import certificate_relpath
except ImportError:  # Supports `python src/derive_generated_sector_alignment.py`.
    from certificate_registry import certificate_relpath

ROOT = Path(__file__).resolve().parents[1]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sector_tuple(dim: int, rank: int, support: int, q42: int, q12: int) -> tuple[int, int, int, int, int]:
    return (int(dim), int(rank), int(support), int(q42), int(q12))


def derive_alignment(
    generated_center_npz: Path,
    canonical_center_cert: Path,
    relation_npz: Path,
    out_npz: Path | None = None,
    out_json: Path | None = None,
) -> dict[str, Any]:
    gen = np.load(generated_center_npz)
    E = np.asarray(gen["primitive_idempotents"], dtype=np.int64)
    dims = np.asarray(gen["block_dimensions"], dtype=np.int64)
    ranks = np.asarray(gen["permutation_ranks"], dtype=np.int64)
    mults = np.asarray(gen["multiplicities"], dtype=np.int64)
    q42_counts = np.asarray(gen["q42_shadow_nonzero_counts"], dtype=np.int64)
    q12_counts = np.asarray(gen["q12_shadow_nonzero_counts"], dtype=np.int64)
    support_sizes = np.count_nonzero(E, axis=0).astype(np.int64)

    hist = load_json(canonical_center_cert)
    profiles = hist["gluing_and_sector_profiles"]["sector_profiles"]

    generated_tuples = [sector_tuple(dims[i], ranks[i], support_sizes[i], q42_counts[i], q12_counts[i]) for i in range(E.shape[1])]
    canonical_tuples = [
        sector_tuple(
            p["block_dimension"],
            p["permutation_rank"],
            p["character_support_size"],
            p["q42_nonzero_count"],
            p["q12_nonzero_count"],
        )
        for p in profiles
    ]

    c_gen = Counter(generated_tuples)
    c_hist = Counter(canonical_tuples)
    tuple_multisets_match = c_gen == c_hist
    tuple_is_unique = all(v == 1 for v in c_gen.values()) and all(v == 1 for v in c_hist.values())

    hist_by_tuple: dict[tuple[int, int, int, int, int], int] = {t: i for i, t in enumerate(canonical_tuples)}
    generated_to_canonical = []
    canonical_to_generated = [-1] * len(canonical_tuples)
    unresolved_generated = []
    for i, t in enumerate(generated_tuples):
        sec = hist_by_tuple.get(t, -1)
        generated_to_canonical.append(int(sec))
        if sec < 0:
            unresolved_generated.append(int(i))
        else:
            canonical_to_generated[sec] = int(i)

    # Recompute active objects from the generated primitive idempotent support.
    rel = np.load(relation_npz)
    block_i = np.asarray(rel["block_i"], dtype=np.int64)
    block_j = np.asarray(rel["block_j"], dtype=np.int64)
    object_labels = ["B-", "B+", "V-", "V+", "S-", "S+"]
    cy_labels = {0: "B", 1: "B", 2: "V", 3: "V", 4: "S", 5: "S"}
    active_objects = []
    active_cy = []
    active_object_pair_counts = []
    for col in range(E.shape[1]):
        support = np.nonzero(E[:, col])[0]
        objs = sorted({int(block_i[a]) for a in support} | {int(block_j[a]) for a in support})
        pairs = sorted({(int(block_i[a]), int(block_j[a])) for a in support})
        active_objects.append([object_labels[i] for i in objs])
        active_cy.append(sorted({cy_labels[i] for i in objs}))
        active_object_pair_counts.append(int(len(pairs)))

    # Sector 33 is now named without using canonical column order: it is the unique generated
    # primitive idempotent with public-zero terminal shadows and the dim/rank/support signature.
    generated_sector33_candidates = [
        int(i)
        for i, t in enumerate(generated_tuples)
        if t == (2, 36, 56, 0, 0)
    ]
    generated_sector33_column = generated_sector33_candidates[0] if len(generated_sector33_candidates) == 1 else None
    canonical_sector33_column = 33
    canonical_sector33_matches = bool(
        generated_sector33_column is not None
        and generated_to_canonical[generated_sector33_column] == canonical_sector33_column
        and canonical_to_generated[canonical_sector33_column] == generated_sector33_column
    )

    rows = []
    for col, sec in enumerate(generated_to_canonical):
        rows.append(
            {
                "generated_column": int(col),
                "canonical_sector": int(sec),
                "signature": {
                    "block_dimension": int(dims[col]),
                    "permutation_rank": int(ranks[col]),
                    "multiplicity": int(mults[col]),
                    "coordinate_support_size": int(support_sizes[col]),
                    "q42_shadow_nonzero_count": int(q42_counts[col]),
                    "q12_shadow_nonzero_count": int(q12_counts[col]),
                    "active_objects_from_generated_support": active_objects[col],
                    "active_cy_from_generated_support": active_cy[col],
                    "active_object_pair_count": int(active_object_pair_counts[col]),
                },
            }
        )

    result = {
        "schema": "d20.constructor.generated_sector_alignment@1",
        "constructor_status": "GENERATED_SECTOR_ALIGNMENT_PASS"
        if (tuple_multisets_match and tuple_is_unique and not unresolved_generated and canonical_sector33_matches)
        else "GENERATED_SECTOR_ALIGNMENT_BOUNDARY",
        "alignment_rule": (
            "Match each generated primitive central idempotent to the canonical sector number by the unique tuple "
            "(block_dimension, permutation_rank, coordinate_support_size, q42_shadow_nonzero_count, q12_shadow_nonzero_count)."
        ),
        "tuple_multisets_match": bool(tuple_multisets_match),
        "tuple_signature_unique_for_all_39_sectors": bool(tuple_is_unique),
        "generated_to_canonical_sector": [int(x) for x in generated_to_canonical],
        "canonical_to_generated_column": [int(x) for x in canonical_to_generated],
        "generated_sector33_column": None if generated_sector33_column is None else int(generated_sector33_column),
        "canonical_sector33": int(canonical_sector33_column),
        "sector33_alignment_pass": bool(canonical_sector33_matches),
        "sector33_intrinsic_signature": {
            "block_dimension": 2,
            "permutation_rank": 36,
            "coordinate_support_size": 56,
            "q42_shadow_nonzero_count": 0,
            "q12_shadow_nonzero_count": 0,
            "active_objects_from_generated_support": active_objects[generated_sector33_column] if generated_sector33_column is not None else [],
            "active_cy_from_generated_support": active_cy[generated_sector33_column] if generated_sector33_column is not None else [],
        },
        "rows": rows,
        "hashes": {
            "primitive_idempotents_sha256": sha_array(E),
            "generated_to_canonical_sector_sha256": sha_array(np.array(generated_to_canonical, dtype=np.int64)),
            "canonical_to_generated_column_sha256": sha_array(np.array(canonical_to_generated, dtype=np.int64)),
        },
        "remaining_boundary_removed": [
            "canonically match generated primitive idempotent columns to canonical sector numbering without relying on column order",
            "identify generated sector-33 column intrinsically from generated primitive idempotent data",
        ],
        "remaining_boundary": [
            "derive fixed coorient generator permutations from a smaller typed coorient formula",
            "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data",
        ],
    }
    result["all_checks_pass"] = bool(result["constructor_status"] == "GENERATED_SECTOR_ALIGNMENT_PASS")
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})

    if out_npz is not None:
        out_npz.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_npz,
            generated_to_canonical_sector=np.array(generated_to_canonical, dtype=np.int64),
            canonical_to_generated_column=np.array(canonical_to_generated, dtype=np.int64),
            generated_sector33_column=np.array([-1 if generated_sector33_column is None else generated_sector33_column], dtype=np.int64),
            sector_signatures=np.array(generated_tuples, dtype=np.int64),
            support_sizes=support_sizes.astype(np.int64),
        )
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated-center", default="generated/center_idempotents_from_generated_T985.npz")
    ap.add_argument("--canonical-center", default=certificate_relpath("drinfeld.full_a985_lift"))
    ap.add_argument("--relations", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--out-npz", default="generated/generated_sector_alignment.npz")
    ap.add_argument("--out-json", default="generated/generated_sector_alignment_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    res = derive_alignment(
        ROOT / args.generated_center,
        ROOT / args.canonical_center,
        ROOT / args.relations,
        ROOT / args.out_npz,
        ROOT / args.out_json,
    )
    print(json.dumps(res, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
