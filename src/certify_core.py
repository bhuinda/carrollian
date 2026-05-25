#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any, Dict

try:
    from .certify_report import assemble_certificate, verified_claims
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_report import assemble_certificate, verified_claims

try:
    from .certify_io import cached_core_block, file_manifest, h_json, load_json, raw_tensor_relpath, ROOT
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import cached_core_block, file_manifest, h_json, load_json, raw_tensor_relpath, ROOT

try:
    from .certificate_registry import certificate_relpath
except ImportError:  # Supports `python src/certify_core.py`.
    from certificate_registry import certificate_relpath

try:
    from .verify_c2_selector_lookup_witness_source_package import (
        validate_theorem_registry_source_package_binding,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from verify_c2_selector_lookup_witness_source_package import (
        validate_theorem_registry_source_package_binding,
    )

try:
    from .certify_raw import (
        validate_clopen,
        validate_f_symbol_shape,
        validate_quotients,
        validate_relations,
        validate_simple_branching,
        validate_tensor,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_raw import (
        validate_clopen,
        validate_f_symbol_shape,
        validate_quotients,
        validate_relations,
        validate_simple_branching,
        validate_tensor,
    )

try:
    from .certify_half_braiding import (
        validate_half_braiding_full_solve,
        validate_half_braiding_prime_stability,
        validate_half_braiding_snf_certificate,
        validate_half_braiding_solver,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_half_braiding import (
        validate_half_braiding_full_solve,
        validate_half_braiding_prime_stability,
        validate_half_braiding_snf_certificate,
        validate_half_braiding_solver,
    )

try:
    from .certify_sandpile import validate_sandpile_critical_group
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_sandpile import validate_sandpile_critical_group

try:
    from .certify_public_boundary import validate_public_boundary_graph_invariants
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_public_boundary import validate_public_boundary_graph_invariants

try:
    from .certify_fourier_residue import validate_fourier_residue_screen
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_fourier_residue import validate_fourier_residue_screen

try:
    from .certify_fourier_a985 import validate_fourier_a985_sector_character_candidates
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_fourier_a985 import validate_fourier_a985_sector_character_candidates

try:
    from .certify_fourier_screen0_tube import validate_fourier_screen0_tube_central_element
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_fourier_screen0_tube import validate_fourier_screen0_tube_central_element

try:
    from .certify_tube_sandpile import validate_tube_sandpile_divisor_map
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile import validate_tube_sandpile_divisor_map

try:
    from .certify_tube_sandpile_kernel import validate_tube_sandpile_kernel_flips
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile_kernel import validate_tube_sandpile_kernel_flips

try:
    from .certify_tube_sandpile_flip_presentation import validate_tube_sandpile_flip_move_presentation
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile_flip_presentation import validate_tube_sandpile_flip_move_presentation

try:
    from .certify_tube_sandpile_flip_coset import validate_tube_sandpile_flip_coset_classifier
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile_flip_coset import validate_tube_sandpile_flip_coset_classifier

try:
    from .certify_tube_sandpile_flip_profile_compression import (
        validate_tube_sandpile_flip_profile_compression,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile_flip_profile_compression import (
        validate_tube_sandpile_flip_profile_compression,
    )

try:
    from .certify_tube_sandpile_flip_sector_refinement import (
        validate_tube_sandpile_flip_sector_refinement,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile_flip_sector_refinement import (
        validate_tube_sandpile_flip_sector_refinement,
    )

try:
    from .certify_tube_sandpile_flip_sector_support_pullback import (
        validate_tube_sandpile_flip_sector_support_pullback,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile_flip_sector_support_pullback import (
        validate_tube_sandpile_flip_sector_support_pullback,
    )

try:
    from .certify_tube_sandpile_flip_unsupported_state import (
        validate_tube_sandpile_flip_unsupported_state_classification,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile_flip_unsupported_state import (
        validate_tube_sandpile_flip_unsupported_state_classification,
    )

try:
    from .certify_tube_sandpile_flip_formal_11_extension import (
        validate_tube_sandpile_flip_formal_11_extension_test,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile_flip_formal_11_extension import (
        validate_tube_sandpile_flip_formal_11_extension_test,
    )

try:
    from .certify_d20_matrix_lift_conjecture import validate_d20_matrix_lift_conjecture
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_matrix_lift_conjecture import validate_d20_matrix_lift_conjecture

try:
    from .certify_d20_minimal_matrix_charge_lift import validate_d20_minimal_matrix_charge_lift
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_minimal_matrix_charge_lift import validate_d20_minimal_matrix_charge_lift

try:
    from .certify_d20_full_packet_matrix_lift import validate_d20_full_packet_matrix_lift
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_full_packet_matrix_lift import validate_d20_full_packet_matrix_lift

try:
    from .certify_d20_packet_quotient_action_probe import (
        validate_d20_packet_quotient_action_probe,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_packet_quotient_action_probe import validate_d20_packet_quotient_action_probe

try:
    from .certify_d20_explicit_packet_restriction_map_test import (
        validate_d20_explicit_packet_restriction_map_test,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_explicit_packet_restriction_map_test import (
        validate_d20_explicit_packet_restriction_map_test,
    )

try:
    from .certify_d20_packet_bridge_snf_obstruction import (
        validate_d20_packet_bridge_snf_obstruction,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_packet_bridge_snf_obstruction import (
        validate_d20_packet_bridge_snf_obstruction,
    )

try:
    from .certify_d20_finite_contour_integration import (
        validate_d20_finite_contour_integration,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_finite_contour_integration import (
        validate_d20_finite_contour_integration,
    )

try:
    from .certify_d20_contour_sector_packet_prime_alignment import (
        validate_d20_contour_sector_packet_prime_alignment,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_contour_sector_packet_prime_alignment import (
        validate_d20_contour_sector_packet_prime_alignment,
    )

try:
    from .certify_d20_contour_charge_pairing_snf import (
        validate_d20_contour_charge_pairing_snf,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_contour_charge_pairing_snf import (
        validate_d20_contour_charge_pairing_snf,
    )

try:
    from .certify_d20_oriented_matroid_contour import (
        validate_d20_oriented_matroid_contour,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_oriented_matroid_contour import (
        validate_d20_oriented_matroid_contour,
    )

try:
    from .certify_d20_oriented_matroid_sector33_extension import (
        validate_d20_oriented_matroid_sector33_extension,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_oriented_matroid_sector33_extension import (
        validate_d20_oriented_matroid_sector33_extension,
    )

try:
    from .certify_d20_oriented_matroid_sector33_dual import (
        validate_d20_oriented_matroid_sector33_dual,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_oriented_matroid_sector33_dual import (
        validate_d20_oriented_matroid_sector33_dual,
    )

try:
    from .certify_d20_oriented_matroid_tutte_os import (
        validate_d20_oriented_matroid_tutte_os,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_oriented_matroid_tutte_os import (
        validate_d20_oriented_matroid_tutte_os,
    )

try:
    from .certify_d20_oriented_matroid_prime_lift_audit import (
        validate_d20_oriented_matroid_prime_lift_audit,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_oriented_matroid_prime_lift_audit import (
        validate_d20_oriented_matroid_prime_lift_audit,
    )

try:
    from .certify_d20_oriented_matroid_rational_tutte_promotion import (
        validate_d20_oriented_matroid_rational_tutte_promotion,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_oriented_matroid_rational_tutte_promotion import (
        validate_d20_oriented_matroid_rational_tutte_promotion,
    )

try:
    from .certify_d20_oriented_matroid_rational_signed_circuits import (
        validate_d20_oriented_matroid_rational_signed_circuits,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_oriented_matroid_rational_signed_circuits import (
        validate_d20_oriented_matroid_rational_signed_circuits,
    )

try:
    from .certify_d20_strict_weak_order_sector26_clock import (
        validate_d20_strict_weak_order_sector26_clock,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_strict_weak_order_sector26_clock import (
        validate_d20_strict_weak_order_sector26_clock,
    )

try:
    from .certify_d20_intrinsic_triple_ordering_clock import (
        validate_d20_intrinsic_triple_ordering_clock,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_intrinsic_triple_ordering_clock import (
        validate_d20_intrinsic_triple_ordering_clock,
    )

try:
    from .certify_d20_triple_13_signature_uniqueness import (
        validate_d20_triple_13_signature_uniqueness,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_triple_13_signature_uniqueness import (
        validate_d20_triple_13_signature_uniqueness,
    )

try:
    from .certify_d20_raw_transport_3x3_discriminant13_search import (
        validate_d20_raw_transport_3x3_discriminant13_search,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_d20_raw_transport_3x3_discriminant13_search import (
        validate_d20_raw_transport_3x3_discriminant13_search,
    )

try:
    from .certify_raw543_repo_c2_kernel_action import (
        validate_raw543_repo_c2_kernel_action,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_raw543_repo_c2_kernel_action import (
        validate_raw543_repo_c2_kernel_action,
    )

try:
    from .certify_zero_axiom_coorient_cache import validate_zero_axiom_coorient_cache
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_zero_axiom_coorient_cache import validate_zero_axiom_coorient_cache

try:
    from .certify_zero_axiom_coorient_strict_replay import validate_zero_axiom_coorient_strict_replay
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_zero_axiom_coorient_strict_replay import validate_zero_axiom_coorient_strict_replay

try:
    from .certify_tube_center import (
        validate_tube_center_algebra_lift,
        validate_tube_center_primitive_idempotents,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_center import (
        validate_tube_center_algebra_lift,
        validate_tube_center_primitive_idempotents,
    )

try:
    from .certify_tube_lift import (
        validate_tube_algebra_lift,
        validate_tube_center_lift,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_lift import (
        validate_tube_algebra_lift,
        validate_tube_center_lift,
    )

try:
    from .certify_tube_projection import (
        validate_full_tube_algebra_solver,
        validate_tube_pair_product_oracle,
        validate_tube_projection_section,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_projection import (
        validate_full_tube_algebra_solver,
        validate_tube_pair_product_oracle,
        validate_tube_projection_section,
    )

CORE_FILES = [
    'data/raw/constants.json',
    raw_tensor_relpath(),
    'data/raw/quotients.npz',
    'data/raw/relation_memberships.npz',
    'data/raw/simple_branching_matrices.npz',
    'data/raw/leech_projective_generators.npz',
    certificate_relpath('core.a985'),
    'src/certify_core.py',
    'src/certify_half_braiding.py',
    'src/certify_io.py',
    'src/certify_linear.py',
    'src/certificate_registry.py',
    'src/certify_raw.py',
    'src/certify_tube_center.py',
    'src/certify_tube_lift.py',
    'src/certify_tube_projection.py',
    'src/certify_report.py',
    'src/verify_c2_selector_lookup_witness_source_package.py',
    'data/invariants/d20/theorems/index.json',
    'src/solve_half_braiding.py',
    'src/derive_half_braiding_prime_sweep.py',
    'src/derive_half_braiding_local_snf.py',
    'src/derive_half_braiding_snf_certificate.py',
    'src/certify_sandpile.py',
    'src/derive_d20_sandpile_critical_group_theorem.py',
    'data/invariants/hcycle/subscript_Hcycle_d20_edges.csv',
    'data/invariants/d20/theorems/sandpile_critical_group/manifest.json',
    'data/invariants/d20/theorems/sandpile_critical_group/report.json',
    'src/certify_public_boundary.py',
    'src/derive_d20_public_boundary_graph_theorem.py',
    'data/invariants/hcycle/subscript_Hcycle_primitive_cycles.csv',
    'data/invariants/hcycle/d20_Hcycle_automorphism_summary.json',
    'data/invariants/d20/theorems/public_boundary_graph_invariants/manifest.json',
    'data/invariants/d20/theorems/public_boundary_graph_invariants/report.json',
    'src/certify_fourier_residue.py',
    'src/derive_d20_fourier_residue_screen_theorem.py',
    'data/invariants/hcycle/d20_Hcycle_mod2_residue_spectrum_all_subsets.csv',
    'data/invariants/d20/theorems/fourier_residue_screen/manifest.json',
    'data/invariants/d20/theorems/fourier_residue_screen/report.json',
    'src/certify_fourier_a985.py',
    'src/derive_d20_fourier_a985_sector_character_candidates.py',
    'data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json',
    'data/invariants/d20/theorems/sector_idempotent_support_admissibility/report.json',
    'data/drinfeld/full_a985_lift.json',
    'data/invariants/d20/theorems/fourier_a985_sector_character_candidates/manifest.json',
    'data/invariants/d20/theorems/fourier_a985_sector_character_candidates/report.json',
    'src/certify_fourier_screen0_tube.py',
    'src/derive_d20_fourier_screen0_tube_central_element.py',
    'data/invariants/d20/theorems/fourier_screen0_tube_central_element/manifest.json',
    'data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json',
    'src/certify_tube_sandpile.py',
    'src/derive_d20_tube_sandpile_divisor_map.py',
    'data/invariants/d20/theorems/tube_sandpile_divisor_map/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_divisor_map/report.json',
    'src/certify_tube_sandpile_kernel.py',
    'src/derive_d20_tube_sandpile_kernel_flips.py',
    'data/invariants/d20/theorems/tube_sandpile_kernel_flips/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_kernel_flips/report.json',
    'src/certify_tube_sandpile_flip_presentation.py',
    'src/derive_d20_tube_sandpile_flip_move_presentation.py',
    'data/invariants/d20/theorems/tube_sandpile_flip_move_presentation/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_flip_move_presentation/report.json',
    'src/certify_tube_sandpile_flip_coset.py',
    'src/derive_d20_tube_sandpile_flip_coset_classifier.py',
    'data/invariants/d20/theorems/tube_sandpile_flip_coset_classifier/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_flip_coset_classifier/report.json',
    'src/certify_tube_sandpile_flip_profile_compression.py',
    'src/derive_d20_tube_sandpile_flip_profile_compression.py',
    'data/invariants/d20/theorems/tube_sandpile_flip_profile_compression/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_flip_profile_compression/report.json',
    'src/certify_tube_sandpile_flip_sector_refinement.py',
    'src/derive_d20_tube_sandpile_flip_sector_refinement.py',
    'data/invariants/d20/theorems/tube_sandpile_flip_sector_refinement/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_flip_sector_refinement/report.json',
    'src/certify_tube_sandpile_flip_sector_support_pullback.py',
    'src/derive_d20_tube_sandpile_flip_sector_support_pullback.py',
    'data/invariants/d20/theorems/tube_sandpile_flip_sector_support_pullback/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_flip_sector_support_pullback/report.json',
    'src/certify_tube_sandpile_flip_unsupported_state.py',
    'src/derive_d20_tube_sandpile_flip_unsupported_state_classification.py',
    'data/invariants/d20/theorems/tube_sandpile_flip_unsupported_state_classification/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_flip_unsupported_state_classification/report.json',
    'src/certify_tube_sandpile_flip_formal_11_extension.py',
    'src/derive_d20_tube_sandpile_flip_formal_11_extension_test.py',
    'data/invariants/d20/theorems/tube_sandpile_flip_formal_11_extension_test/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_flip_formal_11_extension_test/report.json',
    'src/certify_d20_matrix_lift_conjecture.py',
    'src/derive_d20_matrix_lift_conjecture.py',
    'data/invariants/d20/theorems/d20_matrix_lift_conjecture/manifest.json',
    'data/invariants/d20/theorems/d20_matrix_lift_conjecture/report.json',
    'src/certify_d20_minimal_matrix_charge_lift.py',
    'src/derive_d20_minimal_matrix_charge_lift.py',
    'data/invariants/d20/theorems/d20_minimal_matrix_charge_lift/manifest.json',
    'data/invariants/d20/theorems/d20_minimal_matrix_charge_lift/report.json',
    'src/certify_d20_full_packet_matrix_lift.py',
    'src/derive_d20_full_packet_matrix_lift.py',
    'data/invariants/d20/theorems/d20_full_packet_matrix_lift/manifest.json',
    'data/invariants/d20/theorems/d20_full_packet_matrix_lift/report.json',
    'src/certify_d20_packet_quotient_action_probe.py',
    'src/derive_d20_packet_quotient_action_probe.py',
    'data/invariants/d20/theorems/d20_packet_quotient_action_probe/manifest.json',
    'data/invariants/d20/theorems/d20_packet_quotient_action_probe/report.json',
    'src/certify_d20_explicit_packet_restriction_map_test.py',
    'src/derive_d20_explicit_packet_restriction_map_test.py',
    'data/invariants/d20/theorems/d20_explicit_packet_restriction_map_test/manifest.json',
    'data/invariants/d20/theorems/d20_explicit_packet_restriction_map_test/report.json',
    'src/certify_d20_packet_bridge_snf_obstruction.py',
    'src/derive_d20_packet_bridge_snf_obstruction.py',
    'data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/manifest.json',
    'data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json',
    'src/certify_d20_finite_contour_integration.py',
    'src/derive_d20_finite_contour_integration.py',
    'data/invariants/d20/theorems/d20_finite_contour_integration/manifest.json',
    'data/invariants/d20/theorems/d20_finite_contour_integration/report.json',
    'src/certify_d20_contour_sector_packet_prime_alignment.py',
    'src/derive_d20_contour_sector_packet_prime_alignment.py',
    'data/invariants/d20/theorems/d20_contour_sector_packet_prime_alignment/manifest.json',
    'data/invariants/d20/theorems/d20_contour_sector_packet_prime_alignment/report.json',
    'src/certify_d20_contour_charge_pairing_snf.py',
    'src/derive_d20_contour_charge_pairing_snf.py',
    'data/invariants/d20/theorems/d20_contour_charge_pairing_snf/manifest.json',
    'data/invariants/d20/theorems/d20_contour_charge_pairing_snf/report.json',
    'src/certify_d20_oriented_matroid_contour.py',
    'src/derive_d20_oriented_matroid_contour.py',
    'data/invariants/d20/theorems/d20_oriented_matroid_contour/manifest.json',
    'data/invariants/d20/theorems/d20_oriented_matroid_contour/report.json',
    'src/certify_d20_oriented_matroid_sector33_extension.py',
    'src/derive_d20_oriented_matroid_sector33_extension.py',
    'data/invariants/d20/theorems/d20_oriented_matroid_sector33_extension/manifest.json',
    'data/invariants/d20/theorems/d20_oriented_matroid_sector33_extension/report.json',
    'src/certify_d20_oriented_matroid_sector33_dual.py',
    'src/derive_d20_oriented_matroid_sector33_dual.py',
    'data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/manifest.json',
    'data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json',
    'src/certify_d20_oriented_matroid_tutte_os.py',
    'src/derive_d20_oriented_matroid_tutte_os.py',
    'data/invariants/d20/theorems/d20_oriented_matroid_tutte_os/manifest.json',
    'data/invariants/d20/theorems/d20_oriented_matroid_tutte_os/report.json',
    'src/certify_d20_oriented_matroid_prime_lift_audit.py',
    'src/derive_d20_oriented_matroid_prime_lift_audit.py',
    'data/invariants/d20/theorems/d20_oriented_matroid_prime_lift_audit/manifest.json',
    'data/invariants/d20/theorems/d20_oriented_matroid_prime_lift_audit/report.json',
    'src/certify_d20_oriented_matroid_rational_tutte_promotion.py',
    'src/derive_d20_oriented_matroid_rational_tutte_promotion.py',
    'data/invariants/d20/theorems/d20_oriented_matroid_rational_tutte_promotion/manifest.json',
    'data/invariants/d20/theorems/d20_oriented_matroid_rational_tutte_promotion/report.json',
    'src/certify_d20_oriented_matroid_rational_signed_circuits.py',
    'src/derive_d20_oriented_matroid_rational_signed_circuits.py',
    'data/invariants/d20/theorems/d20_oriented_matroid_rational_signed_circuits/manifest.json',
    'data/invariants/d20/theorems/d20_oriented_matroid_rational_signed_circuits/report.json',
    'src/certify_d20_strict_weak_order_sector26_clock.py',
    'src/derive_d20_strict_weak_order_sector26_clock.py',
    'data/invariants/d20/theorems/d20_strict_weak_order_sector26_clock/manifest.json',
    'data/invariants/d20/theorems/d20_strict_weak_order_sector26_clock/report.json',
    'src/certify_d20_intrinsic_triple_ordering_clock.py',
    'src/derive_d20_intrinsic_triple_ordering_clock.py',
    'data/invariants/d20/theorems/d20_intrinsic_triple_ordering_clock/manifest.json',
    'data/invariants/d20/theorems/d20_intrinsic_triple_ordering_clock/report.json',
    'src/certify_d20_triple_13_signature_uniqueness.py',
    'src/derive_d20_triple_13_signature_uniqueness.py',
    'data/invariants/d20/theorems/d20_triple_13_signature_uniqueness/manifest.json',
    'data/invariants/d20/theorems/d20_triple_13_signature_uniqueness/report.json',
    'src/certify_d20_raw_transport_3x3_discriminant13_search.py',
    'src/derive_d20_raw_transport_3x3_discriminant13_search.py',
    'data/invariants/d20/theorems/d20_raw_transport_3x3_discriminant13_search/manifest.json',
    'data/invariants/d20/theorems/d20_raw_transport_3x3_discriminant13_search/report.json',
    'src/certify_raw543_repo_c2_kernel_action.py',
    'src/derive_raw543_repo_c2_kernel_action.py',
    'data/invariants/d20/theorems/raw543_repo_c2_kernel_action/manifest.json',
    'data/invariants/d20/theorems/raw543_repo_c2_kernel_action/report.json',
    'data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_tau_matrix_f2.csv',
    'data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_nilpotent_N_tau_minus_I_matrix_f2.csv',
    'data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_kernel_orbits_raw543.csv',
    'data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_raw543_identities.csv',
    'data/invariants/d20/zero_axiom_coorient.json',
    'src/certify_zero_axiom_coorient_cache.py',
    'src/derive_d20_zero_axiom_coorient_cache_theorem.py',
    'data/invariants/d20/theorems/zero_axiom_coorient_cache/manifest.json',
    'data/invariants/d20/theorems/zero_axiom_coorient_cache/report.json',
    'src/certify_zero_axiom_coorient_strict_replay.py',
    'src/derive_d20_zero_axiom_coorient_strict_replay_theorem.py',
    'data/invariants/d20/theorems/zero_axiom_coorient_strict_replay/manifest.json',
    'data/invariants/d20/theorems/zero_axiom_coorient_strict_replay/report.json',
]


def block_or_compute(name: str, compute) -> Dict[str, Any]:
    block = cached_core_block(name)
    if block is not None:
        return block
    return compute()


def build_certificate() -> Dict[str, Any]:
    constants = load_json('data/raw/constants.json')
    manifest = file_manifest(CORE_FILES)
    blocks = {
        'finite_algebra': validate_tensor(constants),
        'relations': validate_relations(),
        'quotients': validate_quotients(),
        'simple_branching': validate_simple_branching(),
        'f_symbol_shape': validate_f_symbol_shape(cached_core_block('f_symbol_shape')),
        'clopen_boundary': validate_clopen(),
        # The derived blocks below are side certificates committed through
        # file_manifest/data_catalog.  Loading them keeps core certification
        # fast; certify_tube_lift and certify_tube_center keep strict
        # recomputation paths.
        'tube_center_lift': block_or_compute('tube_center_lift', validate_tube_center_lift),
        'tube_algebra_lift': block_or_compute('tube_algebra_lift', validate_tube_algebra_lift),
        'tube_center_algebra': block_or_compute('tube_center_algebra', validate_tube_center_algebra_lift),
        'tube_center_primitive_idempotents': validate_tube_center_primitive_idempotents(),
        'tube_pair_product_oracle': block_or_compute('tube_pair_product_oracle', validate_tube_pair_product_oracle),
        'full_tube_algebra_solver': block_or_compute('full_tube_algebra_solver', validate_full_tube_algebra_solver),
        'tube_projection_section': block_or_compute('tube_projection_section', validate_tube_projection_section),
        'half_braiding_solver': validate_half_braiding_solver(),
        'half_braiding_full_solve': validate_half_braiding_full_solve(),
        'half_braiding_prime_stability': validate_half_braiding_prime_stability(),
        'half_braiding_snf_certificate': validate_half_braiding_snf_certificate(),
        'sandpile_critical_group': validate_sandpile_critical_group(),
        'public_boundary_graph_invariants': validate_public_boundary_graph_invariants(),
        'fourier_residue_screen': validate_fourier_residue_screen(),
        'fourier_a985_sector_character_candidates': validate_fourier_a985_sector_character_candidates(),
        'fourier_screen0_tube_central_element': validate_fourier_screen0_tube_central_element(),
        'tube_sandpile_divisor_map': validate_tube_sandpile_divisor_map(),
        'tube_sandpile_kernel_flips': validate_tube_sandpile_kernel_flips(),
        'tube_sandpile_flip_move_presentation': validate_tube_sandpile_flip_move_presentation(),
        'tube_sandpile_flip_coset_classifier': validate_tube_sandpile_flip_coset_classifier(),
        'tube_sandpile_flip_profile_compression': validate_tube_sandpile_flip_profile_compression(),
        'tube_sandpile_flip_sector_refinement': validate_tube_sandpile_flip_sector_refinement(),
        'tube_sandpile_flip_sector_support_pullback': validate_tube_sandpile_flip_sector_support_pullback(),
        'tube_sandpile_flip_unsupported_state_classification': validate_tube_sandpile_flip_unsupported_state_classification(),
        'tube_sandpile_flip_formal_11_extension_test': validate_tube_sandpile_flip_formal_11_extension_test(),
        'd20_matrix_lift_conjecture': validate_d20_matrix_lift_conjecture(),
        'd20_minimal_matrix_charge_lift': validate_d20_minimal_matrix_charge_lift(),
        'd20_full_packet_matrix_lift': validate_d20_full_packet_matrix_lift(),
        'd20_packet_quotient_action_probe': validate_d20_packet_quotient_action_probe(),
        'd20_explicit_packet_restriction_map_test': validate_d20_explicit_packet_restriction_map_test(),
        'd20_packet_bridge_snf_obstruction': validate_d20_packet_bridge_snf_obstruction(),
        'd20_finite_contour_integration': validate_d20_finite_contour_integration(),
        'd20_contour_sector_packet_prime_alignment': validate_d20_contour_sector_packet_prime_alignment(),
        'd20_contour_charge_pairing_snf': validate_d20_contour_charge_pairing_snf(),
        'd20_oriented_matroid_contour': validate_d20_oriented_matroid_contour(),
        'd20_oriented_matroid_sector33_extension': validate_d20_oriented_matroid_sector33_extension(),
        'd20_oriented_matroid_sector33_dual': validate_d20_oriented_matroid_sector33_dual(),
        'd20_oriented_matroid_tutte_os': validate_d20_oriented_matroid_tutte_os(),
        'd20_oriented_matroid_prime_lift_audit': validate_d20_oriented_matroid_prime_lift_audit(),
        'd20_oriented_matroid_rational_tutte_promotion': validate_d20_oriented_matroid_rational_tutte_promotion(),
        'd20_oriented_matroid_rational_signed_circuits': validate_d20_oriented_matroid_rational_signed_circuits(),
        'd20_strict_weak_order_sector26_clock': validate_d20_strict_weak_order_sector26_clock(),
        'd20_intrinsic_triple_ordering_clock': validate_d20_intrinsic_triple_ordering_clock(),
        'd20_triple_13_signature_uniqueness': validate_d20_triple_13_signature_uniqueness(),
        'd20_raw_transport_3x3_discriminant13_search': validate_d20_raw_transport_3x3_discriminant13_search(),
        'theorem_registry_halloween_source_package_binding': validate_theorem_registry_source_package_binding(),
        'raw543_repo_c2_kernel_action': validate_raw543_repo_c2_kernel_action(),
        'zero_axiom_coorient_cache': validate_zero_axiom_coorient_cache(),
        'zero_axiom_coorient_strict_replay': validate_zero_axiom_coorient_strict_replay(),
    }
    return assemble_certificate(
        constants=constants,
        manifest=manifest,
        blocks=blocks,
        claims=verified_claims(blocks),
        hash_json=h_json,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='certificate.core.json')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    cert = build_certificate()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        if args.pretty:
            json.dump(cert, f, indent=2, sort_keys=True)
        else:
            json.dump(cert, f, sort_keys=True, separators=(',', ':'))
        f.write('\n')
    print('PASS')
    print('certificate_sha256 =', cert['certificate_sha256'])
    print('written =', out)


if __name__ == '__main__':
    main()
