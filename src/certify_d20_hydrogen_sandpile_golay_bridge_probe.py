from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from pathlib import Path
from typing import Any

try:
    from .certify_io import h_json
    from .derive_d20_hydrogen_sandpile_golay_bridge_probe import build_artifact
except ImportError:  # Supports direct script execution.
    from certify_io import h_json
    from derive_d20_hydrogen_sandpile_golay_bridge_probe import build_artifact


ARTIFACT_REL = "generated/d20_hydrogen_sandpile_golay_bridge_probe.json"
ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / ARTIFACT_REL


def validate_d20_hydrogen_sandpile_golay_bridge_probe() -> dict[str, Any]:
    artifact = build_artifact()
    expected_schema = "d20.generated.hydrogen_sandpile_golay_bridge_probe@1"
    expected_status = "D20_HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE_PROVISIONAL_ASSIGNMENT_DEGENERATE"
    if artifact.get("schema") != expected_schema:
        raise AssertionError("bridge probe schema mismatch")
    if artifact.get("status") != expected_status:
        raise AssertionError("bridge probe status mismatch")
    expected_hash = h_json({k: v for k, v in artifact.items() if k != "artifact_sha256"})
    if artifact.get("artifact_sha256") != expected_hash:
        raise AssertionError("bridge probe self hash mismatch")
    if not ARTIFACT_PATH.exists():
        raise AssertionError("bridge probe artifact file missing")
    written_artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    if written_artifact.get("schema") != expected_schema:
        raise AssertionError("bridge probe written artifact schema mismatch")
    if written_artifact.get("status") != expected_status:
        raise AssertionError("bridge probe written artifact status mismatch")
    if written_artifact.get("all_checks_pass") is not True:
        raise AssertionError("bridge probe written artifact checks mismatch")
    if not written_artifact.get("artifact_sha256"):
        raise AssertionError("bridge probe written artifact self hash missing")
    checks = artifact.get("checks", {})
    if not isinstance(checks, dict) or not checks:
        raise AssertionError("bridge probe checks missing")
    if any(value is not True for value in checks.values()):
        raise AssertionError("bridge probe checks did not all pass")
    if artifact.get("all_checks_pass") is not True:
        raise AssertionError("bridge probe all_checks_pass mismatch")

    proof_inventory = artifact.get("proof_obligation_inventory", {})
    if proof_inventory.get("proof_obligation_report_count", 0) <= 0:
        raise AssertionError("bridge probe proof-obligation inventory is empty")
    if proof_inventory.get("outstanding_boundary_count", 0) <= 0:
        raise AssertionError("bridge probe lost outstanding proof boundaries")

    signatures = artifact.get("signatures", {})
    h_frame = signatures.get("hydrogen_golay_hamming_frame", {})
    if h_frame.get("h8_copies") != 3 or h_frame.get("h8_copy_weight") != 8:
        raise AssertionError("bridge probe H8 frame mismatch")
    if h_frame.get("golay_minimum_nonzero_weight") != 8:
        raise AssertionError("bridge probe Golay minimum weight mismatch")

    static_axis = signatures.get("static_axis", {})
    if static_axis.get("group_order") != 32 or static_axis.get("mod2_reduction_rank") != 3:
        raise AssertionError("bridge probe static axis mismatch")

    tropic_axis = signatures.get("tropic_axis", {})
    if tropic_axis.get("gamma8_mask") != 256 or tropic_axis.get("balance_sum") != 0:
        raise AssertionError("bridge probe tropic axis mismatch")

    optic_axis = signatures.get("optic_axis", {})
    if optic_axis.get("rank_over_f2") != 3:
        raise AssertionError("bridge probe optic rank mismatch")
    cell_counts = optic_axis.get("cell_counts_by_signature", {})
    if not isinstance(cell_counts, dict) or len(cell_counts) != 8 or set(cell_counts.values()) != {256}:
        raise AssertionError("bridge probe optic cell split mismatch")

    sandpile_target = signatures.get("sandpile_target", {})
    if sandpile_target.get("mixed_sandpile_class_count") != 154:
        raise AssertionError("bridge probe sandpile mixed-class mismatch")
    if sandpile_target.get("tube_grade_is_sandpile_class_invariant") is not False:
        raise AssertionError("bridge probe sandpile boundary mismatch")

    assignment_search = artifact.get("assignment_search", {})
    if assignment_search.get("permutation_count") != 6:
        raise AssertionError("bridge probe assignment count mismatch")
    if assignment_search.get("best_assignment_count") != 6:
        raise AssertionError("bridge probe assignment degeneracy mismatch")

    discriminator = artifact.get("discriminator_search", {})
    if not isinstance(discriminator, dict) or not discriminator:
        raise AssertionError("bridge probe discriminator search missing")
    h8_sector = discriminator.get("h8_sector_identification", {})
    if h8_sector.get("all_checks_pass") is not True:
        raise AssertionError("bridge probe H8 sector identification checks failed")
    if h8_sector.get("status") != "BVS_UNSIGNED_WEIGHT8_H8_SECTOR_PROXY_CERTIFIED_RGB_NAMING_OPEN":
        raise AssertionError("bridge probe H8 sector identification status mismatch")
    if set(h8_sector.get("unsigned_sector_coordinate_sizes", {}).values()) != {8}:
        raise AssertionError("bridge probe unsigned H8 sector weights mismatch")

    discriminator_result = discriminator.get("discriminator_result", {})
    if discriminator_result.get("bvs_unsigned_h8_sector_proxy_certified") is not True:
        raise AssertionError("bridge probe did not certify B/S/V unsigned H8 proxy")
    if discriminator_result.get("unique_screen_to_unsigned_h8_sector_assignment") is not True:
        raise AssertionError("bridge probe screen-to-sector assignment is not unique")
    if discriminator_result.get("screen_to_unsigned_h8_sector_assignment") != {
        "signed_turn_screen_0": "S",
        "signed_turn_screen_1": "V",
        "signed_turn_screen_2": "B",
    }:
        raise AssertionError("bridge probe screen-to-sector assignment mismatch")
    if discriminator_result.get("rgb_color_naming_remains_open") is not True:
        raise AssertionError("bridge probe overstated RGB color naming closure")
    if discriminator_result.get("screen0_distinguished") is not True:
        raise AssertionError("bridge probe discriminator did not distinguish screen0")
    if discriminator_result.get("screen1_screen2_still_tied_by_selector_choice") is not True:
        raise AssertionError("bridge probe selector-choice tie changed")
    if discriminator_result.get("turn_labels_break_all_three_if_BSV_is_allowed_as_H8_proxy") is not True:
        raise AssertionError("bridge probe B/S/V turn-label discriminator missing")
    if discriminator_result.get("full_certified_h8_assignment_remains_open") is not True:
        raise AssertionError("bridge probe overstated H8 assignment closure")

    hcycle_pullback = discriminator.get("hcycle_pullback", {})
    if hcycle_pullback.get("selector_choice_labels_separate_all_three") is not False:
        raise AssertionError("bridge probe selector-choice separator mismatch")
    if hcycle_pullback.get("turn_type_labels_separate_all_three") is not True:
        raise AssertionError("bridge probe turn-type separator mismatch")

    static_overlap = discriminator.get("static_public_zero_overlap", {})
    if static_overlap.get("profiles_identical_across_static_generators") is not True:
        raise AssertionError("bridge probe static overlap generator profile mismatch")
    if static_overlap.get("screen0_uniquely_scalar_on_public_zero_supports") is not True:
        raise AssertionError("bridge probe static overlap screen0 profile mismatch")

    static_tropic = artifact.get("static_tropic_sector_pullback", {})
    if not isinstance(static_tropic, dict) or not static_tropic:
        raise AssertionError("bridge probe static/tropic sector pullback missing")
    pullback_result = static_tropic.get("result", {})
    expected_true = {
        "static_frame_pulled_into_bvs",
        "static_individual_generator_to_single_sector_remains_open",
        "static_public_zero_overlap_lands_on_S_screen",
        "tropic_gamma8_visible_cycle_lands_on_V",
        "tropic_hidden_residual_lands_on_R33_not_public_BVS",
        "full_static_tropic_bvs_attachment_remains_open",
    }
    for key in expected_true:
        if pullback_result.get(key) is not True:
            raise AssertionError(f"bridge probe static/tropic pullback check mismatch: {key}")

    static = static_tropic.get("static", {})
    if static.get("public_zero_screen_sector") != "S":
        raise AssertionError("bridge probe static public-zero screen sector mismatch")
    if static.get("single_sector_generator_detected") is not False:
        raise AssertionError("bridge probe overstated static single-sector generator")
    if static.get("z2_target_S_dominant_residue", {}).get("rate_num_den") != [452, 454]:
        raise AssertionError("bridge probe z2 target-S near-detector changed")

    tropic = static_tropic.get("tropic", {})
    if tropic.get("gamma8_dominant_visible_sector") != "V":
        raise AssertionError("bridge probe gamma8 visible sector mismatch")
    if tropic.get("gamma8_screen_sector") != "V":
        raise AssertionError("bridge probe gamma8 screen sector mismatch")
    if tropic.get("hidden_residual_is_public_zero_r33") is not True:
        raise AssertionError("bridge probe gamma8 hidden residual mismatch")
    if tropic.get("unique_public_zero_active_objects") != ["B+", "S+"]:
        raise AssertionError("bridge probe R33 active objects mismatch")

    ward_audit = artifact.get("static_tropic_ward_composition_audit", {})
    if not isinstance(ward_audit, dict) or not ward_audit:
        raise AssertionError("bridge probe static/tropic Ward composition audit missing")
    if ward_audit.get("status") != "TROPIC_WARD_COMPOSITION_CERTIFIED_STATIC_Z2_ATTACHMENT_OPEN":
        raise AssertionError("bridge probe Ward composition status mismatch")
    ward_result = ward_audit.get("result", {})
    expected_ward_true = {
        "tropic_ward_composition_found",
        "selected_lift_closes_public_and_hidden_balance",
        "selected_lift_matches_V_screen_signature",
        "static_z2_target_S_remains_unattached_to_bounded_ward_reports",
        "direct_static_tropic_commutator_or_ward_term_remains_open",
    }
    for key in expected_ward_true:
        if ward_result.get(key) is not True:
            raise AssertionError(f"bridge probe Ward composition check mismatch: {key}")
    if ward_audit.get("all_checks_pass") is not True:
        raise AssertionError("bridge probe Ward composition checks did not pass")

    scattering_step = ward_audit.get("scattering_step", {})
    if scattering_step.get("source_mask") != 256 or scattering_step.get("target_mask") != 288:
        raise AssertionError("bridge probe Ward scattering source/target mismatch")
    if scattering_step.get("generator_cycle_id") != 5 or scattering_step.get("toggle") != "add":
        raise AssertionError("bridge probe Ward scattering generator mismatch")
    if scattering_step.get("packet_transfer") != "odd_to_kernel":
        raise AssertionError("bridge probe Ward scattering packet transfer mismatch")

    selector_summary = ward_audit.get("selector_summary", {})
    if selector_summary.get("selected_mask") != 288:
        raise AssertionError("bridge probe Ward selected mask mismatch")
    if selector_summary.get("selected_basis_cycle_ids") != [5, 8]:
        raise AssertionError("bridge probe Ward selected basis mismatch")
    if selector_summary.get("selected_height_action") != 1065984:
        raise AssertionError("bridge probe Ward selected height mismatch")
    if selector_summary.get("selected_corrected_clock_mod26") != 0:
        raise AssertionError("bridge probe Ward selected clock mismatch")

    selected_visible = ward_audit.get("visible_turn_profiles", {}).get("selected_288", {})
    if selected_visible.get("turn_type_counts") != {"B": 4, "S": 1, "V": 5}:
        raise AssertionError("bridge probe Ward selected visible turn counts mismatch")
    if ward_audit.get("selected_turn_signature_screen_sectors") != {"signed_turn_screen_1": "V"}:
        raise AssertionError("bridge probe Ward selected V-screen signature mismatch")
    token_hits = ward_audit.get("bounded_static_token_hits", {})
    if any(token_hits.values()):
        raise AssertionError("bridge probe unexpectedly attached static z2 in bounded Ward reports")

    z2_audit = artifact.get("selected_mask_z2_static_audit", {})
    if not isinstance(z2_audit, dict) or not z2_audit:
        raise AssertionError("bridge probe selected-mask z2 static audit missing")
    if z2_audit.get("status") != "MASK288_Z2_SCREEN_ENVELOPE_EVALUATED_EXACT_SUPPORT_OPEN":
        raise AssertionError("bridge probe selected-mask z2 status mismatch")
    if z2_audit.get("selected_mask") != 288:
        raise AssertionError("bridge probe selected-mask z2 mask mismatch")
    if z2_audit.get("selected_screen_sectors") != {"signed_turn_screen_1": "V"}:
        raise AssertionError("bridge probe selected-mask z2 screen mismatch")
    if z2_audit.get("quotient_generator") != "z2_a12_parity":
        raise AssertionError("bridge probe selected-mask z2 generator mismatch")
    if z2_audit.get("scalar_supports") != ["{33}", "{25,26}"]:
        raise AssertionError("bridge probe selected-mask z2 scalar supports mismatch")
    if z2_audit.get("non_scalar_supports") != ["{6,26}", "{6,26,33}", "{25,26,33}"]:
        raise AssertionError("bridge probe selected-mask z2 non-scalar supports mismatch")
    if z2_audit.get("hidden_sector33_hit") is not True:
        raise AssertionError("bridge probe selected-mask z2 sector33 hit mismatch")
    z2_result = z2_audit.get("result", {})
    expected_z2_true = {
        "z2_evaluated_on_selected_V_screen_envelope",
        "z2_hits_hidden_sector33_kernel",
        "z2_not_scalar_on_full_selected_screen_support_envelope",
        "mask288_exact_sector_support_remains_open",
        "z2_selected_mask_static_attachment_remains_open",
    }
    for key in expected_z2_true:
        if z2_result.get(key) is not True:
            raise AssertionError(f"bridge probe selected-mask z2 check mismatch: {key}")

    exact_h6 = artifact.get("selected_mask_exact_h6_support_audit", {})
    if not isinstance(exact_h6, dict) or not exact_h6:
        raise AssertionError("bridge probe selected-mask exact H6 support audit missing")
    if exact_h6.get("status") != "MASK288_EXACT_H6_SUPPORT_MATERIALIZED_Z2_RETEST_BLOCKED":
        raise AssertionError("bridge probe selected-mask exact H6 status mismatch")
    if exact_h6.get("selected_mask") != 288:
        raise AssertionError("bridge probe selected-mask exact H6 mask mismatch")
    if exact_h6.get("selected_cycle_ids") != [5, 8]:
        raise AssertionError("bridge probe selected-mask exact H6 cycle mismatch")
    if exact_h6.get("selected_step_atom_ids") != [0, 2, 3, 4, 9, 11, 13, 14, 23]:
        raise AssertionError("bridge probe selected-mask exact H6 step atoms mismatch")
    if exact_h6.get("selected_boundary_projection_support_values") != [14, 16, 33, 44, 86]:
        raise AssertionError("bridge probe selected-mask exact H6 support values mismatch")
    if exact_h6.get("selected_h6_public_atom_ids") != [0, 1, 4, 7, 10, 11, 13, 16]:
        raise AssertionError("bridge probe selected-mask exact H6 public atoms mismatch")
    exact_labels = [
        row.get("public_atom_label") for row in exact_h6.get("selected_h6_public_atom_rows", [])
    ]
    if exact_labels != [
        "{B-,B+,V-}",
        "{B-,B+,V+}",
        "{B-,V-,V+}",
        "{B-,V+,S-}",
        "{B+,V-,V+}",
        "{B+,V-,S-}",
        "{B+,V+,S-}",
        "{V-,V+,S-}",
    ]:
        raise AssertionError("bridge probe selected-mask exact H6 labels mismatch")
    if exact_h6.get("selected_h6_unsigned_sector_counts") != {"B": 9, "S": 4, "V": 11}:
        raise AssertionError("bridge probe selected-mask exact H6 unsigned counts mismatch")
    if exact_h6.get("z2_exact_retest_status") != "BLOCKED_MISSING_Q12_TO_H6_PUBLIC_ATOM_PROJECTION":
        raise AssertionError("bridge probe selected-mask z2 exact retest boundary mismatch")
    missing_projection = exact_h6.get("missing_q12_packet_projection", {})
    if missing_projection.get("candidate") != "q42_q12_tensor_to_full_packets":
        raise AssertionError("bridge probe selected-mask missing q12 bridge candidate mismatch")
    if missing_projection.get("status") != "blocked_missing_quotient_class_to_packet_projection":
        raise AssertionError("bridge probe selected-mask missing q12 bridge status mismatch")
    exact_result = exact_h6.get("result", {})
    expected_exact_true = {
        "boundary_loop_step_atom_incidence_certified",
        "selected_cycles_are_cycle5_and_gamma8",
        "selected_cycles_close_on_h6_boundary",
        "selected_h6_public_atom_support_materialized",
        "selected_h6_public_atom_support_is_weight8",
        "selected_step_atom_support_values_materialized",
        "q12_exact_z2_retest_blocked_by_missing_projection",
    }
    for key in expected_exact_true:
        if exact_result.get(key) is not True:
            raise AssertionError(f"bridge probe selected-mask exact H6 check mismatch: {key}")

    q12_h6 = artifact.get("q12_h6_projection_audit", {})
    if not isinstance(q12_h6, dict) or not q12_h6:
        raise AssertionError("bridge probe q12/H6 projection audit missing")
    if (
        q12_h6.get("status")
        != "Q12_H6_SELECTOR_CANDIDATE_MATERIALIZED_PACKET_NORMALIZATION_BLOCKED"
    ):
        raise AssertionError("bridge probe q12/H6 projection status mismatch")
    if q12_h6.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12/H6 selected mask mismatch")
    if q12_h6.get("selected_h6_public_atom_ids") != [0, 1, 4, 7, 10, 11, 13, 16]:
        raise AssertionError("bridge probe q12/H6 target support mismatch")
    q12_section = q12_h6.get("q12_section", {})
    if q12_section.get("class_count") != 12:
        raise AssertionError("bridge probe q12/H6 q12 class count mismatch")
    if q12_section.get("section_indices") != [
        0,
        227,
        613,
        1,
        228,
        614,
        45,
        77,
        215,
        263,
        531,
        573,
    ]:
        raise AssertionError("bridge probe q12/H6 section indices mismatch")
    selector_graph = q12_h6.get("selector_graph", {})
    if selector_graph.get("graph_valid") is not True:
        raise AssertionError("bridge probe q12/H6 selector graph invalid")
    if q12_h6.get("row_weight_histogram") != {"5": 12}:
        raise AssertionError("bridge probe q12/H6 row weights changed")
    if q12_h6.get("coverage_multiplicity_histogram") != {"3": 20}:
        raise AssertionError("bridge probe q12/H6 coverage multiplicity changed")
    if q12_h6.get("coverage_atom_count") != 20:
        raise AssertionError("bridge probe q12/H6 atom coverage count mismatch")
    q12_rows = q12_h6.get("q12_h6_rows", [])
    expected_q12_atom_rows = [
        [0, 1, 8, 17, 12],
        [0, 1, 10, 11, 5],
        [0, 5, 9, 15, 12],
        [1, 8, 6, 4, 10],
        [2, 3, 9, 5, 11],
        [2, 3, 14, 19, 7],
        [2, 7, 4, 10, 11],
        [3, 9, 15, 13, 14],
        [4, 6, 18, 19, 7],
        [6, 8, 17, 16, 18],
        [12, 15, 13, 16, 17],
        [13, 14, 19, 18, 16],
    ]
    if [row.get("h6_public_atom_ids") for row in q12_rows] != expected_q12_atom_rows:
        raise AssertionError("bridge probe q12/H6 pentagon rows changed")
    brute_force = q12_h6.get("raw_combination_bruteforce", {})
    if brute_force.get("search_space_size") != 4096:
        raise AssertionError("bridge probe q12/H6 subset search size mismatch")
    if brute_force.get("raw_union_exact_solution_count") != 0:
        raise AssertionError("bridge probe q12/H6 raw union unexpectedly hit mask288")
    if brute_force.get("raw_parity_exact_solution_count") != 0:
        raise AssertionError("bridge probe q12/H6 raw parity unexpectedly hit mask288")
    best_union = brute_force.get("best_raw_union_candidate", {})
    if best_union.get("selected_q12_classes") != [1, 6]:
        raise AssertionError("bridge probe q12/H6 best union classes mismatch")
    if best_union.get("extra_atom_ids") != [2, 5] or best_union.get("missing_atom_ids") != [
        13,
        16,
    ]:
        raise AssertionError("bridge probe q12/H6 best union boundary changed")
    best_parity = brute_force.get("best_raw_parity_candidate", {})
    if best_parity.get("selected_q12_classes") != [2, 3, 4, 5, 9, 10, 11]:
        raise AssertionError("bridge probe q12/H6 best parity classes mismatch")
    if best_parity.get("extra_atom_ids") != [] or best_parity.get("missing_atom_ids") != [13]:
        raise AssertionError("bridge probe q12/H6 best parity boundary changed")
    signed_unit = q12_h6.get("signed_unit_bruteforce", {})
    if signed_unit.get("search_space_size") != 531440:
        raise AssertionError("bridge probe q12/H6 signed-unit search size mismatch")
    if signed_unit.get("exact_hit_found") is not False:
        raise AssertionError("bridge probe q12/H6 signed-unit search unexpectedly hit mask288")
    if signed_unit.get("tested_until_first_hit_or_exhaustion") != 531440:
        raise AssertionError("bridge probe q12/H6 signed-unit search did not exhaust")
    packet_boundary = q12_h6.get("packet_normalization_boundary", {})
    if packet_boundary.get("boundary_smith_nonunit_factors") != [2, 4, 4]:
        raise AssertionError("bridge probe q12/H6 Smith boundary changed")
    if packet_boundary.get("zero_sum_boundary_lattice_index") != 32:
        raise AssertionError("bridge probe q12/H6 boundary lattice index mismatch")
    if packet_boundary.get("no_visible_loop_step_column_passes_packet_snf") is not True:
        raise AssertionError("bridge probe q12/H6 visible Loop SNF boundary mismatch")
    missing_q12_packet = packet_boundary.get("missing_q12_packet_projection", {})
    if missing_q12_packet.get("status") != "blocked_missing_quotient_class_to_packet_projection":
        raise AssertionError("bridge probe q12/H6 missing packet projection status mismatch")
    q12_result = q12_h6.get("result", {})
    expected_q12_true = {
        "q12_selector_graph_materialized",
        "q12_section_has_12_classes",
        "q12_selector_rows_cover_h6_atoms_uniformly",
        "target_mask_h6_support_is_weight8",
        "raw_q12_union_does_not_materialize_target_support",
        "raw_q12_parity_does_not_materialize_target_support",
        "signed_unit_q12_combination_does_not_materialize_target_support",
        "certified_q12_packet_projection_absent",
        "boundary_torsion_obstruction_present",
        "visible_loop_snf_no_raw_packet_bridge",
        "q12_h6_candidate_not_sufficient_for_z2_retest",
    }
    for key in expected_q12_true:
        if q12_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12/H6 projection check mismatch: {key}")

    q12_packet_seed = artifact.get("q12_packet_low_support_normalization_audit", {})
    if not isinstance(q12_packet_seed, dict) or not q12_packet_seed:
        raise AssertionError("bridge probe q12 packet low-support audit missing")
    if (
        q12_packet_seed.get("status")
        != "MASK288_Q12_PACKET_LOW_SUPPORT_SEED_FOUND_FULL_BRIDGE_OPEN"
    ):
        raise AssertionError("bridge probe q12 packet seed status mismatch")
    if q12_packet_seed.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 packet seed mask mismatch")
    if q12_packet_seed.get("selected_h6_public_atom_ids") != [
        0,
        1,
        4,
        7,
        10,
        11,
        13,
        16,
    ]:
        raise AssertionError("bridge probe q12 packet seed target support mismatch")
    if q12_packet_seed.get("packet_snf_local_image_test") != (
        "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet"
    ):
        raise AssertionError("bridge probe q12 packet seed SNF test mismatch")
    row_norm = q12_packet_seed.get("row_normalization_summary", {})
    if row_norm.get("row_scalar_divisibility_for_any_packet_pairing") != 6:
        raise AssertionError("bridge probe q12 packet seed row scalar mismatch")
    if row_norm.get("nonuniform_row_scaling_improves_on_scalar_6") is not False:
        raise AssertionError("bridge probe q12 packet seed row scaling overclaim")
    if row_norm.get("only_compatible_residue_pair_mod6") != [0, 0]:
        raise AssertionError("bridge probe q12 packet seed residue mismatch")
    low_summary = q12_packet_seed.get("low_support_summary", {})
    if low_summary.get("even_image_support_families") != [[0, 11], [6, 17], [14, 15]]:
        raise AssertionError("bridge probe q12 packet seed support families mismatch")
    if low_summary.get("even_image_support_family_count") != 3:
        raise AssertionError("bridge probe q12 packet seed family count mismatch")
    if low_summary.get("compatible_doublet_count") != 6:
        raise AssertionError("bridge probe q12 packet seed doublet count mismatch")
    if low_summary.get("compatible_doublet_rank_histogram") != {"1": 6}:
        raise AssertionError("bridge probe q12 packet seed doublet rank mismatch")
    if low_summary.get("full_packet_doublet_map_available") is not False:
        raise AssertionError("bridge probe q12 packet seed full-map overclaim")
    family_scan = q12_packet_seed.get("packet_low_support_family_scan_rows", [])
    expected_family_scan = [
        {
            "family": [0, 11],
            "inside": True,
            "q12_class": 1,
            "section_relation_id": 227,
            "q12_atoms": [0, 1, 10, 11, 5],
            "selected_overlap": [0, 1, 10, 11],
            "extra": [5],
            "missing": [4, 7, 13, 16],
        },
        {
            "family": [6, 17],
            "inside": False,
            "q12_class": 9,
            "section_relation_id": 263,
            "q12_atoms": [6, 8, 17, 16, 18],
            "selected_overlap": [16],
            "extra": [6, 8, 17, 18],
            "missing": [0, 1, 4, 7, 10, 11, 13],
        },
        {
            "family": [14, 15],
            "inside": False,
            "q12_class": 7,
            "section_relation_id": 77,
            "q12_atoms": [3, 9, 15, 13, 14],
            "selected_overlap": [13],
            "extra": [3, 9, 14, 15],
            "missing": [0, 1, 4, 7, 10, 11, 16],
        },
    ]
    if len(family_scan) != len(expected_family_scan):
        raise AssertionError("bridge probe q12 packet seed family scan count mismatch")
    for row, expected in zip(family_scan, expected_family_scan):
        if row.get("packet_low_support_family") != expected["family"]:
            raise AssertionError("bridge probe q12 packet seed family mismatch")
        if row.get("contained_in_selected_mask288_support") is not expected["inside"]:
            raise AssertionError("bridge probe q12 packet seed selected-family flag mismatch")
        if row.get("containing_q12_row_count") != 1:
            raise AssertionError("bridge probe q12 packet seed q12 containment count mismatch")
        containing = row.get("containing_q12_rows", [{}])[0]
        if containing.get("q12_class") != expected["q12_class"]:
            raise AssertionError("bridge probe q12 packet seed q12 class mismatch")
        if containing.get("section_relation_id") != expected["section_relation_id"]:
            raise AssertionError("bridge probe q12 packet seed relation mismatch")
        if containing.get("h6_public_atom_ids") != expected["q12_atoms"]:
            raise AssertionError("bridge probe q12 packet seed q12 atoms mismatch")
        if containing.get("selected_overlap_atom_ids") != expected["selected_overlap"]:
            raise AssertionError("bridge probe q12 packet seed selected overlap mismatch")
        if containing.get("extra_atom_ids_outside_selected_mask") != expected["extra"]:
            raise AssertionError("bridge probe q12 packet seed extra atoms mismatch")
        if containing.get("missing_selected_atom_ids") != expected["missing"]:
            raise AssertionError("bridge probe q12 packet seed missing atoms mismatch")
    mask_seed_rows = q12_packet_seed.get("mask288_q12_packet_seed_rows", [])
    if len(mask_seed_rows) != 1:
        raise AssertionError("bridge probe q12 packet seed row count mismatch")
    mask_seed = mask_seed_rows[0]
    if mask_seed.get("packet_low_support_family") != [0, 11]:
        raise AssertionError("bridge probe mask288 q12 packet seed family mismatch")
    if mask_seed.get("q12_class") != 1 or mask_seed.get("section_relation_id") != 227:
        raise AssertionError("bridge probe mask288 q12 packet seed relation mismatch")
    if mask_seed.get("extra_atom_ids_outside_selected_mask") != [5]:
        raise AssertionError("bridge probe mask288 q12 packet seed extra atom mismatch")
    if mask_seed.get("missing_selected_atom_ids") != [4, 7, 13, 16]:
        raise AssertionError("bridge probe mask288 q12 packet seed missing atom mismatch")
    q12_packet_result = q12_packet_seed.get("result", {})
    expected_q12_packet_true = {
        "row_normalization_obstruction_certified",
        "low_support_candidate_atlas_certified",
        "packet_snf_obstruction_certified",
        "all_packet_low_support_families_embed_in_unique_q12_pentagons",
        "mask288_has_unique_low_support_packet_seed",
        "mask288_seed_q12_pentagon_is_not_full_mask_support",
        "row_normalization_still_requires_scalar6",
        "low_support_doublets_are_rank_one_only",
        "packet_operator_obstruction_is_2_power_10_6_power_10",
        "q12_packet_seed_found_but_full_bridge_open",
    }
    for key in expected_q12_packet_true:
        if q12_packet_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 packet seed check mismatch: {key}")

    support3 = artifact.get("mask288_q12_packet_seed_support3_audit", {})
    if not isinstance(support3, dict) or not support3:
        raise AssertionError("bridge probe q12 packet seed support3 audit missing")
    if (
        support3.get("status")
        != "MASK288_Q12_PACKET_SEED_SUPPORT3_EXTENSION_BLOCKED_BY_PARITY"
    ):
        raise AssertionError("bridge probe q12 packet seed support3 status mismatch")
    if support3.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 packet seed support3 mask mismatch")
    if support3.get("seed_packet_low_support_family") != [0, 11]:
        raise AssertionError("bridge probe q12 packet seed support3 seed mismatch")
    if support3.get("seed_q12_class") != 1:
        raise AssertionError("bridge probe q12 packet seed support3 q12 class mismatch")
    if support3.get("seed_section_relation_id") != 227:
        raise AssertionError("bridge probe q12 packet seed support3 relation mismatch")
    if support3.get("seed_q12_pentagon_atom_ids") != [0, 1, 10, 11, 5]:
        raise AssertionError("bridge probe q12 packet seed support3 pentagon mismatch")
    if support3.get("missing_selected_atom_ids") != [4, 7, 13, 16]:
        raise AssertionError("bridge probe q12 packet seed support3 missing atoms mismatch")
    if support3.get("coefficient_set") != [-1, 1] or support3.get("support_size") != 3:
        raise AssertionError("bridge probe q12 packet seed support3 search definition mismatch")
    if support3.get("candidate_count") != 32:
        raise AssertionError("bridge probe q12 packet seed support3 candidate count mismatch")
    if support3.get("even_image_candidate_count") != 0:
        raise AssertionError("bridge probe q12 packet seed support3 found even candidate")
    if support3.get("compatible_doublet_count") != 0:
        raise AssertionError("bridge probe q12 packet seed support3 found compatible doublet")
    expected_by_extra = [
        {
            "extra_atom_id": 4,
            "extra_atom_label": "{B-,V-,V+}",
            "candidate_count": 8,
            "even_image_candidate_count": 0,
            "odd_step_entry_count_histogram": {"2": 8},
            "first_odd_step_atom_ids": [0],
        },
        {
            "extra_atom_id": 7,
            "extra_atom_label": "{B-,V+,S-}",
            "candidate_count": 8,
            "even_image_candidate_count": 0,
            "odd_step_entry_count_histogram": {"4": 8},
            "first_odd_step_atom_ids": [3],
        },
        {
            "extra_atom_id": 13,
            "extra_atom_label": "{B+,V+,S-}",
            "candidate_count": 8,
            "even_image_candidate_count": 0,
            "odd_step_entry_count_histogram": {"2": 8},
            "first_odd_step_atom_ids": [4],
        },
        {
            "extra_atom_id": 16,
            "extra_atom_label": "{V-,V+,S-}",
            "candidate_count": 8,
            "even_image_candidate_count": 0,
            "odd_step_entry_count_histogram": {"4": 8},
            "first_odd_step_atom_ids": [0],
        },
    ]
    if support3.get("by_extra_atom_rows") != expected_by_extra:
        raise AssertionError("bridge probe q12 packet seed support3 by-extra rows mismatch")
    if len(support3.get("candidate_rows", [])) != 32:
        raise AssertionError("bridge probe q12 packet seed support3 row count mismatch")
    if any(row.get("image_is_even") is not False for row in support3.get("candidate_rows", [])):
        raise AssertionError("bridge probe q12 packet seed support3 row parity mismatch")
    if support3.get("compatible_doublet_rows") != []:
        raise AssertionError("bridge probe q12 packet seed support3 doublet rows mismatch")
    support3_result = support3.get("result", {})
    expected_support3_true = {
        "seed_audit_found_relation227_seed",
        "support3_candidate_count_is_32",
        "support3_search_covers_four_missing_mask_atoms",
        "no_support3_seed_extension_has_even_image",
        "support3_packet_snf_doublet_count_zero",
        "packet_snf_local_test_certified",
        "single_missing_atom_support3_extension_blocked_by_parity",
    }
    for key in expected_support3_true:
        if support3_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 packet seed support3 check mismatch: {key}")

    broadened = artifact.get("mask288_q12_packet_seed_broadened_extension_audit", {})
    if not isinstance(broadened, dict) or not broadened:
        raise AssertionError("bridge probe q12 packet broadened seed audit missing")
    if (
        broadened.get("status")
        != "MASK288_Q12_PACKET_SEED_WIDENED_SUPPORT3_RANK2_CANDIDATES_FOUND"
    ):
        raise AssertionError("bridge probe q12 packet broadened seed status mismatch")
    if broadened.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 packet broadened seed mask mismatch")
    if broadened.get("seed_packet_low_support_family") != [0, 11]:
        raise AssertionError("bridge probe q12 packet broadened seed family mismatch")
    if broadened.get("seed_q12_class") != 1:
        raise AssertionError("bridge probe q12 packet broadened seed q12 class mismatch")
    if broadened.get("seed_section_relation_id") != 227:
        raise AssertionError("bridge probe q12 packet broadened seed relation mismatch")
    if broadened.get("missing_selected_atom_ids") != [4, 7, 13, 16]:
        raise AssertionError("bridge probe q12 packet broadened seed missing atoms mismatch")
    support4 = broadened.get("support4_unit_summary", {})
    if support4.get("coefficient_set") != [-1, 1] or support4.get("support_size") != 4:
        raise AssertionError("bridge probe q12 packet support4 definition mismatch")
    if support4.get("missing_pair_count") != 6 or support4.get("candidate_count") != 96:
        raise AssertionError("bridge probe q12 packet support4 search size mismatch")
    if support4.get("even_image_candidate_count") != 0:
        raise AssertionError("bridge probe q12 packet support4 unexpectedly cleared parity")
    if support4.get("compatible_doublet_count") != 0:
        raise AssertionError("bridge probe q12 packet support4 unexpectedly found doublet")
    if support4.get("odd_step_entry_count_histogram") != {"4": 32, "6": 64}:
        raise AssertionError("bridge probe q12 packet support4 odd histogram mismatch")
    expected_support4_pairs = [
        {"missing_atom_pair": [4, 7], "odd_step_entry_count_histogram": {"6": 16}},
        {"missing_atom_pair": [4, 13], "odd_step_entry_count_histogram": {"4": 16}},
        {"missing_atom_pair": [4, 16], "odd_step_entry_count_histogram": {"4": 16}},
        {"missing_atom_pair": [7, 13], "odd_step_entry_count_histogram": {"6": 16}},
        {"missing_atom_pair": [7, 16], "odd_step_entry_count_histogram": {"6": 16}},
        {"missing_atom_pair": [13, 16], "odd_step_entry_count_histogram": {"6": 16}},
    ]
    pair_rows = support4.get("by_missing_pair_rows", [])
    if len(pair_rows) != len(expected_support4_pairs):
        raise AssertionError("bridge probe q12 packet support4 pair row count mismatch")
    for row, expected in zip(pair_rows, expected_support4_pairs):
        if row.get("missing_atom_pair") != expected["missing_atom_pair"]:
            raise AssertionError("bridge probe q12 packet support4 pair mismatch")
        if row.get("candidate_count") != 16 or row.get("even_image_candidate_count") != 0:
            raise AssertionError("bridge probe q12 packet support4 pair count mismatch")
        if row.get("odd_step_entry_count_histogram") != expected["odd_step_entry_count_histogram"]:
            raise AssertionError("bridge probe q12 packet support4 pair odd histogram mismatch")
    widened = broadened.get("support3_widened_summary", {})
    if widened.get("coefficient_set") != [-2, -1, 1, 2]:
        raise AssertionError("bridge probe q12 packet widened coefficient set mismatch")
    if widened.get("support_size") != 3 or widened.get("candidate_count") != 256:
        raise AssertionError("bridge probe q12 packet widened search size mismatch")
    if widened.get("even_image_candidate_count") != 64:
        raise AssertionError("bridge probe q12 packet widened even count mismatch")
    if widened.get("even_image_gcd_histogram") != {"2": 64}:
        raise AssertionError("bridge probe q12 packet widened gcd histogram mismatch")
    if widened.get("even_image_count_by_extra_atom") != {
        "4": 16,
        "7": 16,
        "13": 16,
        "16": 16,
    }:
        raise AssertionError("bridge probe q12 packet widened even count by atom mismatch")
    if widened.get("compatible_doublet_count") != 64:
        raise AssertionError("bridge probe q12 packet widened doublet count mismatch")
    if widened.get("compatible_doublet_rank_histogram") != {"1": 32, "2": 32}:
        raise AssertionError("bridge probe q12 packet widened rank histogram mismatch")
    if widened.get("negative_doublet_count") != 32:
        raise AssertionError("bridge probe q12 packet widened negative doublet count mismatch")
    if widened.get("rank2_doublet_count") != 32:
        raise AssertionError("bridge probe q12 packet widened rank2 count mismatch")
    expected_widened_by_extra = [
        {
            "extra_atom_id": 4,
            "extra_atom_label": "{B-,V-,V+}",
            "candidate_count": 64,
            "even_image_candidate_count": 16,
            "compatible_doublet_count": 16,
            "compatible_doublet_rank_histogram": {"1": 8, "2": 8},
        },
        {
            "extra_atom_id": 7,
            "extra_atom_label": "{B-,V+,S-}",
            "candidate_count": 64,
            "even_image_candidate_count": 16,
            "compatible_doublet_count": 16,
            "compatible_doublet_rank_histogram": {"1": 8, "2": 8},
        },
        {
            "extra_atom_id": 13,
            "extra_atom_label": "{B+,V+,S-}",
            "candidate_count": 64,
            "even_image_candidate_count": 16,
            "compatible_doublet_count": 16,
            "compatible_doublet_rank_histogram": {"1": 8, "2": 8},
        },
        {
            "extra_atom_id": 16,
            "extra_atom_label": "{V-,V+,S-}",
            "candidate_count": 64,
            "even_image_candidate_count": 16,
            "compatible_doublet_count": 16,
            "compatible_doublet_rank_histogram": {"1": 8, "2": 8},
        },
    ]
    if widened.get("by_extra_atom_rows") != expected_widened_by_extra:
        raise AssertionError("bridge probe q12 packet widened by-extra rows mismatch")
    expected_rank2_examples = [
        {
            "extra_atom_id": 4,
            "support_atom_ids": [0, 11, 4],
            "left_candidate_id": 0,
            "right_candidate_id": 23,
            "left_coefficients": [-2, -2, -2],
            "right_coefficients": [-1, -1, 2],
            "doublet_rank_over_Q": 2,
        },
        {
            "extra_atom_id": 7,
            "support_atom_ids": [0, 11, 7],
            "left_candidate_id": 64,
            "right_candidate_id": 87,
            "left_coefficients": [-2, -2, -2],
            "right_coefficients": [-1, -1, 2],
            "doublet_rank_over_Q": 2,
        },
        {
            "extra_atom_id": 13,
            "support_atom_ids": [0, 11, 13],
            "left_candidate_id": 128,
            "right_candidate_id": 151,
            "left_coefficients": [-2, -2, -2],
            "right_coefficients": [-1, -1, 2],
            "doublet_rank_over_Q": 2,
        },
        {
            "extra_atom_id": 16,
            "support_atom_ids": [0, 11, 16],
            "left_candidate_id": 192,
            "right_candidate_id": 215,
            "left_coefficients": [-2, -2, -2],
            "right_coefficients": [-1, -1, 2],
            "doublet_rank_over_Q": 2,
        },
    ]
    if widened.get("rank2_doublet_example_rows") != expected_rank2_examples:
        raise AssertionError("bridge probe q12 packet widened rank2 examples mismatch")
    if len(broadened.get("support3_widened_even_candidate_rows", [])) != 64:
        raise AssertionError("bridge probe q12 packet widened even rows mismatch")
    if len(broadened.get("support3_widened_compatible_doublet_rows", [])) != 64:
        raise AssertionError("bridge probe q12 packet widened doublet rows mismatch")
    broadened_result = broadened.get("result", {})
    expected_broadened_true = {
        "unit_support4_pair_extension_blocked_by_parity",
        "widened_support3_clears_parity",
        "widened_support3_finds_packet_compatible_doublets",
        "widened_support3_finds_rank2_doublets",
        "widened_support3_doublets_stay_within_single_extra_atom_families",
        "widened_support3_not_yet_full_packet_bridge",
        "prior_unit_support3_blocked",
        "widened_support3_rank2_candidates_materialized",
    }
    for key in expected_broadened_true:
        if broadened_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 packet broadened check mismatch: {key}")

    rank2_label = artifact.get("mask288_q12_rank2_doublet_label_audit", {})
    if not isinstance(rank2_label, dict) or not rank2_label:
        raise AssertionError("bridge probe q12 rank2 label audit missing")
    if (
        rank2_label.get("status")
        != "MASK288_Q12_RANK2_PACKET_CANDIDATES_NOT_DIRECTLY_Q12_LABELLED"
    ):
        raise AssertionError("bridge probe q12 rank2 label status mismatch")
    if rank2_label.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 rank2 label mask mismatch")
    if rank2_label.get("seed_q12_class") != 1:
        raise AssertionError("bridge probe q12 rank2 label seed class mismatch")
    if rank2_label.get("seed_section_relation_id") != 227:
        raise AssertionError("bridge probe q12 rank2 label seed relation mismatch")
    if rank2_label.get("seed_packet_low_support_family") != [0, 11]:
        raise AssertionError("bridge probe q12 rank2 label seed family mismatch")
    if rank2_label.get("rank2_doublet_count") != 32:
        raise AssertionError("bridge probe q12 rank2 label doublet count mismatch")
    if rank2_label.get("direct_q12_product_label_count") != 0:
        raise AssertionError("bridge probe q12 rank2 direct product label unexpectedly found")
    seed_self = rank2_label.get("seed_self_product", {})
    if seed_self.get("output_q12_coefficients") != [[1, 2]]:
        raise AssertionError("bridge probe q12 rank2 seed self product mismatch")
    if seed_self.get("readout_support_atom_ids") != [0, 1, 5, 10, 11]:
        raise AssertionError("bridge probe q12 rank2 seed self readout mismatch")
    if seed_self.get("seed_family_covered") is not True:
        raise AssertionError("bridge probe q12 rank2 seed family not covered")
    expected_rank2_family_rows = [
        {
            "extra_atom_id": 4,
            "support_atom_ids": [0, 4, 11],
            "rank2_doublet_count": 8,
            "q12_classes_containing_extra_atom": [3, 6, 8],
            "nonzero_q12_product_count": 2,
            "q12_products_touching_extra_atom_count": 2,
            "nonzero_outputs": [[[6, 48]], [[8, 48]]],
        },
        {
            "extra_atom_id": 7,
            "support_atom_ids": [0, 7, 11],
            "rank2_doublet_count": 8,
            "q12_classes_containing_extra_atom": [5, 6, 8],
            "nonzero_q12_product_count": 2,
            "q12_products_touching_extra_atom_count": 2,
            "nonzero_outputs": [[[6, 48]], [[8, 48]]],
        },
        {
            "extra_atom_id": 13,
            "support_atom_ids": [0, 11, 13],
            "rank2_doublet_count": 8,
            "q12_classes_containing_extra_atom": [7, 10, 11],
            "nonzero_q12_product_count": 1,
            "q12_products_touching_extra_atom_count": 1,
            "nonzero_outputs": [[[11, 124]]],
        },
        {
            "extra_atom_id": 16,
            "support_atom_ids": [0, 11, 16],
            "rank2_doublet_count": 8,
            "q12_classes_containing_extra_atom": [9, 10, 11],
            "nonzero_q12_product_count": 2,
            "q12_products_touching_extra_atom_count": 2,
            "nonzero_outputs": [[[9, 124]], [[11, 124]]],
        },
    ]
    family_rows = rank2_label.get("rank2_family_rows", [])
    if len(family_rows) != len(expected_rank2_family_rows):
        raise AssertionError("bridge probe q12 rank2 family row count mismatch")
    for row, expected in zip(family_rows, expected_rank2_family_rows):
        if row.get("extra_atom_id") != expected["extra_atom_id"]:
            raise AssertionError("bridge probe q12 rank2 family extra atom mismatch")
        if row.get("support_atom_ids") != expected["support_atom_ids"]:
            raise AssertionError("bridge probe q12 rank2 support atoms mismatch")
        if row.get("rank2_doublet_count") != expected["rank2_doublet_count"]:
            raise AssertionError("bridge probe q12 rank2 family count mismatch")
        if row.get("q12_classes_containing_extra_atom") != expected[
            "q12_classes_containing_extra_atom"
        ]:
            raise AssertionError("bridge probe q12 rank2 extra q12 classes mismatch")
        if row.get("q12_product_scan_count") != 6:
            raise AssertionError("bridge probe q12 rank2 scan count mismatch")
        if row.get("nonzero_q12_product_count") != expected["nonzero_q12_product_count"]:
            raise AssertionError("bridge probe q12 rank2 nonzero product count mismatch")
        if row.get("q12_products_touching_extra_atom_count") != expected[
            "q12_products_touching_extra_atom_count"
        ]:
            raise AssertionError("bridge probe q12 rank2 extra-touch count mismatch")
        if row.get("q12_products_preserving_seed_family_count") != 0:
            raise AssertionError("bridge probe q12 rank2 preserved seed unexpectedly")
        if row.get("direct_q12_product_label_count") != 0:
            raise AssertionError("bridge probe q12 rank2 direct product label unexpectedly found")
        nonzero_outputs = [
            product_row.get("output_q12_coefficients")
            for product_row in row.get("nonzero_q12_product_rows", [])
        ]
        if nonzero_outputs != expected["nonzero_outputs"]:
            raise AssertionError("bridge probe q12 rank2 nonzero output mismatch")
    if len(rank2_label.get("q12_product_label_scan_rows", [])) != 24:
        raise AssertionError("bridge probe q12 rank2 product scan row count mismatch")
    missing_rank2_projection = rank2_label.get("missing_q12_packet_projection", {})
    if missing_rank2_projection.get("status") != "blocked_missing_quotient_class_to_packet_projection":
        raise AssertionError("bridge probe q12 rank2 missing projection status mismatch")
    rank2_label_result = rank2_label.get("result", {})
    expected_rank2_label_true = {
        "rank2_doublet_count_is_32",
        "rank2_doublets_split_across_four_missing_atom_families",
        "seed_self_product_preserves_seed_family",
        "q12_products_touch_each_extra_atom",
        "no_rank2_family_has_direct_q12_product_label",
        "q12_product_labels_do_not_preserve_seed_when_touching_extra",
        "q12_packet_projection_still_absent",
        "rank2_doublets_not_directly_q12_tensor_labelled",
    }
    for key in expected_rank2_label_true:
        if rank2_label_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 rank2 label check mismatch: {key}")

    linear_combo = artifact.get("mask288_q12_rank2_linear_combination_audit", {})
    if not isinstance(linear_combo, dict) or not linear_combo:
        raise AssertionError("bridge probe q12 rank2 linear-combination audit missing")
    if (
        linear_combo.get("status")
        != "MASK288_Q12_RANK2_LINEAR_PRODUCT_COVERS_WITH_OVERHANG_ONLY"
    ):
        raise AssertionError("bridge probe q12 rank2 linear-combination status mismatch")
    if linear_combo.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 rank2 linear-combination mask mismatch")
    if linear_combo.get("seed_q12_class") != 1:
        raise AssertionError("bridge probe q12 rank2 linear-combination seed mismatch")
    if linear_combo.get("coefficient_set") != [-1, 0, 1]:
        raise AssertionError("bridge probe q12 rank2 linear-combination coefficients mismatch")
    if linear_combo.get("total_search_space_size") != 86:
        raise AssertionError("bridge probe q12 rank2 linear-combination search size mismatch")
    if linear_combo.get("total_cover_solution_count") != 40:
        raise AssertionError("bridge probe q12 rank2 linear-combination cover count mismatch")
    if linear_combo.get("total_exact_support_solution_count") != 0:
        raise AssertionError("bridge probe q12 rank2 linear-combination exact count mismatch")
    expected_linear_rows = [
        {
            "extra_atom_id": 4,
            "target_atom_ids": [0, 4, 11],
            "local_product_ids": ["seed_self", "seed_right_6", "seed_left_8"],
            "search_space_size": 26,
            "cover_solution_count": 12,
            "exact_support_solution_count": 0,
            "best_extra_atom_ids": [1, 2, 5, 7, 10],
            "best_chosen_product_ids": ["seed_self", "seed_right_6"],
            "best_target_atom_values": {"0": -2, "4": -48, "11": -50},
        },
        {
            "extra_atom_id": 7,
            "target_atom_ids": [0, 7, 11],
            "local_product_ids": ["seed_self", "seed_right_6", "seed_left_8"],
            "search_space_size": 26,
            "cover_solution_count": 12,
            "exact_support_solution_count": 0,
            "best_extra_atom_ids": [1, 2, 4, 5, 10],
            "best_chosen_product_ids": ["seed_self", "seed_right_6"],
            "best_target_atom_values": {"0": -2, "7": -48, "11": -50},
        },
        {
            "extra_atom_id": 13,
            "target_atom_ids": [0, 11, 13],
            "local_product_ids": ["seed_self", "seed_right_11"],
            "search_space_size": 8,
            "cover_solution_count": 4,
            "exact_support_solution_count": 0,
            "best_extra_atom_ids": [1, 5, 10, 14, 16, 18, 19],
            "best_chosen_product_ids": ["seed_self", "seed_right_11"],
            "best_target_atom_values": {"0": -2, "11": -2, "13": -124},
        },
        {
            "extra_atom_id": 16,
            "target_atom_ids": [0, 11, 16],
            "local_product_ids": ["seed_self", "seed_left_9", "seed_right_11"],
            "search_space_size": 26,
            "cover_solution_count": 12,
            "exact_support_solution_count": 0,
            "best_extra_atom_ids": [1, 5, 6, 8, 10, 17, 18],
            "best_chosen_product_ids": ["seed_self", "seed_left_9"],
            "best_target_atom_values": {"0": -2, "11": -2, "16": -124},
        },
    ]
    linear_rows = linear_combo.get("family_combination_rows", [])
    if len(linear_rows) != len(expected_linear_rows):
        raise AssertionError("bridge probe q12 rank2 linear-combination row count mismatch")
    for row, expected in zip(linear_rows, expected_linear_rows):
        if row.get("extra_atom_id") != expected["extra_atom_id"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination extra mismatch")
        if row.get("target_atom_ids") != expected["target_atom_ids"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination target mismatch")
        if row.get("local_product_ids") != expected["local_product_ids"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination local products mismatch")
        if row.get("search_space_size") != expected["search_space_size"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination per-row search mismatch")
        if row.get("cover_solution_count") != expected["cover_solution_count"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination cover mismatch")
        if row.get("exact_support_solution_count") != expected["exact_support_solution_count"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination exact mismatch")
        best_cover = row.get("best_cover_candidate", {})
        if best_cover.get("extra_atom_ids") != expected["best_extra_atom_ids"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination overhang mismatch")
        if best_cover.get("missing_atom_ids") != []:
            raise AssertionError("bridge probe q12 rank2 linear-combination missing target")
        if [
            item.get("product_id") for item in best_cover.get("chosen_products", [])
        ] != expected["best_chosen_product_ids"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination chosen products mismatch")
        if best_cover.get("target_atom_values") != expected["best_target_atom_values"]:
            raise AssertionError("bridge probe q12 rank2 linear-combination target values mismatch")
    linear_result = linear_combo.get("result", {})
    expected_linear_true = {
        "linear_cover_found_for_each_rank2_family",
        "no_exact_support_linear_combination_found",
        "best_covers_all_have_overhang",
        "best_covers_use_two_product_terms",
        "rank2_candidates_still_not_q12_packet_actions",
        "small_q12_product_combinations_cover_with_overhang_only",
    }
    for key in expected_linear_true:
        if linear_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 rank2 linear-combination check mismatch: {key}")

    overhang_audit = artifact.get("mask288_q12_product_overhang_invariant_audit", {})
    if not isinstance(overhang_audit, dict) or not overhang_audit:
        raise AssertionError("bridge probe q12 product overhang audit missing")
    if (
        overhang_audit.get("status")
        != "MASK288_Q12_PRODUCT_OVERHANG_SURVIVES_BVS_PACKET_READOUTS_STATIC_BLOCKED"
    ):
        raise AssertionError("bridge probe q12 product overhang status mismatch")
    if overhang_audit.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 product overhang mask mismatch")
    if overhang_audit.get("coefficient_set") != [-1, 0, 1]:
        raise AssertionError("bridge probe q12 product overhang coefficients mismatch")
    packet_readout = overhang_audit.get("packet_normalization_readout", {})
    if packet_readout.get("row_scalar_divisibility_for_any_packet_pairing") != 6:
        raise AssertionError("bridge probe q12 product overhang row scalar mismatch")
    if packet_readout.get("nonuniform_row_scaling_improves_on_scalar_6") is not False:
        raise AssertionError("bridge probe q12 product overhang row scaling mismatch")
    if packet_readout.get("only_compatible_residue_pair_mod6") != [0, 0]:
        raise AssertionError("bridge probe q12 product overhang residue-pair mismatch")
    if packet_readout.get("families_with_nonzero_overhang_residue_mod6") != [4, 7, 13, 16]:
        raise AssertionError("bridge probe q12 product overhang residue family mismatch")
    static_parity = overhang_audit.get("static_parity_readout", {})
    if static_parity.get("status") != "BLOCKED_MISSING_Q12_TO_H6_PUBLIC_ATOM_PROJECTION":
        raise AssertionError("bridge probe q12 product overhang static status mismatch")
    missing_projection = static_parity.get("missing_q12_packet_projection", {})
    if missing_projection.get("status") != "blocked_missing_quotient_class_to_packet_projection":
        raise AssertionError("bridge probe q12 product overhang missing projection mismatch")
    expected_overhang_rows = [
        {
            "extra_atom_id": 4,
            "overhang_atom_ids": [1, 2, 5, 7, 10],
            "unsigned_sector_counts": {"B": 7, "S": 3, "V": 5},
            "residue_mod6_histogram": {"0": 2, "4": 3},
            "nonzero_mod6_atom_ids": [1, 5, 10],
        },
        {
            "extra_atom_id": 7,
            "overhang_atom_ids": [1, 2, 4, 5, 10],
            "unsigned_sector_counts": {"B": 7, "S": 2, "V": 6},
            "residue_mod6_histogram": {"0": 2, "4": 3},
            "nonzero_mod6_atom_ids": [1, 5, 10],
        },
        {
            "extra_atom_id": 13,
            "overhang_atom_ids": [1, 5, 10, 14, 16, 18, 19],
            "unsigned_sector_counts": {"B": 5, "S": 7, "V": 9},
            "residue_mod6_histogram": {"2": 4, "4": 3},
            "nonzero_mod6_atom_ids": [1, 5, 10, 14, 16, 18, 19],
        },
        {
            "extra_atom_id": 16,
            "overhang_atom_ids": [1, 5, 6, 8, 10, 17, 18],
            "unsigned_sector_counts": {"B": 6, "S": 6, "V": 9},
            "residue_mod6_histogram": {"2": 4, "4": 3},
            "nonzero_mod6_atom_ids": [1, 5, 6, 8, 10, 17, 18],
        },
    ]
    overhang_rows = overhang_audit.get("family_overhang_rows", [])
    if len(overhang_rows) != len(expected_overhang_rows):
        raise AssertionError("bridge probe q12 product overhang row count mismatch")
    for row, expected in zip(overhang_rows, expected_overhang_rows):
        if row.get("extra_atom_id") != expected["extra_atom_id"]:
            raise AssertionError("bridge probe q12 product overhang extra mismatch")
        if row.get("overhang_atom_ids") != expected["overhang_atom_ids"]:
            raise AssertionError("bridge probe q12 product overhang support mismatch")
        overhang_readout = row.get("overhang_readout", {})
        if overhang_readout.get("unsigned_sector_counts") != expected["unsigned_sector_counts"]:
            raise AssertionError("bridge probe q12 product overhang BVS counts mismatch")
        if overhang_readout.get("residue_mod6_histogram") != expected["residue_mod6_histogram"]:
            raise AssertionError("bridge probe q12 product overhang residue histogram mismatch")
        if overhang_readout.get("nonzero_mod6_atom_ids") != expected["nonzero_mod6_atom_ids"]:
            raise AssertionError("bridge probe q12 product overhang nonzero residue mismatch")
        if row.get("missing_atom_ids") != []:
            raise AssertionError("bridge probe q12 product overhang missing target")
    overhang_result = overhang_audit.get("result", {})
    expected_overhang_true = {
        "linear_combinations_still_have_no_exact_support",
        "overhang_present_in_each_best_cover",
        "bvs_public_readout_sees_every_overhang",
        "packet_row_normalization_does_not_annihilate_overhang",
        "static_parity_retest_still_blocked_by_missing_projection",
        "overhang_survives_existing_bvs_and_packet_readouts",
    }
    for key in expected_overhang_true:
        if overhang_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 product overhang check mismatch: {key}")

    outside_cancel = artifact.get(
        "mask288_q12_outside_class1_residue_cancellation_audit", {}
    )
    if not isinstance(outside_cancel, dict) or not outside_cancel:
        raise AssertionError("bridge probe q12 outside-class1 cancellation audit missing")
    if (
        outside_cancel.get("status")
        != "MASK288_Q12_OUTSIDE_CLASS1_RESIDUE_CANCELLATION_FOUND_EXACT_SUPPORT_OPEN"
    ):
        raise AssertionError("bridge probe q12 outside-class1 cancellation status mismatch")
    if outside_cancel.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 outside-class1 cancellation mask mismatch")
    if outside_cancel.get("seed_q12_class") != 1:
        raise AssertionError("bridge probe q12 outside-class1 cancellation seed mismatch")
    if outside_cancel.get("coefficient_set") != [-1, 1]:
        raise AssertionError("bridge probe q12 outside-class1 cancellation coefficients mismatch")
    if outside_cancel.get("max_cancellation_terms") != 3:
        raise AssertionError("bridge probe q12 outside-class1 cancellation depth mismatch")
    if outside_cancel.get("nonzero_q12_product_term_count") != 48:
        raise AssertionError("bridge probe q12 outside-class1 nonzero product count mismatch")
    if outside_cancel.get("outside_class1_q12_product_term_count") != 41:
        raise AssertionError("bridge probe q12 outside-class1 product count mismatch")
    if outside_cancel.get("total_search_space_size") != 354568:
        raise AssertionError("bridge probe q12 outside-class1 search size mismatch")
    if outside_cancel.get("total_valid_candidate_count") != 354120:
        raise AssertionError("bridge probe q12 outside-class1 valid count mismatch")
    if outside_cancel.get("total_residue_clear_candidate_count") != 102:
        raise AssertionError("bridge probe q12 outside-class1 residue count mismatch")
    if outside_cancel.get("total_exact_support_candidate_count") != 0:
        raise AssertionError("bridge probe q12 outside-class1 exact support unexpectedly found")
    expected_cancel_rows = [
        {
            "extra_atom_id": 4,
            "base_extra_atom_ids": [1, 2, 5, 7, 10],
            "base_outside_target_nonzero_mod6_atom_ids": [1, 5, 10],
            "residue_clear_candidate_count": 49,
            "best_cancellation_terms": [("q12_4_4", 1), ("q12_9_11", 1)],
            "best_extra_atom_ids": [1, 2, 3, 5, 7, 9, 10],
            "best_target_atom_values": {"0": 3996, "4": -48, "11": 287664},
        },
        {
            "extra_atom_id": 7,
            "base_extra_atom_ids": [1, 2, 4, 5, 10],
            "base_outside_target_nonzero_mod6_atom_ids": [1, 5, 10],
            "residue_clear_candidate_count": 49,
            "best_cancellation_terms": [("q12_4_4", 1), ("q12_9_11", 1)],
            "best_extra_atom_ids": [1, 2, 3, 4, 5, 9, 10],
            "best_target_atom_values": {"0": 3996, "7": -48, "11": 287664},
        },
        {
            "extra_atom_id": 13,
            "base_extra_atom_ids": [1, 5, 10, 14, 16, 18, 19],
            "base_outside_target_nonzero_mod6_atom_ids": [1, 5, 10, 14, 16, 18, 19],
            "residue_clear_candidate_count": 2,
            "best_cancellation_terms": [
                ("q12_4_4", 1),
                ("q12_5_11", -1),
                ("q12_9_11", 1),
            ],
            "best_extra_atom_ids": [1, 2, 3, 5, 9, 10, 14, 16, 18, 19],
            "best_target_atom_values": {"0": 3996, "11": 287712, "13": -157116},
        },
        {
            "extra_atom_id": 16,
            "base_extra_atom_ids": [1, 5, 6, 8, 10, 17, 18],
            "base_outside_target_nonzero_mod6_atom_ids": [1, 5, 6, 8, 10, 17, 18],
            "residue_clear_candidate_count": 2,
            "best_cancellation_terms": [
                ("q12_4_4", 1),
                ("q12_4_9", -1),
                ("q12_9_11", 1),
            ],
            "best_extra_atom_ids": [1, 2, 3, 5, 6, 8, 9, 10, 17, 18],
            "best_target_atom_values": {"0": 3996, "11": 287712, "16": -89280},
        },
    ]
    cancel_rows = outside_cancel.get("family_cancellation_rows", [])
    if len(cancel_rows) != len(expected_cancel_rows):
        raise AssertionError("bridge probe q12 outside-class1 cancellation row count mismatch")
    for row, expected in zip(cancel_rows, expected_cancel_rows):
        if row.get("extra_atom_id") != expected["extra_atom_id"]:
            raise AssertionError("bridge probe q12 outside-class1 cancellation extra mismatch")
        if row.get("search_space_size") != 88642:
            raise AssertionError("bridge probe q12 outside-class1 per-row search mismatch")
        if row.get("valid_candidate_count") != 88530:
            raise AssertionError("bridge probe q12 outside-class1 per-row valid mismatch")
        if row.get("exact_support_candidate_count") != 0:
            raise AssertionError("bridge probe q12 outside-class1 per-row exact mismatch")
        if row.get("base_extra_atom_ids") != expected["base_extra_atom_ids"]:
            raise AssertionError("bridge probe q12 outside-class1 base support mismatch")
        if row.get("base_outside_target_nonzero_mod6_atom_ids") != expected[
            "base_outside_target_nonzero_mod6_atom_ids"
        ]:
            raise AssertionError("bridge probe q12 outside-class1 base residue mismatch")
        if row.get("residue_clear_candidate_count") != expected[
            "residue_clear_candidate_count"
        ]:
            raise AssertionError("bridge probe q12 outside-class1 residue clear count mismatch")
        best_residue = row.get("best_residue_clear_candidate", {})
        if best_residue.get("outside_target_nonzero_mod6_atom_count") != 0:
            raise AssertionError("bridge probe q12 outside-class1 residue not cleared")
        if best_residue.get("target_nonzero_mod6_atom_ids") != []:
            raise AssertionError("bridge probe q12 outside-class1 target residue mismatch")
        if best_residue.get("extra_atom_ids") != expected["best_extra_atom_ids"]:
            raise AssertionError("bridge probe q12 outside-class1 best support mismatch")
        if best_residue.get("target_atom_values") != expected["best_target_atom_values"]:
            raise AssertionError("bridge probe q12 outside-class1 target values mismatch")
        if [
            (term.get("product_id"), term.get("coefficient"))
            for term in best_residue.get("cancellation_terms", [])
        ] != expected["best_cancellation_terms"]:
            raise AssertionError("bridge probe q12 outside-class1 terms mismatch")
    cancel_result = outside_cancel.get("result", {})
    expected_cancel_true = {
        "outside_class1_q12_terms_available",
        "bounded_cancellation_search_preserves_targets",
        "residue_clear_candidate_found_for_each_family",
        "residue_clear_candidates_zero_outside_target_mod6",
        "residue_clear_candidates_preserve_integer_target_atoms",
        "residue_clear_candidates_are_not_integer_exact_support",
        "outside_class1_residue_cancellation_found_exact_support_open",
    }
    for key in expected_cancel_true:
        if cancel_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 outside-class1 cancellation check mismatch: {key}")

    packet_assembly = artifact.get(
        "mask288_q12_packet_normalized_seed_assembly_audit", {}
    )
    if not isinstance(packet_assembly, dict) or not packet_assembly:
        raise AssertionError("bridge probe q12 packet-normalized assembly audit missing")
    if packet_assembly.get("status") != "MASK288_Q12_PACKET_NORMALIZED_SEED_ASSEMBLY_BLOCKED":
        raise AssertionError("bridge probe q12 packet-normalized assembly status mismatch")
    if packet_assembly.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 packet-normalized assembly mask mismatch")
    if (
        packet_assembly.get("packet_snf_local_image_test")
        != "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet"
    ):
        raise AssertionError("bridge probe q12 packet-normalized assembly local test mismatch")
    expected_normalized_rows = [
        {
            "extra_atom_id": 4,
            "support_atom_ids": [0, 1, 2, 3, 4, 5, 7, 9, 10, 11],
            "support_size": 10,
            "image_gcd": 2,
            "image_nonzero_count": 20,
            "normalized_coefficient_gcd": 2,
        },
        {
            "extra_atom_id": 7,
            "support_atom_ids": [0, 1, 2, 3, 4, 5, 7, 9, 10, 11],
            "support_size": 10,
            "image_gcd": 2,
            "image_nonzero_count": 20,
            "normalized_coefficient_gcd": 2,
        },
        {
            "extra_atom_id": 13,
            "support_atom_ids": [0, 1, 2, 3, 5, 9, 10, 11, 13, 14, 16, 18, 19],
            "support_size": 13,
            "image_gcd": 2,
            "image_nonzero_count": 20,
            "normalized_coefficient_gcd": 2,
        },
        {
            "extra_atom_id": 16,
            "support_atom_ids": [0, 1, 2, 3, 5, 6, 8, 9, 10, 11, 16, 17, 18],
            "support_size": 13,
            "image_gcd": 6,
            "image_nonzero_count": 21,
            "normalized_coefficient_gcd": 6,
        },
    ]
    normalized_rows = packet_assembly.get("normalized_q12_seed_rows", [])
    if len(normalized_rows) != len(expected_normalized_rows):
        raise AssertionError("bridge probe q12 packet-normalized row count mismatch")
    for row, expected in zip(normalized_rows, expected_normalized_rows):
        if row.get("extra_atom_id") != expected["extra_atom_id"]:
            raise AssertionError("bridge probe q12 packet-normalized extra mismatch")
        if row.get("row_kind") != "q12_residue6":
            raise AssertionError("bridge probe q12 packet-normalized row kind mismatch")
        if row.get("scalar6_divisible") is not True:
            raise AssertionError("bridge probe q12 packet-normalized scalar6 mismatch")
        if row.get("image_is_even") is not True:
            raise AssertionError("bridge probe q12 packet-normalized parity mismatch")
        if row.get("support_atom_ids") != expected["support_atom_ids"]:
            raise AssertionError("bridge probe q12 packet-normalized support mismatch")
        if row.get("support_size") != expected["support_size"]:
            raise AssertionError("bridge probe q12 packet-normalized support size mismatch")
        if row.get("image_gcd") != expected["image_gcd"]:
            raise AssertionError("bridge probe q12 packet-normalized image gcd mismatch")
        if row.get("image_nonzero_count") != expected["image_nonzero_count"]:
            raise AssertionError("bridge probe q12 packet-normalized image support mismatch")
        if row.get("normalized_coefficient_gcd") != expected["normalized_coefficient_gcd"]:
            raise AssertionError("bridge probe q12 packet-normalized coefficient gcd mismatch")
    assembly_summary = packet_assembly.get("candidate_pool_summary", {})
    expected_assembly_summary = {
        "q12_residue6_row_count": 4,
        "low_support_even_row_count": 12,
        "support3_widened_even_row_count": 64,
        "candidate_row_count": 80,
        "candidate_pair_count": 3160,
        "q12_involving_pair_count": 310,
        "q12_involving_compatible_doublet_count": 0,
        "compatible_doublet_count": 70,
        "compatible_doublet_rank_histogram": {"1": 38, "2": 32},
        "compatible_doublet_kind_pair_histogram": {
            "low_support2+low_support2": 6,
            "support3_widened+support3_widened": 64,
        },
        "compatible_support_family_count": 7,
        "rank2_support_family_count": 4,
    }
    for key, expected in expected_assembly_summary.items():
        if assembly_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q12 packet-normalized summary mismatch: {key}")
    if len(packet_assembly.get("compatible_doublet_rows", [])) != 70:
        raise AssertionError("bridge probe q12 packet-normalized doublet row count mismatch")
    if any(
        row.get("q12_residue6_involved") is True
        for row in packet_assembly.get("compatible_doublet_rows", [])
    ):
        raise AssertionError("bridge probe q12 packet-normalized q12 doublet unexpectedly found")
    packet_assembly_result = packet_assembly.get("result", {})
    expected_packet_assembly_true = {
        "scalar6_normalized_q12_rows_materialized",
        "scalar6_normalized_q12_rows_are_even_boundary_rows",
        "low_support_packet_atlas_certified_degenerate",
        "support3_packet_atlas_certified_rank2_local_only",
        "q12_normalized_rows_add_no_packet_compatible_doublets",
        "candidate_pool_contains_only_preexisting_atlas_doublets",
        "candidate_pool_still_short_of_full_packet_bridge",
        "packet_normalized_q12_seed_assembly_remains_blocked",
    }
    for key in expected_packet_assembly_true:
        if packet_assembly_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 packet-normalized check mismatch: {key}")

    direct_q12 = artifact.get("mask288_q12_direct_paired_doublet_search_audit", {})
    if not isinstance(direct_q12, dict) or not direct_q12:
        raise AssertionError("bridge probe q12 direct paired doublet audit missing")
    if (
        direct_q12.get("status")
        != "MASK288_Q12_DIRECT_PAIRED_DOUBLET_SEARCH_FINDS_RANK2_SHORT_OF_FULL_BRIDGE"
    ):
        raise AssertionError("bridge probe q12 direct paired doublet status mismatch")
    if direct_q12.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 direct paired doublet mask mismatch")
    if direct_q12.get("seed_q12_class") != 1:
        raise AssertionError("bridge probe q12 direct paired doublet seed mismatch")
    if direct_q12.get("coefficient_set") != [-1, 1]:
        raise AssertionError("bridge probe q12 direct paired doublet coefficient mismatch")
    if direct_q12.get("max_cancellation_terms") != 3:
        raise AssertionError("bridge probe q12 direct paired doublet depth mismatch")
    direct_candidate_summary = direct_q12.get("q12_candidate_summary", {})
    expected_direct_candidate_summary = {
        "candidate_count": 102,
        "candidate_pair_count": 5151,
        "candidate_count_by_extra_atom": {"4": 49, "7": 49, "13": 2, "16": 2},
        "support_size_histogram": {"10": 22, "13": 36, "14": 12, "15": 32},
        "cancellation_term_count_histogram": {"2": 2, "3": 100},
        "image_gcd_histogram": {"2": 92, "6": 6, "18": 2, "222": 2},
    }
    for key, expected in expected_direct_candidate_summary.items():
        if direct_candidate_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q12 direct paired candidate mismatch: {key}")
    expected_direct_family_rows = [
        {
            "extra_atom_id": 4,
            "candidate_count": 49,
            "support_size_histogram": {"10": 11, "13": 16, "14": 6, "15": 16},
            "image_gcd_histogram": {"2": 45, "6": 2, "18": 1, "222": 1},
        },
        {
            "extra_atom_id": 7,
            "candidate_count": 49,
            "support_size_histogram": {"10": 11, "13": 16, "14": 6, "15": 16},
            "image_gcd_histogram": {"2": 45, "6": 2, "18": 1, "222": 1},
        },
        {
            "extra_atom_id": 13,
            "candidate_count": 2,
            "support_size_histogram": {"13": 2},
            "image_gcd_histogram": {"2": 1, "6": 1},
        },
        {
            "extra_atom_id": 16,
            "candidate_count": 2,
            "support_size_histogram": {"13": 2},
            "image_gcd_histogram": {"2": 1, "6": 1},
        },
    ]
    direct_family_rows = direct_q12.get("family_candidate_rows", [])
    if len(direct_family_rows) != len(expected_direct_family_rows):
        raise AssertionError("bridge probe q12 direct paired family row count mismatch")
    for row, expected in zip(direct_family_rows, expected_direct_family_rows):
        for key, expected_value in expected.items():
            if row.get(key) != expected_value:
                raise AssertionError(f"bridge probe q12 direct paired family mismatch: {key}")
    direct_doublet_summary = direct_q12.get("compatible_doublet_summary", {})
    expected_direct_doublet_summary = {
        "compatible_doublet_count": 509,
        "compatible_doublet_rank_histogram": {"1": 4, "2": 505},
        "same_extra_atom_family_histogram": {"False": 265, "True": 244},
        "extra_atom_pair_histogram": {
            "4,4": 122,
            "4,7": 248,
            "4,13": 4,
            "4,16": 4,
            "7,7": 122,
            "7,13": 4,
            "7,16": 4,
            "13,16": 1,
        },
        "rank2_support_family_count": 8,
        "full_packet_target_doublet_family_count": 10,
    }
    for key, expected in expected_direct_doublet_summary.items():
        if direct_doublet_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q12 direct paired doublet mismatch: {key}")
    expected_rank2_support_families = [
        [0, 1, 2, 3, 4, 5, 7, 9, 10, 11],
        [0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 13, 14, 15],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 17],
        [0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 14, 15, 19],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18],
        [0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 15, 16, 17],
        [0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 13, 14, 16, 18, 19],
        [0, 1, 2, 3, 5, 6, 8, 9, 10, 11, 13, 14, 16, 17, 18, 19],
    ]
    rank2_rows = direct_q12.get("rank2_support_family_rows", [])
    if [row.get("support_family_atom_ids") for row in rank2_rows] != expected_rank2_support_families:
        raise AssertionError("bridge probe q12 direct paired rank2 families mismatch")
    if [row.get("compatible_pair_count_for_family") for row in rank2_rows] != [
        72,
        96,
        32,
        64,
        72,
        96,
        72,
        1,
    ]:
        raise AssertionError("bridge probe q12 direct paired family pair count mismatch")
    direct_result = direct_q12.get("result", {})
    expected_direct_true = {
        "q12_residue_clear_rows_match_prior_count",
        "q12_residue_clear_rows_are_even_after_scalar6",
        "direct_q12_packet_compatible_doublets_found",
        "direct_q12_packet_doublets_are_mostly_rank2",
        "direct_q12_rank2_support_families_short_of_ten",
        "raw_packet_bridge_columns_still_absent",
        "direct_q12_paired_doublet_search_finds_rank2_short_of_full_bridge",
    }
    for key in expected_direct_true:
        if direct_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 direct paired check mismatch: {key}")

    seed_correction = artifact.get("mask288_q12_one_sided_seed_correction_audit", {})
    if not isinstance(seed_correction, dict) or not seed_correction:
        raise AssertionError("bridge probe q12 one-sided seed correction audit missing")
    if (
        seed_correction.get("status")
        != "MASK288_Q12_ONE_SIDED_SEED_CORRECTION_FINDS_NEW_RANK2_FAMILIES_PROJECTION_OPEN"
    ):
        raise AssertionError("bridge probe q12 one-sided seed correction status mismatch")
    if seed_correction.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 one-sided seed correction mask mismatch")
    if seed_correction.get("seed_q12_class") != 1:
        raise AssertionError("bridge probe q12 one-sided seed correction seed mismatch")
    if seed_correction.get("coefficient_set") != [-1, 1]:
        raise AssertionError("bridge probe q12 one-sided seed correction coefficients mismatch")
    if seed_correction.get("max_cancellation_terms") != 3:
        raise AssertionError("bridge probe q12 one-sided seed correction depth mismatch")
    if seed_correction.get("seed_correction_term_ids") != [
        "q12_1_1",
        "q12_1_4",
        "q12_1_8",
        "q12_1_9",
        "q12_4_1",
        "q12_6_1",
        "q12_11_1",
    ]:
        raise AssertionError("bridge probe q12 one-sided seed correction term list mismatch")
    correction_attempt = seed_correction.get("correction_attempt_summary", {})
    expected_correction_attempt = {
        "original_q12_row_count": 102,
        "seed_correction_term_count": 7,
        "attempt_count": 1428,
        "target_lost_count": 120,
        "not_scalar6_divisible_count": 1020,
        "scalar6_corrected_row_count": 288,
        "corrected_support_size_histogram": {
            "10": 38,
            "13": 124,
            "14": 12,
            "15": 46,
            "16": 52,
            "18": 16,
        },
        "corrected_image_gcd_histogram": {"2": 274, "6": 8, "18": 6},
        "correction_survivor_histogram": {
            "q12_1_8:-1": 102,
            "q12_1_8:1": 42,
            "q12_6_1:-1": 102,
            "q12_6_1:1": 42,
        },
    }
    for key, expected in expected_correction_attempt.items():
        if correction_attempt.get(key) != expected:
            raise AssertionError(f"bridge probe q12 one-sided correction attempt mismatch: {key}")
    seed_correction_doublets = seed_correction.get("compatible_doublet_summary", {})
    expected_seed_correction_doublets = {
        "compatible_doublet_count": 4628,
        "compatible_doublet_rank_histogram": {"2": 4628},
        "compatible_correction_histogram": {
            "q12_1_8:-1": 128,
            "q12_1_8:1": 128,
            "q12_6_1:-1": 3668,
            "q12_6_1:1": 704,
        },
        "corrected_pair_support_family_count": 27,
        "prior_rank2_support_family_count": 8,
        "new_rank2_support_family_count": 20,
        "combined_rank2_support_family_count": 28,
        "full_packet_target_doublet_family_count": 10,
        "new_rank2_support_family_size_histogram": {
            "13": 1,
            "15": 2,
            "16": 4,
            "17": 5,
            "18": 6,
            "19": 2,
        },
    }
    for key, expected in expected_seed_correction_doublets.items():
        if seed_correction_doublets.get(key) != expected:
            raise AssertionError(f"bridge probe q12 one-sided correction doublet mismatch: {key}")
    new_seed_rows = seed_correction.get("new_rank2_support_family_rows", [])
    if len(new_seed_rows) != 20:
        raise AssertionError("bridge probe q12 one-sided correction new family row count mismatch")
    expected_first_new_seed_row = {
        "left_row_id": "q12_seedcorr_6",
        "right_row_id": "q12_orig_4_13",
        "corrected_base_extra_atom_id": 4,
        "right_extra_atom_id": 4,
        "correction_product_id": "q12_1_8",
        "correction_coefficient": -1,
        "doublet_rank_over_Q": 2,
        "support_family_atom_ids": [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 18, 19],
    }
    expected_last_new_seed_row = {
        "left_row_id": "q12_seedcorr_95",
        "right_row_id": "q12_orig_4_43",
        "corrected_base_extra_atom_id": 4,
        "right_extra_atom_id": 4,
        "correction_product_id": "q12_6_1",
        "correction_coefficient": -1,
        "doublet_rank_over_Q": 2,
        "support_family_atom_ids": [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            14,
            15,
            16,
            17,
            18,
            19,
        ],
    }
    if new_seed_rows[0] != expected_first_new_seed_row:
        raise AssertionError("bridge probe q12 one-sided correction first family mismatch")
    if new_seed_rows[-1] != expected_last_new_seed_row:
        raise AssertionError("bridge probe q12 one-sided correction last family mismatch")
    seed_correction_result = seed_correction.get("result", {})
    expected_seed_correction_true = {
        "one_sided_seed_correction_attempts_materialized",
        "seed_correction_scalar6_survivors_materialized",
        "only_seed_8_corrections_survive_scalar6",
        "one_sided_pairs_are_packet_compatible_rank2",
        "one_sided_pairs_add_new_rank2_support_families",
        "rank2_support_family_count_crosses_ten_family_threshold",
        "corrected_boundary_image_rank_ceiling_is_9",
        "one_sided_seed_correction_finds_new_rank2_families_projection_open",
    }
    for key in expected_seed_correction_true:
        if seed_correction_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 one-sided seed correction check mismatch: {key}")

    seed_rank_summary = seed_correction.get("rank_ceiling_summary", {})
    expected_seed_rank_summary = {
        "rank_method": "exact_fraction_gaussian_elimination_over_Q",
        "original_q12_row_count": 102,
        "scalar6_corrected_row_count": 288,
        "unique_boundary_image_count": 211,
        "original_boundary_image_rank_over_Q": 9,
        "corrected_boundary_image_rank_over_Q": 9,
        "combined_boundary_image_rank_over_Q": 9,
        "rank20_selection_upper_bound": 9,
    }
    for key, expected in expected_seed_rank_summary.items():
        if seed_rank_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q12 one-sided seed rank mismatch: {key}")

    rank20_selection = artifact.get("mask288_q12_corrected_rank20_selection_audit", {})
    if not isinstance(rank20_selection, dict) or not rank20_selection:
        raise AssertionError("bridge probe q12 corrected rank20 selection audit missing")
    if (
        rank20_selection.get("status")
        != "MASK288_Q12_CORRECTED_RANK20_SELECTION_BLOCKED_BY_RANK9_IMAGE_CEILING"
    ):
        raise AssertionError("bridge probe q12 corrected rank20 selection status mismatch")
    if rank20_selection.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 corrected rank20 selection mask mismatch")
    if rank20_selection.get("rank_target") != 20:
        raise AssertionError("bridge probe q12 corrected rank20 target mismatch")
    if rank20_selection.get("support_family_target") != 10:
        raise AssertionError("bridge probe q12 corrected rank20 family target mismatch")
    if rank20_selection.get("available_rank2_support_family_count") != 28:
        raise AssertionError("bridge probe q12 corrected rank20 available family mismatch")
    if rank20_selection.get("rank_ceiling_summary") != expected_seed_rank_summary:
        raise AssertionError("bridge probe q12 corrected rank20 summary mismatch")
    rank20_obstruction = rank20_selection.get("obstruction_summary", {})
    if rank20_obstruction.get("raw_bridge_columns_available") is not False:
        raise AssertionError("bridge probe q12 corrected rank20 raw bridge boundary mismatch")
    if (
        rank20_obstruction.get("why_ten_family_selection_fails")
        != "Every ten-family selection draws its twenty image rows from a row space of rank 9 over Q."
    ):
        raise AssertionError("bridge probe q12 corrected rank20 explanation mismatch")
    rank20_result = rank20_selection.get("result", {})
    expected_rank20_true = {
        "corrected_pool_crosses_ten_family_threshold",
        "boundary_image_rank_computed_exactly",
        "combined_corrected_boundary_image_rank_is_9",
        "rank20_selection_impossible_inside_current_pool",
        "raw_packet_projection_still_absent",
        "corrected_rank20_selection_blocked_by_rank9_image_ceiling",
    }
    for key in expected_rank20_true:
        if rank20_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 corrected rank20 check mismatch: {key}")

    rank_escape = artifact.get("mask288_q12_rank_escape_probe_audit", {})
    if not isinstance(rank_escape, dict) or not rank_escape:
        raise AssertionError("bridge probe q12 rank escape probe audit missing")
    if (
        rank_escape.get("status")
        != "MASK288_Q12_RANK_ESCAPE_PROBE_NONSCALAR_RANK11_STILL_BLOCKED"
    ):
        raise AssertionError("bridge probe q12 rank escape status mismatch")
    if rank_escape.get("selected_mask") != 288:
        raise AssertionError("bridge probe q12 rank escape mask mismatch")
    if rank_escape.get("rank_target") != 20:
        raise AssertionError("bridge probe q12 rank escape target mismatch")

    second_seed_escape = rank_escape.get("second_seed_correction_summary", {})
    expected_second_seed_escape = {
        "first_scalar6_corrected_row_count": 288,
        "second_correction_attempt_count": 4032,
        "second_target_lost_count": 0,
        "second_not_scalar6_divisible_count": 2880,
        "second_scalar6_corrected_row_count": 1152,
        "second_corrected_unique_boundary_image_count": 396,
        "combined_scalar6_unique_boundary_image_count": 554,
        "combined_scalar6_boundary_image_rank_over_Q": 9,
        "second_added_correction_histogram": {
            "q12_1_8:-1": 288,
            "q12_1_8:1": 288,
            "q12_6_1:-1": 288,
            "q12_6_1:1": 288,
        },
    }
    if second_seed_escape != expected_second_seed_escape:
        raise AssertionError("bridge probe q12 rank escape second-seed summary mismatch")

    raw_non_scalar_escape = rank_escape.get("raw_non_scalar_pair_summary", {})
    expected_raw_non_scalar_escape = {
        "max_outside_term_count": 2,
        "raw_attempt_count": 13448,
        "raw_target_lost_count": 8,
        "raw_target_preserved_count": 13440,
        "raw_scalar6_row_count": 2,
        "raw_non_scalar6_row_count": 13438,
        "raw_even_image_count": 13440,
        "raw_odd_image_count": 0,
        "raw_residue_group_count": 473,
        "raw_non_scalar_unique_boundary_image_count": 9134,
        "raw_non_scalar_boundary_image_rank_over_Q": 11,
        "raw_packet_compatible_pair_count": 17610,
        "raw_packet_compatible_pair_rank_histogram": {"2": 17610},
        "raw_packet_compatible_pair_scalar_kind_histogram": {"False,False": 17610},
        "raw_even_support_size_histogram": {
            "10": 204,
            "11": 228,
            "12": 538,
            "13": 2268,
            "14": 1836,
            "15": 1887,
            "16": 3177,
            "17": 1448,
            "18": 864,
            "19": 800,
            "20": 118,
            "8": 72,
        },
    }
    if raw_non_scalar_escape != expected_raw_non_scalar_escape:
        raise AssertionError("bridge probe q12 rank escape raw non-scalar summary mismatch")

    rank11_annihilator = rank_escape.get("rank11_annihilator_summary", {})
    expected_rank11_annihilator = {
        "boundary_coordinate_count": 25,
        "packet_target_coordinate_count": 20,
        "raw_non_scalar_boundary_image_rank_over_Q": 11,
        "annihilator_dimension_over_Q": 14,
        "annihilator_pivot_columns": list(range(11)),
        "annihilator_free_columns": list(range(11, 25)),
        "primitive_constraint_rows_sha256": (
            "ab7096b061a876cfd7dee971ab7aa82cc1a5de3b123a8c95b5c85ab56e4a24d0"
        ),
        "constraint_support_size_histogram": {"12": 12, "2": 2},
        "annihilator_rank_mod_packet_prime_2": 9,
        "annihilator_rank_mod_packet_prime_3": 14,
        "packet_operator_rank_over_Q": 20,
        "packet_snf_rational_constraint_count": 0,
        "packet_constraint_comparison_status": (
            "BLOCKED_MISSING_BOUNDARY_TO_PACKET_PROJECTION"
        ),
        "packet_torsion_primes": [2, 3],
        "outside_q12_rational_generator_lower_bound": 9,
    }
    for key, expected in expected_rank11_annihilator.items():
        if rank11_annihilator.get(key) != expected:
            raise AssertionError(f"bridge probe q12 rank11 annihilator mismatch: {key}")
    if len(rank11_annihilator.get("primitive_constraint_rows", [])) != 14:
        raise AssertionError("bridge probe q12 rank11 constraint row count mismatch")

    rank_escape_obstruction = rank_escape.get("packet_bridge_obstruction_summary", {})
    if rank_escape_obstruction.get("raw_bridge_columns_available") is not False:
        raise AssertionError("bridge probe q12 rank escape raw bridge boundary mismatch")
    rank_escape_result = rank_escape.get("result", {})
    expected_rank_escape_true = {
        "second_seed_correction_still_rank9",
        "bounded_raw_non_scalar_rows_materialized",
        "bounded_raw_non_scalar_pairs_are_rank2",
        "bounded_raw_non_scalar_rank_escapes_to_11",
        "bounded_raw_non_scalar_rank_still_short_of_20",
        "raw_packet_projection_still_absent",
        "rank11_boundary_annihilator_dimension_is_14",
        "packet_snf_has_full_target_rank",
        "q12_rank11_gap_requires_nine_external_generators",
        "annihilator_packet_comparison_blocked_by_missing_projection",
        "rank_escape_probe_finds_nonscalar_rank11_still_blocked",
    }
    for key in expected_rank_escape_true:
        if rank_escape_result.get(key) is not True:
            raise AssertionError(f"bridge probe q12 rank escape check mismatch: {key}")

    ingress_projection = artifact.get("ingress_boundary_packet_projection_inventory_audit", {})
    if not isinstance(ingress_projection, dict) or not ingress_projection:
        raise AssertionError("bridge probe ingress projection inventory audit missing")
    if (
        ingress_projection.get("status")
        != "INGRESS_BOUNDARY_TO_LOOP_PRESENT_PACKET_PROJECTION_MISSING"
    ):
        raise AssertionError("bridge probe ingress projection inventory status mismatch")

    boundary_to_loop = ingress_projection.get("boundary_to_loop_summary", {})
    expected_boundary_to_loop = {
        "status": "ALL_RESIDUE_BOUNDARY_TO_LOOP_VECTORS_MATERIALIZED_PASS",
        "certificate_sha256": (
            "73553f0b77bf91647729fa28472c62b50d846ab6a7f916eb5d1ddecb96045926"
        ),
        "directed_pair_count": 30,
        "primitive_cycle_count": 11,
        "residue_mask_count": 2048,
        "gamma8_lambda_support": 193,
        "gamma8_lambda_sum": 53952,
    }
    if boundary_to_loop != expected_boundary_to_loop:
        raise AssertionError("bridge probe ingress boundary-to-loop summary mismatch")

    height_action = ingress_projection.get("height_action_return_summary", {})
    expected_projection_sanity = {
        "closed_loop_quotient_dimension": 297,
        "projection_kernel_dimension": 44224,
        "projection_section_identity": True,
        "tube_pair_basis_total": 44521,
    }
    expected_height_action = {
        "status": "ALL_RESIDUE_HEIGHT_ACTION_RETURN_RECONSTRUCTED_PASS",
        "certificate_sha256": (
            "1582dc9ad41a1219ff7c7c9d23ba80bf01096419f03ca21efe4db28f2752807c"
        ),
        "nonzero_residue_class_count": 2047,
        "gamma8_height_action": 374784,
        "projection_section_sanity": expected_projection_sanity,
    }
    if height_action != expected_height_action:
        raise AssertionError("bridge probe ingress height-action summary mismatch")

    lambda_shadow = ingress_projection.get("lambda_hc_public_shadow_summary", {})
    expected_lambda_shadow = {
        "status": "LAMBDA_HC_ACT_INVARIANCE_CERTIFIED",
        "certificate_sha256": (
            "cfaa611486bdda499229d2f24c55e6394e4b31441aa6d9f783ecac331800e0d4"
        ),
        "row_count": 2048,
        "q12_shadow_nonzero_histogram": {"0": 2048},
        "q42_shadow_nonzero_histogram": {"0": 2048},
        "support_sector_histogram": {"33": 2048},
    }
    for key, expected in expected_lambda_shadow.items():
        if lambda_shadow.get(key) != expected:
            raise AssertionError(f"bridge probe ingress lambda shadow mismatch: {key}")
    if lambda_shadow.get("gamma8_mask_row", {}).get("corrected_support") != "237":
        raise AssertionError("bridge probe ingress gamma8 corrected support mismatch")

    intertwining = ingress_projection.get("height_coherent_intertwining_summary", {})
    if (
        intertwining.get("status")
        != "HEIGHT_COHERENT_ACTION_RETURN_INTERTWINING_TARGET_LOCKED"
    ):
        raise AssertionError("bridge probe ingress intertwining status mismatch")
    if (
        intertwining.get("certificate_sha256")
        != "6dac92ebd774ded452b2b968d6edcdeb413d6abb2b03a25bd7f12860004c3663"
    ):
        raise AssertionError("bridge probe ingress intertwining hash mismatch")

    packet_gap = ingress_projection.get("packet_restriction_gap_summary", {})
    expected_packet_gap = {
        "status": "D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_CERTIFIED",
        "constructed_restriction": "reduced_scattering_automaton_mask_to_full_packet_projection",
        "constructed_projection_packet_count": 20,
        "constructed_projection_mode_count": 40,
        "missing_bridge_count": 3,
        "missing_bridge_candidates": [
            "A985_relation_basis_to_full_packets",
            "screen0_tube_element_to_full_packets",
            "q42_q12_tensor_to_full_packets",
        ],
        "a985_relation_restriction_constructed": False,
        "q42_q12_restriction_constructed": False,
    }
    if packet_gap != expected_packet_gap:
        raise AssertionError("bridge probe ingress packet gap summary mismatch")

    projection_gap = ingress_projection.get("rank11_projection_gap_summary", {})
    expected_projection_gap = {
        "boundary_coordinate_count": 25,
        "packet_target_coordinate_count": 20,
        "annihilator_dimension_over_Q": 14,
        "outside_q12_rational_generator_lower_bound": 9,
        "packet_constraint_comparison_status": (
            "BLOCKED_MISSING_BOUNDARY_TO_PACKET_PROJECTION"
        ),
    }
    if projection_gap != expected_projection_gap:
        raise AssertionError("bridge probe ingress rank11 projection gap mismatch")

    ingress_projection_result = ingress_projection.get("result", {})
    expected_ingress_projection_true = {
        "ingress_boundary_to_loop_vectors_materialized",
        "ingress_height_action_return_reconstructed",
        "ingress_lambda_hc_has_zero_public_q12_q42_shadow",
        "packet_restriction_names_q12_a985_bridge_missing",
        "rank11_annihilator_still_waits_for_25_to_20_projection",
        "ingress_projection_inventory_confirms_packet_bridge_gap",
    }
    for key in expected_ingress_projection_true:
        if ingress_projection_result.get(key) is not True:
            raise AssertionError(f"bridge probe ingress projection check mismatch: {key}")

    projection_candidate = artifact.get("boundary_packet_projection_candidate_audit", {})
    if not isinstance(projection_candidate, dict) or not projection_candidate:
        raise AssertionError("bridge probe boundary packet projection candidate audit missing")
    if (
        projection_candidate.get("status")
        != "BOUNDARY_PACKET_NATURAL_25_TO_20_PROJECTION_REJECTED_BY_PACKET_SNF"
    ):
        raise AssertionError("bridge probe boundary packet candidate status mismatch")

    candidate_summary = projection_candidate.get("candidate_summary", {})
    expected_candidate_summary = {
        "visible_candidate": "Loop_297_step_atom_mode_incidence_count_columns",
        "candidate_semantics": (
            "for each step atom and full-exposure packet, count how many of the "
            "packet's two mode masks contain that atom"
        ),
        "loop297_step_atom_count": 25,
        "full_exposure_packet_count": 20,
        "tested_column_count": 25,
        "target_vector_length_set": [20],
        "columns_passing_packet_snf_image": [],
        "columns_failing_packet_snf_image": list(range(25)),
        "natural_column_outcome": "all_visible_loop_step_columns_fail_packet_snf_image",
    }
    if candidate_summary != expected_candidate_summary:
        raise AssertionError("bridge probe boundary packet candidate summary mismatch")

    failure_summary = projection_candidate.get("failure_summary", {})
    expected_failure_summary = {
        "failed_blocks_per_column_histogram": {"10": 25},
        "failure_reason_histogram": {
            "u_not_0_mod_2|u_plus_v_not_0_mod_6": 12,
            "u_not_0_mod_2|v_not_0_mod_2|u_plus_v_not_0_mod_6": 2,
            "u_plus_v_not_0_mod_6": 236,
        },
        "component_pair_value_histogram": {"1|1": 2, "1|2": 12, "2|2": 236},
    }
    if failure_summary != expected_failure_summary:
        raise AssertionError("bridge probe boundary packet candidate failure mismatch")

    candidate_rank_context = projection_candidate.get("rank11_projection_context", {})
    expected_candidate_rank_context = {
        "boundary_coordinate_count": 25,
        "packet_target_coordinate_count": 20,
        "annihilator_dimension_over_Q": 14,
        "outside_q12_rational_generator_lower_bound": 9,
    }
    if candidate_rank_context != expected_candidate_rank_context:
        raise AssertionError("bridge probe boundary packet candidate rank context mismatch")

    projection_candidate_result = projection_candidate.get("result", {})
    expected_projection_candidate_true = {
        "natural_loop_step_projection_candidate_materialized",
        "natural_projection_has_25_to_20_shape",
        "natural_projection_columns_all_fail_packet_snf",
        "q12_annihilator_pushforward_blocked_for_natural_projection",
        "natural_25_to_20_projection_candidate_rejected",
    }
    for key in expected_projection_candidate_true:
        if projection_candidate_result.get(key) is not True:
            raise AssertionError(f"bridge probe boundary packet candidate check mismatch: {key}")

    signed_step_search = artifact.get("signed_step_column_packet_search_audit", {})
    if not isinstance(signed_step_search, dict) or not signed_step_search:
        raise AssertionError("bridge probe signed step-column search audit missing")
    if (
        signed_step_search.get("status")
        != "BOUNDARY_PACKET_SIGNED_STEP_COLUMN_SEARCH_FINDS_EXTERNAL_RANK2_ROWS"
    ):
        raise AssertionError("bridge probe signed step-column search status mismatch")
    signed_search_summary = signed_step_search.get("search_summary", {})
    expected_signed_search_core = {
        "coefficient_set": [-2, -1, 1, 2],
        "max_support": 3,
        "attempt_count": 152100,
        "compatible_row_count": 30186,
        "compatible_support_size_histogram": {"1": 2, "2": 1848, "3": 28336},
        "compatible_nonzero_target_count": 20022,
        "compatible_zero_target_count": 10164,
        "outside_q12_annihilator_count": 30186,
        "unique_target_vector_count": 11,
        "unique_target_vector_rank_over_Q": 2,
        "unique_coefficient_vector_count": 30186,
        "unique_coefficient_vector_rank_over_Q": 23,
        "minimal_support_size": 1,
        "minimal_support_row_count": 2,
    }
    for key, expected in expected_signed_search_core.items():
        if signed_search_summary.get(key) != expected:
            raise AssertionError(f"bridge probe signed step-column search mismatch: {key}")
    expected_minimal_rows = [
        {
            "step_atom_ids": [16],
            "coefficients": [-2],
            "target_vector": [-2, -4] * 10,
            "annihilator_values": [0, 0, 0, 0, 0, 74, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        {
            "step_atom_ids": [16],
            "coefficients": [2],
            "target_vector": [2, 4] * 10,
            "annihilator_values": [0, 0, 0, 0, 0, -74, 0, 0, 0, 0, 0, 0, 0, 0],
        },
    ]
    if signed_search_summary.get("minimal_rows") != expected_minimal_rows:
        raise AssertionError("bridge probe signed step-column minimal rows mismatch")
    minimal_step_rows = signed_search_summary.get("minimal_step_incidence_rows", [])
    if len(minimal_step_rows) != 1 or minimal_step_rows[0].get("step_atom_id") != 16:
        raise AssertionError("bridge probe signed step-column minimal step id mismatch")
    if minimal_step_rows[0].get("directed_channel_swaps") != ["B+->S+"]:
        raise AssertionError("bridge probe signed step-column minimal swap mismatch")
    if minimal_step_rows[0].get("signed_vertex_support") != [
        {"coefficient": -2, "public_atom_id": 13},
        {"coefficient": 2, "public_atom_id": 19},
    ]:
        raise AssertionError("bridge probe signed step-column minimal support mismatch")

    signed_step_result = signed_step_search.get("result", {})
    expected_signed_step_true = {
        "bounded_signed_step_column_search_materialized",
        "scalar2_step16_minimal_packet_snf_row_found",
        "all_compatible_rows_escape_q12_rank11_annihilator",
        "compatible_target_span_still_rank2",
        "signed_step_column_search_finds_external_but_rank_limited_rows",
    }
    for key in expected_signed_step_true:
        if signed_step_result.get(key) is not True:
            raise AssertionError(f"bridge probe signed step-column check mismatch: {key}")

    support4_step = artifact.get("support4_signed_step_column_span_audit", {})
    if not isinstance(support4_step, dict) or not support4_step:
        raise AssertionError("bridge probe support4 signed step-column audit missing")
    if (
        support4_step.get("status")
        != "BOUNDARY_PACKET_SUPPORT4_SIGNED_STEP_COLUMNS_STILL_RANK2"
    ):
        raise AssertionError("bridge probe support4 signed step-column status mismatch")
    support4_summary = support4_step.get("support4_summary", {})
    expected_support4_core = {
        "method": "column_type_combinatorial_count",
        "coefficient_set": [-2, -1, 1, 2],
        "column_type_count": 4,
        "column_type_groups": [
            [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 24],
            [3],
            [16],
            [23],
        ],
        "virtual_attempt_count_by_support": {
            "1": 100,
            "2": 4800,
            "3": 147200,
            "4": 3238400,
        },
        "virtual_attempt_count_total_support_le_4": 3390500,
        "compatible_row_count_by_support": {
            "1": 2,
            "2": 1848,
            "3": 28336,
            "4": 751520,
        },
        "compatible_row_count_total_support_le_4": 781706,
        "compatible_nonzero_target_count_by_support": {
            "1": 2,
            "2": 924,
            "3": 19096,
            "4": 488180,
        },
        "unique_target_vector_count_by_support": {
            "1": 2,
            "2": 3,
            "3": 11,
            "4": 15,
        },
        "unique_target_vector_count_support_le_3": 11,
        "unique_target_vector_count_support_le_4": 15,
        "new_unique_target_vector_count_at_support4": 4,
        "unique_target_vector_rank_over_Q_support_le_4": 2,
        "type_sum_witness_count": 31,
        "type_sum_rows_sha256": (
            "5a9af84c44f615952a00c6b201907824b31bad2ae8a778f2097286213cecc044"
        ),
        "q12_boundary_rank_before_external_step16": 11,
        "q12_plus_step16_boundary_rank_lower_bound": 12,
        "minimal_external_step_annihilator_values": [
            0,
            0,
            0,
            0,
            0,
            -74,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
    }
    for key, expected in expected_support4_core.items():
        if support4_summary.get(key) != expected:
            raise AssertionError(f"bridge probe support4 signed step-column mismatch: {key}")
    if len(support4_summary.get("unique_target_vectors_support_le_4", [])) != 15:
        raise AssertionError("bridge probe support4 unique target vector count mismatch")

    support4_result = support4_step.get("result", {})
    expected_support4_true = {
        "support4_combinatorial_count_agrees_with_support_le_3_search",
        "support4_adds_many_packet_snf_compatible_rows",
        "support4_adds_only_four_new_target_vectors",
        "support_le_4_packet_target_span_remains_rank2",
        "step16_external_row_raises_boundary_rank_lower_bound_to_12",
        "support4_signed_step_columns_still_rank2",
    }
    for key in expected_support4_true:
        if support4_result.get(key) is not True:
            raise AssertionError(f"bridge probe support4 signed step-column check mismatch: {key}")

    full_lattice = artifact.get("full_step_column_congruence_lattice_audit", {})
    if not isinstance(full_lattice, dict) or not full_lattice:
        raise AssertionError("bridge probe full step-column lattice audit missing")
    if (
        full_lattice.get("status")
        != "BOUNDARY_PACKET_FULL_STEP_COLUMN_CONGRUENCE_LATTICE_RANK4_STILL_SHORT"
    ):
        raise AssertionError("bridge probe full step-column lattice status mismatch")
    full_lattice_summary = full_lattice.get("full_lattice_summary", {})
    expected_full_lattice_core = {
        "method": "mod6_residue_classes_plus_integer_type_sum_basis",
        "column_type_count": 4,
        "column_type_groups": [
            [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 24],
            [3],
            [16],
            [23],
        ],
        "compatible_residue_class_count_mod6": 6,
        "compatible_residue_classes_mod6": [
            [0, 0, 0, 0],
            [0, 0, 2, 0],
            [0, 0, 4, 0],
            [3, 0, 0, 0],
            [3, 0, 2, 0],
            [3, 0, 4, 0],
        ],
        "integer_type_sum_lattice_basis": [
            [3, 0, 0, 0],
            [0, 6, 0, 0],
            [0, 0, 2, 0],
            [0, 0, 0, 6],
        ],
        "integer_type_sum_lattice_basis_determinant": 216,
        "basis_rows_sha256": (
            "4b7ed890cb572e56b713dd6fbb3456ad561a678dd18788fad6549b0e9d1df2ee"
        ),
        "basis_target_rank_over_Q": 4,
        "basis_rows_passing_packet_snf_count": 4,
        "basis_rows_outside_q12_annihilator_count": 4,
        "basis_annihilator_evaluation_rank_over_Q": 4,
        "support_le_4_target_rank_over_Q": 2,
        "full_lattice_target_rank_gain_over_support_le_4": 2,
        "q12_boundary_rank_before_external_lattice": 11,
        "q12_plus_full_type_lattice_boundary_rank_lower_bound": 15,
        "packet_target_rank": 20,
        "packet_target_rank_shortfall_after_full_type_lattice": 16,
    }
    for key, expected in expected_full_lattice_core.items():
        if full_lattice_summary.get(key) != expected:
            raise AssertionError(f"bridge probe full step-column lattice mismatch: {key}")
    if len(full_lattice_summary.get("basis_rows", [])) != 4:
        raise AssertionError("bridge probe full step-column lattice basis row count mismatch")

    full_lattice_result = full_lattice.get("result", {})
    expected_full_lattice_true = {
        "full_congruence_residue_classes_solved",
        "integer_type_sum_lattice_basis_materialized",
        "full_type_lattice_packet_target_rank_is_4",
        "full_type_lattice_gains_two_target_ranks_over_support4",
        "full_type_lattice_adds_four_q12_external_boundary_directions",
        "natural_step_column_type_lattice_still_short_of_packet_rank20",
        "full_step_column_congruence_lattice_rank4_still_short",
    }
    for key in expected_full_lattice_true:
        if full_lattice_result.get(key) is not True:
            raise AssertionError(f"bridge probe full step-column lattice check mismatch: {key}")

    q42_filter = artifact.get("q42_q12_quotient_adjusted_packet_filter_audit", {})
    if not isinstance(q42_filter, dict) or not q42_filter:
        raise AssertionError("bridge probe q42/q12 quotient filter audit missing")
    if q42_filter.get("status") != "Q42_Q12_QUOTIENT_ADJUSTED_PACKET_FILTER_STILL_RANK3":
        raise AssertionError("bridge probe q42/q12 quotient filter status mismatch")
    q42_summary = q42_filter.get("quotient_adjusted_summary", {})
    expected_q42_filter_core = {
        "method": "q42_product_tensor_pushdown_to_q12_public_readout_then_natural_packet_filter",
        "q42_class_count": 42,
        "q12_class_count": 12,
        "q42_to_q12": [
            0,
            0,
            1,
            1,
            2,
            2,
            3,
            3,
            4,
            4,
            5,
            5,
            3,
            6,
            6,
            7,
            7,
            3,
            6,
            6,
            7,
            7,
            8,
            8,
            4,
            9,
            9,
            8,
            8,
            4,
            9,
            9,
            10,
            10,
            11,
            11,
            5,
            10,
            10,
            11,
            11,
            5,
        ],
        "q42_fiber_size_histogram": {"2": 3, "4": 9},
        "q42_refinement_rows_sha256": (
            "2ca41daf6fbbaf7112234ba21399c2d2c33fb935e361d53e660b7b6c0c54ed1a"
        ),
        "q42_tensor_pushdown_equals_q12_tensor": True,
        "q42_nonzero_product_pair_count": 294,
        "q42_tensor_row_rank_over_Q": 42,
        "q42_pushed_q12_coefficient_rank_over_Q": 12,
        "q42_public_h6_readout_rank_over_Q": 12,
        "q42_hidden_rank_lost_under_q12_public_readout": 30,
        "q42_scalar6_public_row_count": 216,
        "q42_scalar6_public_rank_over_Q": 12,
        "q42_scalar6_boundary_rank_over_Q": 11,
        "q42_scalar6_boundary_compatible_pair_count": 7337,
        "q42_scalar6_boundary_compatible_pair_rank_histogram": {
            "1": 1013,
            "2": 6324,
        },
        "q42_scalar6_natural_target_rank_over_Q": 3,
        "q42_scalar6_natural_target_passing_row_count": 120,
        "q42_scalar6_natural_target_passing_rank_over_Q": 3,
        "full_type_lattice_target_rank_over_Q": 4,
        "q42_scalar6_natural_target_with_type_lattice_rank_over_Q": 4,
        "q42_scalar6_natural_pass_with_type_lattice_rank_over_Q": 4,
        "packet_target_rank": 20,
        "q42_natural_pass_packet_rank_shortfall": 17,
        "q42_scalar6_natural_pass_rows_sha256": (
            "8f54f95fd7ca9dc30f656ef29564896b6fcd544d3b86b41d4fb26ebda97fc710"
        ),
    }
    for key, expected in expected_q42_filter_core.items():
        if q42_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q42/q12 quotient filter mismatch: {key}")
    expected_q42_examples = [
        {
            "q42_pair": [0, 12],
            "pushed_q12_coefficients": [[3, 72]],
            "natural_packet_target_vector": [
                -12,
                0,
                -12,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ],
        },
        {
            "q42_pair": [0, 14],
            "pushed_q12_coefficients": [[6, 144]],
            "natural_packet_target_vector": [
                72,
                0,
                72,
                0,
                0,
                0,
                -24,
                -24,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                -24,
                -24,
                0,
                0,
            ],
        },
        {
            "q42_pair": [0, 15],
            "pushed_q12_coefficients": [[7, 180]],
            "natural_packet_target_vector": [
                -30,
                0,
                -30,
                0,
                60,
                0,
                30,
                -30,
                60,
                0,
                60,
                0,
                60,
                0,
                60,
                0,
                30,
                -30,
                60,
                0,
            ],
        },
    ]
    if q42_summary.get("q42_scalar6_natural_pass_example_rows") != expected_q42_examples:
        raise AssertionError("bridge probe q42/q12 quotient filter example rows mismatch")

    q42_result = q42_filter.get("result", {})
    expected_q42_true = {
        "q42_classes_refine_q12_classes",
        "q42_product_tensor_pushdown_matches_q12_tensor",
        "q42_hidden_rank_collapses_under_q12_public_readout",
        "q42_scalar6_rows_materialize_boundary_rank11",
        "q42_scalar6_boundary_pairs_are_plentiful_but_not_packet_basis",
        "q42_natural_packet_filter_remains_inside_type_lattice",
        "q42_quotient_adjusted_filter_still_short_of_rank20",
        "q42_q12_quotient_adjusted_packet_filter_still_rank_limited",
    }
    for key in expected_q42_true:
        if q42_result.get(key) is not True:
            raise AssertionError(f"bridge probe q42/q12 quotient filter check mismatch: {key}")

    hidden_capacity = artifact.get("hidden_q42_a985_matrix_unit_capacity_audit", {})
    if not isinstance(hidden_capacity, dict) or not hidden_capacity:
        raise AssertionError("bridge probe hidden q42/A985 matrix-unit capacity audit missing")
    if (
        hidden_capacity.get("status")
        != "HIDDEN_Q42_A985_MATRIX_UNIT_SHADOW_RANK42_REQUIRES_PACKET_KERNEL_CHOICE"
    ):
        raise AssertionError("bridge probe hidden q42/A985 capacity status mismatch")
    hidden_summary = hidden_capacity.get("hidden_capacity_summary", {})
    expected_hidden_capacity_core = {
        "method": "q42_a985_matrix_unit_shadow_rank_sandwich_against_packet_capacity",
        "field_prime": 1000003,
        "q42_class_count": 42,
        "q12_class_count": 12,
        "matrix_unit_shape": [985, 985],
        "matrix_unit_report_status": (
            "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        ),
        "matrix_unit_report_all_checks_pass": True,
        "sector_character_report_status": (
            "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
        ),
        "sector_character_report_all_checks_pass": True,
        "full_packet_matrix_lift_status": "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED",
        "full_packet_matrix_lift_all_checks_pass": True,
        "q42_matrix_unit_aggregate_rank_mod_p": 42,
        "q12_matrix_unit_aggregate_rank_mod_p": 12,
        "q42_matrix_unit_representative_rank_mod_p": 42,
        "q12_matrix_unit_representative_rank_mod_p": 12,
        "q42_matrix_unit_aggregate_unique_row_count": 42,
        "q12_matrix_unit_aggregate_unique_row_count": 12,
        "q42_matrix_unit_aggregate_rows_sha256": (
            "47ec8c8c6cf120ea1192bd94da316a4b0d8af9069c4247c02e89278c46f780c5"
        ),
        "q12_matrix_unit_aggregate_rows_sha256": (
            "bf1e906089582b46573f6ba08194754dc18847733211a39deaacd2ea17ffa93f"
        ),
        "q42_pushdown_matrix_unit_equals_q12_aggregate": True,
        "q42_character_aggregate_rank_over_Q": 7,
        "q42_character_representative_rank_over_Q": 12,
        "q12_character_aggregate_rank_over_Q": 4,
        "q12_character_representative_rank_over_Q": 6,
        "q42_character_aggregate_rows_sha256": (
            "efad03beb8a53aa92e46847e9d84341b6db83c195504f5327032234da82bd535"
        ),
        "q42_character_representative_rows_sha256": (
            "f803435c8ca3e345b0263fb0ec4cf559da0bad477718bc2c5db27e02cda551b1"
        ),
        "public_q42_to_q12_packet_filter_rank": 3,
        "packet_target_dimension": 20,
        "block_lift_image_dimension_bound": 40,
        "a985_dimension": 985,
        "a985_to_packet_operator_map_present": False,
        "q42_matrix_unit_rank_excess_over_packet_target": 22,
        "q42_matrix_unit_rank_excess_over_block_lift": 2,
        "q42_character_representative_shortfall_to_packet_target": 8,
        "q42_character_aggregate_shortfall_to_packet_target": 13,
    }
    for key, expected in expected_hidden_capacity_core.items():
        if hidden_summary.get(key) != expected:
            raise AssertionError(f"bridge probe hidden q42/A985 capacity mismatch: {key}")

    hidden_result = hidden_capacity.get("result", {})
    expected_hidden_true = {
        "certified_a985_matrix_unit_shadow_available",
        "q42_matrix_unit_shadow_has_full_q42_rank",
        "q42_matrix_unit_shadow_pushes_down_to_q12",
        "central_character_q42_shadow_too_small_for_packet_rank20",
        "matrix_unit_q42_shadow_exceeds_packet_capacity",
        "no_certified_a985_to_packet_operator_map_yet",
        "hidden_q42_a985_matrix_unit_capacity_requires_kernel_choice",
    }
    for key in expected_hidden_true:
        if hidden_result.get(key) is not True:
            raise AssertionError(f"bridge probe hidden q42/A985 capacity check mismatch: {key}")

    q42_slice = artifact.get("q42_tensor_rank20_slice_quotient_audit", {})
    if not isinstance(q42_slice, dict) or not q42_slice:
        raise AssertionError("bridge probe q42 tensor rank20 slice audit missing")
    if (
        q42_slice.get("status")
        != "Q42_TENSOR_LEFT_SLICE_RANK20_QUOTIENT_FOUND_PACKET_LABEL_OPEN"
    ):
        raise AssertionError("bridge probe q42 tensor rank20 slice status mismatch")
    slice_summary = q42_slice.get("rank20_slice_summary", {})
    expected_slice_core = {
        "method": "bounded_q42_tensor_left_multiplication_slice_rank_search",
        "max_left_slice_combo_size": 3,
        "q42_class_count": 42,
        "q12_class_count": 12,
        "combination_count_by_size": {
            "1": 42,
            "2": 861,
            "3": 11480,
        },
        "rank_histogram_by_combo_size": {
            "1": {"6": 30, "7": 12},
            "2": {"6": 60, "7": 66, "12": 375, "13": 300, "14": 60},
            "3": {
                "6": 60,
                "7": 150,
                "12": 1500,
                "13": 2250,
                "14": 660,
                "18": 2500,
                "19": 3000,
                "20": 1200,
                "21": 160,
            },
        },
        "exact_rank20_combo_count": 1200,
        "first_exact_rank20_left_classes": [0, 1, 22],
        "first_exact_rank20_left_q12_classes": [0, 0, 8],
        "first_exact_rank20_row_count": 126,
        "first_exact_rank20_nonzero_row_count": 21,
        "first_exact_rank20_unique_nonzero_row_count": 21,
        "first_exact_rank20_output_rank_over_Q": 20,
        "first_exact_rank20_kernel_dimension_in_q42_class_space": 22,
        "first_exact_rank20_q12_pushdown_rank_over_Q": 8,
        "first_exact_rank20_rows_sha256": (
            "27655b010d25fcf7f5e5224c95663d3f3701337d51c9cebdd2db572596e9a3db"
        ),
        "first_exact_rank20_q12_pushdown_rows_sha256": (
            "c8ef8dcaf133e354d1d11546d6ebdff5a1e1f34e84ba02e6163736fd17d18811"
        ),
        "first_at_least_rank20_left_classes": [0, 1, 2],
        "first_at_least_rank20_output_rank_over_Q": 21,
        "packet_target_dimension": 20,
        "hidden_matrix_unit_rank_excess_over_packet_target": 22,
        "a985_to_packet_operator_map_present": False,
    }
    for key, expected in expected_slice_core.items():
        if slice_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q42 tensor rank20 slice mismatch: {key}")

    slice_result = q42_slice.get("result", {})
    expected_slice_true = {
        "single_and_pair_left_slices_never_reach_packet_rank20",
        "rank20_left_slice_triples_exist",
        "first_rank20_slice_has_packet_kernel_dimension_22",
        "rank20_slice_is_hidden_not_public_q12",
        "rank20_slice_packet_label_still_open",
        "q42_tensor_left_slice_rank20_quotient_found_packet_label_open",
    }
    for key in expected_slice_true:
        if slice_result.get(key) is not True:
            raise AssertionError(f"bridge probe q42 tensor rank20 slice check mismatch: {key}")

    q42_packet_label = artifact.get("q42_rank20_packet_spectral_label_filter_audit", {})
    if not isinstance(q42_packet_label, dict) or not q42_packet_label:
        raise AssertionError("bridge probe q42 rank20 packet label filter audit missing")
    if (
        q42_packet_label.get("status")
        != "Q42_RANK20_PACKET_SPECTRAL_LABEL_FILTER_CARDINALITY_ONLY"
    ):
        raise AssertionError("bridge probe q42 rank20 packet label filter status mismatch")
    label_summary = q42_packet_label.get("packet_label_filter_summary", {})
    expected_label_core = {
        "method": "packet_spectral_charge_filter_for_q42_rank20_slice_labels",
        "packet_spectral_report_status": (
            "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        ),
        "packet_spectral_report_all_checks_pass": True,
        "packet_graph_report_status": (
            "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        ),
        "packet_graph_report_all_checks_pass": True,
        "q42_rank20_left_classes": [0, 1, 22],
        "q42_rank20_active_q42_class_count": 21,
        "q42_rank20_active_q42_classes": [
            0,
            1,
            2,
            6,
            7,
            8,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
        "q42_rank20_active_q12_classes": [
            0,
            0,
            1,
            3,
            3,
            4,
            3,
            6,
            6,
            7,
            7,
            3,
            6,
            6,
            7,
            7,
            8,
            8,
            4,
            9,
            9,
        ],
        "q42_rank20_active_relation_rank_over_Q": 20,
        "q42_rank20_active_relation_dimension": 1,
        "q42_rank20_active_relation_support": [[2, 13], [8, -1]],
        "q42_rank20_rank_preserving_drop_classes": [2, 8],
        "canonical_drop_q42_class": 8,
        "canonical_basis_q42_classes": [
            0,
            1,
            2,
            6,
            7,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
        "canonical_basis_q42_class_count": 20,
        "canonical_basis_q12_class_histogram": {
            "0": 2,
            "1": 1,
            "3": 4,
            "4": 1,
            "6": 4,
            "7": 4,
            "8": 2,
            "9": 2,
        },
        "full_exposure_packet_count": 20,
        "full_exposure_packet_ids": [
            174,
            175,
            190,
            191,
            238,
            239,
            246,
            247,
            254,
            255,
            430,
            431,
            446,
            447,
            494,
            495,
            502,
            503,
            510,
            511,
        ],
        "full_exposure_fine_spectral_charge_key_count": 20,
        "full_exposure_fine_spectral_charge_keys_sha256": (
            "f736488dfaaea9ec9f86d3d6aaa666055df78872b9e0e6032f015cedb4d443fa"
        ),
        "full_packet_doublet_count": 10,
        "full_packet_doublet_pair_filter_key_count": 10,
        "full_packet_doublet_rows_sha256": (
            "98e8cbe40c7491412a7b3239b200721df0d99154013182ca2444140bb46f8f32"
        ),
        "full_packet_gamma8_mode_count_histogram": {"0": 10, "2": 10},
        "full_packet_sector26_balanced_histogram": {"False": 10, "True": 10},
        "provisional_label_status": (
            "NONCANONICAL_CARDINALITY_AND_FINE_KEY_ALIGNMENT_ONLY"
        ),
        "provisional_label_rows_sha256": (
            "196088a1d4f3f917adb63571a9f6b9101260996ab43f29f99ee25ac3442598b8"
        ),
        "q42_rank20_q12_pushdown_rank_over_Q": 8,
        "a985_to_packet_operator_map_present": False,
    }
    for key, expected in expected_label_core.items():
        if label_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q42 rank20 packet label mismatch: {key}")

    expected_label_basis_options = [
        {
            "drop_q42_class": 2,
            "basis_rank_over_Q": 20,
            "basis_class_count": 20,
            "basis_q12_class_histogram": {
                "0": 2,
                "3": 4,
                "4": 2,
                "6": 4,
                "7": 4,
                "8": 2,
                "9": 2,
            },
            "basis_classes": [
                0,
                1,
                6,
                7,
                8,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
            ],
        },
        {
            "drop_q42_class": 8,
            "basis_rank_over_Q": 20,
            "basis_class_count": 20,
            "basis_q12_class_histogram": {
                "0": 2,
                "1": 1,
                "3": 4,
                "4": 1,
                "6": 4,
                "7": 4,
                "8": 2,
                "9": 2,
            },
            "basis_classes": [
                0,
                1,
                2,
                6,
                7,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
            ],
        },
    ]
    if label_summary.get("q42_rank20_basis_option_rows") != expected_label_basis_options:
        raise AssertionError("bridge probe q42 rank20 packet label basis option mismatch")

    label_result = q42_packet_label.get("result", {})
    expected_label_true = {
        "packet_spectral_filter_certified",
        "packet_fine_spectral_keys_label_all_twenty_full_exposure_packets",
        "packet_doublet_filter_keys_label_all_ten_doublets",
        "q42_rank20_active_support_collapses_21_to_20",
        "q42_packet_label_cardinality_filter_passes",
        "spectral_filter_not_enough_to_certify_hidden_packet_label",
        "q42_rank20_packet_spectral_label_filter_cardinality_only",
    }
    for key in expected_label_true:
        if label_result.get(key) is not True:
            raise AssertionError(f"bridge probe q42 rank20 packet label check mismatch: {key}")

    saturation = artifact.get("q42_rank20_integral_saturation_tie_break_audit", {})
    if not isinstance(saturation, dict) or not saturation:
        raise AssertionError("bridge probe q42 integral saturation tie-break audit missing")
    if (
        saturation.get("status")
        != "Q42_RANK20_INTEGRAL_SATURATION_SELECTS_DROP8_PACKET_MAP_OPEN"
    ):
        raise AssertionError("bridge probe q42 integral saturation tie-break status mismatch")
    saturation_summary = saturation.get("integral_saturation_summary", {})
    expected_saturation_core = {
        "method": "primitive_relation_integral_saturation_for_q42_rank20_basis_choice",
        "q42_rank20_left_classes": [0, 1, 22],
        "q42_rank20_active_q42_classes": [
            0,
            1,
            2,
            6,
            7,
            8,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
        "q42_rank20_active_relation_support": [[2, 13], [8, -1]],
        "q42_column_relation": "q42_8 = 13*q42_2",
        "q42_column_relation_residual_abs_sum": 0,
        "q42_2_column_stats": {
            "nonzero_count": 1,
            "sum": 384,
            "abs_sum": 384,
            "square_sum": 147456,
        },
        "q42_8_column_stats": {
            "nonzero_count": 1,
            "sum": 4992,
            "abs_sum": 4992,
            "square_sum": 24920064,
        },
        "q42_8_over_q42_2_column_abs_sum_ratio": 13,
        "rank_preserving_drop_classes": [2, 8],
        "selected_drop_q42_class_by_integral_saturation": 8,
        "rejected_drop_q42_class_by_integral_saturation": 2,
        "selected_basis_q42_classes_by_integral_saturation": [
            0,
            1,
            2,
            6,
            7,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
        "rejected_basis_index_defect": 13,
        "explicit_q42_to_packet_map_present": False,
    }
    for key, expected in expected_saturation_core.items():
        if saturation_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q42 integral saturation mismatch: {key}")

    expected_saturation_drop_rows = [
        {
            "drop_q42_class": 2,
            "retained_disputed_q42_class": 8,
            "omitted_relation_coefficient": 13,
            "retained_relation_coefficient": -1,
            "basis_rank_over_Q": 20,
            "basis_class_count": 20,
            "active_lattice_index_penalty": 13,
            "integral_saturation_preserving": False,
            "basis_classes": [
                0,
                1,
                6,
                7,
                8,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
            ],
        },
        {
            "drop_q42_class": 8,
            "retained_disputed_q42_class": 2,
            "omitted_relation_coefficient": -1,
            "retained_relation_coefficient": 13,
            "basis_rank_over_Q": 20,
            "basis_class_count": 20,
            "active_lattice_index_penalty": 1,
            "integral_saturation_preserving": True,
            "basis_classes": [
                0,
                1,
                2,
                6,
                7,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
            ],
        },
    ]
    if (
        saturation_summary.get("drop_option_integral_saturation_rows")
        != expected_saturation_drop_rows
    ):
        raise AssertionError("bridge probe q42 integral saturation drop-option mismatch")

    saturation_result = saturation.get("result", {})
    expected_saturation_true = {
        "q42_disputed_columns_have_exact_13_relation",
        "q42_relation_is_primitive_rank20_kernel",
        "drop_q42_8_preserves_integral_saturation",
        "drop_q42_2_has_index13_saturation_defect",
        "integral_saturation_selects_same_drop8_basis",
        "explicit_q42_packet_map_still_absent",
        "q42_rank20_integral_saturation_tie_break_selects_drop8",
    }
    for key in expected_saturation_true:
        if saturation_result.get(key) is not True:
            raise AssertionError(f"bridge probe q42 integral saturation check mismatch: {key}")

    direct_doublet = artifact.get("q42_saturated_basis_direct_doublet_skeleton_audit", {})
    if not isinstance(direct_doublet, dict) or not direct_doublet:
        raise AssertionError("bridge probe q42 direct doublet skeleton audit missing")
    if (
        direct_doublet.get("status")
        != "Q42_SATURATED_BASIS_DIRECT_DOUBLET_SKELETON_ONLY_TWO_OF_TEN_MAP_OPEN"
    ):
        raise AssertionError("bridge probe q42 direct doublet skeleton status mismatch")
    direct_summary = direct_doublet.get("direct_doublet_summary", {})
    expected_direct_core = {
        "method": "direct_q42_support_twin_probe_for_saturated_rank20_packet_doublets",
        "saturated_basis_q42_classes": [
            0,
            1,
            2,
            6,
            7,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
        "saturated_basis_q42_class_count": 20,
        "target_full_packet_doublet_count": 10,
        "target_full_packet_id_count": 20,
        "slice_same_support_q42_pair_count": 2,
        "slice_same_support_q42_pairs": [[0, 6], [1, 7]],
        "global_same_support_q42_pair_count": 2,
        "global_same_support_q42_pairs": [[0, 6], [1, 7]],
        "global_same_support_pair_rows": [
            {
                "q42_pair": [0, 6],
                "q12_pair": [0, 3],
                "slice_support_count": 2,
                "slice_abs_sums": [6, 192],
                "global_support_count": 9,
                "global_abs_sums": [2576, 82432],
            },
            {
                "q42_pair": [1, 7],
                "q12_pair": [0, 3],
                "slice_support_count": 2,
                "slice_abs_sums": [48, 720],
                "global_support_count": 9,
                "global_abs_sums": [2576, 38640],
            },
        ],
        "direct_support_twin_covered_q42_classes": [0, 1, 6, 7],
        "direct_support_twin_uncovered_q42_classes": [
            2,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
        "direct_support_twin_uncovered_q42_class_count": 16,
        "direct_support_twin_packet_doublet_shortfall": 8,
        "explicit_q42_to_packet_map_present": False,
    }
    for key, expected in expected_direct_core.items():
        if direct_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q42 direct doublet mismatch: {key}")

    direct_result = direct_doublet.get("result", {})
    expected_direct_true = {
        "saturated_rank20_basis_has_twenty_coordinates",
        "packet_target_has_ten_doublets",
        "direct_slice_support_twins_find_only_two_doublets",
        "direct_global_support_twins_find_only_two_doublets",
        "direct_q42_support_twin_shortfall_is_eight_doublets",
        "direct_q42_doublet_skeleton_requires_nonlocal_packet_map",
        "q42_saturated_basis_direct_doublet_skeleton_only_two_of_ten",
    }
    for key in expected_direct_true:
        if direct_result.get(key) is not True:
            raise AssertionError(f"bridge probe q42 direct doublet check mismatch: {key}")

    carrier = artifact.get("a985_2x2_sector_carrier_completion_audit", {})
    if not isinstance(carrier, dict) or not carrier:
        raise AssertionError("bridge probe A985 2x2 carrier completion audit missing")
    if (
        carrier.get("status")
        != "A985_2X2_SECTOR_CARRIER_COMPLETES_Q42_DIRECT_DOUBLET_SHORTFALL_MAP_OPEN"
    ):
        raise AssertionError("bridge probe A985 2x2 carrier completion status mismatch")
    carrier_summary = carrier.get("carrier_completion_summary", {})
    expected_carrier_core = {
        "method": "a985_two_by_two_sector_carrier_for_q42_direct_doublet_shortfall",
        "matrix_unit_report_status": (
            "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        ),
        "matrix_unit_report_all_checks_pass": True,
        "packet_matrix_lift_status": "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED",
        "packet_matrix_lift_all_checks_pass": True,
        "a985_source_sector_count": 39,
        "a985_matrix_unit_count": 985,
        "a985_block_dimension_histogram": {
            "1": 7,
            "10": 2,
            "11": 1,
            "12": 1,
            "2": 8,
            "3": 4,
            "4": 8,
            "5": 4,
            "6": 2,
            "8": 1,
            "9": 1,
        },
        "a985_two_by_two_sector_count": 8,
        "a985_two_by_two_source_sectors": [5, 6, 13, 20, 21, 22, 32, 33],
        "a985_two_by_two_raw_sectors": [21, 9, 3, 11, 33, 36, 4, 19],
        "a985_two_by_two_matrix_unit_count": 32,
        "a985_two_by_two_rows": [
            {
                "source_sector": 5,
                "raw_sector": 21,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            },
            {
                "source_sector": 6,
                "raw_sector": 9,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            },
            {
                "source_sector": 13,
                "raw_sector": 3,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            },
            {
                "source_sector": 20,
                "raw_sector": 11,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            },
            {
                "source_sector": 21,
                "raw_sector": 33,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            },
            {
                "source_sector": 22,
                "raw_sector": 36,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            },
            {
                "source_sector": 32,
                "raw_sector": 4,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            },
            {
                "source_sector": 33,
                "raw_sector": 19,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            },
        ],
        "a985_raw_sector33_is_two_by_two": True,
        "q42_direct_support_twin_pair_count": 2,
        "q42_direct_support_twin_packet_doublet_shortfall": 8,
        "packet_block_algebra": "Mat_2(Q)^10",
        "packet_block_algebra_dimension_over_Q": 40,
        "packet_component_count": 10,
        "packet_vector_space_dimension": 20,
        "packet_zero_pair_component_count": 1,
        "packet_zero_pair_component_id": 2,
        "direct_q42_visible_block_dimension_over_Q": 8,
        "a985_two_by_two_shortfall_block_dimension_over_Q": 32,
        "combined_carrier_block_dimension_over_Q": 40,
        "combined_carrier_component_count": 10,
        "explicit_a985_to_packet_operator_map_present": False,
    }
    for key, expected in expected_carrier_core.items():
        if carrier_summary.get(key) != expected:
            raise AssertionError(f"bridge probe A985 2x2 carrier mismatch: {key}")

    carrier_result = carrier.get("result", {})
    expected_carrier_true = {
        "a985_matrix_unit_carrier_is_certified",
        "packet_matrix_lift_carrier_is_certified_mat2x10",
        "a985_has_exactly_eight_two_by_two_sector_blocks",
        "a985_two_by_two_count_matches_direct_q42_doublet_shortfall",
        "direct_q42_plus_a985_two_by_two_carrier_matches_packet_blocks",
        "a985_two_by_two_carrier_contains_raw_sector33",
        "a985_two_by_two_carrier_still_needs_operator_assignment",
        "a985_2x2_sector_carrier_completes_q42_direct_doublet_shortfall",
    }
    for key in expected_carrier_true:
        if carrier_result.get(key) is not True:
            raise AssertionError(f"bridge probe A985 2x2 carrier check mismatch: {key}")

    anchor = artifact.get("sector33_packet239_zero_pair_anchor_audit", {})
    if not isinstance(anchor, dict) or not anchor:
        raise AssertionError("bridge probe sector33 packet239 anchor audit missing")
    if anchor.get("status") != "SECTOR33_PACKET239_ZERO_PAIR_ANCHOR_CANDIDATE_OPERATOR_OPEN":
        raise AssertionError("bridge probe sector33 packet239 anchor status mismatch")
    anchor_summary = anchor.get("anchor_summary", {})
    expected_anchor_core = {
        "method": "raw_sector33_to_packet239_zero_pair_component_anchor_candidate",
        "sector33_unique_status": "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED",
        "sector33_unique_all_checks_pass": True,
        "sector33_boundary_status": "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED",
        "sector33_boundary_all_checks_pass": True,
        "sector33_attachment_status": "D20_SECTOR33_RESIDUAL_ATTACHMENT_CERTIFIED",
        "sector33_attachment_all_checks_pass": True,
        "packet239_root_status": "D20_PACKET239_E8_ROOT_RELATION_PROBE_CERTIFIED",
        "packet239_root_all_checks_pass": True,
        "packet_matrix_lift_status": "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED",
        "packet_matrix_lift_all_checks_pass": True,
        "a985_raw_sector33_carrier_rows": [
            {
                "source_sector": 21,
                "raw_sector": 33,
                "block_dimension": 2,
                "matrix_unit_count": 4,
                "is_square_matrix_unit_block": True,
            }
        ],
        "a985_raw_sector33_source_sector": 21,
        "sector33_unique_public_zero_sector": 33,
        "sector33_block_dimension": 2,
        "sector33_active_objects": ["B+", "S+"],
        "sector33_q42_nonzero_count": 0,
        "sector33_q12_nonzero_count": 0,
        "sector33_profile_active_objects": ["B+", "S+"],
        "sector33_profile_block_dimension": 2,
        "sector33_attachment_type": "unique public-zero, tube-visible A985 sector interface",
        "sector33_boundary_cycle_id": 8,
        "sector33_residual_integral": -374784,
        "sector33_public_terminal_shadow": {
            "A12": "zero",
            "A42": "zero",
            "q12_nonzero_count": 0,
            "q42_nonzero_count": 0,
        },
        "packet239_selection_rule": "full_exposure_sector26_zero_pair_fixed_point",
        "packet239_uses_external_packet_id": False,
        "packet239_selected_packet_ids": [239],
        "packet239_selected_frame_indices": [0],
        "packet239_charge_frame_key": (
            "high|zero_pair|full|gamma8_silent|hidden_cancelled|central_negative|AI|BDI"
        ),
        "packet239_fine_spectral_charge_key": "32|0|0|0|25",
        "packet239_sector26_clock_pair": [0, 0],
        "packet239_sector26_clock_zero_pair": True,
        "packet239_corrected_hidden_clock_pair": [0, 0],
        "packet239_hidden_projection_pair": ["sector_orthogonal", "sector_orthogonal"],
        "packet239_gamma8_touched": False,
        "packet_zero_pair_component_count": 1,
        "packet_zero_pair_component_id": 2,
        "packet_zero_pair_packet_pair": [238, 239],
        "packet_zero_pair_oriented_basis": [239, 238],
        "packet_zero_pair_block_matrix": [[2, 4], [4, 2]],
        "packet_zero_pair_block_decomposition": "2*I + 4*S",
        "explicit_a985_to_packet_operator_map_present": False,
        "anchor_status": "UNIQUE_SOURCE_AND_TARGET_ANCHOR_CANDIDATE_OPERATOR_OPEN",
    }
    for key, expected in expected_anchor_core.items():
        if anchor_summary.get(key) != expected:
            raise AssertionError(f"bridge probe sector33 packet239 anchor mismatch: {key}")

    anchor_result = anchor.get("result", {})
    expected_anchor_true = {
        "sector33_anchor_inputs_are_certified",
        "packet239_anchor_inputs_are_certified",
        "raw_sector33_is_unique_2x2_carrier_row",
        "sector33_is_unique_public_zero_two_dimensional_shadow",
        "sector33_is_cycle8_hidden_residual_anchor",
        "packet239_is_unique_id_free_zero_pair_anchor",
        "packet239_zero_pair_component_is_unique_mat2_block",
        "sector33_packet239_anchor_has_matching_two_dimensional_hidden_zero_profile",
        "sector33_packet239_anchor_operator_still_open",
        "sector33_packet239_zero_pair_anchor_candidate_operator_open",
    }
    for key in expected_anchor_true:
        if anchor_result.get(key) is not True:
            raise AssertionError(f"bridge probe sector33 packet239 anchor check mismatch: {key}")

    chart_constraints = artifact.get(
        "a985_2x2_chart_signature_assignment_constraints_audit", {}
    )
    if not isinstance(chart_constraints, dict) or not chart_constraints:
        raise AssertionError("bridge probe A985 2x2 chart constraints audit missing")
    if (
        chart_constraints.get("status")
        != "A985_2X2_CHART_SIGNATURES_CONSTRAIN_ASSIGNMENT_OPERATOR_OPEN"
    ):
        raise AssertionError("bridge probe A985 2x2 chart constraints status mismatch")
    chart_summary = chart_constraints.get("chart_constraint_summary", {})
    expected_chart_core = {
        "method": "a985_two_by_two_chart_signature_constraints_for_sector_packet_assignment",
        "a985_two_by_two_chart_row_count": 8,
        "saturated_q42_overlap_class_count": 4,
        "saturated_q42_overlap_class_rows": [
            {
                "saturated_q42_overlap": [],
                "source_sectors": [20, 21, 22, 32, 33],
                "raw_sectors": [11, 33, 36, 4, 19],
                "class_size": 5,
            },
            {
                "saturated_q42_overlap": [20, 21],
                "source_sectors": [5],
                "raw_sectors": [21],
                "class_size": 1,
            },
            {
                "saturated_q42_overlap": [21],
                "source_sectors": [6],
                "raw_sectors": [9],
                "class_size": 1,
            },
            {
                "saturated_q42_overlap": [24, 25],
                "source_sectors": [13],
                "raw_sectors": [3],
                "class_size": 1,
            },
        ],
        "full_q42_q12_signature_class_count": 6,
        "full_q42_q12_signature_class_rows": [
            {
                "q42_classes": [20, 20, 21, 21],
                "q12_classes": [7, 7, 7, 7],
                "source_sectors": [5],
                "raw_sectors": [21],
                "class_size": 1,
            },
            {
                "q42_classes": [21, 21, 21, 21],
                "q12_classes": [7, 7, 7, 7],
                "source_sectors": [6],
                "raw_sectors": [9],
                "class_size": 1,
            },
            {
                "q42_classes": [24, 25, 25, 25],
                "q12_classes": [4, 9, 9, 9],
                "source_sectors": [13],
                "raw_sectors": [3],
                "class_size": 1,
            },
            {
                "q42_classes": [9, 9, 9, 9],
                "q12_classes": [4, 4, 4, 4],
                "source_sectors": [20, 21, 22],
                "raw_sectors": [11, 33, 36],
                "class_size": 3,
            },
            {
                "q42_classes": [33, 33, 33, 33],
                "q12_classes": [10, 10, 10, 10],
                "source_sectors": [32],
                "raw_sectors": [4],
                "class_size": 1,
            },
            {
                "q42_classes": [33, 33, 33, 34],
                "q12_classes": [10, 10, 10, 11],
                "source_sectors": [33],
                "raw_sectors": [19],
                "class_size": 1,
            },
        ],
        "sector33_anchor_source_sector": 21,
        "sector33_anchor_raw_sector": 33,
        "sector33_anchor_saturated_q42_overlap": [],
        "sector33_anchor_direct_q42_overlap": [],
        "sector33_anchor_saturated_class_source_sectors": [20, 21, 22, 32, 33],
        "sector33_anchor_saturated_class_raw_sectors": [11, 33, 36, 4, 19],
        "sector33_anchor_chart_twin_source_sectors": [20, 21, 22],
        "sector33_anchor_chart_twin_raw_sectors": [11, 33, 36],
        "sector33_anchor_residual_chart_twin_source_sectors_after_anchor": [20, 22],
        "sector33_anchor_residual_chart_twin_raw_sectors_after_anchor": [11, 36],
        "sector33_anchor_packet_component_id": 2,
        "remaining_a985_two_by_two_source_sectors": [5, 6, 13, 20, 22, 32, 33],
        "remaining_a985_two_by_two_raw_sectors": [21, 9, 3, 11, 36, 4, 19],
        "remaining_a985_two_by_two_count": 7,
        "remaining_packet_component_ids_after_anchor": [0, 1, 3, 4, 5, 6, 7, 8, 9],
        "remaining_packet_component_count_after_anchor": 9,
        "direct_q42_visible_block_count": 2,
        "remaining_carrier_count_after_anchor_plus_direct_q42_blocks": 9,
        "explicit_a985_to_packet_operator_map_present": False,
    }
    for key, expected in expected_chart_core.items():
        if chart_summary.get(key) != expected:
            raise AssertionError(f"bridge probe A985 2x2 chart constraints mismatch: {key}")
    chart_rows = chart_summary.get("a985_two_by_two_chart_rows", [])
    if len(chart_rows) != 8 or any(len(row.get("chart_relation_indices", [])) != 4 for row in chart_rows):
        raise AssertionError("bridge probe A985 2x2 chart row shape mismatch")

    chart_result = chart_constraints.get("result", {})
    expected_chart_true = {
        "chart_constraints_cover_all_eight_a985_2x2_sectors",
        "saturated_q42_chart_constraints_reduce_to_four_classes_with_one_null_cluster",
        "full_q42_q12_chart_signatures_refine_to_six_classes",
        "sector33_anchor_lands_in_full_signature_triple_and_leaves_raw11_raw36_twin",
        "a985_two_by_two_rows_avoid_direct_q42_support_twins",
        "remaining_carrier_count_matches_unanchored_packet_components_when_direct_q42_blocks_included",
        "chart_constraints_are_not_full_operator_assignment",
        "a985_2x2_chart_signatures_constrain_remaining_assignment_operator_open",
    }
    for key in expected_chart_true:
        if chart_result.get(key) is not True:
            raise AssertionError(f"bridge probe A985 2x2 chart constraints check mismatch: {key}")

    charge_partition = artifact.get(
        "q12_packet_charge_sum_partition_fingerprint_audit", {}
    )
    if not isinstance(charge_partition, dict) or not charge_partition:
        raise AssertionError("bridge probe q12 packet charge-sum partition audit missing")
    if (
        charge_partition.get("status")
        != "Q12_PACKET_CHARGE_SUM_PARTITION_FINGERPRINT_OPERATOR_OPEN"
    ):
        raise AssertionError("bridge probe q12 packet charge-sum partition status mismatch")
    partition_summary = charge_partition.get("partition_summary", {})
    expected_partition_core = {
        "method": "q12_carrier_partition_vs_packet_sector26_charge_sum_fingerprint",
        "carrier_count_after_anchor_plus_direct_q42": 9,
        "carrier_q12_signature_class_count": 6,
        "carrier_q12_signature_class_rows": [
            {
                "q12_signature": [0, 3],
                "carrier_ids": ["direct_q42_0_6", "direct_q42_1_7"],
                "carrier_kinds": [
                    "direct_q42_support_twin",
                    "direct_q42_support_twin",
                ],
                "source_sectors": [],
                "raw_sectors": [],
                "direct_q42_pairs": [[0, 6], [1, 7]],
                "class_size": 2,
            },
            {
                "q12_signature": [4, 4, 4, 4],
                "carrier_ids": ["a985_raw11", "a985_raw36"],
                "carrier_kinds": ["a985_2x2_sector", "a985_2x2_sector"],
                "source_sectors": [20, 22],
                "raw_sectors": [11, 36],
                "direct_q42_pairs": [],
                "class_size": 2,
            },
            {
                "q12_signature": [4, 9, 9, 9],
                "carrier_ids": ["a985_raw3"],
                "carrier_kinds": ["a985_2x2_sector"],
                "source_sectors": [13],
                "raw_sectors": [3],
                "direct_q42_pairs": [],
                "class_size": 1,
            },
            {
                "q12_signature": [7, 7, 7, 7],
                "carrier_ids": ["a985_raw21", "a985_raw9"],
                "carrier_kinds": ["a985_2x2_sector", "a985_2x2_sector"],
                "source_sectors": [5, 6],
                "raw_sectors": [21, 9],
                "direct_q42_pairs": [],
                "class_size": 2,
            },
            {
                "q12_signature": [10, 10, 10, 10],
                "carrier_ids": ["a985_raw4"],
                "carrier_kinds": ["a985_2x2_sector"],
                "source_sectors": [32],
                "raw_sectors": [4],
                "direct_q42_pairs": [],
                "class_size": 1,
            },
            {
                "q12_signature": [10, 10, 10, 11],
                "carrier_ids": ["a985_raw19"],
                "carrier_kinds": ["a985_2x2_sector"],
                "source_sectors": [33],
                "raw_sectors": [19],
                "direct_q42_pairs": [],
                "class_size": 1,
            },
        ],
        "carrier_q12_signature_class_size_histogram": [1, 1, 1, 2, 2, 2],
        "packet_component_count_after_anchor": 9,
        "packet_sector26_sum_class_count": 6,
        "packet_sector26_sum_class_rows": [
            {
                "sector26_sum_pair": [0, 22],
                "component_ids": [4, 8],
                "packet_pairs": [[254, 255], [502, 503]],
                "local_patterns": ["1110", "0111"],
                "gamma_frame_pairs": [
                    ["gamma8_silent", "gamma8_silent"],
                    ["gamma8", "gamma8"],
                ],
                "class_size": 2,
            },
            {
                "sector26_sum_pair": [10, 6],
                "component_ids": [1, 9],
                "packet_pairs": [[190, 191], [510, 511]],
                "local_patterns": ["1100", "1111"],
                "gamma_frame_pairs": [
                    ["gamma8_silent", "gamma8_silent"],
                    ["gamma8", "gamma8"],
                ],
                "class_size": 2,
            },
            {
                "sector26_sum_pair": [14, 10],
                "component_ids": [0, 7],
                "packet_pairs": [[174, 175], [494, 495]],
                "local_patterns": ["1000", "1011"],
                "gamma_frame_pairs": [
                    ["gamma8_silent", "gamma8_silent"],
                    ["gamma8", "gamma8"],
                ],
                "class_size": 2,
            },
            {
                "sector26_sum_pair": [16, 12],
                "component_ids": [3],
                "packet_pairs": [[246, 247]],
                "local_patterns": ["0110"],
                "gamma_frame_pairs": [["gamma8_silent", "gamma8_silent"]],
                "class_size": 1,
            },
            {
                "sector26_sum_pair": [20, 16],
                "component_ids": [6],
                "packet_pairs": [[446, 447]],
                "local_patterns": ["1101"],
                "gamma_frame_pairs": [["gamma8", "gamma8"]],
                "class_size": 1,
            },
            {
                "sector26_sum_pair": [24, 20],
                "component_ids": [5],
                "packet_pairs": [[430, 431]],
                "local_patterns": ["1001"],
                "gamma_frame_pairs": [["gamma8", "gamma8"]],
                "class_size": 1,
            },
        ],
        "packet_sector26_sum_class_size_histogram": [1, 1, 1, 2, 2, 2],
        "anchored_component_id": 2,
        "anchored_packet_sector26_sum_pair": [4, 0],
        "anchored_packet_clock_frames": ["delta8_nonzero", "zero_pair"],
        "residual_raw11_raw36_q12_signature": [4, 4, 4, 4],
        "residual_raw11_raw36_source_sectors": [20, 22],
        "residual_raw11_raw36_raw_sectors": [11, 36],
        "size_compatible_class_bijection_count": 36,
        "size_compatible_element_bijection_count": 288,
        "unconstrained_element_bijection_count": 362880,
        "explicit_operator_map_present": False,
    }
    for key, expected in expected_partition_core.items():
        if partition_summary.get(key) != expected:
            raise AssertionError(
                f"bridge probe q12 packet charge-sum partition mismatch: {key}"
            )

    partition_result = charge_partition.get("result", {})
    expected_partition_true = {
        "carrier_q12_partition_covers_nine_unanchored_carriers",
        "packet_sector26_sum_partition_covers_nine_unanchored_components",
        "carrier_and_packet_partition_fingerprints_match",
        "residual_raw11_raw36_is_q12_class4_twin",
        "sector33_anchor_removed_zero_pair_charge_sum_component",
        "partition_size_constraint_reduces_but_does_not_solve_assignment",
        "q12_packet_charge_sum_partition_fingerprint_operator_open",
    }
    for key in expected_partition_true:
        if partition_result.get(key) is not True:
            raise AssertionError(
                f"bridge probe q12 packet charge-sum partition check mismatch: {key}"
            )

    tie_break = artifact.get("q42_packet239_q12_seed_anchor_tie_break_audit", {})
    if not isinstance(tie_break, dict) or not tie_break:
        raise AssertionError("bridge probe q42 packet239 q12 seed tie-break audit missing")
    if (
        tie_break.get("status")
        != "Q42_PACKET239_Q12_SEED_ANCHOR_CONDITIONALLY_SELECTS_DROP8_MAP_OPEN"
    ):
        raise AssertionError("bridge probe q42 packet239 q12 seed tie-break status mismatch")
    tie_summary = tie_break.get("tie_break_summary", {})
    expected_tie_core = {
        "method": "packet239_zero_pair_q12_seed_anchor_for_q42_rank20_basis_choice",
        "packet239_root_status": "D20_PACKET239_E8_ROOT_RELATION_PROBE_CERTIFIED",
        "packet239_root_all_checks_pass": True,
        "packet239_shell_status": "D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_CERTIFIED",
        "packet239_shell_all_checks_pass": True,
        "full_exposure_label_breaking_status": (
            "D20_FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_CERTIFIED"
        ),
        "full_exposure_label_breaking_all_checks_pass": True,
        "packet239_unique_full_exposure_clock_zero": True,
        "packet239_seed_closure_is_238_239": True,
        "packet239_packet_id": 239,
        "packet239_frame_indices": [0],
        "packet239_candidate_a12_classes": list(range(12)),
        "packet239_candidate_a12_class_count": 12,
        "packet239_charge_frame_key": "high|zero_pair|gamma8_silent",
        "packet239_fine_spectral_charge_key": "32|0|0|0|25",
        "packet239_sector26_clock_zero_pair": True,
        "q12_seed_q12_class": 1,
        "q12_seed_section_relation_id": 227,
        "q12_seed_packet_low_support_family": [0, 11],
        "q42_rank20_active_relation_support": [[2, 13], [8, -1]],
        "q42_rank20_rank_preserving_drop_classes": [2, 8],
        "selected_drop_q42_class_by_q12_seed_anchor": 8,
        "rejected_drop_q42_class_by_q12_seed_anchor": 2,
        "selected_basis_q42_classes_by_q12_seed_anchor": [
            0,
            1,
            2,
            6,
            7,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        ],
        "explicit_q42_to_packet_map_present": False,
        "tie_break_status": "CONDITIONAL_ON_Q12_SEED_ANCHOR",
    }
    for key, expected in expected_tie_core.items():
        if tie_summary.get(key) != expected:
            raise AssertionError(f"bridge probe q42 packet239 tie-break mismatch: {key}")

    expected_tie_drop_rows = [
        {
            "drop_q42_class": 2,
            "basis_rank_over_Q": 20,
            "basis_class_count": 20,
            "seed_q12_class_count": 0,
            "preserves_seed_q12_class": False,
            "basis_q12_class_histogram": {
                "0": 2,
                "3": 4,
                "4": 2,
                "6": 4,
                "7": 4,
                "8": 2,
                "9": 2,
            },
            "basis_classes": [
                0,
                1,
                6,
                7,
                8,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
            ],
        },
        {
            "drop_q42_class": 8,
            "basis_rank_over_Q": 20,
            "basis_class_count": 20,
            "seed_q12_class_count": 1,
            "preserves_seed_q12_class": True,
            "basis_q12_class_histogram": {
                "0": 2,
                "1": 1,
                "3": 4,
                "4": 1,
                "6": 4,
                "7": 4,
                "8": 2,
                "9": 2,
            },
            "basis_classes": [
                0,
                1,
                2,
                6,
                7,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
            ],
        },
    ]
    if tie_summary.get("drop_option_q12_seed_anchor_rows") != expected_tie_drop_rows:
        raise AssertionError("bridge probe q42 packet239 tie-break drop-option mismatch")

    tie_result = tie_break.get("result", {})
    expected_tie_true = {
        "packet239_anchor_inputs_are_certified",
        "packet239_unique_zero_pair_anchor_available",
        "packet239_a12_shell_keeps_all_twelve_q12_slots_open",
        "q12_packet_seed_anchor_is_class1",
        "q42_drop2_deletes_q12_seed_class1",
        "q42_drop8_preserves_unique_q12_seed_class1",
        "q12_seed_anchor_conditionally_selects_drop8",
        "explicit_q42_packet_map_still_absent",
        "q42_packet239_q12_seed_anchor_tie_break_conditional",
    }
    for key in expected_tie_true:
        if tie_result.get(key) is not True:
            raise AssertionError(f"bridge probe q42 packet239 tie-break check mismatch: {key}")

    return artifact


if __name__ == "__main__":
    artifact = validate_d20_hydrogen_sandpile_golay_bridge_probe()
    print(
        json.dumps(
            {
                "status": "D20_HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE_VALIDATED",
                "artifact": "recomputed in memory",
                "nominal_artifact": ARTIFACT_REL,
                "artifact_sha256": artifact["artifact_sha256"],
                "best_assignment_count": artifact["assignment_search"]["best_assignment_count"],
                "discriminator_screen0_distinguished": artifact["discriminator_search"][
                    "discriminator_result"
                ]["screen0_distinguished"],
                "full_certified_h8_assignment_remains_open": artifact["discriminator_search"][
                    "discriminator_result"
                ]["full_certified_h8_assignment_remains_open"],
                "screen_to_unsigned_h8_sector_assignment": artifact["discriminator_search"][
                    "discriminator_result"
                ]["screen_to_unsigned_h8_sector_assignment"],
                "gamma8_visible_sector": artifact["static_tropic_sector_pullback"]["tropic"][
                    "gamma8_dominant_visible_sector"
                ],
                "static_public_zero_screen_sector": artifact["static_tropic_sector_pullback"][
                    "static"
                ]["public_zero_screen_sector"],
                "ward_selected_mask": artifact["static_tropic_ward_composition_audit"][
                    "selector_summary"
                ]["selected_mask"],
                "ward_selected_screen_sectors": artifact["static_tropic_ward_composition_audit"][
                    "selected_turn_signature_screen_sectors"
                ],
                "mask288_z2_status": artifact["selected_mask_z2_static_audit"]["status"],
                "mask288_z2_non_scalar_supports": artifact["selected_mask_z2_static_audit"][
                    "non_scalar_supports"
                ],
                "mask288_exact_h6_public_atom_ids": artifact[
                    "selected_mask_exact_h6_support_audit"
                ]["selected_h6_public_atom_ids"],
                "mask288_z2_exact_retest_status": artifact[
                    "selected_mask_exact_h6_support_audit"
                ]["z2_exact_retest_status"],
                "q12_h6_projection_status": artifact["q12_h6_projection_audit"]["status"],
                "q12_h6_raw_union_exact_solution_count": artifact[
                    "q12_h6_projection_audit"
                ]["raw_combination_bruteforce"]["raw_union_exact_solution_count"],
                "q12_h6_raw_parity_exact_solution_count": artifact[
                    "q12_h6_projection_audit"
                ]["raw_combination_bruteforce"]["raw_parity_exact_solution_count"],
                "q12_h6_signed_unit_exact_hit_found": artifact[
                    "q12_h6_projection_audit"
                ]["signed_unit_bruteforce"]["exact_hit_found"],
                "mask288_q12_packet_seed_status": artifact[
                    "q12_packet_low_support_normalization_audit"
                ]["status"],
                "mask288_q12_packet_seed_rows": artifact[
                    "q12_packet_low_support_normalization_audit"
                ]["mask288_q12_packet_seed_rows"],
                "mask288_q12_packet_seed_support3_status": artifact[
                    "mask288_q12_packet_seed_support3_audit"
                ]["status"],
                "mask288_q12_packet_seed_support3_even_candidate_count": artifact[
                    "mask288_q12_packet_seed_support3_audit"
                ]["even_image_candidate_count"],
                "mask288_q12_packet_seed_support3_compatible_doublet_count": artifact[
                    "mask288_q12_packet_seed_support3_audit"
                ]["compatible_doublet_count"],
                "mask288_q12_packet_seed_broadened_status": artifact[
                    "mask288_q12_packet_seed_broadened_extension_audit"
                ]["status"],
                "mask288_q12_packet_seed_widened_rank2_doublet_count": artifact[
                    "mask288_q12_packet_seed_broadened_extension_audit"
                ]["support3_widened_summary"]["rank2_doublet_count"],
                "mask288_q12_packet_seed_support4_unit_even_candidate_count": artifact[
                    "mask288_q12_packet_seed_broadened_extension_audit"
                ]["support4_unit_summary"]["even_image_candidate_count"],
                "mask288_q12_rank2_label_status": artifact[
                    "mask288_q12_rank2_doublet_label_audit"
                ]["status"],
                "mask288_q12_rank2_direct_product_label_count": artifact[
                    "mask288_q12_rank2_doublet_label_audit"
                ]["direct_q12_product_label_count"],
                "mask288_q12_rank2_linear_combination_status": artifact[
                    "mask288_q12_rank2_linear_combination_audit"
                ]["status"],
                "mask288_q12_rank2_linear_cover_count": artifact[
                    "mask288_q12_rank2_linear_combination_audit"
                ]["total_cover_solution_count"],
                "mask288_q12_rank2_linear_exact_count": artifact[
                    "mask288_q12_rank2_linear_combination_audit"
                ]["total_exact_support_solution_count"],
                "mask288_q12_product_overhang_status": artifact[
                    "mask288_q12_product_overhang_invariant_audit"
                ]["status"],
                "mask288_q12_product_overhang_nonzero_mod6_families": artifact[
                    "mask288_q12_product_overhang_invariant_audit"
                ]["packet_normalization_readout"][
                    "families_with_nonzero_overhang_residue_mod6"
                ],
                "mask288_q12_product_overhang_static_parity_status": artifact[
                    "mask288_q12_product_overhang_invariant_audit"
                ]["static_parity_readout"]["status"],
                "mask288_q12_outside_class1_cancellation_status": artifact[
                    "mask288_q12_outside_class1_residue_cancellation_audit"
                ]["status"],
                "mask288_q12_outside_class1_cancellation_residue_clear_count": artifact[
                    "mask288_q12_outside_class1_residue_cancellation_audit"
                ]["total_residue_clear_candidate_count"],
                "mask288_q12_outside_class1_cancellation_exact_count": artifact[
                    "mask288_q12_outside_class1_residue_cancellation_audit"
                ]["total_exact_support_candidate_count"],
                "mask288_q12_packet_normalized_assembly_status": artifact[
                    "mask288_q12_packet_normalized_seed_assembly_audit"
                ]["status"],
                "mask288_q12_packet_normalized_q12_compatible_doublet_count": artifact[
                    "mask288_q12_packet_normalized_seed_assembly_audit"
                ]["candidate_pool_summary"]["q12_involving_compatible_doublet_count"],
                "mask288_q12_packet_normalized_compatible_doublet_count": artifact[
                    "mask288_q12_packet_normalized_seed_assembly_audit"
                ]["candidate_pool_summary"]["compatible_doublet_count"],
                "mask288_q12_direct_paired_doublet_status": artifact[
                    "mask288_q12_direct_paired_doublet_search_audit"
                ]["status"],
                "mask288_q12_direct_paired_doublet_count": artifact[
                    "mask288_q12_direct_paired_doublet_search_audit"
                ]["compatible_doublet_summary"]["compatible_doublet_count"],
                "mask288_q12_direct_paired_rank2_family_count": artifact[
                    "mask288_q12_direct_paired_doublet_search_audit"
                ]["compatible_doublet_summary"]["rank2_support_family_count"],
                "mask288_q12_one_sided_seed_correction_status": artifact[
                    "mask288_q12_one_sided_seed_correction_audit"
                ]["status"],
                "mask288_q12_one_sided_seed_correction_doublet_count": artifact[
                    "mask288_q12_one_sided_seed_correction_audit"
                ]["compatible_doublet_summary"]["compatible_doublet_count"],
                "mask288_q12_one_sided_seed_correction_combined_rank2_family_count": artifact[
                    "mask288_q12_one_sided_seed_correction_audit"
                ]["compatible_doublet_summary"]["combined_rank2_support_family_count"],
                "mask288_q12_corrected_rank20_selection_status": artifact[
                    "mask288_q12_corrected_rank20_selection_audit"
                ]["status"],
                "mask288_q12_corrected_rank20_selection_rank": artifact[
                    "mask288_q12_corrected_rank20_selection_audit"
                ]["rank_ceiling_summary"]["combined_boundary_image_rank_over_Q"],
                "mask288_q12_corrected_rank20_selection_unique_images": artifact[
                    "mask288_q12_corrected_rank20_selection_audit"
                ]["rank_ceiling_summary"]["unique_boundary_image_count"],
                "mask288_q12_rank_escape_status": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["status"],
                "mask288_q12_rank_escape_raw_nonscalar_rank": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["raw_non_scalar_pair_summary"][
                    "raw_non_scalar_boundary_image_rank_over_Q"
                ],
                "mask288_q12_rank_escape_raw_pair_count": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["raw_non_scalar_pair_summary"]["raw_packet_compatible_pair_count"],
                "mask288_q12_rank11_annihilator_dimension": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["rank11_annihilator_summary"]["annihilator_dimension_over_Q"],
                "mask288_q12_rank11_external_generator_lower_bound": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["rank11_annihilator_summary"][
                    "outside_q12_rational_generator_lower_bound"
                ],
                "ingress_projection_inventory_status": artifact[
                    "ingress_boundary_packet_projection_inventory_audit"
                ]["status"],
                "ingress_projection_inventory_missing_bridge_count": artifact[
                    "ingress_boundary_packet_projection_inventory_audit"
                ]["packet_restriction_gap_summary"]["missing_bridge_count"],
                "boundary_packet_projection_candidate_status": artifact[
                    "boundary_packet_projection_candidate_audit"
                ]["status"],
                "boundary_packet_projection_candidate_passing_columns": artifact[
                    "boundary_packet_projection_candidate_audit"
                ]["candidate_summary"]["columns_passing_packet_snf_image"],
                "signed_step_column_search_status": artifact[
                    "signed_step_column_packet_search_audit"
                ]["status"],
                "signed_step_column_search_compatible_count": artifact[
                    "signed_step_column_packet_search_audit"
                ]["search_summary"]["compatible_row_count"],
                "signed_step_column_search_target_rank": artifact[
                    "signed_step_column_packet_search_audit"
                ]["search_summary"]["unique_target_vector_rank_over_Q"],
                "support4_signed_step_column_status": artifact[
                    "support4_signed_step_column_span_audit"
                ]["status"],
                "support4_signed_step_column_compatible_count": artifact[
                    "support4_signed_step_column_span_audit"
                ]["support4_summary"]["compatible_row_count_by_support"]["4"],
                "support4_signed_step_column_target_rank": artifact[
                    "support4_signed_step_column_span_audit"
                ]["support4_summary"][
                    "unique_target_vector_rank_over_Q_support_le_4"
                ],
                "full_step_column_lattice_status": artifact[
                    "full_step_column_congruence_lattice_audit"
                ]["status"],
                "full_step_column_lattice_target_rank": artifact[
                    "full_step_column_congruence_lattice_audit"
                ]["full_lattice_summary"]["basis_target_rank_over_Q"],
                "full_step_column_lattice_packet_shortfall": artifact[
                    "full_step_column_congruence_lattice_audit"
                ]["full_lattice_summary"][
                    "packet_target_rank_shortfall_after_full_type_lattice"
                ],
                "q42_q12_quotient_filter_status": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["status"],
                "q42_q12_quotient_filter_hidden_rank_lost": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["quotient_adjusted_summary"][
                    "q42_hidden_rank_lost_under_q12_public_readout"
                ],
                "q42_q12_quotient_filter_natural_pass_count": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["quotient_adjusted_summary"][
                    "q42_scalar6_natural_target_passing_row_count"
                ],
                "q42_q12_quotient_filter_natural_pass_rank": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["quotient_adjusted_summary"][
                    "q42_scalar6_natural_target_passing_rank_over_Q"
                ],
                "q42_q12_quotient_filter_packet_shortfall": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["quotient_adjusted_summary"][
                    "q42_natural_pass_packet_rank_shortfall"
                ],
                "hidden_q42_a985_capacity_status": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["status"],
                "hidden_q42_a985_matrix_unit_rank": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["hidden_capacity_summary"]["q42_matrix_unit_aggregate_rank_mod_p"],
                "hidden_q42_a985_character_representative_rank": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["hidden_capacity_summary"][
                    "q42_character_representative_rank_over_Q"
                ],
                "hidden_q42_a985_packet_target_excess": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["hidden_capacity_summary"][
                    "q42_matrix_unit_rank_excess_over_packet_target"
                ],
                "hidden_q42_a985_block_lift_excess": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["hidden_capacity_summary"][
                    "q42_matrix_unit_rank_excess_over_block_lift"
                ],
                "q42_tensor_rank20_slice_status": artifact[
                    "q42_tensor_rank20_slice_quotient_audit"
                ]["status"],
                "q42_tensor_rank20_slice_first_exact": artifact[
                    "q42_tensor_rank20_slice_quotient_audit"
                ]["rank20_slice_summary"]["first_exact_rank20_left_classes"],
                "q42_tensor_rank20_slice_exact_count": artifact[
                    "q42_tensor_rank20_slice_quotient_audit"
                ]["rank20_slice_summary"]["exact_rank20_combo_count"],
                "q42_tensor_rank20_slice_q12_pushdown_rank": artifact[
                    "q42_tensor_rank20_slice_quotient_audit"
                ]["rank20_slice_summary"][
                    "first_exact_rank20_q12_pushdown_rank_over_Q"
                ],
                "q42_rank20_packet_label_filter_status": artifact[
                    "q42_rank20_packet_spectral_label_filter_audit"
                ]["status"],
                "q42_rank20_packet_label_filter_active_relation": artifact[
                    "q42_rank20_packet_spectral_label_filter_audit"
                ]["packet_label_filter_summary"][
                    "q42_rank20_active_relation_support"
                ],
                "q42_rank20_packet_label_filter_fine_key_count": artifact[
                    "q42_rank20_packet_spectral_label_filter_audit"
                ]["packet_label_filter_summary"][
                    "full_exposure_fine_spectral_charge_key_count"
                ],
                "q42_rank20_packet_label_filter_doublet_key_count": artifact[
                    "q42_rank20_packet_spectral_label_filter_audit"
                ]["packet_label_filter_summary"][
                    "full_packet_doublet_pair_filter_key_count"
                ],
                "q42_integral_saturation_status": artifact[
                    "q42_rank20_integral_saturation_tie_break_audit"
                ]["status"],
                "q42_integral_saturation_selected_drop": artifact[
                    "q42_rank20_integral_saturation_tie_break_audit"
                ]["integral_saturation_summary"][
                    "selected_drop_q42_class_by_integral_saturation"
                ],
                "q42_integral_saturation_rejected_drop": artifact[
                    "q42_rank20_integral_saturation_tie_break_audit"
                ]["integral_saturation_summary"][
                    "rejected_drop_q42_class_by_integral_saturation"
                ],
                "q42_integral_saturation_rejected_index": artifact[
                    "q42_rank20_integral_saturation_tie_break_audit"
                ]["integral_saturation_summary"]["rejected_basis_index_defect"],
                "q42_direct_doublet_skeleton_status": artifact[
                    "q42_saturated_basis_direct_doublet_skeleton_audit"
                ]["status"],
                "q42_direct_doublet_skeleton_pair_count": artifact[
                    "q42_saturated_basis_direct_doublet_skeleton_audit"
                ]["direct_doublet_summary"]["global_same_support_q42_pair_count"],
                "q42_direct_doublet_skeleton_shortfall": artifact[
                    "q42_saturated_basis_direct_doublet_skeleton_audit"
                ]["direct_doublet_summary"][
                    "direct_support_twin_packet_doublet_shortfall"
                ],
                "a985_2x2_carrier_status": artifact[
                    "a985_2x2_sector_carrier_completion_audit"
                ]["status"],
                "a985_2x2_carrier_sector_count": artifact[
                    "a985_2x2_sector_carrier_completion_audit"
                ]["carrier_completion_summary"]["a985_two_by_two_sector_count"],
                "a985_2x2_carrier_combined_components": artifact[
                    "a985_2x2_sector_carrier_completion_audit"
                ]["carrier_completion_summary"]["combined_carrier_component_count"],
                "a985_2x2_carrier_contains_raw_sector33": artifact[
                    "a985_2x2_sector_carrier_completion_audit"
                ]["carrier_completion_summary"]["a985_raw_sector33_is_two_by_two"],
                "sector33_packet239_anchor_status": artifact[
                    "sector33_packet239_zero_pair_anchor_audit"
                ]["status"],
                "sector33_packet239_anchor_source_sector": artifact[
                    "sector33_packet239_zero_pair_anchor_audit"
                ]["anchor_summary"]["a985_raw_sector33_source_sector"],
                "sector33_packet239_anchor_packet_component": artifact[
                    "sector33_packet239_zero_pair_anchor_audit"
                ]["anchor_summary"]["packet_zero_pair_component_id"],
                "sector33_packet239_anchor_packet_pair": artifact[
                    "sector33_packet239_zero_pair_anchor_audit"
                ]["anchor_summary"]["packet_zero_pair_packet_pair"],
                "a985_chart_constraints_status": artifact[
                    "a985_2x2_chart_signature_assignment_constraints_audit"
                ]["status"],
                "a985_chart_constraints_class_count": artifact[
                    "a985_2x2_chart_signature_assignment_constraints_audit"
                ]["chart_constraint_summary"]["saturated_q42_overlap_class_count"],
                "a985_chart_constraints_remaining_carriers": artifact[
                    "a985_2x2_chart_signature_assignment_constraints_audit"
                ]["chart_constraint_summary"]["remaining_a985_two_by_two_count"],
                "a985_chart_constraints_remaining_packet_components": artifact[
                    "a985_2x2_chart_signature_assignment_constraints_audit"
                ]["chart_constraint_summary"][
                    "remaining_packet_component_count_after_anchor"
                ],
                "q12_packet_charge_sum_partition_status": artifact[
                    "q12_packet_charge_sum_partition_fingerprint_audit"
                ]["status"],
                "q12_packet_charge_sum_partition_carrier_histogram": artifact[
                    "q12_packet_charge_sum_partition_fingerprint_audit"
                ]["partition_summary"]["carrier_q12_signature_class_size_histogram"],
                "q12_packet_charge_sum_partition_packet_histogram": artifact[
                    "q12_packet_charge_sum_partition_fingerprint_audit"
                ]["partition_summary"]["packet_sector26_sum_class_size_histogram"],
                "q12_packet_charge_sum_partition_element_bijections": artifact[
                    "q12_packet_charge_sum_partition_fingerprint_audit"
                ]["partition_summary"]["size_compatible_element_bijection_count"],
                "q42_packet239_tie_break_status": artifact[
                    "q42_packet239_q12_seed_anchor_tie_break_audit"
                ]["status"],
                "q42_packet239_tie_break_selected_drop": artifact[
                    "q42_packet239_q12_seed_anchor_tie_break_audit"
                ]["tie_break_summary"][
                    "selected_drop_q42_class_by_q12_seed_anchor"
                ],
                "q42_packet239_tie_break_rejected_drop": artifact[
                    "q42_packet239_q12_seed_anchor_tie_break_audit"
                ]["tie_break_summary"][
                    "rejected_drop_q42_class_by_q12_seed_anchor"
                ],
                "q42_packet239_tie_break_packet_id": artifact[
                    "q42_packet239_q12_seed_anchor_tie_break_audit"
                ]["tie_break_summary"]["packet239_packet_id"],
                "outstanding_boundary_count": artifact["proof_obligation_inventory"][
                    "outstanding_boundary_count"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
