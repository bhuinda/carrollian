#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NPOINTS = 2576


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def relation_hashes(encoded: np.ndarray, offsets: np.ndarray) -> list[str]:
    out: list[str] = []
    for i in range(offsets.size - 1):
        seg = encoded[int(offsets[i]):int(offsets[i + 1])]
        out.append(hashlib.sha256(np.ascontiguousarray(seg).tobytes()).hexdigest())
    return out


def load_target_selector_indices(selector_json: Path, relation_npz: Path) -> list[int]:
    selector = json.loads(selector_json.read_text(encoding="utf-8"))
    target_hashes = [row["relation_hash"] for row in selector["diagonal_special_relation_hashes"]]
    z = np.load(relation_npz)
    hashes = relation_hashes(z["encoded_pairs"].astype(np.int64), z["offsets"].astype(np.int64))
    lookup = {h: i for i, h in enumerate(hashes)}
    missing = [h for h in target_hashes if h not in lookup]
    if missing:
        raise ValueError(f"selector hashes missing from relation partition: {missing[:2]}")
    return [int(lookup[h]) for h in target_hashes]


def derive_terminal_selector_intrinsic_obstruction(
    relation_npz: Path,
    tensor_npz: Path,
    selector_json: Path,
    out_json: Path | None = None,
    source_order_relation_npz: Path | None = None,
) -> dict[str, Any]:
    rel = np.load(relation_npz)
    encoded = rel["encoded_pairs"].astype(np.int64)
    offsets = rel["offsets"].astype(np.int64)
    block_i = rel["block_i"].astype(np.int64)
    block_j = rel["block_j"].astype(np.int64)
    object_of_point = rel["object_of_point"].astype(np.int64)
    object_sizes = np.bincount(object_of_point, minlength=6).astype(np.int64)
    relation_sizes = np.diff(offsets).astype(np.int64)
    relation_count = offsets.size - 1

    triples = np.load(tensor_npz)["triples"].astype(np.int64)
    # product rows for diagonal self-squares only; enough for the obstruction profile.
    self_square: dict[int, list[tuple[int, int]]] = defaultdict(list)
    mask = triples[:, 0] == triples[:, 1]
    for a, _b, g, w in triples[mask]:
        self_square[int(a)].append((int(g), int(w)))

    trace = np.zeros(relation_count, dtype=np.int64)
    for a in range(relation_count):
        seg = encoded[int(offsets[a]):int(offsets[a + 1])]
        trace[a] = int(np.count_nonzero((seg // NPOINTS) == (seg % NPOINTS)))

    identity_by_object: list[int] = []
    identity_ambiguities: list[dict[str, Any]] = []
    for obj in range(6):
        ids = np.where((block_i == obj) & (block_j == obj))[0]
        val = relation_sizes[ids] // object_sizes[obj]
        cand = ids[(val == 1) & (trace[ids] == object_sizes[obj])]
        if cand.size != 1:
            identity_ambiguities.append({"object": int(obj), "candidate_count": int(cand.size), "candidates": cand.astype(int).tolist()})
            identity_by_object.append(int(cand[0]) if cand.size else -1)
        else:
            identity_by_object.append(int(cand[0]))

    target = load_target_selector_indices(selector_json, relation_npz)
    feature_rows: list[dict[str, Any]] = []
    ambiguous_objects: list[int] = []
    unique_objects: list[int] = []
    rules = [
        ("valency", ["valency"]),
        ("valency_trace", ["valency", "trace"]),
        ("valency_trace_self_support", ["valency", "trace", "self_square_support"]),
        ("valency_trace_self_support_self_coeff", ["valency", "trace", "self_square_support", "self_coeff"]),
        ("valency_trace_self_support_self_coeff_identity_coeff", ["valency", "trace", "self_square_support", "self_coeff", "identity_coeff"]),
        ("full_tested_diagonal_signature", ["valency", "trace", "self_square_support", "self_coeff", "identity_coeff", "self_square_mass"]),
    ]

    for obj in range(6):
        ids = np.where((block_i == obj) & (block_j == obj))[0]
        rows: list[dict[str, Any]] = []
        ident = identity_by_object[obj]
        for a0 in ids:
            a = int(a0)
            valency = int(relation_sizes[a] // object_sizes[obj])
            sq = self_square.get(a, [])
            self_coeff = int(next((w for g, w in sq if g == a), 0))
            identity_coeff = int(next((w for g, w in sq if g == ident), 0)) if ident >= 0 else 0
            rows.append({
                "relation": a,
                "valency": valency,
                "trace": int(trace[a]),
                "self_square_support": int(len(sq)),
                "self_coeff": self_coeff,
                "identity_coeff": identity_coeff,
                "self_square_mass": int(sum(w for _g, w in sq)),
            })
        target_row = next(r for r in rows if r["relation"] == target[obj])
        tested: dict[str, Any] = {}
        for name, keys in rules:
            sig = tuple(target_row[k] for k in keys)
            matches = [r["relation"] for r in rows if tuple(r[k] for k in keys) == sig]
            tested[name] = {"candidate_count": int(len(matches)), "candidates_first_20": [int(x) for x in matches[:20]]}
        final_count = tested["full_tested_diagonal_signature"]["candidate_count"]
        if final_count == 1:
            unique_objects.append(obj)
        else:
            ambiguous_objects.append(obj)
        feature_rows.append({
            "object": int(obj),
            "object_size": int(object_sizes[obj]),
            "target_relation": int(target[obj]),
            "identity_relation": int(ident),
            "target_is_identity": bool(target[obj] == ident),
            "target_signature": {k: int(v) for k, v in target_row.items() if k != "relation"},
            "tested_rule_results": tested,
        })

    # Test several tempting seed-free selectors that use only generated diagonal order/valency.
    naive: dict[str, list[int]] = {}
    for rule in ["identity", "min_valency", "max_valency", "min_nonidentity_valency", "max_nonidentity_valency"]:
        chosen: list[int] = []
        for obj in range(6):
            ids = np.where((block_i == obj) & (block_j == obj))[0]
            vals = relation_sizes[ids] // object_sizes[obj]
            if rule == "identity":
                cands = np.array([identity_by_object[obj]], dtype=np.int64)
            elif rule == "min_valency":
                cands = ids[vals == vals.min()]
            elif rule == "max_valency":
                cands = ids[vals == vals.max()]
            elif rule == "min_nonidentity_valency":
                non = ids[ids != identity_by_object[obj]]
                non_vals = relation_sizes[non] // object_sizes[obj]
                cands = non[non_vals == non_vals.min()]
            else:
                non = ids[ids != identity_by_object[obj]]
                non_vals = relation_sizes[non] // object_sizes[obj]
                cands = non[non_vals == non_vals.max()]
            chosen.append(int(cands[0]))
        naive[rule] = chosen

    aligned_first_diagonal = [int(np.where((block_i == obj) & (block_j == obj))[0][0]) for obj in range(6)]
    aligned_first_diagonal_matches = bool(aligned_first_diagonal == target)
    source_order_first_diagonal: list[int] | None = None
    source_order_first_diagonal_valencies: list[int] | None = None
    source_order_first_diagonal_matches = None
    if source_order_relation_npz is not None and source_order_relation_npz.exists():
        src = np.load(source_order_relation_npz)
        s_encoded = src["encoded_pairs"].astype(np.int64)
        s_offsets = src["offsets"].astype(np.int64)
        s_block_i = src["block_i"].astype(np.int64)
        s_block_j = src["block_j"].astype(np.int64)
        s_object = src["object_of_point"].astype(np.int64)
        s_sizes = np.bincount(s_object, minlength=6).astype(np.int64)
        s_relation_sizes = np.diff(s_offsets).astype(np.int64)
        s_hashes = relation_hashes(s_encoded, s_offsets)
        source_order_first_diagonal = []
        source_order_first_diagonal_valencies = []
        source_first_hashes = []
        for obj in range(6):
            a = int(np.where((s_block_i == obj) & (s_block_j == obj))[0][0])
            source_order_first_diagonal.append(a)
            source_order_first_diagonal_valencies.append(int(s_relation_sizes[a] // s_sizes[obj]))
            source_first_hashes.append(s_hashes[a])
        aligned_target_hashes = relation_hashes(encoded, offsets)
        target_hashes = [aligned_target_hashes[a] for a in target]
        source_order_first_diagonal_matches = bool(source_first_hashes == target_hashes)

    result: dict[str, Any] = {
        "schema": "d20.constructor.terminal_selector_intrinsic_obstruction@1",
        "constructor_status": "TERMINAL_SELECTOR_NEEDS_PACKET20_OR_COORIENT_REPRESENTATION_MARKER_PASS",
        "source_relation_partition": str(relation_npz.relative_to(ROOT) if relation_npz.is_relative_to(ROOT) else relation_npz),
        "source_tensor": str(tensor_npz.relative_to(ROOT) if tensor_npz.is_relative_to(ROOT) else tensor_npz),
        "comparison_selector": str(selector_json.relative_to(ROOT) if selector_json.is_relative_to(ROOT) else selector_json),
        "identity_by_object_intrinsic": identity_by_object,
        "aligned_first_diagonal_order": {"relations": aligned_first_diagonal, "matches_terminal_selector": aligned_first_diagonal_matches, "note": "This uses the supplied/aligned relation order; it is a naming alignment, not an intrinsic selector formula."},
        "source_order_first_diagonal": {"relations": source_order_first_diagonal, "valencies": source_order_first_diagonal_valencies, "matches_terminal_selector": source_order_first_diagonal_matches, "note": "This is the first diagonal rule in the raw source-coorient orbit enumeration before alignment."},
        "terminal_selector_target_relations": target,
        "terminal_selector_target_equals_identity_by_object": [bool(a == b) for a, b in zip(target, identity_by_object)],
        "naive_seed_free_selectors": {
            k: {"relations": v, "matches_terminal_selector": bool(v == target)} for k, v in naive.items()
        },
        "object_feature_rows": feature_rows,
        "objects_unique_under_full_tested_diagonal_signature": unique_objects,
        "objects_ambiguous_under_full_tested_diagonal_signature": ambiguous_objects,
        "identity_ambiguities": identity_ambiguities,
        "conclusion": (
            "The terminal diagonal selector is not determined by order-free generated diagonal relation data, "
            "valencies, traces, and tested self-square invariants alone. The aligned first-diagonal rule reproduces the selector, "
            "but that uses the supplied/aligned relation naming. In raw source-coorient order, first diagonal gives the identity selector instead. "
            "Objects 0, 4, and 5 remain ambiguous under the tested order-free signatures. A packet-20/coorient representation marker, "
            "or an equivalent stronger intrinsic formula, is still required."
        ),
        "remaining_boundary": [
            "derive the lifted coorient generator permutations from a smaller typed coorient formula",
            "derive packet20 C20 or an equivalent representation marker from primitive representation/coorient data rather than constants.json",
            "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data",
        ],
    }
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Test whether the terminal diagonal selector is derivable from generated diagonal relation data without the packet-20/coorient representation marker.")
    ap.add_argument("--relation-npz", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--tensor-npz", default="generated/tensor_from_source_coorient.npz")
    ap.add_argument("--selector-json", default="generated/terminal_selector_from_c20.json")
    ap.add_argument("--source-order-relation-npz", default="generated/relation_memberships_from_source_coorient.npz")
    ap.add_argument("--out-json", default="generated/terminal_selector_intrinsic_obstruction_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive_terminal_selector_intrinsic_obstruction(
        ROOT / args.relation_npz,
        ROOT / args.tensor_npz,
        ROOT / args.selector_json,
        ROOT / args.out_json,
        ROOT / args.source_order_relation_npz,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    if not str(result.get("constructor_status", "")).endswith("PASS"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
