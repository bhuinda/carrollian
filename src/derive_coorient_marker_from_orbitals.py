from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from src.build_be3_from_coorient import close_group, invert_perm
    from src.derive_coorient_relator_profile_from_a0_a5 import (
        RELATOR_PROFILE_THEOREM_JSON,
        derive as derive_a0_a5_relator_profile,
    )
    from src.derive_lifted_coorient_generators_formula import build_label_matrix, reconstruct_perm_from_base_images, signature_keys
    from src.derive_pre_a985_relation_body import PRE_A985_THEOREM_JSON, ensure_pre_a985_relation_body
    from src.recover_be3_from_orbitals import closure_size, compose_index, load_seed, reconstruct_action_from_regular_orbital
except ImportError:
    from .build_be3_from_coorient import close_group, invert_perm
    from .derive_coorient_relator_profile_from_a0_a5 import (
        RELATOR_PROFILE_THEOREM_JSON,
        derive as derive_a0_a5_relator_profile,
    )
    from .derive_lifted_coorient_generators_formula import build_label_matrix, reconstruct_perm_from_base_images, signature_keys
    from .derive_pre_a985_relation_body import PRE_A985_THEOREM_JSON, ensure_pre_a985_relation_body
    from .recover_be3_from_orbitals import closure_size, compose_index, load_seed, reconstruct_action_from_regular_orbital
EXPECTED_GROUP_ORDER = 9216
EXPECTED_POINTS = 2576
EXPECTED_RELATIONS = 985


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def greedy_separating_base(labels: np.ndarray, length: int = 3) -> dict[str, Any]:
    n = labels.shape[0]
    base: list[int] = []
    current = None
    trace: list[dict[str, Any]] = []
    for step in range(length):
        best_count = -1
        best_candidates: list[int] = []
        for c in range(n):
            if c in base:
                continue
            cols = [labels[c, :], labels[:, c]]
            arr = np.column_stack([current] + cols) if current is not None else np.column_stack(cols)
            count = int(np.unique(arr, axis=0).shape[0])
            if count > best_count:
                best_count = count
                best_candidates = [c]
            elif count == best_count:
                best_candidates.append(c)
        chosen = min(best_candidates)
        base.append(chosen)
        cols = [labels[chosen, :], labels[:, chosen]]
        current = np.column_stack([current] + cols) if current is not None else np.column_stack(cols)
        trace.append({
            "step": step + 1,
            "chosen_point": chosen,
            "unique_two_sided_signatures": best_count,
            "lexicographic_tie_count": len(best_candidates),
            "first_ten_ties": best_candidates[:10],
        })
    separated = bool(current is not None and np.unique(current, axis=0).shape[0] == n)
    return {
        "base": base,
        "separates_all_points": separated,
        "trace": trace,
    }


def load_relator_profile(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    profile = payload.get("relator_profile", {})
    required = {"generator_orders", "pair_product_orders", "commutator_orders"}
    if not required <= set(profile):
        raise ValueError(f"{path} does not contain a complete relator_profile")
    return {
        "source_path": str(path.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "generator_orders": [int(x) for x in profile["generator_orders"]],
        "pair_product_orders": [[int(x) for x in row] for row in profile["pair_product_orders"]],
        "commutator_orders": [[int(x) for x in row] for row in profile["commutator_orders"]],
    }


def action_index(P: np.ndarray) -> dict[bytes, int]:
    return {P[i].tobytes(): i for i in range(P.shape[0])}


def inverse_indices(P: np.ndarray, index: dict[bytes, int]) -> list[int]:
    return [index[invert_perm(P[i]).tobytes()] for i in range(P.shape[0])]


def element_orders(P: np.ndarray, index: dict[bytes, int]) -> list[int]:
    def order(i: int) -> int:
        cur = i
        for k in range(1, 1000):
            if cur == 0:
                return k
            cur = compose_index(P, index, i, cur)
        raise ValueError(f"order search exceeded limit for element {i}")

    return [order(i) for i in range(P.shape[0])]


def select_generators_by_profile(P: np.ndarray, profile: dict[str, Any]) -> dict[str, Any]:
    index = action_index(P)
    inverses = inverse_indices(P, index)
    orders = element_orders(P, index)
    target_orders = [int(x) for x in profile["generator_orders"]]
    target_pair = profile["pair_product_orders"]
    target_comm = profile["commutator_orders"]
    target_count = len(target_orders)
    candidates_by_order: dict[int, list[int]] = {}
    for order in sorted(set(target_orders)):
        candidates_by_order[order] = [i for i, value in enumerate(orders) if value == order and i != 0]

    def comp(i: int, j: int) -> int:
        return compose_index(P, index, i, j)

    def comm(i: int, j: int) -> int:
        return comp(comp(comp(i, j), inverses[i]), inverses[j])

    def compatible(prefix: list[int], candidate: int) -> bool:
        j = len(prefix)
        for i, prior in enumerate(prefix):
            if orders[comp(prior, candidate)] != target_pair[i][j]:
                return False
            if orders[comp(candidate, prior)] != target_pair[j][i]:
                return False
            if orders[comm(prior, candidate)] != target_comm[i][j]:
                return False
            if orders[comm(candidate, prior)] != target_comm[j][i]:
                return False
        return True

    checks = 0
    def search(prefix: list[int]) -> list[int] | None:
        nonlocal checks
        pos = len(prefix)
        if pos == target_count:
            return prefix if closure_size(P, prefix) == P.shape[0] else None
        for candidate in candidates_by_order[target_orders[pos]]:
            checks += 1
            if candidate in prefix:
                continue
            if not compatible(prefix, candidate):
                continue
            hit = search(prefix + [candidate])
            if hit is not None:
                return hit
        return None

    selected = search([])
    if selected is None:
        raise ValueError("no generator tuple matches relator profile and full closure")
    return {
        "generator_indices": [int(x) for x in selected],
        "generator_orders": [int(orders[x]) for x in selected],
        "candidate_counts_by_order": {str(k): len(v) for k, v in candidates_by_order.items()},
        "profile_candidate_checks": checks,
    }


def derive(
    relation_npz: Path | None = None,
    word_presentation_json: Path | None = None,
) -> dict[str, Any]:
    if relation_npz is None:
        relation_npz = ensure_pre_a985_relation_body(regenerate=False)
    raw_relation = ROOT / "data" / "raw" / "relation_memberships.npz"
    relation_relpath = str(relation_npz.relative_to(ROOT))
    uses_raw_relation = relation_npz.resolve() == raw_relation.resolve()
    seed = load_seed(relation_npz)
    P, regular_meta = reconstruct_action_from_regular_orbital(seed)
    labels = build_label_matrix(seed["encoded_pairs"], seed["offsets"], seed["points"])
    base = greedy_separating_base(labels, 3)
    profile_theorem = derive_a0_a5_relator_profile(relation_npz)
    profile = {
        key: profile_theorem["relator_profile"][key]
        for key in ("generator_orders", "pair_product_orders", "commutator_orders")
    }
    selected = {
        "generator_indices": [int(x) for x in profile_theorem["selected_generators"]["generator_indices"]],
        "generator_orders": [int(x) for x in profile["generator_orders"]],
        "selection_rule": "A0-A5 reduced greedy full-closure basis",
        "profile_candidate_checks": 0,
    }
    gens = P[np.array(selected["generator_indices"], dtype=np.int64)].astype(np.int16)
    base_points = [int(x) for x in base["base"]]
    base_images = gens[:, base_points].astype(int).tolist()
    signature_base = [int(x) for x in regular_meta["base_points"]]
    signature_images = gens[:, signature_base].astype(int).tolist()
    reconstructed = np.vstack([
        reconstruct_perm_from_base_images(labels, base_points, row) for row in base_images
    ]).astype(np.int16)
    reconstructed_matches = bool(np.array_equal(reconstructed, gens))
    action, closure_trace = close_group(gens)
    result = {
        "schema": "d20.coorient.marker_from_orbitals@1",
        "status": "COORIENT_MARKER_DERIVED_FROM_ORBITALS_PASS"
        if reconstructed_matches
        and action.shape == (EXPECTED_GROUP_ORDER, EXPECTED_POINTS)
        and profile_theorem.get("status") == "COORIENT_RELATOR_PROFILE_FROM_A0_A5_PASS"
        else "COORIENT_MARKER_DERIVED_FROM_ORBITALS_FAIL",
        "construction_method": (
            "recover the 9216-element coherent lift group from the regular ordered-pair orbital, "
            "derive the relator profile by the A0-A5 reduced greedy full-closure basis rule, "
            "then read the selected generators' images on the derived separating base"
        ),
        "uses_coorient_marker_file": False,
        "uses_word_presentation_certificate": False,
        "uses_supplied_relation_partition": uses_raw_relation,
        "uses_pre_a985_generated_relation_body": not uses_raw_relation,
        "remaining_boundary": [],
        "relation_input": {
            "path": relation_relpath,
            "points": int(seed["points"]),
            "relations": int(seed["offsets"].size - 1),
            "group_order": int(seed["group_order"]),
            "relation_table_is_audit_target_only": not uses_raw_relation,
        },
        "relation_body_theorem": (
            {
                "path": str(PRE_A985_THEOREM_JSON.relative_to(ROOT)),
                "status": json.loads(PRE_A985_THEOREM_JSON.read_text(encoding="utf-8")).get("status"),
                "sha256": hashlib.sha256(PRE_A985_THEOREM_JSON.read_bytes()).hexdigest(),
            }
            if PRE_A985_THEOREM_JSON.exists() and not uses_raw_relation
            else None
        ),
        "regular_orbital_reconstruction": regular_meta,
        "relator_profile_derivation": {
            "path": str(RELATOR_PROFILE_THEOREM_JSON.relative_to(ROOT)),
            "status": profile_theorem.get("status"),
            "certificate_sha256": profile_theorem.get("certificate_sha256"),
        },
        "derived_relator_profile": profile,
        "canonical_base": {
            **base,
            "base_signature_unique_points": int(np.unique(signature_keys(labels, base_points)).size),
        },
        "selected_generators": {
            **selected,
            "base_points": base_points,
            "generator_base_images": base_images,
            "signature_base_points": signature_base,
            "signature_generator_base_images": signature_images,
            "generator_permutations_sha256": sha_array(gens),
            "reconstructed_from_base_images_sha256": sha_array(reconstructed),
            "reconstructed_matches_selected_generators": reconstructed_matches,
        },
        "closed_action": {
            "group_order": int(action.shape[0]),
            "degree": int(action.shape[1]),
            "closure_trace_last_values": [int(x) for x in closure_trace[-10:]],
            "action_sha256": sha_array(action),
        },
    }
    result["certificate_sha256"] = sha_json({k: v for k, v in result.items() if k != "certificate_sha256"})
    return result


def canonical_marker_formula(marker: dict[str, Any]) -> dict[str, Any]:
    selected = marker["selected_generators"]
    relation_path = marker["relation_input"]["path"]
    return {
        "schema": "d20.coorient.lift.canonical_marker_formula@1",
        "d6_marker": "marked D6 Coxeter-polarity d20 selector; canonical separating base derived from two-sided coherent relation signatures",
        "formula": (
            "Derive the 9216 coherent lifts from the regular ordered-pair orbital, select the "
            "A0-A5 reduced greedy full-closure generator basis, then "
            "reconstruct each full permutation from its images on the canonical separating base."
        ),
        "base_selection": "greedy max unique two-sided relation signatures, lexicographic tie-break",
        "base_points": selected["base_points"],
        "generator_base_images": selected["generator_base_images"],
        "generator_indices": selected["generator_indices"],
        "expected_closure_order": EXPECTED_GROUP_ORDER,
        "expected_pair_orbitals": EXPECTED_RELATIONS,
        "relation_body_source": relation_path,
        "derived_from": f"{relation_path} plus data/invariants/d20/coorient_relator_profile_from_a0_a5.json",
    }


def signature_formula(marker: dict[str, Any]) -> dict[str, Any]:
    selected = marker["selected_generators"]
    relation_path = marker["relation_input"]["path"]
    return {
        "schema": "d20.coorient.lift.signature_formula@1",
        "d6_marker": "marked D6 Coxeter-polarity d20 selector; generator basis fixed by the derived A0-A5 relator-profile rule",
        "formula": (
            "For each listed base-image tuple, reconstruct the unique permutation of the 2576 dodecads "
            "preserving all coherent relation labels. The base-image tuples are derived from the regular "
            "ordered-pair orbital and the A0-A5 relator profile, not read as a marker seed."
        ),
        "base_points": selected["signature_base_points"],
        "generator_base_images": selected["signature_generator_base_images"],
        "generator_indices": selected["generator_indices"],
        "expected_closure_order": EXPECTED_GROUP_ORDER,
        "expected_orbit_sizes": [384, 192, 144, 576, 512, 768],
        "expected_pair_orbitals": EXPECTED_RELATIONS,
        "relation_body_source": relation_path,
        "derived_from": f"{relation_path} plus data/invariants/d20/coorient_relator_profile_from_a0_a5.json",
    }


def write_outputs(
    marker: dict[str, Any],
    coorient_dir: Path = ROOT / "data" / "coorient",
    relation_npz: Path | None = None,
) -> None:
    coorient_dir.mkdir(parents=True, exist_ok=True)
    (coorient_dir / "lifted_coorient_canonical_marker_formula.json").write_text(
        json.dumps(canonical_marker_formula(marker), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (coorient_dir / "lifted_coorient_signature_formula.json").write_text(
        json.dumps(signature_formula(marker), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    relation_path = relation_npz
    if relation_path is None:
        relation_path = ROOT / marker["relation_input"]["path"]
    seed = load_seed(relation_path)
    labels = build_label_matrix(seed["encoded_pairs"], seed["offsets"], seed["points"])
    gens = np.vstack([
        reconstruct_perm_from_base_images(labels, marker["selected_generators"]["base_points"], row)
        for row in marker["selected_generators"]["generator_base_images"]
    ]).astype(np.int16)
    np.savez_compressed(
        coorient_dir / "be3_coorient_generators.npz",
        generator_permutations=gens,
        generator_indices=np.array(marker["selected_generators"]["generator_indices"], dtype=np.int32),
        base_points=np.array(marker["selected_generators"]["base_points"], dtype=np.int16),
        generator_base_images=np.array(marker["selected_generators"]["generator_base_images"], dtype=np.int16),
        derivation_source=np.array([f"{marker['relation_input']['path']} plus A0-A5 relator profile"]),
    )


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Derive coorient marker images from the regular orbital instead of marker seed data.")
    ap.add_argument("--relation", default=None)
    ap.add_argument("--word-presentation", default=None, help="Deprecated; the relator profile is derived from A0-A5.")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    relation = ROOT / args.relation if args.relation else None
    result = derive(relation, ROOT / args.word_presentation if args.word_presentation else None)
    if args.write:
        write_outputs(result, relation_npz=relation)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
