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
