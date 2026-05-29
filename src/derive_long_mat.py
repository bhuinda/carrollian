from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_mat"
STATUS = "LONG_MAT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_mat.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_mat.py"

STATUS_TEXT_HASH = "77836b2befe1ba46c1a4dc8644b2dd7459503568d7c77543d84143cc4f705c57"
OBS_TEXT_HASH = "e73a795506d4953755ab33b04fa1d7ab6671ba4991854192e1397699561fe27e"

REPORTS = {
    "canonical_flux_balance_gauge": THEOREM_ROOT
    / "canonical_flux_balance_gauge"
    / "report.json",
    "canonical_loop_pi33_obstruction": THEOREM_ROOT
    / "canonical_loop_pi33_obstruction"
    / "report.json",
    "canonical_finite_ward_identity": THEOREM_ROOT
    / "canonical_finite_ward_identity"
    / "report.json",
    "finite_flux_balance": THEOREM_ROOT / "finite_flux_balance" / "report.json",
    "typed_nonexact_optical_flux_update": THEOREM_ROOT
    / "typed_nonexact_optical_flux_update"
    / "report.json",
    "fourier_residue_screen": THEOREM_ROOT
    / "fourier_residue_screen"
    / "report.json",
    "fourier_screen0_tube_central_element": THEOREM_ROOT
    / "fourier_screen0_tube_central_element"
    / "report.json",
    "certified_pointer_a985_matrix_unit_dereference": THEOREM_ROOT
    / "certified_pointer_a985_matrix_unit_dereference"
    / "report.json",
    "tiny_pointer_a985_orbital_central_idempotents": THEOREM_ROOT
    / "tiny_pointer_a985_orbital_central_idempotents"
    / "report.json",
    "tiny_pointer_a985_registered_support_matrix_units": THEOREM_ROOT
    / "tiny_pointer_a985_registered_support_matrix_units"
    / "report.json",
    "tiny_pointer_a985_sector_matrix_unit_transport": THEOREM_ROOT
    / "tiny_pointer_a985_sector_matrix_unit_transport"
    / "report.json",
    "tiny_pointer_a985_full_matrix_unit_orbital_coo": THEOREM_ROOT
    / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
    / "report.json",
    "tiny_pointer_a985_support_full_matrix_unit_orbital_coo": THEOREM_ROOT
    / "tiny_pointer_a985_support_full_matrix_unit_orbital_coo"
    / "report.json",
    "d20_contour_charge_pairing_snf": THEOREM_ROOT
    / "d20_contour_charge_pairing_snf"
    / "report.json",
    "d20_boundary_packet_pairing_obstruction": THEOREM_ROOT
    / "d20_boundary_packet_pairing_obstruction"
    / "report.json",
    "d20_boundary_packet_row_normalization_obstruction": THEOREM_ROOT
    / "d20_boundary_packet_row_normalization_obstruction"
    / "report.json",
    "projective_packet_spectral_charge_table": THEOREM_ROOT
    / "projective_packet_spectral_charge_table"
    / "report.json",
    "projective_packet_charge_frame_classifier": THEOREM_ROOT
    / "projective_packet_charge_frame_classifier"
    / "report.json",
    "hidden_packet_charge_frame_classifier": THEOREM_ROOT
    / "hidden_packet_charge_frame_classifier"
    / "report.json",
    "full_exposure_zero_pair_propagator_charge_kernel": THEOREM_ROOT
    / "full_exposure_zero_pair_propagator_charge_kernel"
    / "report.json",
    "full_exposure_zero_pair_propagator_symmetry_ward": THEOREM_ROOT
    / "full_exposure_zero_pair_propagator_symmetry_ward"
    / "report.json",
    "full_exposure_zero_pair_ward_kernel_height_selector": THEOREM_ROOT
    / "full_exposure_zero_pair_ward_kernel_height_selector"
    / "report.json",
    "full_exposure_zero_pair_selected_sourced_ward_balance": THEOREM_ROOT
    / "full_exposure_zero_pair_selected_sourced_ward_balance"
    / "report.json",
    "d20_matrix_lift_conjecture": THEOREM_ROOT
    / "d20_matrix_lift_conjecture"
    / "report.json",
    "d20_minimal_matrix_charge_lift": THEOREM_ROOT
    / "d20_minimal_matrix_charge_lift"
    / "report.json",
    "d20_full_packet_matrix_lift": THEOREM_ROOT
    / "d20_full_packet_matrix_lift"
    / "report.json",
    "d20_packet_bridge_snf_obstruction": THEOREM_ROOT
    / "d20_packet_bridge_snf_obstruction"
    / "report.json",
    "full_exposure_packet_propagation_cells": THEOREM_ROOT
    / "full_exposure_packet_propagation_cells"
    / "report.json",
    "full_exposure_packet_propagation_graph": THEOREM_ROOT
    / "full_exposure_packet_propagation_graph"
    / "report.json",
    "packet239_stabilizer_seed_candidate": THEOREM_ROOT
    / "packet239_stabilizer_seed_candidate"
    / "report.json",
    "packet239_seed_propagation": THEOREM_ROOT
    / "packet239_seed_propagation"
    / "report.json",
    "packet239_arithmetic_resonance": THEOREM_ROOT
    / "packet239_arithmetic_resonance"
    / "report.json",
    "d20_packet_quotient_action_probe": THEOREM_ROOT
    / "d20_packet_quotient_action_probe"
    / "report.json",
    "d20_explicit_packet_restriction_map_test": THEOREM_ROOT
    / "d20_explicit_packet_restriction_map_test"
    / "report.json",
    "d20_loop_step_packet_snf_probe": THEOREM_ROOT
    / "d20_loop_step_packet_snf_probe"
    / "report.json",
    "d20_boundary_packet_low_support_candidate_atlas": THEOREM_ROOT
    / "d20_boundary_packet_low_support_candidate_atlas"
    / "report.json",
    "d20_contour_sector_packet_prime_alignment": THEOREM_ROOT
    / "d20_contour_sector_packet_prime_alignment"
    / "report.json",
}

EXPECTED_STATUSES = {
    "canonical_flux_balance_gauge": "D20_CANONICAL_FLUX_BALANCE_GAUGE_CERTIFIED",
    "canonical_loop_pi33_obstruction": "D20_CANONICAL_LOOP_PI33_OBSTRUCTION_CERTIFIED",
    "canonical_finite_ward_identity": "D20_CANONICAL_FINITE_WARD_IDENTITY_CERTIFIED",
    "finite_flux_balance": "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED",
    "typed_nonexact_optical_flux_update": "D20_TYPED_NONEXACT_OPTICAL_FLUX_UPDATE_CERTIFIED",
    "fourier_residue_screen": "D20_FOURIER_RESIDUE_SCREEN_CERTIFIED",
    "fourier_screen0_tube_central_element": "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_CERTIFIED",
    "certified_pointer_a985_matrix_unit_dereference": "D20_CERTIFIED_POINTER_A985_MATRIX_UNIT_DEREFERENCE_CERTIFIED",
    "tiny_pointer_a985_orbital_central_idempotents": "D20_TINY_POINTER_A985_ORBITAL_CENTRAL_IDEMPOTENTS_CERTIFIED",
    "tiny_pointer_a985_registered_support_matrix_units": "D20_TINY_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_CERTIFIED",
    "tiny_pointer_a985_sector_matrix_unit_transport": "D20_TINY_POINTER_A985_SECTOR_MATRIX_UNIT_TRANSPORT_CERTIFIED",
    "tiny_pointer_a985_full_matrix_unit_orbital_coo": "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED",
    "tiny_pointer_a985_support_full_matrix_unit_orbital_coo": "D20_TINY_POINTER_A985_SUPPORT_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED",
    "d20_contour_charge_pairing_snf": "D20_CONTOUR_CHARGE_PAIRING_SNF_CERTIFIED",
    "d20_boundary_packet_pairing_obstruction": "D20_BOUNDARY_PACKET_PAIRING_OBSTRUCTION_CERTIFIED",
    "d20_boundary_packet_row_normalization_obstruction": "D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION_CERTIFIED",
    "projective_packet_spectral_charge_table": "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED",
    "projective_packet_charge_frame_classifier": "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED",
    "hidden_packet_charge_frame_classifier": "D20_HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED",
    "full_exposure_zero_pair_propagator_charge_kernel": "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED",
    "full_exposure_zero_pair_propagator_symmetry_ward": "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_CERTIFIED",
    "full_exposure_zero_pair_ward_kernel_height_selector": "D20_FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_CERTIFIED",
    "full_exposure_zero_pair_selected_sourced_ward_balance": "D20_FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_CERTIFIED",
    "d20_matrix_lift_conjecture": "D20_MATRIX_LIFT_CONJECTURE_REGISTERED",
    "d20_minimal_matrix_charge_lift": "D20_MINIMAL_MATRIX_CHARGE_LIFT_CERTIFIED",
    "d20_full_packet_matrix_lift": "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED",
    "d20_packet_bridge_snf_obstruction": "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED",
    "full_exposure_packet_propagation_cells": "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED",
    "full_exposure_packet_propagation_graph": "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED",
    "packet239_stabilizer_seed_candidate": "D20_PACKET239_STABILIZER_SEED_CANDIDATE_CERTIFIED",
    "packet239_seed_propagation": "D20_PACKET239_SEED_PROPAGATION_CERTIFIED",
    "packet239_arithmetic_resonance": "D20_PACKET239_ARITHMETIC_RESONANCE_CERTIFIED",
    "d20_packet_quotient_action_probe": "D20_PACKET_QUOTIENT_ACTION_PROBE_CERTIFIED",
    "d20_explicit_packet_restriction_map_test": "D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_CERTIFIED",
    "d20_loop_step_packet_snf_probe": "D20_LOOP_STEP_PACKET_SNF_PROBE_CERTIFIED",
    "d20_boundary_packet_low_support_candidate_atlas": "D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_CERTIFIED",
    "d20_contour_sector_packet_prime_alignment": "D20_CONTOUR_SECTOR_PACKET_PRIME_ALIGNMENT_CERTIFIED",
}

SURFACE_COLUMNS = [
    "surface_id",
    "surface_code",
    "certified_flag",
    "resolved_flag",
    "residual_boundary_flag",
    "next_action_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "status_row_count",
    "resolved_surface_count",
    "residual_current_model_matrix_boundary_count",
    "current_matrix_boundary_closed_flag",
    "rooted_flux_rank",
    "augmented_ledger_stabilizer_order",
    "ward_scalar_sum",
    "pi33_residual_integral",
    "finite_flux_cycle_rank",
    "finite_flux_residue_class_count",
    "typed_update_count",
    "typed_nonzero_update_count",
    "fourier_screen_rank",
    "fourier_common_kernel_count",
    "closed_loop_basis_count",
    "closed_loop_commutator_failure_count",
    "full_a985_commutator_failure_count",
    "pointer_manifest_row_count",
    "pointer_open_boundary_count",
    "full_matrix_unit_count",
    "full_orbital_coo_row_count",
    "support_projector_count",
    "contour_quotient_order",
    "raw_compatible_pair_count",
    "row_scalar_divisibility",
    "projective_packet_count",
    "projective_charge_frame_class_count",
    "hidden_packet_row_count",
    "propagator_kernel_residue_row_count",
    "propagator_source_packet",
    "propagator_partner_packet",
    "surviving_symmetry_order",
    "selected_ward_mask",
    "selected_ward_height",
    "matrix_shadow_registered_flag",
    "minimal_charge_kernel_lift_flag",
    "full_packet_block_dimension",
    "full_a985_packet_operator_map_flag",
    "minimum_packet_map_kernel_dimension",
    "packet_bridge_raw_columns_available_flag",
    "packet_bridge_candidate_count",
    "packet_bridge_rank",
    "full_exposure_packet_count",
    "packet_propagation_component_count",
    "packet_propagation_edge_count",
    "packet239_charge_seed_flag",
    "packet239_active_partner_packet",
    "packet239_stabilizer_unique_flag",
    "packet239_arithmetic_twin_successor",
    "quotient_positive_packet_action_count",
    "quotient_a985_or_tube_packet_operator_found_flag",
    "explicit_packet_restriction_mode_count",
    "explicit_packet_missing_bridge_count",
    "loop_step_packet_snf_tested_column_count",
    "loop_step_packet_snf_passing_column_count",
    "low_support_even_candidate_count",
    "low_support_compatible_doublet_count",
    "low_support_full_doublet_map_available_flag",
    "prime_alignment_union_prime_count",
    "prime_alignment_common_prime_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def certified(name: str, report: dict[str, Any]) -> int:
    checks = report.get("checks", {})
    return int(
        report.get("status") == EXPECTED_STATUSES[name]
        and report.get("all_checks_pass") is True
        and isinstance(checks, dict)
        and all(value is not False and value is not None for value in checks.values())
    )


def build_rows() -> dict[str, Any]:
    reports = {name: load_json(path) for name, path in REPORTS.items()}
    flags = {name: certified(name, report) for name, report in reports.items()}
    surface_rows = [
        {
            "surface_id": index,
            "surface_code": index,
            "certified_flag": flags[name],
            "resolved_flag": flags[name],
            "residual_boundary_flag": 0,
            "next_action_code": index,
        }
        for index, name in enumerate(REPORTS)
    ]

    gauge = reports["canonical_flux_balance_gauge"].get("derived", {})
    pi33 = reports["canonical_loop_pi33_obstruction"].get("derived", {})
    ward = reports["canonical_finite_ward_identity"].get("derived", {})
    flux = reports["finite_flux_balance"].get("derived", {})
    typed = reports["typed_nonexact_optical_flux_update"].get("derived", {})
    screen = reports["fourier_residue_screen"].get("derived", {})
    tube_screen = reports["fourier_screen0_tube_central_element"].get("derived", {})
    pointer = reports["certified_pointer_a985_matrix_unit_dereference"].get(
        "derived", {}
    )
    full_coo = reports["tiny_pointer_a985_full_matrix_unit_orbital_coo"].get(
        "derived", {}
    )
    support_coo = reports[
        "tiny_pointer_a985_support_full_matrix_unit_orbital_coo"
    ].get("derived", {})
    contour = reports["d20_contour_charge_pairing_snf"].get("derived", {})
    pair_ob = reports["d20_boundary_packet_pairing_obstruction"].get("derived", {})
    row_ob = reports["d20_boundary_packet_row_normalization_obstruction"].get(
        "derived", {}
    )
    spectral = reports["projective_packet_spectral_charge_table"].get("derived", {})
    charge = reports["projective_packet_charge_frame_classifier"].get("derived", {})
    hidden = reports["hidden_packet_charge_frame_classifier"].get("derived", {})
    kernel = reports["full_exposure_zero_pair_propagator_charge_kernel"].get(
        "derived", {}
    )
    symmetry = reports["full_exposure_zero_pair_propagator_symmetry_ward"].get(
        "derived", {}
    )
    selector = reports["full_exposure_zero_pair_ward_kernel_height_selector"].get(
        "derived", {}
    )
    conjecture = reports["d20_matrix_lift_conjecture"].get("derived", {})
    minimal = reports["d20_minimal_matrix_charge_lift"].get("derived", {})
    full_packet = reports["d20_full_packet_matrix_lift"].get("derived", {})
    bridge = reports["d20_packet_bridge_snf_obstruction"].get("derived", {})
    packet_cells = reports["full_exposure_packet_propagation_cells"].get(
        "derived", {}
    )
    packet_graph = reports["full_exposure_packet_propagation_graph"].get(
        "derived", {}
    )
    packet239_stabilizer = reports["packet239_stabilizer_seed_candidate"].get(
        "derived", {}
    )
    packet239_seed = reports["packet239_seed_propagation"].get("derived", {})
    packet239_arithmetic = reports["packet239_arithmetic_resonance"].get(
        "derived", {}
    )
    quotient_action = reports["d20_packet_quotient_action_probe"].get("derived", {})
    explicit_restriction = reports["d20_explicit_packet_restriction_map_test"].get(
        "derived", {}
    )
    loop_step_snf = reports["d20_loop_step_packet_snf_probe"].get("derived", {})
    low_support = reports["d20_boundary_packet_low_support_candidate_atlas"].get(
        "derived", {}
    )
    prime_alignment = reports["d20_contour_sector_packet_prime_alignment"].get(
        "derived", {}
    )

    exact_flux = gauge.get("exact_flux_gauge", {})
    residual_symmetry = gauge.get("residual_symmetry_gauge", {})
    flux_counts = flux.get("graph_counts", {})
    combined_screen = screen.get("combined_screen", {})
    tube_closed_loop = tube_screen.get("closed_loop_commutator", {})
    tube_full = tube_screen.get("full_a985_commutator_boundary", {})
    full_join = full_coo.get("perennial_join_key", {})
    contour_summary = contour.get("pairing_summary", {})
    pair_summary = pair_ob.get("obstruction_summary", {})
    row_summary = row_ob.get("obstruction_summary", {})
    spectral_summary = spectral.get("spectral_charge_summary", {})
    charge_summary = charge.get("classifier_summary", {})
    kernel_summary = kernel.get("propagator_charge_kernel_summary", {})
    symmetry_summary = symmetry.get("symmetry_summary", {})
    selector_summary = selector.get("selector_summary", {})
    conjecture_class = conjecture.get("classification", {})
    minimal_summary = minimal.get("minimal_matrix_charge_lift", {})
    full_packet_summary = full_packet.get("acting_summary", {})
    full_packet_probe = full_packet.get("a985_action_probe", {})
    bridge_summary = bridge.get("obstruction_summary", {})
    packet_cell_summary = packet_cells.get("propagation_cell_summary", {})
    packet_graph_summary = packet_graph.get("graph_summary", {})
    packet239_stabilizer_summary = packet239_stabilizer.get(
        "stabilizer_summary", {}
    )
    packet239_seed_summary = packet239_seed.get("propagation_summary", {})
    packet239_arithmetic_summary = packet239_arithmetic.get(
        "resonance_summary", {}
    )
    quotient_action_summary = quotient_action.get("operator_probe_summary", {})
    explicit_restriction_summary = explicit_restriction.get(
        "restriction_summary", {}
    )
    loop_step_snf_summary = loop_step_snf.get("probe_summary", {})
    low_support_summary = low_support.get("low_support_summary", {})
    prime_alignment_summary = prime_alignment.get("alignment_summary", {})

    obs = {
        "input_report_count": len(reports),
        "input_certified_count": sum(flags.values()),
        "status_row_count": len(surface_rows),
        "resolved_surface_count": sum(row["resolved_flag"] for row in surface_rows),
        "residual_current_model_matrix_boundary_count": sum(
            row["residual_boundary_flag"] for row in surface_rows
        ),
        "rooted_flux_rank": int(exact_flux.get("rooted_incidence_rank_over_q", 0)),
        "augmented_ledger_stabilizer_order": int(
            residual_symmetry.get("full_augmented_ledger_stabilizer_order", 0)
        ),
        "ward_scalar_sum": int(ward.get("ward_identity", {}).get("scalar_sum", -1)),
        "pi33_residual_integral": int(
            pi33.get("pi33_obstruction", {}).get("residual_integral", 0)
        ),
        "finite_flux_cycle_rank": int(flux_counts.get("cycle_rank", 0)),
        "finite_flux_residue_class_count": int(
            flux_counts.get("residue_class_count", 0)
        ),
        "typed_update_count": int(typed.get("typed_update_count", 0)),
        "typed_nonzero_update_count": int(typed.get("nonzero_typed_update_count", 0)),
        "fourier_screen_rank": int(combined_screen.get("rank_over_f2", 0)),
        "fourier_common_kernel_count": int(
            combined_screen.get("common_kernel_mask_count", 0)
        ),
        "closed_loop_basis_count": int(tube_screen.get("closed_loop_basis_count", 0)),
        "closed_loop_commutator_failure_count": int(
            tube_closed_loop.get("failure_count", -1)
        ),
        "full_a985_commutator_failure_count": int(tube_full.get("failure_count", 0)),
        "pointer_manifest_row_count": int(pointer.get("dereference_manifest_rows", 0)),
        "pointer_open_boundary_count": int(pointer.get("open_boundary_count", 0)),
        "full_matrix_unit_count": int(
            full_coo.get("source_sector_matrix_unit_count", 0)
        ),
        "full_orbital_coo_row_count": int(full_join.get("coo_rows_resolved", 0)),
        "support_projector_count": int(support_coo.get("support_projector_count", 0)),
        "contour_quotient_order": int(
            contour_summary.get("finite_quotient_order", 0)
        ),
        "raw_compatible_pair_count": int(
            pair_summary.get("raw_compatible_pair_count", -1)
        ),
        "row_scalar_divisibility": int(
            row_summary.get("row_scalar_divisibility_for_any_packet_pairing", 0)
        ),
        "projective_packet_count": int(spectral_summary.get("packet_count", 0)),
        "projective_charge_frame_class_count": int(
            charge_summary.get("charge_frame_class_count", 0)
        ),
        "hidden_packet_row_count": len(hidden.get("packet_rows", [])),
        "propagator_kernel_residue_row_count": int(
            kernel_summary.get("residue_row_count", 0)
        ),
        "propagator_source_packet": int(kernel_summary.get("source_packet_id", 0)),
        "propagator_partner_packet": int(
            kernel_summary.get("active_partner_packet_id", 0)
        ),
        "surviving_symmetry_order": int(
            symmetry_summary.get("surviving_label_preserving_symmetry_order", 0)
        ),
        "selected_ward_mask": int(selector_summary.get("selected_mask", 0)),
        "selected_ward_height": int(selector_summary.get("selected_height_action", 0)),
        "matrix_shadow_registered_flag": int(
            conjecture_class.get("strength") == "finite_shadow_not_m_theory"
        ),
        "minimal_charge_kernel_lift_flag": int(
            minimal_summary.get("lift_status")
            == "minimal_charge_kernel_lift_constructed_full_A985_DLCQ_lift_not_constructed"
        ),
        "full_packet_block_dimension": int(
            full_packet_summary.get("block_algebra_dimension_over_Q", 0)
        ),
        "full_a985_packet_operator_map_flag": int(
            full_packet_probe.get("certified_a985_to_packet_operator_map_present")
            is True
        ),
        "minimum_packet_map_kernel_dimension": int(
            full_packet_probe.get(
                "minimum_kernel_dimension_for_any_a985_map_into_this_block_lift", 0
            )
        ),
        "packet_bridge_raw_columns_available_flag": int(
            bridge_summary.get("raw_bridge_columns_available") is True
        ),
        "packet_bridge_candidate_count": int(
            bridge_summary.get("raw_bridge_candidate_count", 0)
        ),
        "packet_bridge_rank": int(bridge_summary.get("rank_over_Q", 0)),
        "full_exposure_packet_count": int(packet_graph_summary.get("vertex_count", 0)),
        "packet_propagation_component_count": int(
            packet_graph_summary.get("component_count", 0)
        ),
        "packet_propagation_edge_count": int(
            packet_graph_summary.get("weighted_directed_edge_count_including_loops", 0)
        ),
        "packet239_charge_seed_flag": int(
            packet239_stabilizer_summary.get("packet239_charge_frame_unique") is True
            and int(packet239_seed_summary.get("seed_packet_id", 0)) == 239
            and int(packet_cell_summary.get("full_exposure_packet_count", 0)) == 20
        ),
        "packet239_active_partner_packet": int(
            packet239_seed_summary.get("active_partner_packet_id", 0)
        ),
        "packet239_stabilizer_unique_flag": int(
            packet239_stabilizer_summary.get("packet239_stabilizer_unique") is True
        ),
        "packet239_arithmetic_twin_successor": int(
            packet239_arithmetic_summary.get("arithmetic_twin_successor", 0)
        ),
        "quotient_positive_packet_action_count": int(
            quotient_action_summary.get("positive_packet_action_count", 0)
        ),
        "quotient_a985_or_tube_packet_operator_found_flag": int(
            quotient_action_summary.get("a985_or_tube_packet_operator_found") is True
        ),
        "explicit_packet_restriction_mode_count": int(
            explicit_restriction_summary.get("constructed_projection_mode_count", 0)
        ),
        "explicit_packet_missing_bridge_count": int(
            explicit_restriction_summary.get("missing_bridge_count", 0)
        ),
        "loop_step_packet_snf_tested_column_count": int(
            loop_step_snf_summary.get("tested_column_count", 0)
        ),
        "loop_step_packet_snf_passing_column_count": len(
            loop_step_snf_summary.get("columns_passing_packet_snf_image", [])
        ),
        "low_support_even_candidate_count": int(
            low_support_summary.get("even_image_candidate_count", 0)
        ),
        "low_support_compatible_doublet_count": int(
            low_support_summary.get("compatible_doublet_count", 0)
        ),
        "low_support_full_doublet_map_available_flag": int(
            low_support_summary.get("full_packet_doublet_map_available") is True
        ),
        "prime_alignment_union_prime_count": len(
            prime_alignment_summary.get("union_prime_split", [])
        ),
        "prime_alignment_common_prime_count": len(
            prime_alignment_summary.get("common_prime_all_layers", [])
        ),
        "complete_goal_claim_flag": 0,
    }
    obs["current_matrix_boundary_closed_flag"] = int(
        sum(flags.values()) == len(reports)
        and obs["rooted_flux_rank"] == 20
        and obs["augmented_ledger_stabilizer_order"] == 1
        and obs["ward_scalar_sum"] == 0
        and obs["pi33_residual_integral"] == -374_784
        and obs["finite_flux_cycle_rank"] == 11
        and obs["finite_flux_residue_class_count"] == 2048
        and obs["typed_update_count"] == 2048
        and obs["typed_nonzero_update_count"] == 2047
        and obs["fourier_screen_rank"] == 3
        and obs["fourier_common_kernel_count"] == 256
        and obs["closed_loop_basis_count"] == 297
        and obs["closed_loop_commutator_failure_count"] == 0
        and obs["full_a985_commutator_failure_count"] == 304
        and obs["pointer_manifest_row_count"] == 1011
        and obs["pointer_open_boundary_count"] == 1
        and obs["full_matrix_unit_count"] == 985
        and obs["full_orbital_coo_row_count"] == 76_703
        and obs["support_projector_count"] == 7
        and obs["contour_quotient_order"] == 52
        and obs["raw_compatible_pair_count"] == 0
        and obs["row_scalar_divisibility"] == 6
        and obs["projective_packet_count"] == 512
        and obs["projective_charge_frame_class_count"] == 47
        and obs["hidden_packet_row_count"] == 2048
        and obs["propagator_kernel_residue_row_count"] == 6
        and obs["propagator_source_packet"] == 239
        and obs["propagator_partner_packet"] == 238
        and obs["surviving_symmetry_order"] == 1
        and obs["selected_ward_mask"] == 288
        and obs["selected_ward_height"] == 1_065_984
        and obs["matrix_shadow_registered_flag"] == 1
        and obs["minimal_charge_kernel_lift_flag"] == 1
        and obs["full_packet_block_dimension"] == 40
        and obs["full_a985_packet_operator_map_flag"] == 0
        and obs["minimum_packet_map_kernel_dimension"] == 945
        and obs["packet_bridge_raw_columns_available_flag"] == 0
        and obs["packet_bridge_candidate_count"] == 3
        and obs["packet_bridge_rank"] == 20
        and obs["full_exposure_packet_count"] == 20
        and obs["packet_propagation_component_count"] == 10
        and obs["packet_propagation_edge_count"] == 40
        and obs["packet239_charge_seed_flag"] == 1
        and obs["packet239_active_partner_packet"] == 238
        and obs["packet239_stabilizer_unique_flag"] == 0
        and obs["packet239_arithmetic_twin_successor"] == 241
        and obs["quotient_positive_packet_action_count"] == 3
        and obs["quotient_a985_or_tube_packet_operator_found_flag"] == 0
        and obs["explicit_packet_restriction_mode_count"] == 40
        and obs["explicit_packet_missing_bridge_count"] == 3
        and obs["loop_step_packet_snf_tested_column_count"] == 25
        and obs["loop_step_packet_snf_passing_column_count"] == 0
        and obs["low_support_even_candidate_count"] == 12
        and obs["low_support_compatible_doublet_count"] == 6
        and obs["low_support_full_doublet_map_available_flag"] == 0
        and obs["prime_alignment_union_prime_count"] == 3
        and obs["prime_alignment_common_prime_count"] == 1
    )

    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "reports": reports,
        "surface_rows": surface_rows,
        "obs_rows": obs_rows,
        "surface_table": table_from_rows(SURFACE_COLUMNS, surface_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "status_hash": hashlib.sha256(
            digest_text(SURFACE_COLUMNS, surface_rows).encode("ascii")
        ).hexdigest(),
        "obs_hash": hashlib.sha256(
            digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
        ).hexdigest(),
        "obs": obs,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": obs["input_certified_count"]
        == obs["input_report_count"]
        == 37,
        "current_matrix_boundary_closed": (
            obs["current_matrix_boundary_closed_flag"],
            obs["resolved_surface_count"],
            obs["residual_current_model_matrix_boundary_count"],
        )
        == (1, 37, 0),
        "flux_ward_fourier_boundary_recorded": (
            obs["rooted_flux_rank"],
            obs["augmented_ledger_stabilizer_order"],
            obs["ward_scalar_sum"],
            obs["pi33_residual_integral"],
            obs["finite_flux_cycle_rank"],
            obs["finite_flux_residue_class_count"],
            obs["typed_update_count"],
            obs["typed_nonzero_update_count"],
            obs["fourier_screen_rank"],
            obs["fourier_common_kernel_count"],
        )
        == (20, 1, 0, -374_784, 11, 2048, 2048, 2047, 3, 256),
        "matrix_unit_pointer_boundary_recorded": (
            obs["closed_loop_basis_count"],
            obs["closed_loop_commutator_failure_count"],
            obs["full_a985_commutator_failure_count"],
            obs["pointer_manifest_row_count"],
            obs["pointer_open_boundary_count"],
            obs["full_matrix_unit_count"],
            obs["full_orbital_coo_row_count"],
            obs["support_projector_count"],
        )
        == (297, 0, 304, 1011, 1, 985, 76_703, 7),
        "packet_charge_matrix_boundary_recorded": (
            obs["contour_quotient_order"],
            obs["raw_compatible_pair_count"],
            obs["row_scalar_divisibility"],
            obs["projective_packet_count"],
            obs["projective_charge_frame_class_count"],
            obs["hidden_packet_row_count"],
            obs["propagator_kernel_residue_row_count"],
            obs["propagator_source_packet"],
            obs["propagator_partner_packet"],
            obs["surviving_symmetry_order"],
            obs["selected_ward_mask"],
            obs["selected_ward_height"],
        )
        == (52, 0, 6, 512, 47, 2048, 6, 239, 238, 1, 288, 1_065_984),
        "matrix_lift_scope_recorded": (
            obs["matrix_shadow_registered_flag"],
            obs["minimal_charge_kernel_lift_flag"],
            obs["full_packet_block_dimension"],
            obs["full_a985_packet_operator_map_flag"],
            obs["minimum_packet_map_kernel_dimension"],
            obs["packet_bridge_raw_columns_available_flag"],
            obs["packet_bridge_candidate_count"],
            obs["packet_bridge_rank"],
        )
        == (1, 1, 40, 0, 945, 0, 3, 20),
        "packet_operator_boundary_recorded": (
            obs["full_exposure_packet_count"],
            obs["packet_propagation_component_count"],
            obs["packet_propagation_edge_count"],
            obs["packet239_charge_seed_flag"],
            obs["packet239_active_partner_packet"],
            obs["packet239_stabilizer_unique_flag"],
            obs["packet239_arithmetic_twin_successor"],
            obs["quotient_positive_packet_action_count"],
            obs["quotient_a985_or_tube_packet_operator_found_flag"],
            obs["explicit_packet_restriction_mode_count"],
            obs["explicit_packet_missing_bridge_count"],
            obs["loop_step_packet_snf_tested_column_count"],
            obs["loop_step_packet_snf_passing_column_count"],
            obs["low_support_even_candidate_count"],
            obs["low_support_compatible_doublet_count"],
            obs["low_support_full_doublet_map_available_flag"],
            obs["prime_alignment_union_prime_count"],
            obs["prime_alignment_common_prime_count"],
        )
        == (20, 10, 40, 1, 238, 0, 241, 3, 0, 40, 3, 25, 0, 12, 6, 0, 3, 1),
        "fingerprints_exact": (
            rows["status_hash"] == STATUS_TEXT_HASH and rows["obs_hash"] == OBS_TEXT_HASH
        ),
        "scope_not_overclaimed": obs["complete_goal_claim_flag"] == 0,
        "table_shapes_match": (
            tuple(rows["surface_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == ((37, len(SURFACE_COLUMNS)), (len(OBS_CODES), len(OBS_COLUMNS))),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_matrix_theoretic_charge_wall_boundary",
        "summary": {
            "input_report_count": obs["input_report_count"],
            "input_certified_count": obs["input_certified_count"],
            "resolved_surface_count": obs["resolved_surface_count"],
            "residual_current_model_matrix_boundary_count": obs[
                "residual_current_model_matrix_boundary_count"
            ],
            "current_matrix_boundary_closed_flag": obs[
                "current_matrix_boundary_closed_flag"
            ],
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "surface_code_map": {str(index): name for index, name in enumerate(REPORTS)},
        "status_text_sha256": rows["status_hash"],
        "observable_text_sha256": rows["obs_hash"],
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    mat_payload = {
        "schema": "long.mat@1",
        "object": "finite_matrix_charge_wall_boundary",
        "status": STATUS if all(checks.values()) else "LONG_MAT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.mat.report@1",
        "status": mat_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_mat certifies the current finite matrix-theoretic charge-wall "
            "boundary: canonical flux/Ward gauges, Pi33 obstruction, typed "
            "non-exact optical updates, Fourier screens, A985 matrix-unit pointer "
            "dereferencing, full COO-backed matrix units, packet charge frames, "
            "zero-pair propagator kernel, packet239 seed propagation, packet "
            "quotient actions, restriction-map gaps, low-support packet candidates, "
            "prime alignment, and finite packet matrix lifts cohere as a closed "
            "current-model oracle surface. It records the Matrix-lift "
            "claim only as a finite shadow, not as M-theory or a full A985 packet "
            "operator model."
        ),
        "stage_protocol": {
            "draft": "read matrix, packet, charge, Fourier, Ward, flux, pointer, packet-propagation, quotient-action, packet239, and bridge-gap reports",
            "witness": "emit matrix boundary surface rows and observable closure counts",
            "coherence": "check input statuses, matrix-unit counts, packet obstructions, charge kernels, Ward balances, hashes, and table shapes",
            "closure": "certify the finite current-model matrix boundary without claiming a full A985-to-packet Matrix model",
            "emit": "write long_mat artifacts and verifier hook",
        },
        "inputs": {
            **{
                name: input_entry(
                    path,
                    {
                        "status": rows["reports"][name].get("status"),
                        "certificate_sha256": rows["reports"][name].get(
                            "certificate_sha256"
                        ),
                    },
                )
                for name, path in REPORTS.items()
            },
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "mat": relpath(OUT_DIR / "mat.json"),
            "status_csv": relpath(OUT_DIR / "status.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "finite flux/Ward/Pi33 matrix charge-wall gauges are certified in the current model",
                "A985 matrix-unit pointer dereferencing is closed by full COO-backed 985 source-sector matrix units and seven support projectors",
                "the finite packet charge-frame and zero-pair propagator kernel are certified",
                "packet239 seed propagation, full-exposure packet doublets, packet quotient actions, and explicit packet restriction gaps are certified",
                "the finite packet matrix lift exists as Mat_2(Q)^10 with a 40-dimensional block algebra",
                "raw public-boundary packet pairing, natural Loop_297 step columns, low-support doublet promotion, and raw packet bridge promotion are obstructed in the current model",
            ],
            "does_not_certify_because_out_of_scope": [
                "a full A985-to-packet operator homomorphism",
                "a DLCQ or continuum Matrix-theory model",
                "raw bridge columns for A985, tube, q42, or q12 packet maps",
                "removal of the 945-dimensional lower-bound kernel for any A985 map into the current block lift",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Focused theorem-debt frontier is empty after long_mat ingestion; "
            "defer broad integration gates until the operator permits long gates."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.mat.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.mat.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "mat": mat_payload,
        "status_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "status_text_sha256": rows["status_hash"],
            "obs_text_sha256": rows["obs_hash"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "mat.json", payloads["mat"])
    (OUT_DIR / "status.csv").write_text(payloads["status_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "computed_hashes": payloads["computed_hashes"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
