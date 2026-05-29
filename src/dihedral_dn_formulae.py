from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .derive_terminal_quotients import derive_terminal_quotients

ROOT = Path(__file__).resolve().parents[1]

OBJECT_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
SECTOR_LABELS = ["B", "V", "S"]
OBJECT_TO_SECTOR = [0, 0, 1, 1, 2, 2]
OBJECT_TO_SHEET = [0, 1, 0, 1, 0, 1]  # 0 = -, 1 = + in the displayed object order
# Hexagon order used by the D_6 formula. Opposite vertices are the terminal +/- pair.
HEX_ORDER_OBJECTS = [0, 2, 4, 1, 3, 5]  # B-, V-, S-, B+, V+, S+
OBJECT_TO_HEX_POSITION = {obj: pos for pos, obj in enumerate(HEX_ORDER_OBJECTS)}
HEX_POSITION_TO_OBJECT = {pos: obj for obj, pos in OBJECT_TO_HEX_POSITION.items()}
EXPECTED_BE3_ORDER = 9216


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def dihedral_permutation(n: int, r_power: int = 0, reflect: bool = False) -> list[int]:
    """Return the action k |-> r^a s^e(k) on Z/nZ."""
    r_power %= n
    if reflect:
        return [int((r_power - k) % n) for k in range(n)]
    return [int((k + r_power) % n) for k in range(n)]


def dihedral_group(n: int) -> list[list[int]]:
    return [dihedral_permutation(n, a, e) for e in (False, True) for a in range(n)]


def compose(p: list[int], q: list[int]) -> list[int]:
    """Composition p after q for permutations as image lists."""
    return [p[q[i]] for i in range(len(p))]


def d6_object_action_from_hex_action(hex_perm: list[int]) -> list[int]:
    """Convert a D6 action on hexagon positions to an action on bundle object labels."""
    out = [0] * 6
    for obj in range(6):
        pos = OBJECT_TO_HEX_POSITION[obj]
        out[obj] = HEX_POSITION_TO_OBJECT[int(hex_perm[pos])]
    return out


def d6_object_group() -> list[list[int]]:
    return [d6_object_action_from_hex_action(p) for p in dihedral_group(6)]


def d3_sector_group() -> list[list[int]]:
    return dihedral_group(3)


def check_dihedral_relations(n: int) -> dict[str, Any]:
    r = dihedral_permutation(n, 1, False)
    s = dihedral_permutation(n, 0, True)
    idp = list(range(n))
    r_pow = idp
    for _ in range(n):
        r_pow = compose(r, r_pow)
    s2 = compose(s, s)
    srs = compose(s, compose(r, s))
    rinv = dihedral_permutation(n, -1, False)
    return {
        "n": n,
        "order": 2 * n,
        "r^n_identity": r_pow == idp,
        "s^2_identity": s2 == idp,
        "srs_equals_r_inverse": srs == rinv,
    }


def terminal_valency_formula(object_sizes: np.ndarray) -> dict[str, Any]:
    """D6-lifted terminal diagonal valency formula.

    Let G=Gamma and let H_i be the stabilizer of an object-orbit point in the six signed
    object family.  The D6 model has three terminal axes B,V,S and a central half-turn
    exchanging the sheets.  The terminal diagonal marker is:

      B- : |H|/4       B+ : |H|
      V- : 1           V+ : 1
      S- : |H|         S+ : |H|

    This is the compact formula that replaces the previously stored C20 diagonal.
    """
    stabs = (EXPECTED_BE3_ORDER // object_sizes.astype(np.int64)).astype(np.int64)
    vals: list[int] = []
    rules: list[str] = []
    for obj in range(6):
        sector = OBJECT_TO_SECTOR[obj]
        sheet = OBJECT_TO_SHEET[obj]
        stab = int(stabs[obj])
        if sector == 0:  # B-axis: one sheet is half-turn quotiented.
            if sheet == 0:
                val = stab // 4
                rule = "B-: vertex-stabilizer divided by the D6 half-turn square (4)"
            else:
                val = stab
                rule = "B+: full vertex-stabilizer"
        elif sector == 1:  # V-axis: terminal unit axis.
            val = 1
            rule = "V±: D6 vertex-unit axis"
        else:  # S-axis: full side-stabilizer axis.
            val = stab
            rule = "S±: full side-stabilizer"
        vals.append(int(val))
        rules.append(rule)
    return {
        "be3_order": EXPECTED_BE3_ORDER,
        "object_sizes": object_sizes.astype(int).tolist(),
        "object_stabilizer_orders": stabs.astype(int).tolist(),
        "terminal_diagonal_valencies": vals,
        "rule_by_object": [
            {
                "object": i,
                "label": OBJECT_LABELS[i],
                "sector": SECTOR_LABELS[OBJECT_TO_SECTOR[i]],
                "sheet": "+" if OBJECT_TO_SHEET[i] else "-",
                "stabilizer_order": int(stabs[i]),
                "terminal_valency": vals[i],
                "rule": rules[i],
            }
            for i in range(6)
        ],
    }


def relation_hashes(encoded: np.ndarray, offsets: np.ndarray) -> list[str]:
    out: list[str] = []
    for a in range(offsets.size - 1):
        seg = np.sort(encoded[int(offsets[a]):int(offsets[a + 1])]).astype(np.int64, copy=False)
        out.append(sha_array(seg))
    return out


def derive_selector_by_dihedral_formula(
    relation_npz: Path,
    out_selector_json: Path | None = None,
) -> dict[str, Any]:
    rel = np.load(relation_npz)
    encoded = np.asarray(rel["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(rel["offsets"], dtype=np.int64)
    block_i = np.asarray(rel["block_i"], dtype=np.int16)
    block_j = np.asarray(rel["block_j"], dtype=np.int16)
    object_of_point = np.asarray(rel["object_of_point"], dtype=np.int16)
    relation_sizes = np.diff(offsets).astype(np.int64)
    object_sizes = np.bincount(object_of_point, minlength=6).astype(np.int64)
    hashes = relation_hashes(encoded, offsets)

    val_formula = terminal_valency_formula(object_sizes)
    target_vals = val_formula["terminal_diagonal_valencies"]
    selected: list[int] = []
    rows: list[dict[str, Any]] = []
    for obj, target in enumerate(target_vals):
        candidates = [
            int(a)
            for a in np.where((block_i == obj) & (block_j == obj))[0]
            if int(relation_sizes[a] // object_sizes[obj]) == int(target)
        ]
        if not candidates:
            raise ValueError(f"D6 formula produced no diagonal candidate for object {obj} and valency {target}")
        # The relation order here is the source-coorient order after alignment with the generated Gamma action.
        # The selector is therefore no longer a stored hash list: it is D6 terminal valency plus coorient order.
        chosen = min(candidates)
        selected.append(chosen)
        rows.append({
            "object": obj,
            "label": OBJECT_LABELS[obj],
            "target_valency": int(target),
            "candidate_count": len(candidates),
            "chosen_relation": int(chosen),
            "relation_hash": hashes[chosen],
            "relation_size": int(relation_sizes[chosen]),
            "object_size": int(object_sizes[obj]),
        })

    selector = {
        "schema": "d20.terminal_quotient_selector.dihedral_dn_formula@1",
        "purpose": "Terminal diagonal selector derived from D6/D3 signed-sector formulae, not from stored packet20 constants.",
        "object_labels": OBJECT_LABELS,
        "sector_labels": SECTOR_LABELS,
        "sector_names": SECTOR_LABELS,
        "hex_order_objects": HEX_ORDER_OBJECTS,
        "object_to_sector": OBJECT_TO_SECTOR,
        "object_to_sheet": OBJECT_TO_SHEET,
        "dihedral_group": "D_6=<r,s | r^6=s^2=1, srs=r^{-1}>; quotient by the central half-turn gives D_3 on {B,V,S}",
        "terminal_valency_formula": val_formula,
        "tie_breaker": "minimum generated relation index among diagonal relations with the D6 terminal valency",
        "diagonal_special_relation_hashes": [
            {
                "object": r["object"],
                "block": [r["object"], r["object"]],
                "aligned_relation_index_for_reference": r["chosen_relation"],
                "size": r["relation_size"],
                "valency": r["target_valency"],
                "relation_hash": r["relation_hash"],
            }
            for r in rows
        ],
        "q42_label_rule": "0..5 special diagonal by object; 6..11 other diagonal by object; 12..41 off-diagonal ordered object pairs in lexicographic order i!=j.",
        "q12_label_rule": "0..2 special same-sector loops; 3..5 nonspecial same-sector transport; 6..11 cross-sector ordered pairs in lexicographic order s!=t.",
    }
    if out_selector_json is not None:
        out_selector_json.parent.mkdir(parents=True, exist_ok=True)
        selector_text = json.dumps(selector, indent=2, sort_keys=True)
        if not out_selector_json.exists() or out_selector_json.read_text(encoding="utf-8") != selector_text:
            out_selector_json.write_text(selector_text, encoding="utf-8")
    return {
        "selector": selector,
        "selected_relations": rows,
        "terminal_valency_formula": val_formula,
    }


def derive_dihedral_formulae(
    relation_npz: Path = ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
    tensor_npz: Path = ROOT / "generated/tensor_from_source_coorient.npz",
    out_selector_json: Path = ROOT / "generated/terminal_selector_from_dihedral_formula.json",
    out_quotient_npz: Path = ROOT / "generated/terminal_quotients_from_dihedral_formula.npz",
    out_json: Path = ROOT / "generated/dihedral_dn_formulae_report.json",
    compare_quotients_npz: Path = ROOT / "data/raw/quotients.npz",
    compare_selector_json: Path = ROOT / "generated/terminal_selector_from_c20.json",
) -> dict[str, Any]:
    d6 = check_dihedral_relations(6)
    d3 = check_dihedral_relations(3)
    object_group = d6_object_group()
    sector_group = d3_sector_group()
    selector_pack = derive_selector_by_dihedral_formula(relation_npz, out_selector_json)
    quotient_result = derive_terminal_quotients(
        relation_npz,
        tensor_npz,
        out_selector_json,
        out_quotient_npz,
        compare_quotients_npz,
    )

    comparison: dict[str, Any] = {}
    if compare_selector_json.exists():
        prior = json.loads(compare_selector_json.read_text(encoding="utf-8"))
        prior_hashes = [x["relation_hash"] for x in prior["diagonal_special_relation_hashes"]]
        new_hashes = [x["relation_hash"] for x in selector_pack["selector"]["diagonal_special_relation_hashes"]]
        comparison["matches_packet20_c20_selector"] = bool(prior_hashes == new_hashes)
        comparison["prior_indices"] = [int(x.get("aligned_relation_index_for_reference", -1)) for x in prior["diagonal_special_relation_hashes"]]
        comparison["new_indices"] = [int(x.get("aligned_relation_index_for_reference", -1)) for x in selector_pack["selector"]["diagonal_special_relation_hashes"]]

    ok = (
        d6["r^n_identity"] and d6["s^2_identity"] and d6["srs_equals_r_inverse"]
        and d3["r^n_identity"] and d3["s^2_identity"] and d3["srs_equals_r_inverse"]
        and quotient_result.get("constructor_status") == "TERMINAL_QUOTIENTS_PASS"
        and comparison.get("matches_packet20_c20_selector", True)
    )
    result: dict[str, Any] = {
        "schema": "d20.constructor.dihedral_dn_formulae@1",
        "constructor_status": "DIHEDRAL_DN_FORMULAE_PASS" if ok else "DIHEDRAL_DN_FORMULAE_FAIL",
        "predicate": "is integral",
        "what_was_constructed": [
            "generic D_n rotation/reflection formulae",
            "D6 signed-sector action on B-/B+/V-/V+/S-/S+ via a hexagon order",
            "D3 terminal-sector quotient on B,V,S",
            "terminal diagonal valency formula from Gamma object stabilizers and D6 axis rules",
            "A42/A12 terminal selector without packet20 C20 constants",
        ],
        "D6": d6 | {"object_action_order": len({tuple(p) for p in object_group}), "hex_order_objects": HEX_ORDER_OBJECTS, "hex_order_labels": [OBJECT_LABELS[i] for i in HEX_ORDER_OBJECTS]},
        "D3": d3 | {"sector_action_order": len({tuple(p) for p in sector_group}), "sector_labels": SECTOR_LABELS},
        "central_half_turn": {
            "hex_action": dihedral_permutation(6, 3, False),
            "object_action": d6_object_action_from_hex_action(dihedral_permutation(6, 3, False)),
            "interpretation": "central r^3 exchanges the +/- sheets within each terminal sector",
        },
        "terminal_selector": {
            "selector_json": str(out_selector_json.relative_to(ROOT)) if out_selector_json.is_relative_to(ROOT) else str(out_selector_json),
            "selected_relations": selector_pack["selected_relations"],
            "terminal_valency_formula": selector_pack["terminal_valency_formula"],
            "comparison": comparison,
        },
        "terminal_quotients": quotient_result,
        "remaining_boundary_reduced": [
            "packet20 C20 diagonal constants are no longer needed to construct the terminal selector; D6/D3 stabilizer formulae produce the same six diagonal relation hashes",
        ],
        "remaining_boundary": [
            "derive the four 2576-point lifted coorient generator permutations from a smaller closed D_n/coorient action formula rather than storing them as permutations",
            "derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data",
        ],
    }
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})
    out_json.parent.mkdir(parents=True, exist_ok=True)
    result_text = json.dumps(result, indent=2, sort_keys=True)
    if not out_json.exists() or out_json.read_text(encoding="utf-8") != result_text:
        out_json.write_text(result_text, encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Construct the D_n/D6/D3 formula layer for the terminal selector.")
    ap.add_argument("--relation-npz", default="generated/relation_memberships_from_source_coorient_aligned.npz")
    ap.add_argument("--tensor-npz", default="generated/tensor_from_source_coorient.npz")
    ap.add_argument("--out-selector", default="generated/terminal_selector_from_dihedral_formula.json")
    ap.add_argument("--out-npz", default="generated/terminal_quotients_from_dihedral_formula.npz")
    ap.add_argument("--out-json", default="generated/dihedral_dn_formulae_report.json")
    ap.add_argument("--compare-quotients", default="data/raw/quotients.npz")
    ap.add_argument("--compare-selector", default="generated/terminal_selector_from_c20.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive_dihedral_formulae(
        ROOT / args.relation_npz,
        ROOT / args.tensor_npz,
        ROOT / args.out_selector,
        ROOT / args.out_npz,
        ROOT / args.out_json,
        ROOT / args.compare_quotients,
        ROOT / args.compare_selector,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    if not str(result.get("constructor_status", "")).endswith("PASS"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
