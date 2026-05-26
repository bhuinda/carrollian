from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from src.derive_terminal_quotients import derive_terminal_quotients, relation_hashes

ROOT = Path(__file__).resolve().parents[1]


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_c20(path: Path) -> tuple[np.ndarray, str]:
    if path.suffix == ".npz":
        z = np.load(path)
        return np.asarray(z["C20"], dtype=np.int64), str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    constants = load_json(path)
    return np.asarray(constants["packet20"]["C20"], dtype=np.int64), str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def derive_selector_from_c20(
    relation_npz: Path,
    c20_source: Path,
    out_selector_json: Path | None = None,
    out_quotient_npz: Path | None = None,
    out_report_json: Path | None = None,
    compare_selector_json: Path | None = None,
    compare_quotients_npz: Path | None = None,
    tensor_npz: Path | None = None,
) -> dict[str, Any]:
    rel = np.load(relation_npz)
    encoded = np.asarray(rel["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(rel["offsets"], dtype=np.int64)
    block_i = np.asarray(rel["block_i"], dtype=np.int16)
    block_j = np.asarray(rel["block_j"], dtype=np.int16)
    object_of_point = np.asarray(rel["object_of_point"], dtype=np.int16)
    c20, c20_source_label = load_c20(c20_source)
    object_sizes = np.bincount(object_of_point, minlength=6).astype(np.int64)
    relation_sizes = np.diff(offsets).astype(np.int64)
    hashes = relation_hashes(encoded, offsets)

    selected: list[int] = []
    rows: list[dict[str, Any]] = []
    ambiguity: list[dict[str, Any]] = []
    for obj in range(6):
        target_valency = int(c20[obj, obj])
        ids = np.where((block_i == obj) & (block_j == obj))[0].astype(int).tolist()
        candidates = [a for a in ids if int(relation_sizes[a] // object_sizes[obj]) == target_valency]
        if not candidates:
            raise ValueError(f"no diagonal relation for object {obj} has C20 diagonal valency {target_valency}")
        # Deterministic source-coorient order tie-breaker.  This order is produced by the
        # generated Be3 action on the generated dodecad list; it replaces six stored hashes.
        chosen = min(candidates)
        selected.append(chosen)
        if len(candidates) > 1:
            ambiguity.append({
                "object": obj,
                "target_valency": target_valency,
                "candidate_count": len(candidates),
                "tie_breaker": "minimum generated relation index in source-coorient orbit enumeration",
            })
        rows.append({
            "object": obj,
            "chosen_relation": int(chosen),
            "block": [int(block_i[chosen]), int(block_j[chosen])],
            "object_size": int(object_sizes[obj]),
            "relation_size": int(relation_sizes[chosen]),
            "valency": int(relation_sizes[chosen] // object_sizes[obj]),
            "c20_diagonal": target_valency,
            "candidate_count_same_valency": len(candidates),
            "relation_hash": hashes[chosen],
        })

    selector = {
        "schema": "d20.terminal_quotient_selector.from_packet20_diagonal@1",
        "purpose": "Derived selector: choose the diagonal terminal relation for each object by the packet-20 C20 diagonal valency, with deterministic source-coorient relation-order tie-break.",
        "object_labels": ["B-", "B+", "V-", "V+", "S-", "S+"],
        "sector_labels": ["B", "V", "S"],
        "sector_names": ["B", "V", "S"],
        "object_to_sector": [0, 0, 1, 1, 2, 2],
        "c20_diagonal": [int(c20[i, i]) for i in range(6)],
        "tie_breaker": "minimum generated relation index among diagonal relations with the required C20 diagonal valency",
        "diagonal_special_relation_hashes": [
            {
                "object": row["object"],
                "block": row["block"],
                "aligned_relation_index_for_reference": row["chosen_relation"],
                "size": row["relation_size"],
                "valency": row["valency"],
                "relation_hash": row["relation_hash"],
            }
            for row in rows
        ],
        "q42_label_rule": "0..5 special diagonal by object; 6..11 other diagonal by object; 12..41 off-diagonal ordered object pairs in lexicographic order i!=j.",
        "q12_label_rule": "0..2 special same-sector loops; 3..5 nonspecial same-sector transport; 6..11 cross-sector ordered pairs in lexicographic order s!=t.",
    }
    if out_selector_json is not None:
        out_selector_json.parent.mkdir(parents=True, exist_ok=True)
        out_selector_json.write_text(json.dumps(selector, indent=2, sort_keys=True), encoding="utf-8")

    comparison: dict[str, Any] = {}
    if compare_selector_json is not None and compare_selector_json.exists():
        prior = load_json(compare_selector_json)
        prior_hashes = [x["relation_hash"] for x in prior["diagonal_special_relation_hashes"]]
        new_hashes = [x["relation_hash"] for x in selector["diagonal_special_relation_hashes"]]
        comparison["matches_previous_six_hash_selector"] = bool(prior_hashes == new_hashes)
        comparison["previous_special_relation_indices"] = [int(x.get("aligned_relation_index_for_reference", -1)) for x in prior["diagonal_special_relation_hashes"]]

    quotient_result: dict[str, Any] | None = None
    if tensor_npz is not None and out_selector_json is not None:
        quotient_result = derive_terminal_quotients(
            relation_npz,
            tensor_npz,
            out_selector_json,
            out_quotient_npz,
            compare_quotients_npz,
        )

    ok = all(row["valency"] == row["c20_diagonal"] for row in rows)
    if comparison:
        ok = ok and comparison.get("matches_previous_six_hash_selector") is True
    if quotient_result is not None:
        ok = ok and quotient_result.get("constructor_status") == "TERMINAL_QUOTIENTS_PASS"

    result: dict[str, Any] = {
        "schema": "d20.constructor.terminal_selector_from_packet20_diagonal@1",
        "constructor_status": "TERMINAL_SELECTOR_FROM_PACKET20_DIAGONAL_PASS" if ok else "TERMINAL_SELECTOR_FROM_PACKET20_DIAGONAL_FAIL",
        "predicate": "is integral",
        "construction_method": "derive the six terminal diagonal selector hashes from packet-20 C20 diagonal valencies plus deterministic source-coorient relation ordering",
        "input_replaced": "six stored diagonal special relation hashes",
        "input_still_used": [
            "packet20 C20 diagonal from a generated packet20 C20 artifact or constants.json",
            "generated source-coorient relation ordering",
        ],
        "relation_npz": str(relation_npz.relative_to(ROOT)) if relation_npz.is_relative_to(ROOT) else str(relation_npz),
        "c20_source": c20_source_label,
        "object_sizes": object_sizes.astype(int).tolist(),
        "c20_diagonal": [int(c20[i, i]) for i in range(6)],
        "selected_relations": rows,
        "ambiguous_same_valency_classes_resolved_by_order": ambiguity,
        "selector_json": str(out_selector_json.relative_to(ROOT)) if out_selector_json is not None and out_selector_json.exists() and out_selector_json.is_relative_to(ROOT) else (str(out_selector_json) if out_selector_json is not None else None),
        "selector_sha256": hashlib.sha256(canonical(selector)).hexdigest(),
        "comparison": comparison,
        "terminal_quotients": quotient_result,
        "remaining_boundary_removed": [
            "the six terminal selector hashes are no longer primary seed data; they are derived from C20 diagonal valencies and generated source-coorient relation order",
        ],
        "remaining_boundary": [
            "derive packet20 C20 itself from primitive representation/coorient data instead of constants.json",
            "derive the fixed coorient generator permutations from a smaller typed coorient formula",
            "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data",
        ],
    }
    result["constructor_result_sha256"] = hashlib.sha256(canonical({k: v for k, v in result.items() if k != "constructor_result_sha256"})).hexdigest()
    if out_report_json is not None:
        out_report_json.parent.mkdir(parents=True, exist_ok=True)
        out_report_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Derive terminal selector from packet-20 C20 diagonal data.")
    ap.add_argument("--relation-npz", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--constants", default="data/raw/constants.json")
    ap.add_argument("--tensor-npz", default="generated/tensor_from_source_coorient.npz")
    ap.add_argument("--out-selector", default="generated/terminal_selector_from_c20.json")
    ap.add_argument("--out-npz", default="generated/terminal_quotients_from_c20_selector.npz")
    ap.add_argument("--out-json", default="generated/terminal_selector_from_c20_report.json")
    ap.add_argument("--compare-selector", default="data/quotient/terminal_quotient_selector.json")
    ap.add_argument("--compare-quotients", default="data/raw/quotients.npz")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive_selector_from_c20(
        ROOT / args.relation_npz,
        ROOT / args.constants,
        ROOT / args.out_selector,
        ROOT / args.out_npz,
        ROOT / args.out_json,
        ROOT / args.compare_selector,
        ROOT / args.compare_quotients,
        ROOT / args.tensor_npz,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    if not str(result.get("constructor_status", "")).endswith("PASS"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
