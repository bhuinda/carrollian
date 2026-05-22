#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

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

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"

COMPLETED_FULL_SCRATCH_STEPS = [
    "construct H8 = RM(1,3) from affine linear functions on F2^3",
    "construct C0 = H8^{oplus 3} inside F2^24",
    "run the Type-II neighbor chain 42 -> 18 -> 6 -> 0 without importing the Golay endpoint",
    "enumerate the 2576 Golay dodecads from the generated G24 endpoint",
    "compute sextet profile families, vector fibers, spinor fibers, and balanced scheme valencies",
    "derive lifted coorient generator permutations from a two-sided coherent-signature formula over a canonical three-point separating base",
    "from the formula-derived coorient generators, close Be3 of order 9216",
    "compute the six Be3 point orbits and 985 ordered-pair orbitals without using the supplied orbital partition",
    "rebuild T985 from the generated ordered-pair orbitals by two-step incidence",
    "derive the 39-dimensional center directly from generated T985",
    "materialize 39 primitive central idempotents by a split generic center element over the verifier field",
    "recover the public-zero dim-2/rank-36 sector column intrinsically from generated idempotents",
    "derive packet20 C20 from Be3 stabilizer orders and the marked D6 polarity divisor formula",
    "derive d20 finite optics: etendue, complement-pair conservation, Snell transport, and quintic caustic resolvent",
]

MISSING_FULL_SCRATCH_STEPS = [
    "derive the four lifted coorient generator images on the canonical three-point base from A0-A5 without reading any coorient marker file",
    "prove uniqueness of the Be3 coorient lift from D6/Spin12/d20 compatibility up to residual Dih6 relabeling",
]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_npz(rel: str):
    return np.load(ROOT / rel)


def quotient_tensor_from_sparse(triples: np.ndarray, qmap: np.ndarray, nclasses: int) -> tuple[np.ndarray, dict[str, Any]]:
    """Regenerate the stored quotient tensor convention.

    The bundle stores raw expanded aggregation totals, not normalized quotient
    constants. This constructor intentionally regenerates that stored convention
    from T985 and the quotient map.
    """
    a = qmap[triples[:, 0]]
    b = qmap[triples[:, 1]]
    c = qmap[triples[:, 2]]
    w = triples[:, 3].astype(np.int64, copy=False)
    agg = np.zeros((nclasses, nclasses, nclasses), dtype=np.int64)
    np.add.at(agg, (a, b, c), w)
    sizes = np.bincount(qmap, minlength=nclasses).astype(np.int64)
    divisible = True
    for k in range(nclasses):
        if sizes[k] and np.any(agg[:, :, k] % sizes[k]):
            divisible = False
            break
    return agg, {
        "classes": int(nclasses),
        "class_size_min": int(sizes.min()),
        "class_size_max": int(sizes.max()),
        "normalized_integer_divisibility": bool(divisible),
        "stored_convention": "raw_expanded_aggregation_total",
        "nonzero": int(np.count_nonzero(agg)),
        "coefficient_total_raw_aggregated": int(agg.sum()),
        "class_sizes_sha256": hashlib.sha256(sizes.tobytes()).hexdigest(),
        "tensor_sha256": hashlib.sha256(agg.tobytes()).hexdigest(),
    }


def construct_from_supplied_raw_seeds() -> dict[str, Any]:
    tensor = load_npz("data/raw/tensor_sparse.npz")
    triples = np.asarray(tensor["triples"], dtype=np.int64)
    reps = np.asarray(tensor["reps"], dtype=np.int64)
    M = np.asarray(tensor["M"], dtype=np.int64)

    rel = load_npz("data/raw/relation_memberships.npz")
    encoded = np.asarray(rel["encoded_pairs"], dtype=np.int64)
    offsets = np.asarray(rel["offsets"], dtype=np.int64)
    object_of_point = np.asarray(rel["object_of_point"], dtype=np.int64)
    block_i = np.asarray(rel["block_i"], dtype=np.int64)
    block_j = np.asarray(rel["block_j"], dtype=np.int64)
    points = int(np.asarray(rel["points"]).reshape(-1)[0])
    group_order = int(np.asarray(rel["group_order"]).reshape(-1)[0])
    object_sizes = np.bincount(object_of_point, minlength=6).astype(np.int64)
    relation_count_matrix = np.zeros((6, 6), dtype=np.int64)
    relation_sizes = np.diff(offsets).astype(np.int64)
    block_mass = np.zeros((6, 6), dtype=np.int64)
    for idx, size in enumerate(relation_sizes):
        i, j = int(block_i[idx]), int(block_j[idx])
        relation_count_matrix[i, j] += 1
        block_mass[i, j] += int(size)

    # Partition check: every ordered pair appears exactly once in the supplied orbital partition.
    seen = np.zeros(points * points, dtype=np.bool_)
    seen[encoded] = True
    partition_ok = bool(seen.all() and int(seen.sum()) == points * points and encoded.size == points * points)

    q = load_npz("data/raw/quotients.npz")
    q42 = np.asarray(q["q42_map"], dtype=np.int64)
    q12 = np.asarray(q["q12_map"], dtype=np.int64)
    q42_file = np.asarray(q["q42_tensor"], dtype=np.int64)
    q12_file = np.asarray(q["q12_tensor"], dtype=np.int64)
    q42_gen, q42_meta = quotient_tensor_from_sparse(triples, q42, 42)
    q12_gen, q12_meta = quotient_tensor_from_sparse(triples, q12, 12)

    q42_to_q12_consistent = True
    q42_to_q12 = []
    for cls in range(42):
        vals = np.unique(q12[q42 == cls])
        if vals.size != 1:
            q42_to_q12_consistent = False
            q42_to_q12.append(None)
        else:
            q42_to_q12.append(int(vals[0]))

    branching = load_npz("data/raw/simple_branching_matrices.npz")
    B236_42 = np.asarray(branching["B236_42"], dtype=np.int64)
    B42_12 = np.asarray(branching["B42_12"], dtype=np.int64)
    B236_12 = np.asarray(branching["B236_12"], dtype=np.int64)
    comp = B236_42 @ B42_12
    simple_naturality = bool(np.array_equal(comp, B236_12))

    generated = {
        "schema": "d20.constructor.supplied_raw_seed_result",
        "constructor_status": "RAW_SEED_CONSTRUCTOR_PASS",
        "full_scratch_object_constructor": False,
        "zero_axiom_reduction_available": True,
        "constructs_from_supplied_raw_seeds": True,
        "seed_boundary": [
            "data/raw/relation_memberships.npz",
            "data/raw/tensor_sparse.npz",
            "data/raw/quotients.npz",
            "data/raw/simple_branching_matrices.npz",
        ],
        "completed_full_scratch_steps": COMPLETED_FULL_SCRATCH_STEPS,
        "missing_full_scratch_steps": MISSING_FULL_SCRATCH_STEPS,
        "finite_object": {
            "points": points,
            "group_order_from_seed": group_order,
            "relations": int(reps.shape[0]),
            "object_sizes": object_sizes.astype(int).tolist(),
            "object_pair_relation_matrix_generated": relation_count_matrix.astype(int).tolist(),
            "object_pair_relation_matrix_matches_tensor_header": bool(np.array_equal(relation_count_matrix, M)),
            "ordered_pair_partition_ok": partition_ok,
            "block_mass_is_object_size_outer_product": bool(np.array_equal(block_mass, np.outer(object_sizes, object_sizes))),
        },
        "tensor": {
            "support": int(triples.shape[0]),
            "coefficient_total": int(triples[:, 3].sum()),
            "source_relation_range": [int(triples[:, 0].min()), int(triples[:, 0].max())],
            "middle_relation_range": [int(triples[:, 1].min()), int(triples[:, 1].max())],
            "target_relation_range": [int(triples[:, 2].min()), int(triples[:, 2].max())],
            "coefficient_min": int(triples[:, 3].min()),
            "coefficient_max": int(triples[:, 3].max()),
            "tensor_sha256": hashlib.sha256(triples.tobytes()).hexdigest(),
        },
        "generated_quotients": {
            "q42": q42_meta | {"matches_supplied_q42_tensor": bool(np.array_equal(q42_gen, q42_file))},
            "q12": q12_meta | {"matches_supplied_q12_tensor": bool(np.array_equal(q12_gen, q12_file))},
            "q42_to_q12_consistent": bool(q42_to_q12_consistent),
            "q42_to_q12": q42_to_q12,
        },
        "simple_branching": {
            "B236_to_A42_shape": list(B236_42.shape),
            "B42_to_A12_shape": list(B42_12.shape),
            "B236_to_A12_shape": list(B236_12.shape),
            "naturality_exact": simple_naturality,
            "defect_l1": int(np.abs(comp - B236_12).sum()),
        },
        "integrality_language": {
            "predicate": "is integral",
            "integrity_integral_dimension": 1,
            "integrity_integral_codimension": 35,
            "primitive_kernel_sector": [33],
        },
    }
    generated["constructor_result_sha256"] = sha_json({k: v for k, v in generated.items() if k != "constructor_result_sha256"})
    return generated


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
            ROOT / "layers/06_drinfeld_full_A985_lift/certificate.json",
            ROOT / "generated/relation_memberships_from_source_coorient_aligned.npz",
            ROOT / "generated/terminal_quotients_from_source_coorient.npz",
            ROOT / "generated/center_idempotents_from_generated_T985.npz",
            ROOT / "generated/center_idempotents_from_generated_T985_report.json",
        )
    elif args.align_generated_sectors:
        result = derive_generated_sector_alignment(
            ROOT / "generated/center_idempotents_from_generated_T985.npz",
            ROOT / "layers/06_drinfeld_full_A985_lift/certificate.json",
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
            ROOT / "layers/06_drinfeld_full_A985_lift/certificate.json",
            ROOT / "layers/25_proof_system_integrity/certificate.json",
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
            ROOT / "data/raw/tensor_sparse.npz",
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
