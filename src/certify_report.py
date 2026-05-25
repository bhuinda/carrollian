from __future__ import annotations

from typing import Any, Callable, Dict

try:
    from .certify_io import raw_tensor_relpath
except ImportError:  # Supports `python src/certify_report.py`.
    from certify_io import raw_tensor_relpath


def data_catalog(manifest: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Human-readable object-data catalog.

    The certificate commits to files, but arrays stay external. This module owns
    report prose so the core verifier can focus on numerical checks.
    """
    tensor_path = raw_tensor_relpath()
    required_catalog = {
        'data/raw/constants.json': {
            'role': 'global constants and declared finite-object dimensions',
            'complete': True,
            'required_for_reconstruction': True,
            'contains': ['object sizes', 'Wedderburn summary', 'declared tensor counts'],
        },
        tensor_path: {
            'role': 'sparse multiplication tensor T_985',
            'complete': True,
            'required_for_reconstruction': True,
            'contains': ['1,414,965 nonzero products (alpha,beta,gamma,coefficient)', 'representative relation data', 'object-pair relation matrix'],
        },
        'data/raw/relation_memberships.npz': {
            'role': 'complete relation membership table R_alpha subset Omega x Omega',
            'complete': True,
            'required_for_reconstruction': True,
            'contains': ['6,635,776 encoded ordered dodecad pairs', '986 offsets for 985 relation segments', 'object block labels', 'relation representatives'],
        },
        'data/raw/quotients.npz': {
            'role': 'quotient maps and quotient multiplication tensors',
            'complete': True,
            'required_for_reconstruction': True,
            'contains': ['q42 map', 'q12 map', 'A42 tensor', 'A12 tensor'],
        },
        'data/raw/simple_branching_matrices.npz': {
            'role': 'simple-branching matrices for square descent',
            'complete': True,
            'required_for_reconstruction': True,
            'contains': ['B236->42', 'B42->12', 'B236->12', 'simple dimensions'],
        },
        'data/raw/leech_projective_generators.npz': {
            'role': 'Leech-boundary generator data used by the boundary reconstruction certificate',
            'complete': True,
            'required_for_reconstruction': False,
            'contains': ['projective-shell generator data for the Leech boundary layer'],
        },
    }
    optional_catalog = {
        'data/samples/f_symbol_permutations_256.npz': {
            'role': 'sampled concrete F-symbol permutation witnesses',
            'complete': False,
            'required_for_reconstruction': False,
            'contains': ['256 sampled left/right associator-basis permutations'],
        },
        'data/samples/f_symbol_inventory_manifest_1m.npz': {
            'role': 'prefix manifest for the F-symbol inventory address space',
            'complete': False,
            'required_for_reconstruction': False,
            'contains': ['first 1,000,000 rows of the deterministic F-symbol inventory manifest'],
        },
    }
    out = {}
    for rel, info in required_catalog.items():
        m = manifest.get(rel, {})
        x = dict(info)
        x.update({'bytes': m.get('bytes'), 'sha256': m.get('sha256')})
        out[rel] = x
    for rel, info in optional_catalog.items():
        if rel not in manifest:
            continue
        m = manifest[rel]
        x = dict(info)
        x.update({'bytes': m.get('bytes'), 'sha256': m.get('sha256')})
        out[rel] = x
    # Derived files are complete certificates of checks, not primitive object payload.
    for rel, m in manifest.items():
        if rel.startswith('data/derived/'):
            out[rel] = {
                'role': 'derived verification block',
                'complete': True,
                'required_for_reconstruction': False,
                'contains': ['machine-readable proof/check output for one verified invariant'],
                'bytes': m.get('bytes'),
                'sha256': m.get('sha256'),
            }
        elif rel.startswith('data/samples/') and rel not in out:
            out[rel] = {
                'role': 'sample witness data',
                'complete': False,
                'required_for_reconstruction': False,
                'contains': ['sampled witness data'],
                'bytes': m.get('bytes'),
                'sha256': m.get('sha256'),
            }
        elif rel.startswith('src/') and rel not in out:
            out[rel] = {
                'role': 'verifier source code',
                'complete': True,
                'required_for_reconstruction': False,
                'contains': ['source code for certificate generation or optional solver execution'],
                'bytes': m.get('bytes'),
                'sha256': m.get('sha256'),
            }
    return out


def object_summary(constants: Dict[str, Any], blocks: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': 'd20 core',
        'code_algebra': 'A985',
        'points': 2576,
        'relations': 985,
        'tensor_support': 1414965,
        'coefficient_total': 2537360,
        'center_dimension': int(constants['wedderburn']['center_dim']),
        'wedderburn_block_size_multiplicities': constants['wedderburn']['block_size_multiplicities'],
        'quotient_dimensions': [985,236,42,12],
        'center_descent': [39,34,7,4],
        'measured_clopen_automorphism_group_order': 1,
        'tube_pairs': blocks['tube_center_lift']['tube_basis']['reverse_typed_tube_pairs'],
        'closed_loop_tube_basis': blocks['tube_algebra_lift']['closed_loop_algebra']['basis_count_total'],
        'closed_loop_tube_center_dimension': blocks['tube_algebra_lift']['center_skeleton']['center_dimension_total'],
        'closed_loop_tube_center_algebra_support': blocks['tube_center_algebra']['center_algebra']['center_product_support_rows_total'],
        'closed_loop_tube_primitive_idempotents': blocks['tube_center_primitive_idempotents']['idempotent_skeleton']['total_primitive_idempotents'],
        'tube_pair_basis': blocks['tube_pair_product_oracle']['tube_pair_basis']['basis_count_total'],
        'tube_pair_same_base_product_rows': blocks['tube_pair_product_oracle']['tube_product_address_space']['same_base_product_rows'],
        'full_tube_projection_kernel_dimension': blocks['full_tube_algebra_solver']['projection_solver']['projection_kernel_dimension_total'],
        'full_tube_projection_surjective': blocks['full_tube_algebra_solver']['projection_solver']['projection_surjective_on_all_base_blocks'],
        'tube_projection_section_pivots': blocks['tube_projection_section']['section']['pivot_tube_pair_representatives'],
        'tube_projection_section_nonzero_coefficients': blocks['tube_projection_section']['section']['section_nonzero_coefficients'],
        'tube_projection_section_identity': blocks['tube_projection_section']['section']['projection_section_identity'],
        'half_braiding_solver_unknowns': blocks['half_braiding_solver']['unknown_family']['unknown_count'],
        'half_braiding_full_rank': blocks['half_braiding_full_solve']['linear_system']['rank'],
        'half_braiding_full_nullity': blocks['half_braiding_full_solve']['linear_system']['nullity'],
        'half_braiding_prime_stability_primes': blocks['half_braiding_prime_stability']['field_primes'],
        'half_braiding_prime_stable_rank': blocks['half_braiding_prime_stability']['stable']['rank'],
        'half_braiding_prime_stable_nullity': blocks['half_braiding_prime_stability']['stable']['nullity'],
        'half_braiding_snf_diagonal_multiplicities': blocks['half_braiding_snf_certificate']['smith_normal_form']['diagonal_multiplicities'],
        'half_braiding_snf_rank_bad_primes': blocks['half_braiding_snf_certificate']['smith_normal_form']['rank_bad_primes'],
        'half_braiding_rank_determinantal_divisor': blocks['half_braiding_snf_certificate']['smith_normal_form']['rank_determinantal_divisor'],
        'sandpile_critical_group': blocks['sandpile_critical_group']['derived']['critical_group']['presentation'],
        'sandpile_critical_group_order': blocks['sandpile_critical_group']['derived']['critical_group']['order'],
        'sandpile_reduced_laplacian_snf': blocks['sandpile_critical_group']['derived']['smith_normal_form']['reduced_laplacian_diagonal'],
        'public_boundary_graph': blocks['public_boundary_graph_invariants']['derived']['public_graph'],
        'public_boundary_shift_entropy': blocks['public_boundary_graph_invariants']['derived']['symbolic_dynamics']['shift_entropy_natural'],
        'public_boundary_nonbacktracking_entropy': blocks['public_boundary_graph_invariants']['derived']['symbolic_dynamics']['nonbacktracking_entropy_natural'],
        'public_boundary_fourier_screen_defects': blocks['public_boundary_graph_invariants']['derived']['fourier_screen']['best_nontrivial_defect_count'],
        'fourier_residue_screen_count': len(blocks['fourier_residue_screen']['derived']['screens']),
        'fourier_residue_combined_rank': blocks['fourier_residue_screen']['derived']['combined_screen']['rank_over_f2'],
        'fourier_residue_cell_counts': blocks['fourier_residue_screen']['derived']['combined_screen']['cell_counts_by_signature'],
        'fourier_a985_candidate_count': blocks['fourier_a985_sector_character_candidates']['derived']['candidate_count'],
        'fourier_a985_public_zero_scalar_profile': blocks['fourier_a985_sector_character_candidates']['derived']['public_zero_scalar_profile'],
        'fourier_screen0_tube_element_support': blocks['fourier_screen0_tube_central_element']['derived']['reconstructed_from_local_primitives']['support'],
        'fourier_screen0_tube_closed_loop_commutator_failures': blocks['fourier_screen0_tube_central_element']['derived']['closed_loop_commutator']['failure_count'],
        'fourier_screen0_tube_full_a985_commutator_failures': blocks['fourier_screen0_tube_central_element']['derived']['full_a985_commutator_boundary']['failure_count'],
        'tube_sandpile_class_count_in_mask_image': blocks['tube_sandpile_divisor_map']['derived']['sandpile_class_count_in_mask_image'],
        'tube_sandpile_mixed_class_count': blocks['tube_sandpile_divisor_map']['derived']['tube_grade_vs_sandpile_class']['mixed_class_count'],
        'tube_sandpile_mixed_class_mask_count': blocks['tube_sandpile_divisor_map']['derived']['tube_grade_vs_sandpile_class']['mixed_class_mask_count'],
        'tube_sandpile_exact_divisor_fiber_count': blocks['tube_sandpile_kernel_flips']['derived']['exact_divisor_fiber_count'],
        'tube_sandpile_grade_flip_pair_count': blocks['tube_sandpile_kernel_flips']['derived']['grade_flip_pair_count'],
        'tube_sandpile_flip_delta_count': blocks['tube_sandpile_kernel_flips']['derived']['unique_grade_flip_delta_count'],
        'tube_sandpile_flip_delta_rank': blocks['tube_sandpile_kernel_flips']['derived']['grade_flip_delta_rank_over_f2'],
        'tube_sandpile_flip_presentation_relation_count': blocks['tube_sandpile_flip_move_presentation']['derived']['presentation']['relation_count'],
        'tube_sandpile_flip_presentation_basis_deltas': blocks['tube_sandpile_flip_move_presentation']['derived']['presentation']['basis_delta_masks'],
        'tube_sandpile_five_cover_rank': blocks['tube_sandpile_flip_move_presentation']['derived']['five_cover']['rank_over_f2'],
        'tube_sandpile_five_cover_relation_count': blocks['tube_sandpile_flip_move_presentation']['derived']['five_cover']['relation_count'],
        'tube_sandpile_five_cover_quotient_dimension': blocks['tube_sandpile_flip_move_presentation']['derived']['five_cover']['quotient_dimension'],
        'tube_sandpile_flip_coset_count': blocks['tube_sandpile_flip_coset_classifier']['derived']['coset_count'],
        'tube_sandpile_flip_coset_pair_mass': blocks['tube_sandpile_flip_coset_classifier']['derived']['grade_flip_pair_mass'],
        'tube_sandpile_flip_coset_cover_summary': blocks['tube_sandpile_flip_coset_classifier']['derived']['cover_span_coset_summary'],
        'tube_sandpile_flip_profile_public_automorphism_compression_trivial': blocks['tube_sandpile_flip_profile_compression']['derived']['automorphism_compression']['public_automorphism_compression_is_trivial'],
        'tube_sandpile_flip_combined_order_profile_class_count': blocks['tube_sandpile_flip_profile_compression']['derived']['combined_order_profile']['class_count'],
        'tube_sandpile_flip_combined_order_profile_size_histogram': blocks['tube_sandpile_flip_profile_compression']['derived']['combined_order_profile']['class_size_histogram'],
        'tube_sandpile_flip_screen12_refinement_class_count': blocks['tube_sandpile_flip_sector_refinement']['derived']['screen12_pair_transition_profile']['class_count'],
        'tube_sandpile_flip_screen12_refinement_size_histogram': blocks['tube_sandpile_flip_sector_refinement']['derived']['screen12_pair_transition_profile']['class_size_histogram'],
        'tube_sandpile_flip_sector_support_pullback_class_count': blocks['tube_sandpile_flip_sector_support_pullback']['derived']['support_pullback_profile']['class_count'],
        'tube_sandpile_flip_sector_support_pullback_missing_states': blocks['tube_sandpile_flip_sector_support_pullback']['derived']['missing_screen12_states'],
        'tube_sandpile_flip_unsupported_state': blocks['tube_sandpile_flip_unsupported_state_classification']['derived']['classification']['unsupported_state'],
        'tube_sandpile_flip_unsupported_state_residue_count': blocks['tube_sandpile_flip_unsupported_state_classification']['derived']['residue_screen12_counts']['screen12_counts']['11'],
        'tube_sandpile_flip_formal_11_extension_status': blocks['tube_sandpile_flip_formal_11_extension_test']['status'],
        'tube_sandpile_flip_formal_11_extension_valid_nonempty_count': len(blocks['tube_sandpile_flip_formal_11_extension_test']['derived']['valid_nonempty_extension_scenarios']),
        'd20_matrix_lift_conjecture_status': blocks['d20_matrix_lift_conjecture']['status'],
        'd20_matrix_lift_shadow_strength': blocks['d20_matrix_lift_conjecture']['derived']['classification']['strength'],
        'd20_matrix_lift_missing_bridge_count': blocks['d20_matrix_lift_conjecture']['derived']['missing_bridge_count'],
        'd20_minimal_matrix_charge_lift_status': blocks['d20_minimal_matrix_charge_lift']['status'],
        'd20_minimal_matrix_charge_lift_algebra': blocks['d20_minimal_matrix_charge_lift']['derived']['minimal_matrix_charge_lift']['algebra'],
        'd20_minimal_matrix_charge_lift_status_detail': blocks['d20_minimal_matrix_charge_lift']['derived']['minimal_matrix_charge_lift']['lift_status'],
        'd20_full_packet_matrix_lift_status': blocks['d20_full_packet_matrix_lift']['status'],
        'd20_full_packet_matrix_lift_algebra': blocks['d20_full_packet_matrix_lift']['derived']['acting_summary']['block_algebra'],
        'd20_full_packet_matrix_lift_a985_kernel_bound': blocks['d20_full_packet_matrix_lift']['derived']['a985_action_probe']['minimum_kernel_dimension_for_any_a985_map_into_this_block_lift'],
        'd20_packet_quotient_action_probe_status': blocks['d20_packet_quotient_action_probe']['status'],
        'd20_packet_quotient_action_probe_operator': blocks['d20_packet_quotient_action_probe']['derived']['operator_probe_summary']['strongest_certified_packet_action'],
        'd20_packet_quotient_action_probe_a985_tube_found': blocks['d20_packet_quotient_action_probe']['derived']['operator_probe_summary']['a985_or_tube_packet_operator_found'],
        'd20_explicit_packet_restriction_map_test_status': blocks['d20_explicit_packet_restriction_map_test']['status'],
        'd20_explicit_packet_restriction_map_constructed': blocks['d20_explicit_packet_restriction_map_test']['derived']['restriction_summary']['constructed_restriction'],
        'd20_explicit_packet_restriction_missing_bridge_count': blocks['d20_explicit_packet_restriction_map_test']['derived']['restriction_summary']['missing_bridge_count'],
        'd20_packet_bridge_snf_obstruction_status': blocks['d20_packet_bridge_snf_obstruction']['status'],
        'd20_packet_bridge_snf_diagonal_multiplicities': blocks['d20_packet_bridge_snf_obstruction']['derived']['obstruction_summary']['smith_diagonal_multiplicities'],
        'd20_packet_bridge_snf_cokernel': blocks['d20_packet_bridge_snf_obstruction']['derived']['obstruction_summary']['cokernel'],
        'd20_packet_bridge_snf_torsion_primes': blocks['d20_packet_bridge_snf_obstruction']['derived']['obstruction_summary']['torsion_primes'],
        'd20_finite_contour_integration_status': blocks['d20_finite_contour_integration']['status'],
        'd20_finite_contour_cycle_rank': blocks['d20_finite_contour_integration']['derived']['contour_summary']['cycle_rank_expected'],
        'd20_finite_contour_signed_gcd': blocks['d20_finite_contour_integration']['derived']['signed_contour_residue']['gcd_signed_integrals'],
        'd20_finite_contour_mod26_residue': blocks['d20_finite_contour_integration']['derived']['signed_contour_residue']['mod26_residue_vector'],
        'd20_contour_sector_packet_prime_alignment_status': blocks['d20_contour_sector_packet_prime_alignment']['status'],
        'd20_contour_sector_packet_prime_split': blocks['d20_contour_sector_packet_prime_alignment']['derived']['alignment_summary']['union_prime_split'],
        'd20_contour_sector_packet_common_prime': blocks['d20_contour_sector_packet_prime_alignment']['derived']['alignment_summary']['common_prime_all_layers'],
        'd20_contour_sector_packet_alignment_strength': blocks['d20_contour_sector_packet_prime_alignment']['derived']['alignment_summary']['alignment_strength'],
        'd20_contour_charge_pairing_snf_status': blocks['d20_contour_charge_pairing_snf']['status'],
        'd20_contour_charge_pairing_row_subgroup_order': blocks['d20_contour_charge_pairing_snf']['derived']['pairing_summary']['finite_row_subgroup_order'],
        'd20_contour_charge_pairing_quotient_smith_diagonal': blocks['d20_contour_charge_pairing_snf']['derived']['pairing_summary']['finite_quotient_smith_diagonal'],
        'd20_contour_charge_pairing_quotient_order': blocks['d20_contour_charge_pairing_snf']['derived']['pairing_summary']['finite_quotient_order'],
        'd20_contour_charge_pairing_strict_weak_order_count': blocks['d20_contour_charge_pairing_snf']['derived']['weak_order_summary']['strict_weak_order_count'],
        'd20_oriented_matroid_contour_status': blocks['d20_oriented_matroid_contour']['status'],
        'd20_oriented_matroid_circuit_count': blocks['d20_oriented_matroid_contour']['derived']['contour_oriented_matroid_summary']['signed_circuit_count'],
        'd20_oriented_matroid_cocircuit_count': blocks['d20_oriented_matroid_contour']['derived']['contour_oriented_matroid_summary']['signed_cocircuit_count'],
        'd20_oriented_matroid_gamma8_tope_extends': blocks['d20_oriented_matroid_contour']['derived']['gamma8_tests']['active_positive_extends_to_acyclic_tope'],
        'd20_oriented_matroid_gamma8_stabilizer_order': blocks['d20_oriented_matroid_contour']['derived']['pure_contour_symmetry_tests']['active_positive_signed_row_stabilizer_order'],
        'd20_oriented_matroid_public_automorphism_order': blocks['d20_oriented_matroid_contour']['derived']['pure_contour_symmetry_tests']['public_graph_automorphism_order'],
        'd20_oriented_matroid_sector33_extension_status': blocks['d20_oriented_matroid_sector33_extension']['status'],
        'd20_oriented_matroid_sector33_positive_circuit': blocks['d20_oriented_matroid_sector33_extension']['derived']['sector33_height_attachment']['is_positive_circuit'],
        'd20_oriented_matroid_sector33_cocircuit_verdict': blocks['d20_oriented_matroid_sector33_extension']['derived']['sector33_cocircuit_summary']['verdict'],
        'd20_oriented_matroid_sector33_transport_scalar': blocks['d20_oriented_matroid_sector33_extension']['derived']['sector33_height_attachment']['new_column']['height_coordinate'],
        'd20_oriented_matroid_sector33_dual_status': blocks['d20_oriented_matroid_sector33_dual']['status'],
        'd20_oriented_matroid_sector33_dual_rank': blocks['d20_oriented_matroid_sector33_dual']['derived']['dual_summary']['dual_rank'],
        'd20_oriented_matroid_sector33_dual_cocircuit': blocks['d20_oriented_matroid_sector33_dual']['derived']['dual_positive_cocircuit']['support_is_dual_cocircuit'],
        'd20_oriented_matroid_sector33_dual_hyperplane_rank': blocks['d20_oriented_matroid_sector33_dual']['derived']['dual_positive_cocircuit']['dual_hyperplane_rank'],
        'd20_oriented_matroid_tutte_os_status': blocks['d20_oriented_matroid_tutte_os']['status'],
        'd20_oriented_matroid_tutte_os_field_prime': blocks['d20_oriented_matroid_tutte_os']['derived']['field_matroid']['field_prime'],
        'd20_oriented_matroid_tutte_os_rank': blocks['d20_oriented_matroid_tutte_os']['derived']['field_matroid']['rank'],
        'd20_oriented_matroid_tutte_os_term_count': blocks['d20_oriented_matroid_tutte_os']['derived']['tutte_polynomial']['term_count'],
        'd20_oriented_matroid_tutte_os_basis_count': blocks['d20_oriented_matroid_tutte_os']['derived']['tutte_polynomial']['specializations']['T_1_1_basis_count'],
        'd20_oriented_matroid_tutte_os_total_nbc_monomials': blocks['d20_oriented_matroid_tutte_os']['derived']['orlik_solomon_algebra']['total_nbc_monomials'],
        'd20_oriented_matroid_prime_lift_audit_status': blocks['d20_oriented_matroid_prime_lift_audit']['status'],
        'd20_oriented_matroid_prime_lift_audit_primes': blocks['d20_oriented_matroid_prime_lift_audit']['derived']['audit_primes'],
        'd20_oriented_matroid_prime_lift_audit_exact_q_rank': blocks['d20_oriented_matroid_prime_lift_audit']['derived']['exact_rational_audit']['matrix_rank_over_q'],
        'd20_oriented_matroid_prime_lift_audit_exact_q_circuit': blocks['d20_oriented_matroid_prime_lift_audit']['derived']['exact_rational_audit']['positive_support_is_exact_q_circuit'],
        'd20_oriented_matroid_prime_lift_audit_full_q_promotion': blocks['d20_oriented_matroid_prime_lift_audit']['derived']['promotion_boundary']['full_rational_promotion_certified'],
        'd20_oriented_matroid_rational_tutte_promotion_status': blocks['d20_oriented_matroid_rational_tutte_promotion']['status'],
        'd20_oriented_matroid_rational_tutte_promotion_rank': blocks['d20_oriented_matroid_rational_tutte_promotion']['derived']['rational_matrix']['rank'],
        'd20_oriented_matroid_rational_tutte_promotion_cache_entries': blocks['d20_oriented_matroid_rational_tutte_promotion']['derived']['exact_deletion_contraction_replay']['cache_entries'],
        'd20_oriented_matroid_rational_tutte_promotion_term_count': blocks['d20_oriented_matroid_rational_tutte_promotion']['derived']['rational_tutte_polynomial']['term_count'],
        'd20_oriented_matroid_rational_tutte_promotion_promoted': blocks['d20_oriented_matroid_rational_tutte_promotion']['derived']['promotion_boundary']['rational_tutte_os_promoted'],
        'd20_oriented_matroid_rational_signed_circuits_status': blocks['d20_oriented_matroid_rational_signed_circuits']['status'],
        'd20_oriented_matroid_rational_circuit_support_count': blocks['d20_oriented_matroid_rational_signed_circuits']['derived']['generation_summary']['rational_circuit_support_count'],
        'd20_oriented_matroid_rational_signed_circuit_count': blocks['d20_oriented_matroid_rational_signed_circuits']['derived']['generation_summary']['signed_rational_circuit_count'],
        'd20_oriented_matroid_rational_signed_circuits_positive_gamma8': blocks['d20_oriented_matroid_rational_signed_circuits']['derived']['positive_gamma8_e33_circuit'],
        'd20_oriented_matroid_rational_signed_cocircuit_full_set': blocks['d20_oriented_matroid_rational_signed_circuits']['derived']['promotion_boundary']['full_rational_signed_cocircuit_set_certified'],
        'd20_strict_weak_order_sector26_clock_status': blocks['d20_strict_weak_order_sector26_clock']['status'],
        'd20_strict_weak_order_sector26_clock_count': blocks['d20_strict_weak_order_sector26_clock']['derived']['weak_order_summary']['strict_weak_order_count'],
        'd20_strict_weak_order_sector26_clock_matches_pairing_line': blocks['d20_strict_weak_order_sector26_clock']['derived']['weak_order_summary']['matches_contour_charge_pairing_order13_line'],
        'd20_strict_weak_order_sector26_clock_doubled_count': len(blocks['d20_strict_weak_order_sector26_clock']['derived']['weak_order_summary']['polarity_doubled_sector26_image']),
        'd20_strict_weak_order_sector26_clock_full_ledger_stabilizer': blocks['d20_strict_weak_order_sector26_clock']['derived']['d20_symmetry_test']['full_augmented_ledger_stabilizer_order'],
        'd20_intrinsic_triple_ordering_clock_status': blocks['d20_intrinsic_triple_ordering_clock']['status'],
        'd20_intrinsic_triple_ordering_clock_basis': blocks['d20_intrinsic_triple_ordering_clock']['derived']['intrinsic_triple_summary']['basis_order'],
        'd20_intrinsic_triple_ordering_clock_discriminant': blocks['d20_intrinsic_triple_ordering_clock']['derived']['intrinsic_triple_summary']['composite_block_discriminant'],
        'd20_intrinsic_triple_ordering_clock_permutation_stabilizer': blocks['d20_intrinsic_triple_ordering_clock']['derived']['intrinsic_triple_summary']['transport_preserving_permutation_count'],
        'd20_intrinsic_triple_ordering_clock_matches_prior_line': blocks['d20_intrinsic_triple_ordering_clock']['derived']['clock_summary']['matches_prior_weak_order_clock_line'],
        'd20_triple_13_signature_uniqueness_status': blocks['d20_triple_13_signature_uniqueness']['status'],
        'd20_triple_13_signature_unique_count': blocks['d20_triple_13_signature_uniqueness']['derived']['summary']['triple_13_signature_count'],
        'd20_triple_13_signature_unique_basis': blocks['d20_triple_13_signature_uniqueness']['derived']['unique_certified_triple_signatures'][0]['basis_order'],
        'd20_triple_13_signature_corpus_count': blocks['d20_triple_13_signature_uniqueness']['derived']['summary']['corpus_report_count'],
        'd20_triple_13_signature_uniqueness_scope': blocks['d20_triple_13_signature_uniqueness']['derived']['summary']['classification_scope'],
        'd20_raw_transport_3x3_search_status': blocks['d20_raw_transport_3x3_discriminant13_search']['status'],
        'd20_raw_transport_3x3_search_principal_subforms': blocks['d20_raw_transport_3x3_discriminant13_search']['derived']['summary']['principal_3x3_subform_count'],
        'd20_raw_transport_3x3_search_raw_certificate_hits': blocks['d20_raw_transport_3x3_discriminant13_search']['derived']['summary']['raw_or_certificate_discriminant13_hit_count'],
        'd20_raw_transport_3x3_search_unreported_hits': blocks['d20_raw_transport_3x3_discriminant13_search']['derived']['summary']['unreported_discriminant13_hit_count'],
        'raw543_repo_c2_kernel_action_status': blocks['raw543_repo_c2_kernel_action']['status'],
        'raw543_repo_c2_kernel_basis_image_masks': blocks['raw543_repo_c2_kernel_action']['derived']['actual_nontrivial_c2_preserver']['basis_image_masks'],
        'raw543_repo_c2_kernel_nonzero_orbits': blocks['raw543_repo_c2_kernel_action']['derived']['raw543_kernel']['nonzero_kernel_orbit_count'],
        'raw543_repo_c2_kernel_fixed_nonzero_orbits': blocks['raw543_repo_c2_kernel_action']['derived']['raw543_kernel']['fixed_nonzero_orbits'],
        'raw543_repo_c2_kernel_two_cycle_orbits': blocks['raw543_repo_c2_kernel_action']['derived']['raw543_kernel']['two_cycle_orbits'],
        'zero_axiom_coorient_cache_base': blocks['zero_axiom_coorient_cache']['derived']['canonical_base'],
        'zero_axiom_coorient_cache_closure_order': blocks['zero_axiom_coorient_cache']['derived']['closed_action']['group_order'],
        'zero_axiom_coorient_strict_replay_byte_length': blocks['zero_axiom_coorient_strict_replay']['derived']['cache_byte_length'],
        'zero_axiom_coorient_strict_replay_newline': blocks['zero_axiom_coorient_strict_replay']['derived']['cache_newline'],
    }


def verified_claims(blocks: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Plain-language certificate index. No opaque status strings."""
    finite = blocks['finite_algebra']
    rel = blocks['relations']
    quot = blocks['quotients']
    sb = blocks['simple_branching']
    fshape = blocks['f_symbol_shape']
    clo = blocks['clopen_boundary']
    tube = blocks.get('tube_center_lift', {})
    return [
        {
            'id': 'finite_algebra',
            'name': 'A985 multiplication tensor',
            'status': 'verified',
            'statement': 'The sparse tensor has 1,414,965 nonzero products and total coefficient mass 2,537,360.',
            'evidence': {'support': finite['support'], 'coefficient_total': finite['coefficient_total']},
        },
        {
            'id': 'relation_partition',
            'name': '985 relations partition Omega x Omega',
            'status': 'verified',
            'statement': 'The relation-membership table partitions all 2,576^2 ordered dodecad pairs into 985 typed relations.',
            'evidence': {'encoded_pairs': rel['encoded_pairs'], 'partition_ok': rel['partition_ok'], 'segments_typed': rel['segments_typed']},
        },
        {
            'id': 'relation_merkle',
            'name': 'content address for relation table',
            'status': 'verified',
            'statement': 'Each relation segment is hashed, the relation list has a global Merkle-style root, and transpose duality is an involution.',
            'evidence': {'relation_merkle_root': rel['relation_merkle_root'], 'transpose_involution_ok': rel['transpose_involution_ok']},
        },
        {
            'id': 'quotient_tower',
            'name': 'terminal quotient readouts A985 -> A42 -> A12',
            'status': 'verified',
            'statement': 'The stored A985-to-A42 and A42-to-A12 quotient maps/tensors close. This is a terminal quotient-readout claim, not a claim that the full d20 stack is strictly a quotient tower or that A236 is an ordinary A985 quotient.',
            'evidence': {'q42_classes': quot['q42_classes'], 'q12_classes': quot['q12_classes'], 'q42_to_q12_consistent': quot['q42_to_q12_consistent'], 'scope': 'A236 is covered by native simple-branching/fusion data, outside this terminal quotient-readout claim.'},
        },
        {
            'id': 'simple_branching_square',
            'name': 'simple-branching naturality square',
            'status': 'verified',
            'statement': 'The simple branching matrices satisfy B236_to_12 = B236_to_42 * B42_to_12 with zero defect.',
            'evidence': {'matrix_identity': sb['naturality_B236_12_equals_B236_42_B42_12'], 'defect_l1': sb['defect_l1'], 'shapes': [sb['B236_42_shape'], sb['B42_12_shape'], sb['B236_12_shape']]},
        },
        {
            'id': 'f_symbol_address_space',
            'name': 'F-symbol inventory address space',
            'status': 'verified',
            'statement': 'The full left-bracketing associator-domain has an exact row count and is represented by deterministic row addressing, not by a monolithic table.',
            'evidence': {'full_left_bracketing_rows': fshape['full_left_bracketing_rows'], 'representative_pair_basis_vectors': fshape['representative_pair_basis_vectors']},
        },
        {
            'id': 'f_symbol_sample_bijections',
            'name': 'sampled F-symbol permutation witnesses',
            'status': 'sampled verification',
            'statement': 'The sampled left/right associator-basis maps are verified sparse bijections.',
            'evidence': {'sample_permutations': fshape['sample_permutations'], 'sample_basis_vectors': fshape['sample_basis_vectors'], 'bijections_ok': fshape['sample_permutation_bijections_ok']},
        },
        {
            'id': 'clopen_projection',
            'name': 'ternary clopen boundary projection',
            'status': 'verified',
            'statement': 'The six signed object blocks collapse to three sectors B,V,S; the length-2 adjacency is full and the measured sector sizes are unequal.',
            'evidence': {'alphabet': clo['alphabet'], 'ternary_sector_sizes': clo['ternary_sector_sizes'], 'level2_adjacency_full': clo['level2_adjacency_full']},
        },
        {
            'id': 'inverse_limit_levels',
            'name': 'finite approximation to 3^omega',
            'status': 'verified finite levels',
            'statement': 'The certificate records finite clopen levels 1 through 8 with word counts 3^k.',
            'evidence': {'levels': clo['inverse_limit_levels_certified'], 'word_counts': clo['inverse_limit_word_counts']},
        },
        {
            'id': 'measured_clopen_rigidity',
            'name': 'measured clopen automorphism group',
            'status': 'verified',
            'statement': 'The measured A985 refinement of the ternary boundary has no nontrivial symbol permutation automorphisms.',
            'evidence': {'measured_group_order': 1},
        },

        {
            'id': 'tube_center_lift',
            'name': 'tube / center skeleton lift',
            'status': 'verified skeleton',
            'statement': 'Reverse-typed relation pairs form a closed-loop tube basis; tube products land in diagonal sectors and transpose duality acts internally.',
            'evidence': {
                'reverse_typed_tube_pairs': tube.get('tube_basis', {}).get('reverse_typed_tube_pairs'),
                'tube_product_rows': tube.get('tube_basis', {}).get('tube_product_rows'),
                'tube_products_closed': tube.get('tube_basis', {}).get('tube_products_target_closed_diagonal_relations'),
                'identity_returns': tube.get('return_channels', {}).get('alpha_times_alpha_dual_contains_source_identity'),
                'A12_center_dimension': tube.get('quotient_center_lift', {}).get('A12_center_mod_prime', {}).get('dimension'),
                'A42_center_dimension': tube.get('quotient_center_lift', {}).get('A42_center_mod_prime', {}).get('dimension'),
            },
        },
        {
            'id': 'tube_algebra_lift',
            'name': 'closed-loop tube algebra lift',
            'status': 'verified skeleton plus sampled associativity',
            'statement': 'The closed diagonal relation sectors form a typed loop algebra with stable center dimensions over check primes, valid object units, and sampled associativity challenges passing.',
            'evidence': {
                'basis_count_total': blocks.get('tube_algebra_lift', {}).get('closed_loop_algebra', {}).get('basis_count_total'),
                'multiplication_support_rows_total': blocks.get('tube_algebra_lift', {}).get('closed_loop_algebra', {}).get('multiplication_support_rows_total'),
                'center_dimension_total': blocks.get('tube_algebra_lift', {}).get('center_skeleton', {}).get('center_dimension_total'),
                'center_dimension_by_object': blocks.get('tube_algebra_lift', {}).get('center_skeleton', {}).get('center_dimension_by_object'),
                'sampled_associativity_ok': blocks.get('tube_algebra_lift', {}).get('unit_and_associativity_challenges', {}).get('sampled_associativity_ok'),
            },
        },
        {
            'id': 'tube_center_algebra_lift',
            'name': 'closed-loop tube center algebra',
            'status': 'verified finite-field center basis',
            'statement': 'The verifier computes explicit finite-field center bases for the closed-loop tube blocks and verifies center multiplication closure, commutativity, unit laws, and sampled associativity.',
            'evidence': {
                'field_prime': blocks.get('tube_center_algebra', {}).get('field', {}).get('prime'),
                'total_center_dimension': blocks.get('tube_center_algebra', {}).get('center_algebra', {}).get('total_center_dimension'),
                'center_dimension_by_object': blocks.get('tube_center_algebra', {}).get('center_algebra', {}).get('center_dimension_by_object'),
                'center_product_support_rows_total': blocks.get('tube_center_algebra', {}).get('center_algebra', {}).get('center_product_support_rows_total'),
                'center_product_closure_ok': blocks.get('tube_center_algebra', {}).get('center_algebra', {}).get('center_product_closure_ok'),
                'center_product_commutative_ok': blocks.get('tube_center_algebra', {}).get('center_algebra', {}).get('center_product_commutative_ok'),
                'sampled_center_associativity_ok': blocks.get('tube_center_algebra', {}).get('unit_and_associativity', {}).get('sampled_center_associativity_ok'),
            },
        },
        {
            'id': 'tube_center_primitive_idempotents',
            'name': 'closed-loop tube primitive idempotent skeleton',
            'status': 'verified finite-field split idempotents',
            'statement': 'The closed-loop tube center algebra splits over F_1000003 into 109 pairwise orthogonal primitive central idempotents; these sum to the six block units and diagonalize deterministic separating elements.',
            'evidence': {
                'field_prime': blocks.get('tube_center_primitive_idempotents', {}).get('field', {}).get('prime'),
                'total_primitive_idempotents': blocks.get('tube_center_primitive_idempotents', {}).get('idempotent_skeleton', {}).get('total_primitive_idempotents'),
                'primitive_idempotents_by_object': blocks.get('tube_center_primitive_idempotents', {}).get('idempotent_skeleton', {}).get('primitive_idempotents_by_object'),
                'orthogonal': blocks.get('tube_center_primitive_idempotents', {}).get('idempotent_skeleton', {}).get('all_idempotents_orthogonal'),
                'sum_to_units': blocks.get('tube_center_primitive_idempotents', {}).get('idempotent_skeleton', {}).get('all_idempotents_sum_to_units'),
                'separator_diagonal_actions': blocks.get('tube_center_primitive_idempotents', {}).get('idempotent_skeleton', {}).get('all_separator_actions_diagonal'),
            },
        },

        {
            'id': 'tube_pair_product_oracle',
            'name': 'full tube-pair product address oracle',
            'status': 'verified address/projection layer',
            'statement': 'The verifier now certifies the full reverse-typed tube-pair basis, its projection into closed-loop multiplication, a deterministic same-base product row space, and sampled projected-product associativity.',
            'evidence': {
                'tube_pair_basis': blocks.get('tube_pair_product_oracle', {}).get('tube_pair_basis', {}).get('basis_count_total'),
                'basis_count_by_base_object': blocks.get('tube_pair_product_oracle', {}).get('tube_pair_basis', {}).get('basis_count_by_base_object'),
                'projection_rows': blocks.get('tube_pair_product_oracle', {}).get('tube_to_closed_loop_projection', {}).get('projection_rows'),
                'projection_coefficient_mass': blocks.get('tube_pair_product_oracle', {}).get('tube_to_closed_loop_projection', {}).get('projection_coefficient_mass'),
                'same_base_product_rows': blocks.get('tube_pair_product_oracle', {}).get('tube_product_address_space', {}).get('same_base_product_rows'),
                'decoder_roundtrip_ok': blocks.get('tube_pair_product_oracle', {}).get('tube_product_address_space', {}).get('decoder_roundtrip_ok'),
                'projected_product_challenges_ok': blocks.get('tube_pair_product_oracle', {}).get('projected_product_challenges', {}).get('all_projected_products_land_in_base_closed_loop_block'),
                'projected_associativity_ok': blocks.get('tube_pair_product_oracle', {}).get('projected_associativity_challenges', {}).get('ok'),
            },
        },

        {
            'id': 'full_tube_algebra_solver',
            'name': 'full tube algebra solver scaffold',
            'status': 'verified projection-rank boundary',
            'statement': 'The verifier constructs the full tube-pair projection solver: each base-object tube-pair block surjects onto its closed-loop algebra, with the projection kernel explicitly dimensioned and hashed. This is the required quotient boundary before full tube-module/Drinfeld-center representation theory.',
            'evidence': {
                'tube_pair_basis_total': blocks.get('full_tube_algebra_solver', {}).get('tube_pair_basis', {}).get('total'),
                'projection_rank_total': blocks.get('full_tube_algebra_solver', {}).get('projection_solver', {}).get('projection_rank_total'),
                'projection_kernel_dimension_total': blocks.get('full_tube_algebra_solver', {}).get('projection_solver', {}).get('projection_kernel_dimension_total'),
                'projection_surjective_on_all_base_blocks': blocks.get('full_tube_algebra_solver', {}).get('projection_solver', {}).get('projection_surjective_on_all_base_blocks'),
                'same_base_product_rows': blocks.get('full_tube_algebra_solver', {}).get('product_address_space', {}).get('same_base_product_rows'),
                'chunk_count': blocks.get('full_tube_algebra_solver', {}).get('product_address_space', {}).get('chunk_count'),
            },
        },

        {
            'id': 'tube_projection_section',
            'name': 'canonical section of the tube-pair projection',
            'status': 'verified right inverse',
            'statement': 'The verifier constructs a deterministic finite-field section S:Loop_297->TubePair_44521 of the tube-pair projection P, with P S = I_297. This gives every closed-loop class a canonical representative modulo the 44,224-dimensional projection kernel.',
            'evidence': {
                'tube_pair_basis_total': blocks.get('tube_projection_section', {}).get('projection', {}).get('tube_pair_basis_total'),
                'closed_loop_quotient_dimension': blocks.get('tube_projection_section', {}).get('projection', {}).get('closed_loop_quotient_dimension'),
                'projection_kernel_dimension': blocks.get('tube_projection_section', {}).get('projection', {}).get('projection_kernel_dimension'),
                'pivot_tube_pair_representatives': blocks.get('tube_projection_section', {}).get('section', {}).get('pivot_tube_pair_representatives'),
                'section_nonzero_coefficients': blocks.get('tube_projection_section', {}).get('section', {}).get('section_nonzero_coefficients'),
                'projection_section_identity': blocks.get('tube_projection_section', {}).get('section', {}).get('projection_section_identity'),
                'section_challenges_ok': blocks.get('tube_projection_section', {}).get('section_challenges', {}).get('ok'),
                'section_hash_root': blocks.get('tube_projection_section', {}).get('section', {}).get('section_hash_root'),
            },
        },

        {
            'id': 'half_braiding_solver',
            'name': 'Grothendieck half-braiding solver',
            'status': 'registered and prefix-sample verified',
            'statement': 'The verifier now contains a finite-field solver for the equations z_src(alpha)*alpha = alpha*z_tgt(alpha); the fast certificate recomputes a prefix-sample smoke check and exposes a full optional solve mode.',
            'evidence': {
                'field_prime': blocks.get('half_braiding_solver', {}).get('field', {}).get('prime'),
                'unknown_count': blocks.get('half_braiding_solver', {}).get('unknown_family', {}).get('unknown_count'),
                'unknown_count_by_object': blocks.get('half_braiding_solver', {}).get('unknown_family', {}).get('unknown_count_by_object'),
                'sample_relations': blocks.get('half_braiding_solver', {}).get('sample_relations'),
                'sample_rows': blocks.get('half_braiding_solver', {}).get('linear_system', {}).get('raw_rows_seen'),
                'sample_rank': blocks.get('half_braiding_solver', {}).get('linear_system', {}).get('rank'),
                'sample_nullity': blocks.get('half_braiding_solver', {}).get('linear_system', {}).get('nullity'),
            },
        },

        {
            'id': 'half_braiding_full_solve',
            'name': 'complete Grothendieck half-braiding solve',
            'status': 'complete finite-field solve recorded',
            'statement': 'Solving z_src(alpha)*alpha = alpha*z_tgt(alpha) over all 985 relations gives rank 258 and nullity 39 over F_1000003; the nullity matches the center dimension recorded for A985.',
            'evidence': {
                'field_prime': blocks.get('half_braiding_full_solve', {}).get('field', {}).get('prime'),
                'relations_used': blocks.get('half_braiding_full_solve', {}).get('relations_used'),
                'raw_rows_seen': blocks.get('half_braiding_full_solve', {}).get('linear_system', {}).get('raw_rows_seen'),
                'unknown_count': blocks.get('half_braiding_full_solve', {}).get('unknown_family', {}).get('unknown_count'),
                'rank': blocks.get('half_braiding_full_solve', {}).get('linear_system', {}).get('rank'),
                'nullity': blocks.get('half_braiding_full_solve', {}).get('linear_system', {}).get('nullity'),
                'free_columns_sha256': blocks.get('half_braiding_full_solve', {}).get('linear_system', {}).get('free_columns_sha256'),
            },
        },

        {
            'id': 'half_braiding_prime_stability',
            'name': 'multi-prime stability of the complete half-braiding solve',
            'status': 'complete finite-field solves recorded over multiple primes',
            'statement': 'The complete Grothendieck half-braiding system has stable rank 258 and nullity 39 over the certified primes, supporting that the 39-dimensional solution space is not a single-prime artifact.',
            'evidence': {
                'field_primes': blocks.get('half_braiding_prime_stability', {}).get('field_primes'),
                'rank': blocks.get('half_braiding_prime_stability', {}).get('stable', {}).get('rank'),
                'nullity': blocks.get('half_braiding_prime_stability', {}).get('stable', {}).get('nullity'),
                'raw_rows_seen': blocks.get('half_braiding_prime_stability', {}).get('stable', {}).get('raw_rows_seen'),
                'unknown_count': blocks.get('half_braiding_prime_stability', {}).get('stable', {}).get('unknown_count'),
            },
        },

        {
            'id': 'half_braiding_snf_certificate',
            'name': 'Smith normal form of the half-braiding system',
            'status': 'rank-bad-prime certificate',
            'statement': 'The integer half-braiding matrix has Smith diagonal multiplicities 1^231, 2^23, 4^4, 0^39; therefore rank drops only in characteristic 2.',
            'evidence': {
                'diagonal_multiplicities': blocks.get('half_braiding_snf_certificate', {}).get('smith_normal_form', {}).get('diagonal_multiplicities'),
                'rank_bad_primes': blocks.get('half_braiding_snf_certificate', {}).get('smith_normal_form', {}).get('rank_bad_primes'),
                'rank_determinantal_divisor': blocks.get('half_braiding_snf_certificate', {}).get('smith_normal_form', {}).get('rank_determinantal_divisor'),
                'rank_mod_2': blocks.get('half_braiding_snf_certificate', {}).get('two_primary_local_snf', {}).get('rank_mod_2'),
                'rank_drop_mod_2': blocks.get('half_braiding_snf_certificate', {}).get('two_primary_local_snf', {}).get('rank_drop_mod_2'),
                'odd_prime_gcd_exclusion': blocks.get('half_braiding_snf_certificate', {}).get('odd_prime_exclusion', {}).get('gcd_odd_part'),
            },
        },

        {
            'id': 'sandpile_critical_group',
            'name': 'D20 sandpile critical group',
            'status': 'certified reduced-Laplacian Smith normal form',
            'statement': 'The unweighted D20 H-cycle boundary graph has critical group Z/2 x Z/12 x Z/60^3 and 5,184,000 recurrent sandpile states.',
            'evidence': {
                'graph': blocks.get('sandpile_critical_group', {}).get('derived', {}).get('graph'),
                'invariant_factors': blocks.get('sandpile_critical_group', {}).get('derived', {}).get('critical_group', {}).get('invariant_factors'),
                'order': blocks.get('sandpile_critical_group', {}).get('derived', {}).get('critical_group', {}).get('order'),
                'spanning_tree_count': blocks.get('sandpile_critical_group', {}).get('derived', {}).get('critical_group', {}).get('spanning_tree_count'),
                'snf_diagonal_multiplicities': blocks.get('sandpile_critical_group', {}).get('derived', {}).get('smith_normal_form', {}).get('diagonal_multiplicities'),
            },
        },

        {
            'id': 'public_boundary_graph_invariants',
            'name': 'D20 public-boundary graph invariants',
            'status': 'certified finite graph, dynamics, and phase-screen invariants',
            'statement': 'The public boundary is the dodecahedral 20-vertex cubic graph with cycle rank 11, automorphism order 120, shift entropy log(3), nonbacktracking entropy log(2), and a best nontrivial signed-turn Fourier screen with two defects.',
            'evidence': {
                'graph': blocks.get('public_boundary_graph_invariants', {}).get('derived', {}).get('public_graph'),
                'cycle_rank': blocks.get('public_boundary_graph_invariants', {}).get('derived', {}).get('cycle_space', {}).get('cycle_rank'),
                'automorphism_order': blocks.get('public_boundary_graph_invariants', {}).get('derived', {}).get('automorphisms', {}).get('aut_gamma_order'),
                'sandpile': blocks.get('public_boundary_graph_invariants', {}).get('derived', {}).get('sandpile'),
                'symbolic_dynamics': blocks.get('public_boundary_graph_invariants', {}).get('derived', {}).get('symbolic_dynamics'),
                'fourier_screen': blocks.get('public_boundary_graph_invariants', {}).get('derived', {}).get('fourier_screen'),
            },
        },

        {
            'id': 'fourier_residue_screen',
            'name': 'D20 Fourier residue-screen characters',
            'status': 'certified finite F2 residue characters',
            'statement': 'The three best signed-turn two-defect screens act on all 2048 closed-return masks as nonzero F2 characters; each splits 1024/1024, and together they have rank 3 with eight 256-mask cells.',
            'evidence': {
                'residue_space': blocks.get('fourier_residue_screen', {}).get('derived', {}).get('residue_space'),
                'screens': blocks.get('fourier_residue_screen', {}).get('derived', {}).get('screens'),
                'combined_screen': {
                    key: value
                    for key, value in blocks.get('fourier_residue_screen', {})
                    .get('derived', {})
                    .get('combined_screen', {})
                    .items()
                    if key != 'residue_screen_rows'
                },
                'sandpile_pairing_seam': blocks.get('fourier_residue_screen', {}).get('derived', {}).get('sandpile_pairing_seam'),
            },
        },

        {
            'id': 'fourier_a985_sector_character_candidates',
            'name': 'D20 Fourier A985 sector-character candidates',
            'status': 'candidate evaluation certified',
            'statement': 'The three signed-turn residue screens act as signed-object involutions on the 109 local primitive tube pieces, but none is scalar on all 39 A985/tube sectors; only the first is scalar on every nonzero public-zero idempotent support.',
            'evidence': {
                'sector_count': blocks.get('fourier_a985_sector_character_candidates', {}).get('derived', {}).get('sector_count'),
                'local_primitive_piece_count': blocks.get('fourier_a985_sector_character_candidates', {}).get('derived', {}).get('local_primitive_piece_count'),
                'public_zero_scalar_profile': blocks.get('fourier_a985_sector_character_candidates', {}).get('derived', {}).get('public_zero_scalar_profile'),
                'pi33_scalars': blocks.get('fourier_a985_sector_character_candidates', {}).get('derived', {}).get('pi33_scalars'),
                'candidate_summary': [
                    {
                        'screen_id': row.get('screen_id'),
                        'homogeneous_sector_count': row.get('homogeneous_sector_count'),
                        'mixed_sector_count': row.get('mixed_sector_count'),
                        'descends_to_all_39_sector_scalars': row.get('descends_to_all_39_sector_scalars'),
                        'all_nonzero_public_zero_supports_scalar': row.get('all_nonzero_public_zero_supports_scalar'),
                    }
                    for row in blocks.get('fourier_a985_sector_character_candidates', {})
                    .get('derived', {})
                    .get('candidates', [])
                ],
            },
        },

        {
            'id': 'fourier_screen0_tube_central_element',
            'name': 'D20 Fourier screen-0 tube central element',
            'status': 'closed-loop central involution certified',
            'statement': 'The public-zero-compatible screen reconstructs from the 109 local primitive tube pieces as a six-term signed object unit. It squares to the closed-loop unit, commutes with all 297 closed-loop basis relations, and is explicitly not central on the full 985-relation algebra.',
            'evidence': {
                'object_phase_assignment': blocks.get('fourier_screen0_tube_central_element', {}).get('derived', {}).get('object_phase_assignment'),
                'signed_object_unit': blocks.get('fourier_screen0_tube_central_element', {}).get('derived', {}).get('signed_object_unit'),
                'closed_loop_commutator': blocks.get('fourier_screen0_tube_central_element', {}).get('derived', {}).get('closed_loop_commutator'),
                'full_a985_commutator_boundary': {
                    key: value
                    for key, value in blocks.get('fourier_screen0_tube_central_element', {})
                    .get('derived', {})
                    .get('full_a985_commutator_boundary', {})
                    .items()
                    if key != 'failures_first_16'
                },
                'public_zero_support_action': blocks.get('fourier_screen0_tube_central_element', {}).get('derived', {}).get('public_zero_support_action'),
            },
        },

        {
            'id': 'tube_sandpile_divisor_map',
            'name': 'D20 tube grade to sandpile divisor map',
            'status': 'certified divisor-class comparison',
            'statement': 'The screen-0 tube grade and canonical oriented-edge divisor map send the 2048 closed-return masks to 1360 D20 sandpile classes. The tube grade is not sandpile-class invariant: 154 classes are mixed, accounting for 576 masks.',
            'evidence': {
                'tree_count': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('tree_count'),
                'screen0_defect_mask': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('screen0_defect_mask'),
                'tube_grade_counts': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('tube_grade_counts'),
                'sandpile_class_count_in_mask_image': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('sandpile_class_count_in_mask_image'),
                'zero_class_masks': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('zero_class_masks'),
                'tube_grade_vs_sandpile_class': {
                    key: value
                    for key, value in blocks.get('tube_sandpile_divisor_map', {})
                    .get('derived', {})
                    .get('tube_grade_vs_sandpile_class', {})
                    .items()
                    if key != 'mixed_classes_first_16'
                },
                'class_multiplicity_histogram': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('class_multiplicity_histogram'),
                'sandpile_class_order_histogram_by_class': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('sandpile_class_order_histogram_by_class'),
                'adjugate_certificate': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('adjugate_certificate'),
                'mask_divisor_rows_sha256': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('mask_divisor_rows_sha256'),
                'sandpile_class_rows_sha256': blocks.get('tube_sandpile_divisor_map', {}).get('derived', {}).get('sandpile_class_rows_sha256'),
            },
        },

        {
            'id': 'tube_sandpile_kernel_flips',
            'name': 'D20 exact-divisor tube-grade flip moves',
            'status': 'certified exact-divisor move census',
            'statement': 'The 154 mixed sandpile classes are already mixed inside exact oriented-divisor fibers. There are 1285 same-divisor grade-flip mask pairs, 392 distinct XOR flip moves, and these flip moves span rank 11 over F2. A deterministic five-move cover hits every mixed fiber.',
            'evidence': {
                'exact_divisor_fiber_count': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('exact_divisor_fiber_count'),
                'sandpile_class_exact_divisor_count_histogram': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('sandpile_class_exact_divisor_count_histogram'),
                'mixed_exact_divisor_fiber_count': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('mixed_exact_divisor_fiber_count'),
                'mixed_exact_divisor_mask_count': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('mixed_exact_divisor_mask_count'),
                'same_divisor_pair_count': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('same_divisor_pair_count'),
                'grade_flip_pair_count': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('grade_flip_pair_count'),
                'grade_preserving_pair_count': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('grade_preserving_pair_count'),
                'unique_grade_flip_delta_count': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('unique_grade_flip_delta_count'),
                'single_bit_flip_deltas': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('single_bit_flip_deltas'),
                'grade_flip_delta_rank_over_f2': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('grade_flip_delta_rank_over_f2'),
                'grade_flip_pair_delta_weight_histogram': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('grade_flip_pair_delta_weight_histogram'),
                'small_flip_cover_rows': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('small_flip_cover_rows'),
                'canonical_flip_witness_rows_sha256': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('canonical_flip_witness_rows_sha256'),
                'grade_flip_pair_rows_sha256': blocks.get('tube_sandpile_kernel_flips', {}).get('derived', {}).get('grade_flip_pair_rows_sha256'),
            },
        },

        {
            'id': 'tube_sandpile_flip_move_presentation',
            'name': 'D20 finite F2 flip-move presentation',
            'status': 'certified finite presentation',
            'statement': 'The 392 exact-divisor tube-grade flip moves present the full 11-dimensional F2 residue move space. A canonical 11-move basis gives 381 linear relations. The five cover moves are independent, so there is no nonzero F2 relation among them.',
            'evidence': {
                'generator_count': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('presentation', {}).get('generator_count'),
                'basis_count': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('presentation', {}).get('basis_count'),
                'basis_delta_masks': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('presentation', {}).get('basis_delta_masks'),
                'relation_count': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('presentation', {}).get('relation_count'),
                'relation_weight_histogram': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('presentation', {}).get('relation_weight_histogram'),
                'quotient_order': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('presentation', {}).get('quotient_order'),
                'five_cover': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('five_cover'),
                'relation_rows_sha256': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('relation_rows_sha256'),
                'cover_nonzero_sum_rows_sha256': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('cover_nonzero_sum_rows_sha256'),
                'cover_coset_rows_sha256': blocks.get('tube_sandpile_flip_move_presentation', {}).get('derived', {}).get('cover_coset_rows_sha256'),
            },
        },

        {
            'id': 'tube_sandpile_flip_coset_classifier',
            'name': 'D20 flip-move quotient coset classifier',
            'status': 'certified 64-coset observable classifier',
            'statement': 'The quotient of the 392 exact-divisor grade-flip moves by the five-cover span has 64 observable cosets. The cover-span coset is the unique coset containing the five cover moves and it touches all 154 mixed exact-divisor fibers.',
            'evidence': {
                'quotient_dimension': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('quotient_dimension'),
                'coset_count': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('coset_count'),
                'generator_delta_mass': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('generator_delta_mass'),
                'grade_flip_pair_mass': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('grade_flip_pair_mass'),
                'exact_divisor_fiber_union_count': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('exact_divisor_fiber_union_count'),
                'sandpile_class_union_count': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('sandpile_class_union_count'),
                'cover_span_coset_summary': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('cover_span_coset_summary'),
                'generator_delta_count_histogram': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('generator_delta_count_histogram'),
                'grade_flip_pair_count_histogram': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('grade_flip_pair_count_histogram'),
                'pair_sandpile_class_order_histogram': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('pair_sandpile_class_order_histogram'),
                'coset_rows_sha256': blocks.get('tube_sandpile_flip_coset_classifier', {}).get('derived', {}).get('coset_rows_sha256'),
            },
        },

        {
            'id': 'tube_sandpile_flip_profile_compression',
            'name': 'D20 flip-coset profile compression',
            'status': 'certified profile compression',
            'statement': 'The full public automorphism group does not nontrivially compress the 64 flip-coset quotient: only the identity preserves the flip-generator set and five-cover span. Sandpile-order observables compress the 64 cosets into 48 combined-order classes.',
            'evidence': {
                'automorphism_compression': blocks.get('tube_sandpile_flip_profile_compression', {}).get('derived', {}).get('automorphism_compression'),
                'pair_order_profile': {
                    key: value
                    for key, value in blocks.get('tube_sandpile_flip_profile_compression', {})
                    .get('derived', {})
                    .get('pair_order_profile', {})
                    .items()
                    if key != 'class_rows'
                },
                'fiber_order_profile': {
                    key: value
                    for key, value in blocks.get('tube_sandpile_flip_profile_compression', {})
                    .get('derived', {})
                    .get('fiber_order_profile', {})
                    .items()
                    if key != 'class_rows'
                },
                'combined_order_profile': {
                    key: value
                    for key, value in blocks.get('tube_sandpile_flip_profile_compression', {})
                    .get('derived', {})
                    .get('combined_order_profile', {})
                    .items()
                    if key != 'class_rows'
                },
                'measured_profile': {
                    key: value
                    for key, value in blocks.get('tube_sandpile_flip_profile_compression', {})
                    .get('derived', {})
                    .get('measured_profile', {})
                    .items()
                    if key != 'class_rows'
                },
            },
        },

        {
            'id': 'tube_sandpile_flip_sector_refinement',
            'name': 'D20 flip-coset screen refinement',
            'status': 'certified singleton screen refinement',
            'statement': 'The three signed-turn residue screens refine the 48 combined-order flip-coset profile classes to all 64 cosets. The 12 non-singleton combined-order classes split into singleton classes using only the screen1/screen2 transition profile on grade-flip pairs.',
            'evidence': {
                'screen_summary': blocks.get('tube_sandpile_flip_sector_refinement', {}).get('derived', {}).get('screen_summary'),
                'combined_order_profile': {
                    key: value
                    for key, value in blocks.get('tube_sandpile_flip_sector_refinement', {})
                    .get('derived', {})
                    .get('combined_order_profile', {})
                    .items()
                    if key != 'non_singleton_rows'
                },
                'screen12_pair_transition_profile': {
                    key: value
                    for key, value in blocks.get('tube_sandpile_flip_sector_refinement', {})
                    .get('derived', {})
                    .get('screen12_pair_transition_profile', {})
                    .items()
                    if key != 'class_rows'
                },
                'combined_order_split_rows_sha256': blocks.get('tube_sandpile_flip_sector_refinement', {}).get('derived', {}).get('combined_order_split_rows_sha256'),
                'coset_screen_refinement_rows_sha256': blocks.get('tube_sandpile_flip_sector_refinement', {}).get('derived', {}).get('coset_screen_refinement_rows_sha256'),
            },
        },

        {
            'id': 'tube_sandpile_flip_sector_support_pullback',
            'name': 'D20 flip-coset sector-support pullback',
            'status': 'certified support pullback with explicit obstruction',
            'statement': 'The screen1/screen2 residue split pulls back to explicit 39-sector support cells for states 00, 01, and 10. State 11 has no local primitive sector support, but the support-admissible transition profile still splits all 64 cosets.',
            'evidence': {
                'supported_screen12_states': blocks.get('tube_sandpile_flip_sector_support_pullback', {}).get('derived', {}).get('supported_screen12_states'),
                'missing_screen12_states': blocks.get('tube_sandpile_flip_sector_support_pullback', {}).get('derived', {}).get('missing_screen12_states'),
                'transition_obstruction_summary': blocks.get('tube_sandpile_flip_sector_support_pullback', {}).get('derived', {}).get('transition_obstruction_summary'),
                'support_pullback_profile': {
                    key: value
                    for key, value in blocks.get('tube_sandpile_flip_sector_support_pullback', {})
                    .get('derived', {})
                    .get('support_pullback_profile', {})
                    .items()
                    if key != 'class_rows'
                },
                'state_cell_rows_sha256': blocks.get('tube_sandpile_flip_sector_support_pullback', {}).get('derived', {}).get('state_cell_rows_sha256'),
                'coset_support_pullback_rows_sha256': blocks.get('tube_sandpile_flip_sector_support_pullback', {}).get('derived', {}).get('coset_support_pullback_rows_sha256'),
            },
        },

        {
            'id': 'tube_sandpile_flip_unsupported_state_classification',
            'name': 'D20 flip-coset unsupported-state classification',
            'status': 'certified object-phase boundary',
            'statement': 'The unsupported screen12=11 state is residue-visible but outside the current A985/tube six-object phase image. The residue cube has 512 masks in that state and grade-flip data uses it, but no signed object label or local primitive sector piece realizes it.',
            'evidence': {
                'classification': blocks.get('tube_sandpile_flip_unsupported_state_classification', {}).get('derived', {}).get('classification'),
                'object_state_counts': blocks.get('tube_sandpile_flip_unsupported_state_classification', {}).get('derived', {}).get('object_state_counts'),
                'object_labels_by_state': blocks.get('tube_sandpile_flip_unsupported_state_classification', {}).get('derived', {}).get('object_labels_by_state'),
                'residue_screen12_counts': blocks.get('tube_sandpile_flip_unsupported_state_classification', {}).get('derived', {}).get('residue_screen12_counts'),
                'transition_obstruction_summary': blocks.get('tube_sandpile_flip_unsupported_state_classification', {}).get('derived', {}).get('transition_obstruction_summary'),
                'sector_support_state_rows_sha256': blocks.get('tube_sandpile_flip_unsupported_state_classification', {}).get('derived', {}).get('sector_support_state_rows_sha256'),
            },
        },

        {
            'id': 'tube_sandpile_flip_formal_11_extension_test',
            'name': 'D20 flip-coset formal 11 extension test',
            'status': 'certified obstruction',
            'statement': 'A nonempty formal support-level realization of screen12=11 is obstructed by the current finite A985/tube support constraints. The empty cell is compatible but explains no residue transitions; every nonempty option breaks an existing finite boundary.',
            'evidence': {
                'object_full_signature_counts': blocks.get('tube_sandpile_flip_formal_11_extension_test', {}).get('derived', {}).get('object_full_signature_counts'),
                'residue_state11_screen0_lifts': blocks.get('tube_sandpile_flip_formal_11_extension_test', {}).get('derived', {}).get('residue_state11_screen0_lifts'),
                'state11_transition_obstruction': blocks.get('tube_sandpile_flip_formal_11_extension_test', {}).get('derived', {}).get('state11_transition_obstruction'),
                'constraint_preserving_scenarios': blocks.get('tube_sandpile_flip_formal_11_extension_test', {}).get('derived', {}).get('constraint_preserving_scenarios'),
                'valid_nonempty_extension_scenarios': blocks.get('tube_sandpile_flip_formal_11_extension_test', {}).get('derived', {}).get('valid_nonempty_extension_scenarios'),
                'formal_extension_scenarios_sha256': blocks.get('tube_sandpile_flip_formal_11_extension_test', {}).get('derived', {}).get('formal_extension_scenarios_sha256'),
            },
        },

        {
            'id': 'd20_matrix_lift_conjecture',
            'name': 'D20 Matrix Lift Conjecture',
            'status': 'registered finite-shadow conjecture',
            'statement': 'D20 exhibits a finite Matrix-theoretic charge-wall shadow: a finite matrix/algebraic bulk, a Lambda^3 H6 public boundary, a half-integral zero-pair propagator residue that descends to a denominator-cleared sector-26 charge ledger, and primitive public-zero wall sector 33. The certificate registers the conjecture and explicitly does not prove M-theory or a DLCQ matrix model.',
            'evidence': {
                'classification': blocks.get('d20_matrix_lift_conjecture', {}).get('derived', {}).get('classification'),
                'half_integral_descent': blocks.get('d20_matrix_lift_conjecture', {}).get('derived', {}).get('half_integral_descent'),
                'wall_sector': blocks.get('d20_matrix_lift_conjecture', {}).get('derived', {}).get('wall_sector'),
                'missing_bridge_count': blocks.get('d20_matrix_lift_conjecture', {}).get('derived', {}).get('missing_bridge_count'),
                'matrix_lift_conjecture': blocks.get('d20_matrix_lift_conjecture', {}).get('derived', {}).get('matrix_lift_conjecture'),
            },
        },

        {
            'id': 'd20_minimal_matrix_charge_lift',
            'name': 'D20 minimal matrix charge-lift',
            'status': 'certified local charge-kernel lift',
            'statement': 'The denominator-cleared zero-pair propagator charge kernel has an explicit Mat_2(Q) lift on packet basis [239,238]. The swap projectors (I+S)/2 and (I-S)/2 reproduce the half-integral residue directions, and their cleared packet vectors recover the certified sector-26 plus/minus ledger images. This remains a local charge-kernel lift, not a full A985-to-DLCQ matrix model.',
            'evidence': {
                'minimal_matrix_charge_lift': blocks.get('d20_minimal_matrix_charge_lift', {}).get('derived', {}).get('minimal_matrix_charge_lift'),
                'mode_direction_checks': blocks.get('d20_minimal_matrix_charge_lift', {}).get('derived', {}).get('mode_direction_checks'),
                'remaining_promotion_bridge': blocks.get('d20_minimal_matrix_charge_lift', {}).get('derived', {}).get('remaining_promotion_bridge'),
            },
        },

        {
            'id': 'd20_full_packet_matrix_lift',
            'name': 'D20 full-packet matrix lift',
            'status': 'certified full-exposure propagation lift',
            'statement': 'The local Mat_2(Q) charge-kernel lift extends to the full 20-packet full-exposure propagation operator as Mat_2(Q)^10. Each active-partner doublet has transition block 2I+4S with the same plus/minus projectors, and the zero-pair block embeds the [239,238] minimal lift. This realizes the certified propagation operator but not a faithful full A985 action.',
            'evidence': {
                'acting_summary': blocks.get('d20_full_packet_matrix_lift', {}).get('derived', {}).get('acting_summary'),
                'a985_action_probe': blocks.get('d20_full_packet_matrix_lift', {}).get('derived', {}).get('a985_action_probe'),
                'component_lift_rows_sha256': blocks.get('d20_full_packet_matrix_lift', {}).get('derived', {}).get('component_lift_rows_sha256'),
            },
        },

        {
            'id': 'd20_packet_quotient_action_probe',
            'name': 'D20 packet quotient-action probe',
            'status': 'certified packet-level scattering action',
            'statement': 'The quotient-action probe finds certified packet-level scattering actions that preserve the 20 full-exposure packets and land in Mat_2(Q)^10: [5,10]+[10,5] acts as 2I, the remaining ordered crossing pairs act as 4S, and their sum is the 2I+4S block. It does not certify an A985, tube, or terminal-quotient packet operator map.',
            'evidence': {
                'operator_probe_summary': blocks.get('d20_packet_quotient_action_probe', {}).get('derived', {}).get('operator_probe_summary'),
                'certified_packet_actions': blocks.get('d20_packet_quotient_action_probe', {}).get('derived', {}).get('certified_packet_actions'),
                'negative_boundary': blocks.get('d20_packet_quotient_action_probe', {}).get('derived', {}).get('negative_boundary'),
            },
        },

        {
            'id': 'd20_explicit_packet_restriction_map_test',
            'name': 'D20 explicit packet restriction map test',
            'status': 'certified scattering restriction with missing raw bridges',
            'statement': 'The reduced scattering automaton has an explicit restriction to the 20 full-exposure packets by projecting 40 kernel mode masks to packet ids. One crossing step leaves the kernel packet space, while two ordered crossing steps recover the certified 2I+4S block in Mat_2(Q)^10. The current A985 relation basis, screen-0 tube element, and q42/q12 quotient tensors still have no certified projection to packet modes.',
            'evidence': {
                'domain_inventory': blocks.get('d20_explicit_packet_restriction_map_test', {}).get('derived', {}).get('domain_inventory'),
                'restriction_summary': blocks.get('d20_explicit_packet_restriction_map_test', {}).get('derived', {}).get('restriction_summary'),
                'automaton_block_rows_sha256': blocks.get('d20_explicit_packet_restriction_map_test', {}).get('derived', {}).get('automaton_block_rows_sha256'),
                'missing_bridge_inventory': blocks.get('d20_explicit_packet_restriction_map_test', {}).get('derived', {}).get('missing_bridge_inventory'),
            },
        },

        {
            'id': 'd20_packet_bridge_snf_obstruction',
            'name': 'D20 packet bridge SNF obstruction',
            'status': 'certified packet Smith obstruction',
            'statement': 'The certified 20-packet operator has exact Smith factors 2^10 and 6^10, so its cokernel is Z/2^10 x Z/6^10. On each packet doublet, an integer target pair (u,v) lies in the packet image only if u-v is 0 mod 2 and u+v is 0 mod 6. This gives the integral obstruction template for future A985, tube, and q42/q12 packet bridges, but does not construct those raw bridges.',
            'evidence': {
                'obstruction_summary': blocks.get('d20_packet_bridge_snf_obstruction', {}).get('derived', {}).get('obstruction_summary'),
                'smith_normal_form': blocks.get('d20_packet_bridge_snf_obstruction', {}).get('derived', {}).get('smith_normal_form'),
                'packet_image_congruence_rows_sha256': blocks.get('d20_packet_bridge_snf_obstruction', {}).get('derived', {}).get('packet_image_congruence_rows_sha256'),
                'raw_bridge_snf_tasks': blocks.get('d20_packet_bridge_snf_obstruction', {}).get('derived', {}).get('raw_bridge_snf_tasks'),
            },
        },

        {
            'id': 'd20_finite_contour_integration',
            'name': 'D20 finite contour integration',
            'status': 'certified finite contour calculus',
            'statement': 'The D20 H-cycle table is a finite contour-action table: the 11 primitive cycles form a full F2 cycle basis, have zero boundary defects, and their positive contour integrals reproduce the stored optical actions. The signed contour residues are not exact; after division by 3072 they form the primitive residue vector (-106,-94,12,20,-40,-159,-174,-180,-40,-67,-81), whose mod-26 reduction is (24,10,12,20,12,23,8,2,12,11,23).',
            'evidence': {
                'contour_summary': blocks.get('d20_finite_contour_integration', {}).get('derived', {}).get('contour_summary'),
                'positive_contour_action': blocks.get('d20_finite_contour_integration', {}).get('derived', {}).get('positive_contour_action'),
                'signed_contour_residue': blocks.get('d20_finite_contour_integration', {}).get('derived', {}).get('signed_contour_residue'),
                'exactness_obstruction': blocks.get('d20_finite_contour_integration', {}).get('derived', {}).get('exactness_obstruction'),
            },
        },

        {
            'id': 'd20_contour_sector_packet_prime_alignment',
            'name': 'D20 contour-sector-packet prime alignment',
            'status': 'certified prime-support alignment',
            'statement': 'The contour, packet-SNF, and sector-26 charge certificates exhibit a stratified 2/3/13 split. Prime 2 is common to all three layers. Prime 3 occurs in raw contour/action quantization and packet SNF torsion. Prime 13 appears only after sector-26 ledger reduction. This is prime-support alignment, not an isomorphism of the three structures.',
            'evidence': {
                'alignment_summary': blocks.get('d20_contour_sector_packet_prime_alignment', {}).get('derived', {}).get('alignment_summary'),
                'factorizations': blocks.get('d20_contour_sector_packet_prime_alignment', {}).get('derived', {}).get('factorizations'),
                'sector26_charge_summary': blocks.get('d20_contour_sector_packet_prime_alignment', {}).get('derived', {}).get('sector26_charge_summary'),
                'comparison_rows_sha256': blocks.get('d20_contour_sector_packet_prime_alignment', {}).get('derived', {}).get('comparison_rows_sha256'),
            },
        },

        {
            'id': 'd20_contour_charge_pairing_snf',
            'name': 'D20 contour-charge pairing Smith form',
            'status': 'certified finite quotient Smith form',
            'statement': 'The 11-entry primitive contour residue line pairs with the sector-26 plus/minus charge doublet to generate one order-13 anti-diagonal line in (Z/26)^2. The finite quotient has Smith factors [2,26], hence order 52. The 13 strict weak orderings of three labelled elements are recorded as a compatible comparison only, not as a certified source theorem.',
            'evidence': {
                'pairing_summary': blocks.get('d20_contour_charge_pairing_snf', {}).get('derived', {}).get('pairing_summary'),
                'raw_pairing_smith_forms': blocks.get('d20_contour_charge_pairing_snf', {}).get('derived', {}).get('raw_pairing_smith_forms'),
                'finite_quotient_smith_forms': blocks.get('d20_contour_charge_pairing_snf', {}).get('derived', {}).get('finite_quotient_smith_forms'),
                'weak_order_summary': blocks.get('d20_contour_charge_pairing_snf', {}).get('derived', {}).get('weak_order_summary'),
            },
        },

        {
            'id': 'd20_oriented_matroid_contour',
            'name': 'D20 oriented-matroid contour spine',
            'status': 'certified graphic oriented matroid witness',
            'statement': 'The D20 public contour incidence matrix defines a graphic oriented matroid with 1168 signed circuits and 12878 signed cocircuits. The gamma8 active height row extends to an acyclic tope and has trivial signed stabilizer, while the pure contour matroid does not by itself certify sector 33 as a cocircuit/hyperplane or produce the hidden C2 relaxation.',
            'evidence': {
                'contour_oriented_matroid_summary': blocks.get('d20_oriented_matroid_contour', {}).get('derived', {}).get('contour_oriented_matroid_summary'),
                'gamma8_tests': blocks.get('d20_oriented_matroid_contour', {}).get('derived', {}).get('gamma8_tests'),
                'pure_contour_symmetry_tests': blocks.get('d20_oriented_matroid_contour', {}).get('derived', {}).get('pure_contour_symmetry_tests'),
                'blocked_or_deferred': blocks.get('d20_oriented_matroid_contour', {}).get('derived', {}).get('blocked_or_deferred'),
            },
        },

        {
            'id': 'd20_oriented_matroid_sector33_extension',
            'name': 'D20 sector-33 oriented-matroid extension',
            'status': 'certified positive-circuit extension test',
            'statement': 'The natural sector-33 one-element extensions of the D20 contour matroid do not make sector 33 a cocircuit or hyperplane. The height-derived sector-33 attachment instead makes gamma8+e33 a positive circuit obstruction: the five active gamma8 edges plus two copies of the sector-33 unit close the certified -374784 residual.',
            'evidence': {
                'signed_residue_extension': blocks.get('d20_oriented_matroid_sector33_extension', {}).get('derived', {}).get('signed_residue_extension'),
                'hidden_sector_scalar_extension': blocks.get('d20_oriented_matroid_sector33_extension', {}).get('derived', {}).get('hidden_sector_scalar_extension'),
                'sector33_height_attachment': blocks.get('d20_oriented_matroid_sector33_extension', {}).get('derived', {}).get('sector33_height_attachment'),
                'sector33_cocircuit_summary': blocks.get('d20_oriented_matroid_sector33_extension', {}).get('derived', {}).get('sector33_cocircuit_summary'),
            },
        },

        {
            'id': 'd20_oriented_matroid_sector33_dual',
            'name': 'D20 sector-33 dual oriented-matroid witness',
            'status': 'certified positive dual cocircuit',
            'statement': 'An explicit integer nullspace basis for the sector-33 height attachment represents the dual oriented matroid. In that dual, gamma8+e33 is a positive cocircuit: its complement is a rank-10 hyperplane and adding any one of the six cocircuit elements restores dual rank 11.',
            'evidence': {
                'dual_summary': blocks.get('d20_oriented_matroid_sector33_dual', {}).get('derived', {}).get('dual_summary'),
                'dual_positive_cocircuit': blocks.get('d20_oriented_matroid_sector33_dual', {}).get('derived', {}).get('dual_positive_cocircuit'),
                'element_tests': blocks.get('d20_oriented_matroid_sector33_dual', {}).get('derived', {}).get('element_tests'),
            },
        },

        {
            'id': 'd20_oriented_matroid_tutte_os',
            'name': 'D20 sector-33 Tutte/Orlik-Solomon package',
            'status': 'certified finite-field Tutte/OS witness',
            'statement': 'Over F_1000003, the 31-element sector-33 height attachment has rank 20, a 93-term Tutte polynomial, 18,356,358 bases, and a nonnegative NBC/Orlik-Solomon Hilbert vector beginning [1,31]. This is explicitly a finite-field witness pending a rational prime-good audit.',
            'evidence': {
                'field_matroid': blocks.get('d20_oriented_matroid_tutte_os', {}).get('derived', {}).get('field_matroid'),
                'deletion_contraction_cache': blocks.get('d20_oriented_matroid_tutte_os', {}).get('derived', {}).get('deletion_contraction_cache'),
                'tutte_polynomial': blocks.get('d20_oriented_matroid_tutte_os', {}).get('derived', {}).get('tutte_polynomial'),
                'characteristic_polynomial': blocks.get('d20_oriented_matroid_tutte_os', {}).get('derived', {}).get('characteristic_polynomial'),
                'orlik_solomon_algebra': blocks.get('d20_oriented_matroid_tutte_os', {}).get('derived', {}).get('orlik_solomon_algebra'),
            },
        },

        {
            'id': 'd20_oriented_matroid_prime_lift_audit',
            'name': 'D20 oriented-matroid prime-lift audit',
            'status': 'certified multi-prime stability audit',
            'statement': 'The sector-33 Tutte/OS package is stable over five audited primes 1000003, 1000033, 1000037, 1000039, and 1000081: all give rank 20, 93 Tutte terms, the same polynomial hash, and 18,356,358 bases. The integer matrix has exact rational rank 20 and gamma8+e33 is an exact primitive rational circuit; full rational matroid promotion remains explicitly unclaimed.',
            'evidence': {
                'baseline': blocks.get('d20_oriented_matroid_prime_lift_audit', {}).get('derived', {}).get('baseline'),
                'prime_field_records': blocks.get('d20_oriented_matroid_prime_lift_audit', {}).get('derived', {}).get('prime_field_records'),
                'prime_stability_summary': blocks.get('d20_oriented_matroid_prime_lift_audit', {}).get('derived', {}).get('prime_stability_summary'),
                'exact_rational_audit': blocks.get('d20_oriented_matroid_prime_lift_audit', {}).get('derived', {}).get('exact_rational_audit'),
                'promotion_boundary': blocks.get('d20_oriented_matroid_prime_lift_audit', {}).get('derived', {}).get('promotion_boundary'),
            },
        },

        {
            'id': 'd20_oriented_matroid_rational_tutte_promotion',
            'name': 'D20 rational Tutte/Orlik-Solomon promotion',
            'status': 'certified exact rational Tutte/OS replay',
            'statement': 'The sector-33 height-attachment matrix has an exact rational deletion-contraction replay with rank 20, 307218 cached states, 93 Tutte terms, and the same Tutte hash as the audited finite-field package. The Tutte polynomial, characteristic polynomial, and NBC/Orlik-Solomon Hilbert vector are therefore promoted to the rational matroid represented by the integer sector-33 matrix.',
            'evidence': {
                'rational_matrix': blocks.get('d20_oriented_matroid_rational_tutte_promotion', {}).get('derived', {}).get('rational_matrix'),
                'exact_deletion_contraction_replay': blocks.get('d20_oriented_matroid_rational_tutte_promotion', {}).get('derived', {}).get('exact_deletion_contraction_replay'),
                'rational_tutte_polynomial': blocks.get('d20_oriented_matroid_rational_tutte_promotion', {}).get('derived', {}).get('rational_tutte_polynomial'),
                'rational_characteristic_polynomial': blocks.get('d20_oriented_matroid_rational_tutte_promotion', {}).get('derived', {}).get('rational_characteristic_polynomial'),
                'rational_orlik_solomon_algebra': blocks.get('d20_oriented_matroid_rational_tutte_promotion', {}).get('derived', {}).get('rational_orlik_solomon_algebra'),
                'promotion_boundary': blocks.get('d20_oriented_matroid_rational_tutte_promotion', {}).get('derived', {}).get('promotion_boundary'),
            },
        },

        {
            'id': 'd20_oriented_matroid_rational_signed_circuits',
            'name': 'D20 rational signed-circuit system',
            'status': 'certified rational signed circuits',
            'statement': 'The sector-33 rational lift matroid has 24,946 circuit supports and 49,892 signed circuits up to global sign. The full signed-circuit list is generated from balanced simple cycles and height-zero pairs of unbalanced cycles; gamma8+e33 appears with primitive coefficients [1,1,1,1,1,2]. The distinguished positive dual cocircuit is retained, while full signed-cocircuit enumeration remains open.',
            'evidence': {
                'rational_matrix': blocks.get('d20_oriented_matroid_rational_signed_circuits', {}).get('derived', {}).get('rational_matrix'),
                'generation_summary': blocks.get('d20_oriented_matroid_rational_signed_circuits', {}).get('derived', {}).get('generation_summary'),
                'positive_gamma8_e33_circuit': blocks.get('d20_oriented_matroid_rational_signed_circuits', {}).get('derived', {}).get('positive_gamma8_e33_circuit'),
                'distinguished_dual_cocircuit': blocks.get('d20_oriented_matroid_rational_signed_circuits', {}).get('derived', {}).get('distinguished_dual_cocircuit'),
                'circuit_rows_sha256': blocks.get('d20_oriented_matroid_rational_signed_circuits', {}).get('derived', {}).get('circuit_rows_sha256'),
                'promotion_boundary': blocks.get('d20_oriented_matroid_rational_signed_circuits', {}).get('derived', {}).get('promotion_boundary'),
            },
        },

        {
            'id': 'd20_strict_weak_order_sector26_clock',
            'name': 'D20 strict weak order sector-26 clock',
            'status': 'certified 13-ordering clock map',
            'statement': 'The 13 strict weak orderings on {a,b,c} map by k -> 2k mod 26 onto the order-13 anti-diagonal line certified by the contour-charge pairing. Polarity doubling covers all 26 sector residues. The full augmented D20 ledger preserves this clock only trivially because its stabilizer is identity; the hidden C2 quotient requires forgetting sector-26 clock refinements.',
            'evidence': {
                'weak_order_summary': blocks.get('d20_strict_weak_order_sector26_clock', {}).get('derived', {}).get('weak_order_summary'),
                'd20_symmetry_test': blocks.get('d20_strict_weak_order_sector26_clock', {}).get('derived', {}).get('d20_symmetry_test'),
                'anti_diagonal_pairs_sha256': blocks.get('d20_strict_weak_order_sector26_clock', {}).get('derived', {}).get('anti_diagonal_pairs_sha256'),
                'relabel_records_sha256': blocks.get('d20_strict_weak_order_sector26_clock', {}).get('derived', {}).get('relabel_records_sha256'),
            },
        },

        {
            'id': 'd20_intrinsic_triple_ordering_clock',
            'name': 'D20 intrinsic triple ordering clock',
            'status': 'certified intrinsic 13-ordering clock',
            'statement': 'The sector-26 hidden transport form supplies the intrinsic, permutation-rigid triple (R33, K_mixed_S, K_pure_Sminus). Its strict weak orderings reproduce the same order-13 anti-diagonal line and 26-state polarity-doubled clock as the placeholder weak-order theorem. The composite block has discriminant 13, and only the identity preserves the full 3x3 transport matrix.',
            'evidence': {
                'intrinsic_triple_summary': blocks.get('d20_intrinsic_triple_ordering_clock', {}).get('derived', {}).get('intrinsic_triple_summary'),
                'clock_summary': blocks.get('d20_intrinsic_triple_ordering_clock', {}).get('derived', {}).get('clock_summary'),
                'transport_permutation_records_sha256': blocks.get('d20_intrinsic_triple_ordering_clock', {}).get('derived', {}).get('transport_permutation_records_sha256'),
                'intrinsic_order_records_sha256': blocks.get('d20_intrinsic_triple_ordering_clock', {}).get('derived', {}).get('intrinsic_order_records_sha256'),
            },
        },

        {
            'id': 'd20_triple_13_signature_uniqueness',
            'name': 'D20 triple 13-signature uniqueness',
            'status': 'certified corpus uniqueness',
            'statement': 'Across the certified D20 theorem-report corpus, every explicit 3-object matrix triple with a discriminant-13 or order-13 clock signature has the same signature: basis (R33, K_mixed_S, K_pure_Sminus) and matrix [[4,0,0],[0,5,1],[0,1,2]]. This proves uniqueness in the current explicit theorem-report corpus, not in every conceivable raw D20 subform.',
            'evidence': {
                'summary': blocks.get('d20_triple_13_signature_uniqueness', {}).get('derived', {}).get('summary'),
                'unique_certified_triple_signatures': blocks.get('d20_triple_13_signature_uniqueness', {}).get('derived', {}).get('unique_certified_triple_signatures'),
                'certified_discriminant13_records_sha256': blocks.get('d20_triple_13_signature_uniqueness', {}).get('derived', {}).get('certified_discriminant13_records_sha256'),
                'certified_order13_records_sha256': blocks.get('d20_triple_13_signature_uniqueness', {}).get('derived', {}).get('certified_order13_records_sha256'),
            },
        },

        {
            'id': 'd20_raw_transport_3x3_discriminant13_search',
            'name': 'D20 raw/transport 3x3 discriminant-13 search',
            'status': 'certified bounded JSON survey',
            'statement': 'A bounded survey of d20.json, every layer JSON file, and transport/sector/anomaly theorem reports checked 42,185 principal 3x3 subforms. Raw d20/layer JSON has zero discriminant-13 hits; the only transport-sector hits are the known hidden transport matrix in sector26_invariant_suite and finite_anomaly_counter. No determinant-13 principal 3x3 subform appears.',
            'evidence': {
                'summary': blocks.get('d20_raw_transport_3x3_discriminant13_search', {}).get('derived', {}).get('summary'),
                'known_hidden_transport_hits_sha256': blocks.get('d20_raw_transport_3x3_discriminant13_search', {}).get('derived', {}).get('known_hidden_transport_hits_sha256'),
                'unreported_discriminant13_hits_sha256': blocks.get('d20_raw_transport_3x3_discriminant13_search', {}).get('derived', {}).get('unreported_discriminant13_hits_sha256'),
                'determinant13_hits_sha256': blocks.get('d20_raw_transport_3x3_discriminant13_search', {}).get('derived', {}).get('determinant13_hits_sha256'),
            },
        },

        {
            'id': 'raw543_repo_c2_kernel_action',
            'name': 'Raw543 actual D20 C2-kernel action',
            'status': 'certified actual hidden-split orbit theorem',
            'statement': 'The nonidentity C2 preserver recorded in the public D20 hidden-split theorem acts on F2^11 by basis-image masks [16,2,512,1034,1,64,32,128,256,4,1024]. On the nonzero hidden-character kernel it has 543 orbits: 63 fixed nonzero vectors and 480 two-cycles.',
            'evidence': {
                'actual_nontrivial_c2_preserver': blocks.get('raw543_repo_c2_kernel_action', {}).get('derived', {}).get('actual_nontrivial_c2_preserver'),
                'nilpotent_part': blocks.get('raw543_repo_c2_kernel_action', {}).get('derived', {}).get('nilpotent_part'),
                'raw543_kernel': blocks.get('raw543_repo_c2_kernel_action', {}).get('derived', {}).get('raw543_kernel'),
                'identities': blocks.get('raw543_repo_c2_kernel_action', {}).get('derived', {}).get('identities'),
            },
        },

        {
            'id': 'zero_axiom_coorient_cache',
            'name': 'D20 zero-axiom coorient cache boundary',
            'status': 'certified cache boundary',
            'statement': 'The zero-axiom coorient cache has a valid self hash and current source-file hashes. It records the canonical base [18,67,37], separation of all 2576 points, nine derived marker integers, and closure order 9216.',
            'evidence': {
                'cache_path': blocks.get('zero_axiom_coorient_cache', {}).get('definition', {}).get('cache_path'),
                'cache_certificate_sha256': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('cache_certificate_sha256'),
                'canonical_base': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('canonical_base'),
                'final_signature_count': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('final_signature_count'),
                'marker_integer_count': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('marker_integer_count'),
                'selected_generator_indices': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('selected_generator_indices'),
                'selected_generator_orders': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('selected_generator_orders'),
                'closed_action': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('closed_action'),
                'word_presentation': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('word_presentation'),
                'source_file_rows_sha256': blocks.get('zero_axiom_coorient_cache', {}).get('derived', {}).get('source_file_rows_sha256'),
            },
        },

        {
            'id': 'zero_axiom_coorient_strict_replay',
            'name': 'D20 zero-axiom coorient strict replay',
            'status': 'certified strict replay witness',
            'statement': 'A fresh strict replay of the zero-axiom coorient reduction reproduces the stored cache byte-for-byte under the cache file newline convention, including the same certificate hash, base [18,67,37], 2576 separated points, and closure order 9216.',
            'evidence': {
                'cache_certificate_sha256': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('cache_certificate_sha256'),
                'fresh_certificate_sha256': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('fresh_certificate_sha256'),
                'cache_file_sha256': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('cache_file_sha256'),
                'fresh_pretty_sha256': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('fresh_pretty_sha256'),
                'cache_newline': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('cache_newline'),
                'cache_byte_length': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('cache_byte_length'),
                'fresh_pretty_byte_length': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('fresh_pretty_byte_length'),
                'canonical_base': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('canonical_base'),
                'final_signature_count': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('final_signature_count'),
                'marker_integer_count': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('marker_integer_count'),
                'closed_action_order': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('closed_action_order'),
                'word_presentation_closure_order': blocks.get('zero_axiom_coorient_strict_replay', {}).get('derived', {}).get('word_presentation_closure_order'),
            },
        },

        {
            'id': 'leech_boundary',
            'name': 'Leech boundary reconstruction',
            'status': 'recorded boundary certificate',
            'statement': 'The bundle records the Leech-boundary reconstruction certificate as a boundary layer; it is not required to reconstruct A985 itself.',
            'evidence': {'derived_file': 'data/derived/leech_reconstruction.json'},
        },
        {
            'id': 'hexagon_boundary',
            'name': 'raw braiding obstruction / center boundary',
            'status': 'recorded boundary certificate',
            'statement': 'The raw typed incidence category is not globally braided; a Drinfeld-center or tube-completion construction is the next categorical object.',
            'evidence': {'derived_file': 'data/derived/hexagon_boundary.json'},
        },
    ]


def assemble_certificate(
    constants: Dict[str, Any],
    manifest: Dict[str, Dict[str, Any]],
    blocks: Dict[str, Any],
    claims: list[Dict[str, Any]],
    hash_json: Callable[[Any], str],
) -> Dict[str, Any]:
    cert = {
        'schema': 'gnatural.core_directory_certificate_tube_projection_section',
        'status': 'PASS',
        'object': object_summary(constants, blocks),
        'policy': {'core_only': True},
        'data_catalog': data_catalog(manifest),
        'verified_claims': claims,
        'file_manifest': manifest,
        'blocks': blocks,
    }
    cert['certificate_sha256'] = hash_json(cert)
    return cert
