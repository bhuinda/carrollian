#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime import ensure_numpy_runtime

ensure_numpy_runtime(ROOT, __file__)

from src.certify_constructor import (
    COMPLETED_FULL_SCRATCH_STEPS,
    MISSING_FULL_SCRATCH_STEPS,
    construct_from_supplied_raw_seeds,
    stable_constructor_sha_json,
)
from src.certify_io import raw_tensor_relpath
from src.paths import D20_INVARIANTS, GENERATED, ROOT
from src.token_burn_guard import emit_json


def is_full_scratch_constructor(result: dict) -> bool:
    return (
        result.get("full_scratch_object_constructor") is True
        and result.get("constructs_from_supplied_raw_seeds") is False
        and str(result.get("constructor_status", "")).endswith("_PASS")
    )


def mark_strict_scratch_blocked(result: dict) -> dict:
    previous_status = result.get("constructor_status")
    result["strict_scratch_required"] = True
    result["strict_scratch_passed"] = False
    result["constructor_status"] = "D20_FULL_SCRATCH_BLOCKED"
    result["full_scratch_object_constructor"] = False
    result["blocked_reason"] = (
        "The bundle can regenerate the certified object from checked source data "
        "and compact raw seeds, but it still has an explicit non-scratch boundary."
    )
    result["blocked_previous_constructor_status"] = previous_status
    result["remaining_boundary"] = (
        result.get("missing_full_scratch_steps")
        or result.get("remaining_boundary")
        or MISSING_FULL_SCRATCH_STEPS
    )
    result["completed_full_scratch_steps"] = result.get(
        "completed_full_scratch_steps",
        COMPLETED_FULL_SCRATCH_STEPS,
    )
    result["next_high_yield_step"] = result["remaining_boundary"][0] if result["remaining_boundary"] else None
    result["constructor_result_sha256"] = stable_constructor_sha_json(result)
    return result


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _prefer_existing(primary: Path, fallback: Path) -> Path:
    return primary if primary.exists() else fallback


def _relation_summary(path: Path) -> dict[str, Any]:
    import numpy as np

    z = np.load(path)
    encoded = np.asarray(z["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(z["offsets"], dtype=np.int64)
    object_of_point = np.asarray(z["object_of_point"], dtype=np.int64)
    block_i = np.asarray(z["block_i"], dtype=np.int64)
    block_j = np.asarray(z["block_j"], dtype=np.int64)
    points = int(np.asarray(z["points"]).reshape(-1)[0])
    relation_sizes = np.diff(offsets).astype(np.int64)
    object_sizes = np.bincount(object_of_point, minlength=6).astype(np.int64)
    relation_count_matrix = np.zeros((6, 6), dtype=np.int64)
    block_mass = np.zeros((6, 6), dtype=np.int64)
    for idx, size in enumerate(relation_sizes):
        i, j = int(block_i[idx]), int(block_j[idx])
        relation_count_matrix[i, j] += 1
        block_mass[i, j] += int(size)
    seen = np.zeros(points * points, dtype=np.bool_)
    seen[encoded] = True
    return {
        "path": _rel(path),
        "points": points,
        "relations": int(offsets.size - 1),
        "ordered_pair_partition_size": int(encoded.size),
        "ordered_pair_partition_ok": bool(seen.all() and int(seen.sum()) == points * points and encoded.size == points * points),
        "group_order": int(np.asarray(z["group_order"]).reshape(-1)[0]),
        "object_sizes": object_sizes.astype(int).tolist(),
        "object_pair_relation_matrix": relation_count_matrix.astype(int).tolist(),
        "block_mass_is_object_size_outer_product": bool(np.array_equal(block_mass, np.outer(object_sizes, object_sizes))),
    }


def construct_from_generated_strict_scratch_pipeline() -> dict[str, Any]:
    from src.build_orbit_tensor import compute_tensor_from_orbitals
    from src.derive_absolute_coorient_word_presentation import derive as derive_absolute_word
    from src.derive_a236_generated_branching_boundary import derive_boundary as derive_a236_boundary
    from src.derive_a236_profunctor_from_tube_cache import derive_profunctor as derive_a236_profunctor
    from src.derive_center_idempotents_from_t985 import derive_center_idempotents
    from src.derive_lifted_coorient_generators_formula import derive_formula as derive_lifted_generators
    from src.derive_native_a236_formulae import derive as derive_native_a236
    from src.derive_packet20_c20_from_d6_stabilizers import derive as derive_packet20_c20
    from src.derive_pre_a985_relation_body import ensure_pre_a985_relation_body
    from src.dihedral_dn_formulae import derive_dihedral_formulae

    pre_relation = ensure_pre_a985_relation_body(regenerate=False, write_report=True)
    pre_report_path = GENERATED / "pre_A985_source_to_relation_body_report.json"
    if not pre_report_path.exists():
        pre_relation = ensure_pre_a985_relation_body(regenerate=True, write_report=True)
    pre_report = _load_json(pre_report_path)

    strict_formula_relation = GENERATED / "strict_scratch_relation_memberships_from_canonical_marker.npz"
    formula = derive_lifted_generators(
        pre_relation,
        ROOT / "data/coorient/lifted_coorient_canonical_marker_formula.json",
        ROOT / "data/coorient/be3_coorient_generators.npz",
        GENERATED / "strict_scratch_lifted_coorient_generators.npz",
        strict_formula_relation,
        GENERATED / "strict_scratch_lifted_coorient_generators_report.json",
    )
    absolute = derive_absolute_word(
        strict_formula_relation,
        D20_INVARIANTS / "d20_d6_selector_derivation.json",
        ROOT / "data/coorient/lifted_coorient_canonical_marker_formula.json",
        GENERATED / "strict_scratch_lifted_coorient_generators.npz",
        GENERATED / "strict_scratch_absolute_d20_word_presentation.json",
        GENERATED / "strict_scratch_lifted_coorient_generators_from_word_presentation.npz",
        GENERATED / "strict_scratch_relation_memberships_from_word_presentation.npz",
        GENERATED / "strict_scratch_be3_action_words.npz",
        GENERATED / "strict_scratch_absolute_coorient_word_presentation_report.json",
    )

    strict_tensor = GENERATED / "strict_scratch_tensor_from_pre_a985.npz"
    tensor = compute_tensor_from_orbitals(
        pre_relation,
        strict_tensor,
        ROOT / raw_tensor_relpath(),
        None,
        False,
    )
    c20 = derive_packet20_c20(
        pre_relation,
        ROOT / "data/raw/constants.json",
        GENERATED / "strict_scratch_packet20_C20_from_d6_stabilizers.npz",
        GENERATED / "strict_scratch_packet20_C20_from_d6_stabilizers_report.json",
    )
    terminal = derive_dihedral_formulae(
        pre_relation,
        strict_tensor,
        GENERATED / "strict_scratch_terminal_selector_from_dihedral_formula.json",
        GENERATED / "strict_scratch_terminal_quotients_from_dihedral_formula.npz",
        GENERATED / "strict_scratch_dihedral_dn_formulae_report.json",
        ROOT / "data/raw/quotients.npz",
        GENERATED / "strict_scratch_terminal_selector_from_c20.json",
    )
    center = derive_center_idempotents(
        strict_tensor,
        None,
        pre_relation,
        GENERATED / "strict_scratch_terminal_quotients_from_dihedral_formula.npz",
        GENERATED / "strict_scratch_center_idempotents_from_generated_T985.npz",
        GENERATED / "strict_scratch_center_idempotents_from_generated_T985_report.json",
    )
    a236 = derive_native_a236(
        None,
        GENERATED / "strict_scratch_native_a236_formulae.npz",
        GENERATED / "strict_scratch_native_a236_formulae_report.json",
    )
    a236_boundary = derive_a236_boundary(
        GENERATED / "strict_scratch_center_idempotents_from_generated_T985.npz",
        GENERATED / "strict_scratch_terminal_quotients_from_dihedral_formula.npz",
        GENERATED / "strict_scratch_a236_generated_branching_boundary_report.json",
    )
    a236_profunctor = derive_a236_profunctor(
        GENERATED / "strict_scratch_center_idempotents_from_generated_T985.npz",
        GENERATED / "strict_scratch_terminal_quotients_from_dihedral_formula.npz",
        ROOT / "data/a236_compute/cache",
        GENERATED / "strict_scratch_a236_profunctor_from_tube_cache.npz",
        GENERATED / "strict_scratch_a236_profunctor_from_tube_cache_report.json",
    )

    relation_matches_formula = (
        formula.get("ordered_pair_orbits", {}).get("encoded_pairs_sha256")
        == pre_report.get("ordered_pair_orbits", {}).get("encoded_pairs_sha256")
        and formula.get("ordered_pair_orbits", {}).get("offsets_sha256")
        == pre_report.get("ordered_pair_orbits", {}).get("offsets_sha256")
    )
    quotient = terminal.get("terminal_quotients") or {}
    checks = {
        "pre_A985_relation_body_pass": pre_report.get("constructor_status") == "SOURCE_COORIENT_TO_BE3_ORBITALS_PASS",
        "formula_generators_pass": formula.get("all_checks_pass") is True,
        "formula_relation_matches_pre_A985_generated_relation_order": relation_matches_formula,
        "absolute_word_presentation_pass": absolute.get("all_checks_pass") is True,
        "tensor_rebuild_pass": tensor.get("constructor_status") == "ORBITALS_TO_TENSOR_PASS",
        "tensor_matches_canonical_audit_target": tensor.get("comparison", {}).get("matches_supplied_tensor") is True,
        "packet20_c20_pass": c20.get("all_checks_pass") is True,
        "terminal_selector_dihedral_formulae_pass": terminal.get("constructor_status") == "DIHEDRAL_DN_FORMULAE_PASS",
        "terminal_quotients_pass": quotient.get("constructor_status") == "TERMINAL_QUOTIENTS_PASS",
        "center_idempotents_pass": center.get("constructor_status") == "CENTER_IDEMPOTENTS_FROM_GENERATED_T985_PASS",
        "native_a236_formulae_pass": a236.get("all_checks_pass") is True,
        "a236_generated_branching_boundary_pass": a236_boundary.get("all_checks_pass") is True,
        "a236_profunctor_from_tube_cache_pass": a236_profunctor.get("all_checks_pass") is True,
    }
    resolved_full_scratch_steps = list(COMPLETED_FULL_SCRATCH_STEPS)
    if checks["a236_profunctor_from_tube_cache_pass"]:
        resolved_full_scratch_steps.extend(MISSING_FULL_SCRATCH_STEPS)
        unresolved_boundaries: list[str] = []
    else:
        unresolved_boundaries = list(MISSING_FULL_SCRATCH_STEPS)
    ok = all(checks.values()) and not unresolved_boundaries
    relation = _relation_summary(pre_relation)
    result: dict[str, Any] = {
        "schema": "d20.constructor.generated_strict_scratch_pipeline@1",
        "constructor_status": "GENERATED_STRICT_SCRATCH_CONSTRUCTOR_PASS" if ok else "D20_FULL_SCRATCH_BLOCKED",
        "strict_scratch_required": True,
        "strict_scratch_passed": bool(ok),
        "full_scratch_object_constructor": bool(ok),
        "constructs_from_supplied_raw_seeds": False,
        "seed_boundary": [],
        "audit_targets_not_constructor_inputs": [
            "data/raw/relation_memberships.npz",
            raw_tensor_relpath(),
            "data/raw/constants.json",
            "data/quotient/terminal_quotient_selector.json",
            "data/raw/quotients.npz",
            "data/raw/simple_branching_matrices.npz",
        ],
        "constructor_scope": "H8^3 source relation body, formula-derived coorient action, A985 tensor, D6/D3 terminal selector, A42/A12 terminal quotients, native A236 branching formulae, and tube-cache-aligned A985->A236 profunctor",
        "completed_full_scratch_steps": resolved_full_scratch_steps,
        "missing_full_scratch_steps": [] if ok else unresolved_boundaries,
        "remaining_boundary": [] if ok else unresolved_boundaries,
        "checks": checks,
        "finite_object": relation,
        "coorient": {
            "pre_A985_report": _rel(pre_report_path),
            "formula_status": formula.get("constructor_status"),
            "absolute_word_status": absolute.get("constructor_status"),
            "generator_sha256": formula.get("derived_generators", {}).get("generator_permutations_sha256"),
            "word_action_sha256": absolute.get("sha256", {}).get("word_action"),
        },
        "tensor": {
            "report": tensor,
            "npz": _rel(strict_tensor),
        },
        "readouts": {
            "packet20_C20_status": c20.get("constructor_status"),
            "terminal_selector_status": terminal.get("constructor_status"),
            "terminal_quotients_status": quotient.get("constructor_status"),
            "center_idempotents_status": center.get("constructor_status"),
            "native_a236_status": a236.get("constructor_status"),
            "native_a236_seed_required": a236.get("seed_independence", {}).get("simple_branching_seed_required"),
            "native_a236_not_claimed": a236.get("seed_independence", {}).get("not_claimed"),
            "simple_branching_naturality": a236.get("branching", {}).get("naturality_exact"),
            "a236_generated_branching_boundary_status": a236_boundary.get("constructor_status"),
            "a236_generated_branching_remaining_boundary": a236_boundary.get("remaining_boundary"),
            "a236_profunctor_status": a236_profunctor.get("constructor_status"),
            "a236_profunctor_input_boundary": a236_profunctor.get("input_boundary"),
            "a236_profunctor_remaining_boundary": a236_profunctor.get("remaining_boundary"),
            "a236_profunctor_sha256": a236_profunctor.get("constructor_result_sha256"),
        },
        "computability": {
            "regeneration_scope": "generated_source_coorient_pipeline",
            "whole_object_regenerable_from_checked_bundle": bool(ok),
            "constructs_from_supplied_raw_seeds": False,
            "full_scratch_object_constructor": bool(ok),
            "large_artifacts_regenerated_from_seed_boundary": False,
            "seed_boundary_file_count": 0,
            "completed_full_scratch_step_count": len(resolved_full_scratch_steps),
            "missing_full_scratch_step_count": 0 if ok else len(unresolved_boundaries),
            "next_high_yield_step": None if ok else unresolved_boundaries[0],
        },
    }
    result["constructor_result_sha256"] = stable_constructor_sha_json(result)
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the d20 finite object as far as this bundle actually contains constructors.")
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--out", default="generated/constructed_from_raw_seeds.json")
    ap.add_argument("--strict-scratch", action="store_true", help="Exit nonzero unless the bundle contains a full H8^3 -> Be3 -> A985 constructor.")
    ap.add_argument("--from-source", action="store_true", help="Generate H8^3 -> G24 -> 2576 dodecads from scratch and report the remaining Be3/T985 boundary.")
    ap.add_argument("--from-orbitals", action="store_true", help="Regenerate T985 by two-step incidence from the supplied ordered-pair orbital partition.")
    ap.add_argument("--recover-be3-from-orbitals", action="store_true", help="Recover a Be3 action and compact generators from the supplied ordered-pair orbital partition.")
    ap.add_argument("--from-source-coorient", action="store_true", help="Generate H8^3 -> G24 -> dodecads, apply fixed coorient generators to construct Be3 orbitals, and rebuild T985.")
    ap.add_argument("--derive-terminal-quotients", action="store_true", help="Derive A42/A12 terminal quotient maps and tensors from source+coorient generated relation data and generated T985 without supplied q maps.")
    ap.add_argument("--derive-midlevel-a236", action="store_true", help="Generate the natural 236-dimensional S->S clopen block from source+coorient T985 and test it against the certified A236 invariants.")
    ap.add_argument("--search-midlevel-a236", action="store_true", help="Search low-order intrinsic candidates for the true A236 selector and record the remaining obstruction.")
    ap.add_argument("--derive-representation-integral-wall", action="store_true", help="Derive the A236 representation/fusion presentation, simple branching, sector 33, and the integral wall from center/integrity data.")
    ap.add_argument("--derive-center-idempotents", action="store_true", help="Derive the A985 center basis and primitive central idempotents directly from generated T985.")
    ap.add_argument("--align-generated-sectors", action="store_true", help="Canonically align generated primitive idempotent columns to canonical sector numbering by intrinsic signatures.")
    ap.add_argument("--derive-a236-center-obstruction", action="store_true", help="Prove A236 is not an ordinary central projection of generated A985.")
    ap.add_argument("--derive-a236-generated-branching-boundary", action="store_true", help="Show that generated A985 center and terminal readouts do not determine the native A236 branching functor.")
    ap.add_argument("--derive-a236-profunctor", action="store_true", help="Derive the checked tube-cache-aligned A985->A236 semisimple profunctor.")
    ap.add_argument("--derive-terminal-selector-from-c20", action="store_true", help="Derive the six terminal selector hashes from packet-20 C20 diagonal valencies instead of storing them as primary seed data.")
    ap.add_argument("--derive-coorient-formula-obstruction", action="store_true", help="Prove the fixed coorient Be3 generators are not ordinary 24-coordinate Golay permutations.")
    ap.add_argument("--derive-terminal-selector-intrinsic-obstruction", action="store_true", help="Test whether the terminal diagonal selector is derivable from generated diagonal relation data without packet-20/coorient representation marker.")
    ap.add_argument("--derive-dihedral-formulae", action="store_true", help="Construct D_n/D6/D3 formulae for signed sectors and derive the terminal selector without packet20 C20 constants.")
    ap.add_argument("--derive-d20-selector-from-d6", action="store_true", help="Derive the 20-face d20 selector from marked D6 Coxeter-polarity data and Lambda^3 U.")
    ap.add_argument("--derive-lifted-coorient-generators", action="store_true", help="Derive full lifted Be3 coorient generator permutations from the smaller coherent-signature base-image formula.")
    ap.add_argument("--derive-native-a236-formulae", action="store_true", help="Derive native d20/D6 A236 fusion dimensions and branching matrices without reading the compact branching seed as constructor input.")
    ap.add_argument("--derive-packet20-c20", action="store_true", help="Derive packet-20 C20 from Be3 stabilizer orders and the marked D6 polarity divisor formula, without reading constants.json as constructor input.")
    ap.add_argument("--derive-coorient-canonical-marker", action="store_true", help="Derive the coorient base-image marker canonically from two-sided relation signatures and the formula-derived generator action.")
    ap.add_argument("--derive-lifted-coorient-generators-canonical", action="store_true", help="Derive full lifted Be3 coorient generator permutations from the canonical 15-integer coherent-signature marker.")
    ap.add_argument("--derive-absolute-coorient-word-presentation", action="store_true", help="Derive the lifted coorient action from a d20/D6 word presentation recovered from the regular coherent orbital, without reading a generator action witness.")
    ap.add_argument("--derive-t985-csdo-theorem", action="store_true", help="Write the canonical T985 -> CSDO theorem input bundle.")
    ap.add_argument("--derive-d20-optics", action="store_true", help="Derive d20 optical invariants: etendue, complement conservation, Snell law, and quintic caustic resolvent.")
    ap.add_argument("--derive-d20", action="store_true", help="Derive d20.")
    args = ap.parse_args()

    explicit_constructor_mode = any(
        getattr(args, name)
        for name in (
            "from_source",
            "from_orbitals",
            "recover_be3_from_orbitals",
            "from_source_coorient",
            "derive_terminal_quotients",
            "derive_midlevel_a236",
            "search_midlevel_a236",
            "derive_representation_integral_wall",
            "derive_center_idempotents",
            "align_generated_sectors",
            "derive_a236_center_obstruction",
            "derive_a236_generated_branching_boundary",
            "derive_a236_profunctor",
            "derive_terminal_selector_from_c20",
            "derive_coorient_formula_obstruction",
            "derive_terminal_selector_intrinsic_obstruction",
            "derive_dihedral_formulae",
            "derive_d20_selector_from_d6",
            "derive_lifted_coorient_generators",
            "derive_native_a236_formulae",
            "derive_packet20_c20",
            "derive_coorient_canonical_marker",
            "derive_lifted_coorient_generators_canonical",
            "derive_absolute_coorient_word_presentation",
            "derive_t985_csdo_theorem",
            "derive_d20_optics",
            "derive_d20",
        )
    )

    if args.strict_scratch and not explicit_constructor_mode:
        result = construct_from_generated_strict_scratch_pipeline()
    elif args.derive_t985_csdo_theorem:
        from src.derive_t985_csdo_theorem import write_theorem

        result = write_theorem()
        if args.out == "generated/constructed_from_raw_seeds.json":
            args.out = "data/invariants/d20/theorems/t985_csdo/report.json"
    elif args.derive_d20:
        from src.derive_d20 import derive as derive_d20

        result = derive_d20()
        out_path = ROOT / args.out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)), encoding="utf-8")
    elif args.derive_d20_optics:
        from src.derive_d20_optics import derive as derive_d20_optics

        result = derive_d20_optics(ROOT, ROOT / "generated/d20_optics_report.json")
    elif args.derive_absolute_coorient_word_presentation:
        from src.derive_absolute_coorient_word_presentation import derive as derive_absolute_coorient_word_presentation

        result = derive_absolute_coorient_word_presentation(
            ROOT / "generated/relation_memberships_from_canonical_coorient_marker.npz",
            D20_INVARIANTS / "d20_d6_selector_derivation.json",
            ROOT / "data/coorient/lifted_coorient_canonical_marker_formula.json",
            ROOT / "generated/lifted_coorient_generators_from_canonical_marker.npz",
            ROOT / "data/coorient/absolute_d20_word_presentation.json",
            ROOT / "generated/lifted_coorient_generators_from_word_presentation.npz",
            ROOT / "generated/relation_memberships_from_absolute_word_presentation.npz",
            ROOT / "generated/be3_action_words_from_absolute_presentation.npz",
            ROOT / "generated/absolute_coorient_word_presentation_report.json",
        )
    elif args.derive_packet20_c20:
        from src.derive_packet20_c20_from_d6_stabilizers import derive as derive_packet20_c20_from_d6_stabilizers

        result = derive_packet20_c20_from_d6_stabilizers(
            ROOT / "generated/relation_memberships_from_lifted_coorient_formula.npz",
            ROOT / "data/raw/constants.json",
            ROOT / "generated/packet20_C20_from_d6_stabilizers.npz",
            ROOT / "generated/packet20_C20_from_d6_stabilizers_report.json",
        )
    elif args.derive_coorient_canonical_marker:
        from src.derive_coorient_canonical_marker import derive as derive_coorient_canonical_marker

        result = derive_coorient_canonical_marker(
            ROOT / "generated/relation_memberships_from_lifted_coorient_formula.npz",
            ROOT / "generated/lifted_coorient_generators_from_formula.npz",
            ROOT / "data/coorient/lifted_coorient_canonical_marker_formula.json",
            ROOT / "generated/coorient_canonical_marker_report.json",
        )
    elif args.derive_lifted_coorient_generators_canonical:
        from src.derive_lifted_coorient_generators_formula import derive_formula as derive_lifted_coorient_generators_formula

        result = derive_lifted_coorient_generators_formula(
            ROOT / "generated/relation_memberships_from_lifted_coorient_formula.npz",
            ROOT / "data/coorient/lifted_coorient_canonical_marker_formula.json",
            ROOT / "data/coorient/be3_coorient_generators.npz",
            ROOT / "generated/lifted_coorient_generators_from_canonical_marker.npz",
            ROOT / "generated/relation_memberships_from_canonical_coorient_marker.npz",
            ROOT / "generated/lifted_coorient_generators_from_canonical_marker_report.json",
        )
    elif args.derive_lifted_coorient_generators:
        from src.derive_lifted_coorient_generators_formula import derive_formula as derive_lifted_coorient_generators_formula

        result = derive_lifted_coorient_generators_formula(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "data/coorient/lifted_coorient_signature_formula.json",
            ROOT / "data/coorient/be3_coorient_generators.npz",
            ROOT / "generated/lifted_coorient_generators_from_formula.npz",
            ROOT / "generated/relation_memberships_from_lifted_coorient_formula.npz",
            ROOT / "generated/lifted_coorient_generators_formula_report.json",
        )
    elif args.derive_native_a236_formulae:
        from src.derive_native_a236_formulae import derive as derive_native_a236_formulae

        result = derive_native_a236_formulae(
            ROOT / "data/raw/simple_branching_matrices.npz",
            ROOT / "generated/native_a236_formulae.npz",
            ROOT / "generated/native_a236_formulae_report.json",
        )
    elif args.derive_d20_selector_from_d6:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "src" / "derive_d20_selector_from_d6.py")],
            capture_output=True,
            text=True,
            check=True,
        )
        result = json.loads(proc.stdout)
        result.setdefault("schema", "d20.constructor.d6_coxeter_polarity_selector@1")
        (ROOT / "generated").mkdir(exist_ok=True)
        (ROOT / "generated" / "d20_d6_selector_derivation.json").write_text(
            json.dumps(result, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    elif args.derive_dihedral_formulae:
        from src.build_orbit_tensor import compute_tensor_from_orbitals
        from src.derive_pre_a985_relation_body import ensure_pre_a985_relation_body
        from src.dihedral_dn_formulae import derive_dihedral_formulae

        relation_npz = ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz"
        if not relation_npz.exists():
            relation_npz = ensure_pre_a985_relation_body(regenerate=False, write_report=True)
        tensor_npz = ROOT / "generated/tensor_from_source_coorient.npz"
        if not tensor_npz.exists():
            compute_tensor_from_orbitals(
                relation_npz,
                tensor_npz,
                ROOT / raw_tensor_relpath(),
                None,
                False,
            )
        result = derive_dihedral_formulae(
            relation_npz,
            tensor_npz,
            ROOT / "generated/terminal_selector_from_dihedral_formula.json",
            ROOT / "generated/terminal_quotients_from_dihedral_formula.npz",
            ROOT / "generated/dihedral_dn_formulae_report.json",
            ROOT / "data/raw/quotients.npz",
            ROOT / "generated/terminal_selector_from_c20.json",
        )
    elif args.derive_terminal_selector_intrinsic_obstruction:
        from src.derive_terminal_selector_intrinsic_obstruction import derive_terminal_selector_intrinsic_obstruction

        result = derive_terminal_selector_intrinsic_obstruction(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
            ROOT / "generated/terminal_selector_from_c20.json",
            ROOT / "generated/terminal_selector_intrinsic_obstruction_report.json",
            ROOT / "generated/relation_memberships_from_source_coorient.npz",
        )
    elif args.derive_terminal_selector_from_c20:
        from src.derive_terminal_selector_from_c20 import derive_selector_from_c20

        result = derive_selector_from_c20(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "data/raw/constants.json",
            ROOT / "generated/terminal_selector_from_c20.json",
            ROOT / "generated/terminal_quotients_from_c20_selector.npz",
            ROOT / "generated/terminal_selector_from_c20_report.json",
            ROOT / "data/quotient/terminal_quotient_selector.json",
            ROOT / "data/raw/quotients.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
        )
    elif args.derive_coorient_formula_obstruction:
        from src.derive_coorient_formula_obstruction import derive_obstruction as derive_coorient_formula_obstruction

        result = derive_coorient_formula_obstruction(
            ROOT / "data/coorient/be3_coorient_generators.npz",
            ROOT / "generated/coorient_formula_obstruction_report.json",
        )
    elif args.derive_center_idempotents:
        from src.derive_center_idempotents_from_t985 import derive_center_idempotents

        result = derive_center_idempotents(
            ROOT / "generated/tensor_from_source_coorient.npz",
            None,
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/terminal_quotients_from_source_coorient.npz",
            ROOT / "generated/center_idempotents_from_generated_T985.npz",
            ROOT / "generated/center_idempotents_from_generated_T985_report.json",
        )
    elif args.align_generated_sectors:
        from src.derive_generated_sector_alignment import derive_alignment as derive_generated_sector_alignment
        from src.certificate_registry import certificate_path

        result = derive_generated_sector_alignment(
            ROOT / "generated/center_idempotents_from_generated_T985.npz",
            certificate_path("drinfeld.full_a985_lift"),
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/generated_sector_alignment.npz",
            ROOT / "generated/generated_sector_alignment_report.json",
        )
    elif args.derive_a236_center_obstruction:
        from src.derive_a236_center_obstruction import derive_obstruction as derive_a236_center_obstruction

        result = derive_a236_center_obstruction(
            ROOT / "generated/center_idempotents_from_generated_T985.npz",
            ROOT / "data/raw/simple_branching_matrices.npz",
            ROOT / "generated/a236_center_obstruction_report.json",
        )
    elif args.derive_a236_generated_branching_boundary:
        from src.derive_a236_generated_branching_boundary import derive_boundary as derive_a236_generated_branching_boundary

        result = derive_a236_generated_branching_boundary(
            _prefer_existing(
                ROOT / "generated/center_idempotents_from_generated_T985.npz",
                ROOT / "generated/strict_scratch_center_idempotents_from_generated_T985.npz",
            ),
            _prefer_existing(
                ROOT / "generated/terminal_quotients_from_source_coorient.npz",
                ROOT / "generated/strict_scratch_terminal_quotients_from_dihedral_formula.npz",
            ),
            ROOT / "generated/a236_generated_branching_boundary_report.json",
        )
    elif args.derive_a236_profunctor:
        from src.derive_a236_profunctor_from_tube_cache import derive_profunctor as derive_a236_profunctor

        result = derive_a236_profunctor(
            _prefer_existing(
                ROOT / "generated/strict_scratch_center_idempotents_from_generated_T985.npz",
                ROOT / "generated/center_idempotents_from_generated_T985.npz",
            ),
            _prefer_existing(
                ROOT / "generated/strict_scratch_terminal_quotients_from_dihedral_formula.npz",
                ROOT / "generated/terminal_quotients_from_source_coorient.npz",
            ),
            ROOT / "data/a236_compute/cache",
            ROOT / "generated/a236_profunctor_from_tube_cache.npz",
            ROOT / "generated/a236_profunctor_from_tube_cache_report.json",
        )
    elif args.derive_representation_integral_wall:
        from src.derive_representation_integral_wall import derive_all as derive_representation_integral_wall
        from src.derive_native_a236_formulae import derive as derive_native_a236_formulae
        from src.certificate_registry import certificate_path

        native_a236_npz = ROOT / "generated/native_a236_formulae.npz"
        if not native_a236_npz.exists():
            derive_native_a236_formulae(
                None,
                native_a236_npz,
                ROOT / "generated/native_a236_formulae_report.json",
            )
        result = derive_representation_integral_wall(
            native_a236_npz,
            _prefer_existing(
                ROOT / "generated/terminal_quotients_from_source_coorient.npz",
                ROOT / "generated/strict_scratch_terminal_quotients_from_dihedral_formula.npz",
            ),
            certificate_path("drinfeld.full_a985_lift"),
            certificate_path("integrity.proof_system"),
            ROOT / "generated/a236_representation_fusion_from_center.npz",
            ROOT / "generated/remaining_representation_integral_chain_report.json",
            _prefer_existing(
                ROOT / "generated/center_idempotents_from_generated_T985.npz",
                ROOT / "generated/strict_scratch_center_idempotents_from_generated_T985.npz",
            ),
            _prefer_existing(
                ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
                ROOT / "generated/relation_memberships_pre_A985_from_source_aligned.npz",
            ),
            _prefer_existing(
                ROOT / "generated/tensor_from_source_coorient.npz",
                ROOT / "generated/strict_scratch_tensor_from_pre_a985.npz",
            ),
        )
    elif args.search_midlevel_a236:
        from src.derive_midlevel_selector_search import run_search as run_midlevel_selector_search

        result = run_midlevel_selector_search(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
            ROOT / "data/raw/quotients.npz",
            ROOT / "generated/a236_candidate_from_source_coorient.npz",
            ROOT / "generated/midlevel_selector_search_report.json",
        )
    elif args.derive_midlevel_a236:
        from src.derive_midlevel_a236 import derive_midlevel_a236

        result = derive_midlevel_a236(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
            ROOT / "data/quotient/terminal_quotient_selector.json",
            ROOT / "generated/a236_candidate_from_source_coorient.npz",
            ROOT / "data/raw/constants.json",
            True,
        )
    elif args.derive_terminal_quotients:
        from src.derive_terminal_quotients import derive_terminal_quotients

        result = derive_terminal_quotients(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
            ROOT / "data/quotient/terminal_quotient_selector.json",
            ROOT / "generated/terminal_quotients_from_source_coorient.npz",
            ROOT / "data/raw/quotients.npz",
        )
    elif args.from_source_coorient:
        be3_report_path = GENERATED / "source_coorient_to_be3_orbitals.json"
        tensor_report_path = GENERATED / "tensor_from_source_coorient_report.json"
        if not be3_report_path.exists() or not tensor_report_path.exists():
            raise SystemExit("Run python -m src.build_be3_from_coorient and python -m src.build_orbit_tensor first to regenerate the source+coorient reports.")
        be3_result = json.loads(be3_report_path.read_text(encoding="utf-8"))
        tensor_result = json.loads(tensor_report_path.read_text(encoding="utf-8"))
        ok = (
            be3_result.get("constructor_status") == "SOURCE_COORIENT_TO_BE3_ORBITALS_PASS"
            and tensor_result.get("constructor_status") == "ORBITALS_TO_TENSOR_PASS"
            and tensor_result.get("comparison", {}).get("matches_supplied_tensor") is True
        )
        result = {
            "schema": "d20.constructor.source_coorient_to_T985@1",
            "constructor_status": "SOURCE_COORIENT_TO_T985_PASS" if ok else "SOURCE_COORIENT_TO_T985_FAIL",
            "predicate": "is integral",
            "uses_supplied_orbital_partition": False,
            "uses_fixed_coorient_generator_seed": True,
            "be3": be3_result,
            "tensor": tensor_result,
            "completed_steps": COMPLETED_FULL_SCRATCH_STEPS,
            "remaining_boundary": MISSING_FULL_SCRATCH_STEPS,
        }
        result["constructor_result_sha256"] = stable_constructor_sha_json(result)
    elif args.recover_be3_from_orbitals:
        from src.recover_be3_from_orbitals import recover_be3_from_orbitals

        result = recover_be3_from_orbitals(
            ROOT / "data/raw/relation_memberships.npz",
            ROOT / args.out if args.out else GENERATED / "be3_action_from_orbitals.json",
            GENERATED / "be3_generators_from_orbitals.npz",
            None,
        )
    elif args.from_source:
        from src.generate_source import source_constructor_certificate

        result = source_constructor_certificate()
    elif args.from_orbitals:
        from src.build_orbit_tensor import compute_tensor_from_orbitals

        result = compute_tensor_from_orbitals(
            ROOT / "data/raw/relation_memberships.npz",
            ROOT / "generated/tensor_from_orbitals.npz",
            ROOT / raw_tensor_relpath(),
            None,
            False,
        )
    else:
        result = construct_from_supplied_raw_seeds()
    if args.strict_scratch:
        if is_full_scratch_constructor(result):
            result["strict_scratch_required"] = True
            result["strict_scratch_passed"] = True
            result["constructor_result_sha256"] = stable_constructor_sha_json(result)
        else:
            result = mark_strict_scratch_blocked(result)

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True), encoding="utf-8")
    emit_json(result, pretty=args.pretty)
    if args.strict_scratch and not result.get("strict_scratch_passed", False):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
