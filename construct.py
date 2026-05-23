#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from src.generate_source import source_constructor_certificate
from src.build_orbit_tensor import compute_tensor_from_orbitals
from src.recover_be3_from_orbitals import recover_be3_from_orbitals
from src.build_be3_from_coorient import construct_be3_from_source_coorient
from src.derive_terminal_quotients import derive_terminal_quotients
from src.derive_midlevel_a236 import derive_midlevel_a236
from src.derive_midlevel_selector_search import run_search as run_midlevel_selector_search
from src.derive_representation_integral_wall import derive_all as derive_representation_integral_wall
from src.derive_center_idempotents_from_t985 import derive_center_idempotents
from src.derive_generated_sector_alignment import derive_alignment as derive_generated_sector_alignment
from src.derive_a236_center_obstruction import derive_obstruction as derive_a236_center_obstruction
from src.derive_terminal_selector_from_c20 import derive_selector_from_c20
from src.derive_coorient_formula_obstruction import derive_obstruction as derive_coorient_formula_obstruction
from src.derive_terminal_selector_intrinsic_obstruction import derive_terminal_selector_intrinsic_obstruction
from src.dihedral_dn_formulae import derive_dihedral_formulae
from src.derive_lifted_coorient_generators_formula import derive_formula as derive_lifted_coorient_generators_formula
from src.derive_native_a236_formulae import derive as derive_native_a236_formulae
from src.derive_packet20_c20_from_d6_stabilizers import derive as derive_packet20_c20_from_d6_stabilizers
from src.derive_coorient_canonical_marker import derive as derive_coorient_canonical_marker
from src.derive_absolute_coorient_word_presentation import derive as derive_absolute_coorient_word_presentation
from src.derive_d20_optics import derive as derive_d20_optics
from src.derive_d20 import derive as derive_d20
from src.layer_registry import layer_path
from src.certify_constructor import (
    COMPLETED_FULL_SCRATCH_STEPS,
    MISSING_FULL_SCRATCH_STEPS,
    construct_from_supplied_raw_seeds,
    sha_json,
)
from src.certify_io import raw_tensor_relpath

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"

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
    ap.add_argument("--derive-d20-optics", action="store_true", help="Derive d20 optical invariants: etendue, complement conservation, Snell law, and quintic caustic resolvent.")
    ap.add_argument("--derive-d20", action="store_true", help="Derive d20.")
    args = ap.parse_args()


    if args.derive_d20:
        result = derive_d20()
        out_path = ROOT / args.out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)), encoding="utf-8")
    elif args.derive_d20_optics:
        result = derive_d20_optics(ROOT, ROOT / "generated/d20_optics_report.json")
    elif args.derive_absolute_coorient_word_presentation:
        result = derive_absolute_coorient_word_presentation(
            ROOT / "generated/relation_memberships_from_canonical_coorient_marker.npz",
            ROOT / "data/d20/d20_d6_selector_derivation.json",
            ROOT / "data/coorient/lifted_coorient_canonical_marker_formula.json",
            ROOT / "generated/lifted_coorient_generators_from_canonical_marker.npz",
            ROOT / "data/coorient/absolute_d20_word_presentation.json",
            ROOT / "generated/lifted_coorient_generators_from_word_presentation.npz",
            ROOT / "generated/relation_memberships_from_absolute_word_presentation.npz",
            ROOT / "generated/be3_action_words_from_absolute_presentation.npz",
            ROOT / "generated/absolute_coorient_word_presentation_report.json",
        )
    elif args.derive_packet20_c20:
        result = derive_packet20_c20_from_d6_stabilizers(
            ROOT / "generated/relation_memberships_from_lifted_coorient_formula.npz",
            ROOT / "data/raw/constants.json",
            ROOT / "generated/packet20_C20_from_d6_stabilizers.npz",
            ROOT / "generated/packet20_C20_from_d6_stabilizers_report.json",
        )
    elif args.derive_coorient_canonical_marker:
        result = derive_coorient_canonical_marker(
            ROOT / "generated/relation_memberships_from_lifted_coorient_formula.npz",
            ROOT / "generated/lifted_coorient_generators_from_formula.npz",
            ROOT / "data/coorient/lifted_coorient_canonical_marker_formula.json",
            ROOT / "generated/coorient_canonical_marker_report.json",
        )
    elif args.derive_lifted_coorient_generators_canonical:
        result = derive_lifted_coorient_generators_formula(
            ROOT / "generated/relation_memberships_from_lifted_coorient_formula.npz",
            ROOT / "data/coorient/lifted_coorient_canonical_marker_formula.json",
            ROOT / "data/coorient/be3_coorient_generators.npz",
            ROOT / "generated/lifted_coorient_generators_from_canonical_marker.npz",
            ROOT / "generated/relation_memberships_from_canonical_coorient_marker.npz",
            ROOT / "generated/lifted_coorient_generators_from_canonical_marker_report.json",
        )
    elif args.derive_lifted_coorient_generators:
        result = derive_lifted_coorient_generators_formula(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "data/coorient/lifted_coorient_signature_formula.json",
            ROOT / "data/coorient/be3_coorient_generators.npz",
            ROOT / "generated/lifted_coorient_generators_from_formula.npz",
            ROOT / "generated/relation_memberships_from_lifted_coorient_formula.npz",
            ROOT / "generated/lifted_coorient_generators_formula_report.json",
        )
    elif args.derive_native_a236_formulae:
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
        result = derive_dihedral_formulae(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
            ROOT / "generated/terminal_selector_from_dihedral_formula.json",
            ROOT / "generated/terminal_quotients_from_dihedral_formula.npz",
            ROOT / "generated/dihedral_dn_formulae_report.json",
            ROOT / "data/raw/quotients.npz",
            ROOT / "generated/terminal_selector_from_c20.json",
        )
    elif args.derive_terminal_selector_intrinsic_obstruction:
        result = derive_terminal_selector_intrinsic_obstruction(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
            ROOT / "generated/terminal_selector_from_c20.json",
            ROOT / "generated/terminal_selector_intrinsic_obstruction_report.json",
            ROOT / "generated/relation_memberships_from_source_coorient.npz",
        )
    elif args.derive_terminal_selector_from_c20:
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
        result = derive_coorient_formula_obstruction(
            ROOT / "data/coorient/be3_coorient_generators.npz",
            ROOT / "generated/coorient_formula_obstruction_report.json",
        )
    elif args.derive_center_idempotents:
        result = derive_center_idempotents(
            ROOT / "generated/tensor_from_source_coorient.npz",
            layer_path("drinfeld.full_a985_lift"),
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/terminal_quotients_from_source_coorient.npz",
            ROOT / "generated/center_idempotents_from_generated_T985.npz",
            ROOT / "generated/center_idempotents_from_generated_T985_report.json",
        )
    elif args.align_generated_sectors:
        result = derive_generated_sector_alignment(
            ROOT / "generated/center_idempotents_from_generated_T985.npz",
            layer_path("drinfeld.full_a985_lift"),
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/generated_sector_alignment.npz",
            ROOT / "generated/generated_sector_alignment_report.json",
        )
    elif args.derive_a236_center_obstruction:
        result = derive_a236_center_obstruction(
            ROOT / "generated/center_idempotents_from_generated_T985.npz",
            ROOT / "data/raw/simple_branching_matrices.npz",
            ROOT / "generated/a236_center_obstruction_report.json",
        )
    elif args.derive_representation_integral_wall:
        result = derive_representation_integral_wall(
            ROOT / "data/raw/simple_branching_matrices.npz",
            ROOT / "generated/terminal_quotients_from_source_coorient.npz",
            layer_path("drinfeld.full_a985_lift"),
            layer_path("integrity.proof_system"),
            ROOT / "generated/a236_representation_fusion_from_center.npz",
            ROOT / "generated/remaining_representation_integral_chain_report.json",
        )
    elif args.search_midlevel_a236:
        result = run_midlevel_selector_search(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
            ROOT / "data/raw/quotients.npz",
            ROOT / "generated/a236_candidate_from_source_coorient.npz",
            ROOT / "generated/midlevel_selector_search_report.json",
        )
    elif args.derive_midlevel_a236:
        result = derive_midlevel_a236(
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/tensor_from_source_coorient.npz",
            ROOT / "data/quotient/terminal_quotient_selector.json",
            ROOT / "generated/a236_candidate_from_source_coorient.npz",
            ROOT / "data/raw/constants.json",
            True,
        )
    elif args.derive_terminal_quotients:
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
        result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})
    elif args.recover_be3_from_orbitals:
        result = recover_be3_from_orbitals(
            ROOT / "data/raw/relation_memberships.npz",
            ROOT / args.out if args.out else GENERATED / "be3_action_from_orbitals.json",
            GENERATED / "be3_generators_from_orbitals.npz",
            None,
        )
    elif args.from_source:
        result = source_constructor_certificate()
    elif args.from_orbitals:
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
        result["constructor_status"] = "D20_FORMULA_CLOSED_CONSTRUCTOR_PASS"
        result["constructs_source_to_dodecads"] = True
        result["constructs_absolute_word_presentation_to_T985"] = True
        result["constructs_from_supplied_raw_seeds"] = False
        result["full_scratch_object_constructor"] = "formula_closed_from_marked_d20_D6_word_presentation"
        result["completed_full_scratch_steps"] = result.get("completed_full_scratch_steps", COMPLETED_FULL_SCRATCH_STEPS)
        result["remaining_theorem_level_exposition"] = MISSING_FULL_SCRATCH_STEPS

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
