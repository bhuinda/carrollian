#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
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
    from src.paths import D20_INVARIANTS
    from src.derive_absolute_coorient_word_presentation import order_tables
    from src.derive_pre_a985_relation_body import PRE_A985_THEOREM_JSON, ensure_pre_a985_relation_body
    from src.recover_be3_from_orbitals import (
        closure_size,
        find_generators,
        load_seed,
        reconstruct_action_from_regular_orbital,
    )
except ImportError:
    from .paths import D20_INVARIANTS
    from .derive_absolute_coorient_word_presentation import order_tables
    from .derive_pre_a985_relation_body import PRE_A985_THEOREM_JSON, ensure_pre_a985_relation_body
    from .recover_be3_from_orbitals import (
        closure_size,
        find_generators,
        load_seed,
        reconstruct_action_from_regular_orbital,
    )


RELATOR_PROFILE_THEOREM_JSON = D20_INVARIANTS / "coorient_relator_profile_from_a0_a5.json"
EXPECTED_GROUP_ORDER = 9216
EXPECTED_POINTS = 2576
EXPECTED_RELATIONS = 985


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def reduce_generator_basis(P: np.ndarray, initial: list[int]) -> dict[str, Any]:
    """Delete redundant greedy generators while preserving full closure.

    At each deletion round, every one-generator deletion is tested.  If more than
    one deletion still closes the full group, the lexicographically smallest
    remaining tuple is kept.  This keeps the rule deterministic without reading
    any word-presentation certificate.
    """
    target = int(P.shape[0])
    basis = [int(x) for x in initial]
    deletion_steps: list[dict[str, Any]] = []
    tested_deletions: list[dict[str, Any]] = []

    while len(basis) > 1:
        removable: list[tuple[list[int], int, int, int]] = []
        for pos, removed in enumerate(basis):
            trial = basis[:pos] + basis[pos + 1 :]
            size = int(closure_size(P, trial)) if trial else 1
            row = {
                "from_basis": basis,
                "removed_index": int(removed),
                "remaining_basis": trial,
                "closure_size": size,
                "preserves_full_closure": bool(size == target),
            }
            tested_deletions.append(row)
            if size == target:
                removable.append((trial, pos, int(removed), size))
        if not removable:
            break
        trial, pos, removed, size = min(removable, key=lambda item: tuple(item[0]))
        deletion_steps.append(
            {
                "removed_position": int(pos),
                "removed_index": int(removed),
                "chosen_remaining_basis": trial,
                "closure_size": int(size),
            }
        )
        basis = trial

    return {
        "generator_indices": basis,
        "deletion_steps": deletion_steps,
        "tested_deletions": tested_deletions,
        "deletion_minimal": not any(row["preserves_full_closure"] for row in tested_deletions[-len(basis) :])
        if basis
        else True,
    }


def derive(relation_npz: Path | None = None) -> dict[str, Any]:
    if relation_npz is None:
        relation_npz = ensure_pre_a985_relation_body(regenerate=False)
    seed = load_seed(relation_npz)
    P, regular_meta = reconstruct_action_from_regular_orbital(seed)
    greedy_indices, greedy_closure_sizes = find_generators(P)
    reduced = reduce_generator_basis(P, greedy_indices)
    selected_indices = [int(x) for x in reduced["generator_indices"]]
    selected = P[np.array(selected_indices, dtype=np.int64)].astype(np.int16)
    selected_closure = int(closure_size(P, selected_indices)) if selected_indices else 1
    relator_profile = order_tables(selected.astype(np.int64))
    checks = {
        "relation_body_path": str(relation_npz.relative_to(ROOT)),
        "relation_count": int(seed["offsets"].size - 1),
        "point_count": int(seed["points"]),
        "recovered_action_order": int(P.shape[0]),
        "greedy_basis_closes_full_group": bool(greedy_closure_sizes and greedy_closure_sizes[-1] == P.shape[0]),
        "reduced_basis_closes_full_group": bool(selected_closure == P.shape[0]),
        "derived_generator_count": int(len(selected_indices)),
        "derived_generator_count_is_positive": bool(len(selected_indices) > 0),
        "uses_word_presentation_certificate": False,
        "pre_a985_theorem_present": PRE_A985_THEOREM_JSON.exists(),
    }
    status_ok = bool(
        checks["relation_count"] == EXPECTED_RELATIONS
        and checks["point_count"] == EXPECTED_POINTS
        and checks["recovered_action_order"] == EXPECTED_GROUP_ORDER
        and checks["greedy_basis_closes_full_group"]
        and checks["reduced_basis_closes_full_group"]
        and checks["derived_generator_count_is_positive"]
    )
    result = {
        "schema": "d20.coorient.relator_profile_from_A0_A5@1",
        "status": "COORIENT_RELATOR_PROFILE_FROM_A0_A5_PASS" if status_ok else "COORIENT_RELATOR_PROFILE_FROM_A0_A5_FAIL",
        "construction_method": (
            "recover the coherent lift group from the pre-A985 generated relation body; "
            "extract generators by increasing recovered action index; delete redundant "
            "generators by lexicographically minimal full-closure deletion; compute the "
            "relator profile from the resulting basis"
        ),
        "input_axioms": {
            "A0_source": "H8^3 source constructor and Golay dodecad shell",
            "A1_relation_body": "pre-A985 generated 985-class ordered-pair relation body",
            "A2_coherent_lifts": "permutations preserving two-sided coherent relation signatures",
            "A3_integral_closure": "the coherent lift group has order 9216",
            "A4_generator_basis_rule": "deterministic greedy expansion followed by lexicographic deletion reduction",
            "A5_profile_readout": "orders of generators, pair products, and commutators of the derived basis",
        },
        "source_files": {
            "relation_body": {
                "path": str(relation_npz.relative_to(ROOT)),
                "sha256": hashlib.sha256(relation_npz.read_bytes()).hexdigest(),
            },
            "relation_body_theorem": {
                "path": str(PRE_A985_THEOREM_JSON.relative_to(ROOT)),
                "present": PRE_A985_THEOREM_JSON.exists(),
                "sha256": hashlib.sha256(PRE_A985_THEOREM_JSON.read_bytes()).hexdigest()
                if PRE_A985_THEOREM_JSON.exists()
                else None,
            },
        },
        "regular_orbital_reconstruction": regular_meta,
        "basis_derivation": {
            "action_index_convention": "rows are ordered by the regular orbital reconstruction over the generated relation body",
            "greedy_generator_indices": [int(x) for x in greedy_indices],
            "greedy_closure_sizes": [int(x) for x in greedy_closure_sizes],
            "reduced_generator_indices": selected_indices,
            "reduced_closure_size": selected_closure,
            "deletion_reduction": reduced,
        },
        "selected_generators": {
            "generator_indices": selected_indices,
            "generator_permutations_sha256": sha_array(selected),
        },
        "relator_profile": relator_profile,
        "checks": checks,
    }
    result["certificate_sha256"] = sha_json({k: v for k, v in result.items() if k != "certificate_sha256"})
    return result


def write_report(result: dict[str, Any], path: Path = RELATOR_PROFILE_THEOREM_JSON) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_coorient_relator_profile(relation_npz: Path | None = None, *, write: bool = True) -> dict[str, Any]:
    result = derive(relation_npz)
    if write:
        write_report(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Derive the coorient relator profile from the A0-A5 finite data.")
    parser.add_argument("--relation", default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    relation = ROOT / args.relation if args.relation else None
    result = derive(relation)
    if args.write:
        write_report(result)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
