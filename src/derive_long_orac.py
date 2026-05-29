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


THEOREM_ID = "long_orac"
STATUS = "LONG_ORAC_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

LONG_GAPIND_REPORT = PROOF_ROOT / "long_gapind" / "report.json"
LONG_COMP_REPORT = PROOF_ROOT / "long_comp" / "report.json"
LONG_SHEAF_REPORT = PROOF_ROOT / "long_sheaf" / "report.json"
LONG_LINF_REPORT = PROOF_ROOT / "long_linf" / "report.json"
LONG_H16_REPORT = PROOF_ROOT / "long_h16" / "report.json"
LONG_PROF_REPORT = PROOF_ROOT / "long_prof" / "report.json"
LONG_EXT_REPORT = PROOF_ROOT / "long_ext" / "report.json"
LONG_OBJ_REPORT = PROOF_ROOT / "long_obj" / "report.json"
LONG_TENS_REPORT = PROOF_ROOT / "long_tens" / "report.json"
LONG_LIFT_REPORT = PROOF_ROOT / "long_lift" / "report.json"
LONG_RAW_REPORT = PROOF_ROOT / "long_raw" / "report.json"
LONG_PATH_REPORT = PROOF_ROOT / "long_path" / "report.json"
LONG_PATHS_REPORT = PROOF_ROOT / "long_paths" / "report.json"
LONG_MEASURE_REPORT = PROOF_ROOT / "long_measure" / "report.json"
LONG_ORIENT_REPORT = PROOF_ROOT / "long_orient" / "report.json"
LONG_DUAL_REPORT = PROOF_ROOT / "long_dual" / "report.json"
LONG_PROB_REPORT = PROOF_ROOT / "long_prob" / "report.json"
LONG_MART_REPORT = PROOF_ROOT / "long_mart" / "report.json"
LONG_STOP_REPORT = PROOF_ROOT / "long_stop" / "report.json"
LONG_DLIM_REPORT = PROOF_ROOT / "long_dlim" / "report.json"
LONG_INV_REPORT = PROOF_ROOT / "long_inv" / "report.json"
LONG_INV_EXHAUST_REPORT = PROOF_ROOT / "long_inv_exhaust" / "report.json"
LONG_ANOM_REPORT = PROOF_ROOT / "long_anom" / "report.json"
LONG_AUTO_REPORT = PROOF_ROOT / "long_auto" / "report.json"
LONG_MAT_REPORT = PROOF_ROOT / "long_mat" / "report.json"
C985_FINAL_REPORT = PROOF_ROOT / "c985_final_multifusion_certificate" / "report.json"
MATRIX_UNITS_REPORT = (
    THEOREM_ROOT / "tiny_pointer_a985_canonical_sector_matrix_units" / "report.json"
)
SECTOR_CHARACTERS_REPORT = (
    THEOREM_ROOT / "tiny_pointer_a985_canonical_sector_characters" / "report.json"
)
FOURIER_A985_REPORT = THEOREM_ROOT / "fourier_a985_sector_character_candidates" / "report.json"
SECTOR11_FORMAL_REPORT = (
    THEOREM_ROOT / "tube_sandpile_flip_formal_11_extension_test" / "report.json"
)
C2_ANOMALY_REPORT = (
    THEOREM_ROOT
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
    / "report.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_orac.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_orac.py"

REPORTS = {
    "long_gapind": LONG_GAPIND_REPORT,
    "long_comp": LONG_COMP_REPORT,
    "long_sheaf": LONG_SHEAF_REPORT,
    "long_linf": LONG_LINF_REPORT,
    "long_h16": LONG_H16_REPORT,
    "long_prof": LONG_PROF_REPORT,
    "long_ext": LONG_EXT_REPORT,
    "long_obj": LONG_OBJ_REPORT,
    "long_tens": LONG_TENS_REPORT,
    "long_lift": LONG_LIFT_REPORT,
    "long_raw": LONG_RAW_REPORT,
    "long_path": LONG_PATH_REPORT,
    "long_paths": LONG_PATHS_REPORT,
    "long_measure": LONG_MEASURE_REPORT,
    "long_orient": LONG_ORIENT_REPORT,
    "long_dual": LONG_DUAL_REPORT,
    "long_prob": LONG_PROB_REPORT,
    "long_mart": LONG_MART_REPORT,
    "long_stop": LONG_STOP_REPORT,
    "long_dlim": LONG_DLIM_REPORT,
    "long_inv": LONG_INV_REPORT,
    "long_inv_exhaust": LONG_INV_EXHAUST_REPORT,
    "long_anom": LONG_ANOM_REPORT,
    "long_auto": LONG_AUTO_REPORT,
    "long_mat": LONG_MAT_REPORT,
    "c985_final": C985_FINAL_REPORT,
    "matrix_units": MATRIX_UNITS_REPORT,
    "sector_characters": SECTOR_CHARACTERS_REPORT,
    "fourier_a985": FOURIER_A985_REPORT,
    "sector11_formal": SECTOR11_FORMAL_REPORT,
    "c2_anomaly": C2_ANOMALY_REPORT,
}

STATUS_COLUMNS = [
    "surface_id",
    "surface_code",
    "input_certified_flag",
    "resolved_flag",
    "open_boundary_flag",
    "proof_gap_count",
    "next_action_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "status_row_count",
    "resolved_surface_count",
    "open_boundary_count",
    "inventory_update_needed_flag",
    "c985_final_certified_flag",
    "matrix_unit_count",
    "source_sector_count",
    "sector_character_row_count",
    "sector11_transition_mass",
    "sector11_valid_nonempty_extension_count",
    "support_gap_check_count",
    "support_gap_nonnegative_count",
    "sheaf_section_count",
    "lift_horizon",
    "h16_materialized_profunctor_flag",
    "h16_boundary_decision_code",
    "h16_current_model_obstruction_flag",
    "h16_active_frontier_flag",
    "long_prof_object_count",
    "long_prof_profunctor_count",
    "long_prof_compose_violation_count",
    "long_ext_formal_added_row_count",
    "long_ext_genuine_tensor_lookup_flag",
    "long_ext_convolution_shadow_flag",
    "long_obj_gap_row_count",
    "long_obj_source_horizon_gap",
    "long_obj_genuine_extension_flag",
    "long_tens_gap_component_path_count",
    "long_tens_total_component_path_count",
    "long_tens_materialized_path_object_count",
    "long_tens_sum_profunctor_flag",
    "long_lift_active_owner_total",
    "long_lift_owner_cell_total",
    "long_lift_materialized_owner_path_flag",
    "long_lift_raw_line_address_lift_flag",
    "long_raw_support_count",
    "long_raw_coeff_sum",
    "long_raw_materialized_path_flag",
    "long_raw_fiber_positive_count",
    "long_path_path_count",
    "long_path_gap_path_count",
    "long_path_single_witness_flag",
    "long_path_all_raw_paths_flag",
    "long_path_composable_raw_address_flag",
    "long_paths_component_path_total",
    "long_paths_gap_component_path_total",
    "long_paths_selected_witness_count",
    "long_paths_compressed_family_flag",
    "long_paths_materialized_family_flag",
    "long_paths_exact_composable_family_flag",
    "long_measure_scoped_law_flag",
    "long_measure_full_raw_certified_flag",
    "long_measure_full_raw_scope_gap_flag",
    "long_measure_conditional_normalization_count",
    "long_measure_variance_decomp_count",
    "orientation_positive_section_count",
    "orientation_reverse_section_count",
    "orientation_mobius_roundtrip_count",
    "dual_coeff_path_nonzero_count",
    "dual_count_path_nonzero_count",
    "dual_transition_compose_count",
    "prob_path_count",
    "prob_variance_shrink_count",
    "prob_variance_decomp_flag",
    "mart_global_martingale_flag",
    "mart_eventual_submartingale_flag",
    "mart_negative_drift_count",
    "stop_tail_gap_nonnegative_count",
    "stop_stopped_gap_nonnegative_count",
    "stop_grammar_match_flag",
    "dlim_defect_count",
    "dlim_eventual_cone_negative_count",
    "dlim_eventual_cone_level_count",
    "c2_anomaly_counterterm_flag",
    "long_inv_exhaust_current_inventory_flag",
    "long_inv_exhaust_active_frontier_remaining_count",
    "long_anom_resolved_surface_count",
    "long_anom_residual_boundary_count",
    "long_anom_current_suite_closed_flag",
    "long_auto_resolved_surface_count",
    "long_auto_residual_boundary_count",
    "long_auto_current_boundary_closed_flag",
    "long_mat_resolved_surface_count",
    "long_mat_residual_boundary_count",
    "long_mat_current_boundary_closed_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def certified(report: dict[str, Any]) -> int:
    status = str(report.get("status", ""))
    return int(
        report.get("all_checks_pass") is True
        and "FAIL" not in status
        and "PROVISIONAL" not in status
    )


def load_reports() -> dict[str, dict[str, Any]]:
    return {name: load_json(path) for name, path in REPORTS.items()}


def build_rows() -> dict[str, Any]:
    reports = load_reports()
    gapind = reports["long_gapind"].get("witness", {}).get("gap_induction", {})
    comp_current = reports["long_comp"].get("witness", {}).get("current_representation", {})
    sheaf_sections = reports["long_sheaf"].get("witness", {}).get("sections", {})
    sheaf_current = reports["long_sheaf"].get("witness", {}).get("current_representation", {})
    linf_lift = reports["long_linf"].get("witness", {}).get("lift", {})
    linf_cone = reports["long_linf"].get("witness", {}).get("extension_cone", {})
    h16_summary = reports["long_h16"].get("witness", {}).get("summary", {})
    h16_horizon = reports["long_h16"].get("witness", {}).get("horizon16", {})
    prof_objects = reports["long_prof"].get("witness", {}).get("objects", {})
    prof_profunctors = reports["long_prof"].get("witness", {}).get("profunctors", {})
    prof_composition = reports["long_prof"].get("witness", {}).get("composition", {})
    ext_extension = reports["long_ext"].get("witness", {}).get("extension", {})
    ext_flags = reports["long_ext"].get("witness", {}).get("classification_flags", {})
    obj_comparison = reports["long_obj"].get("witness", {}).get("comparison", {})
    obj_gap = reports["long_obj"].get("witness", {}).get("object_gap", {})
    tens_horizons = reports["long_tens"].get("witness", {}).get("horizons", {})
    tens_current = reports["long_tens"].get("witness", {}).get(
        "current_representation", {}
    )
    lift_components = reports["long_lift"].get("witness", {}).get("components", {})
    lift_current = reports["long_lift"].get("witness", {}).get(
        "current_representation", {}
    )
    raw_owner = reports["long_raw"].get("witness", {}).get("raw_owner_assignment", {})
    raw_fibers = reports["long_raw"].get("witness", {}).get("fibers", {})
    raw_current = reports["long_raw"].get("witness", {}).get(
        "current_representation", {}
    )
    path_paths = reports["long_path"].get("witness", {}).get("paths", {})
    path_current = reports["long_path"].get("witness", {}).get(
        "current_representation", {}
    )
    paths_summary = reports["long_paths"].get("witness", {}).get("summary", {})
    measure_summary = reports["long_measure"].get("witness", {}).get("summary", {})
    orient_moments = reports["long_orient"].get("witness", {}).get("component_moments", {})
    orient_mobius = reports["long_orient"].get("witness", {}).get("mobius", {})
    dual_path = reports["long_dual"].get("witness", {}).get("path_composition", {})
    dual_transition = reports["long_dual"].get("witness", {}).get(
        "transition_composition", {}
    )
    prob_measure = reports["long_prob"].get("witness", {}).get("measure", {})
    prob_curve = reports["long_prob"].get("witness", {}).get("conditional_lln_curve", {})
    prob_decomp = reports["long_prob"].get("witness", {}).get(
        "variance_decomposition", {}
    )
    mart_current = reports["long_mart"].get("witness", {}).get("current_representation", {})
    mart_drift = reports["long_mart"].get("witness", {}).get("drift", {})
    stop_tail = reports["long_stop"].get("witness", {}).get("tail", {})
    stop_stopped = reports["long_stop"].get("witness", {}).get("stopped_tail", {})
    stop_comparison = reports["long_stop"].get("witness", {}).get("comparison", {})
    dlim_defect = reports["long_dlim"].get("witness", {}).get("boundary_defect", {})
    dlim_cone = reports["long_dlim"].get("witness", {}).get("eventual_cone", {})
    c985_witness = reports["c985_final"].get("witness", {})
    matrix_derived = reports["matrix_units"].get("derived", {})
    char_derived = reports["sector_characters"].get("derived", {})
    sector11_derived = reports["sector11_formal"].get("derived", {})
    c2_checks = reports["c2_anomaly"].get("checks", {})
    inv_ranking = reports["long_inv"].get("witness", {}).get("ranking", {})
    inv_exhaust_summary = reports["long_inv_exhaust"].get("witness", {}).get(
        "summary", {}
    )
    anom_summary = reports["long_anom"].get("witness", {}).get("summary", {})
    auto_summary = reports["long_auto"].get("witness", {}).get("summary", {})
    mat_summary = reports["long_mat"].get("witness", {}).get("summary", {})

    sector11_obstruction = sector11_derived.get("state11_transition_obstruction", {})
    formal_scenarios = sector11_derived.get("formal_extension_scenarios", [])
    valid_nonempty_extensions = sum(
        1 for row in formal_scenarios if row.get("valid_nonempty_extension") is True
    )
    inventory_update_needed = int(
        certified(reports["c985_final"]) == 1
        and "long_assoc" in set(str(value) for value in inv_ranking.get("next_codes", {}).values())
    )

    input_certified_count = sum(certified(report) for report in reports.values())
    c985_ok = int(
        certified(reports["c985_final"]) == 1
        and int(c985_witness.get("simple_count", 0)) == 985
        and int(c985_witness.get("zigzag_failure_count", -1)) == 0
    )
    gap_ok = int(
        certified(reports["long_gapind"]) == 1
        and int(gapind.get("finite_gap_check_count", 0))
        == int(gapind.get("finite_gap_nonnegative_count", -1))
        == 131_586
    )
    prof_sample_ok = int(
        certified(reports["long_comp"]) == 1
        and certified(reports["long_sheaf"]) == 1
        and int(comp_current.get("current_alexandrov_zeta_composable_path_flag", 0)) == 1
        and int(sheaf_current.get("current_interval_sheaf_flag", 0)) == 1
    )
    linf_ok = int(
        certified(reports["long_linf"]) == 1
        and int(linf_lift.get("lift_horizon", 0)) == 128
        and int(linf_cone.get("negative_count", -1)) == 0
    )
    matrix_ok = int(
        certified(reports["matrix_units"]) == 1
        and int(matrix_derived.get("matrix_unit_count", 0)) == 985
        and int(matrix_derived.get("source_sector_count", 0)) == 39
    )
    char_shape = char_derived.get("character_table_shape", [0, 0])
    character_ok = int(
        certified(reports["sector_characters"]) == 1
        and list(char_shape) == [39, 985]
    )
    sector11_ok = int(
        certified(reports["sector11_formal"]) == 1
        and int(sector11_obstruction.get("missing_state_pair_count", 0)) == 420
        and valid_nonempty_extensions == 0
    )
    c2_ok = int(
        certified(reports["c2_anomaly"]) == 1
        and c2_checks.get("representative_counterterm_is_exact_coboundary_for_action_and_height")
        is True
    )
    inv_exhaust_ok = int(
        certified(reports["long_inv_exhaust"]) == 1
        and int(inv_exhaust_summary.get("current_inventory_exhaustive_flag", 0)) == 1
        and int(inv_exhaust_summary.get("active_frontier_remaining_count", -1)) == 0
        and int(inv_exhaust_summary.get("absolute_exhaustiveness_claim_flag", -1))
        == 0
    )
    anom_ok = int(
        certified(reports["long_anom"]) == 1
        and int(anom_summary.get("current_anomaly_suite_closed_flag", 0)) == 1
        and int(anom_summary.get("residual_anomaly_boundary_count", -1)) == 0
        and int(anom_summary.get("resolved_surface_count", 0)) == 14
    )
    auto_ok = int(
        certified(reports["long_auto"]) == 1
        and int(auto_summary.get("current_automorphic_boundary_closed_flag", 0)) == 1
        and int(auto_summary.get("residual_auto_boundary_count", -1)) == 0
        and int(auto_summary.get("resolved_surface_count", 0)) == 18
    )
    mat_ok = int(
        certified(reports["long_mat"]) == 1
        and int(mat_summary.get("current_matrix_boundary_closed_flag", 0)) == 1
        and int(
            mat_summary.get("residual_current_model_matrix_boundary_count", -1)
        )
        == 0
        and int(mat_summary.get("resolved_surface_count", 0)) == 37
    )
    h16_ok = int(
        certified(reports["long_h16"]) == 1
        and int(h16_summary.get("materialized_h16_profunctor_flag", -1)) == 0
        and int(h16_summary.get("boundary_decision_code", 0)) == 3
        and int(h16_summary.get("current_model_obstruction_flag", 0)) == 1
        and int(h16_summary.get("active_h16_frontier_flag", -1)) == 0
        and int(h16_horizon.get("sum_state_count", 0)) == 288
        and int(h16_horizon.get("sample_path_count", 0)) == 288
        and int(h16_horizon.get("exact_composable_path_count", -1)) == 0
    )
    prof_ok = int(
        certified(reports["long_prof"]) == 1
        and int(prof_objects.get("count", 0)) == 9
        and int(prof_profunctors.get("count", 0)) == 8
        and int(prof_composition.get("violation_count", -1)) == 0
        and int(prof_composition.get("law_count", 0)) == 92
    )
    ext_ok = int(
        certified(reports["long_ext"]) == 1
        and int(ext_extension.get("existing_prof_row_count", 0)) == 80
        and int(ext_extension.get("formal_added_row_count", 0)) == 208
        and int(ext_flags.get("current_evidence_convolution_shadow_flag", 0)) == 1
        and int(ext_flags.get("current_evidence_genuine_tensor_lookup_flag", -1)) == 0
    )
    obj_ok = int(
        certified(reports["long_obj"]) == 1
        and int(obj_comparison.get("object_gap_row_count", 0)) == 208
        and int(obj_comparison.get("tensor_lookup_object_row_count", 0)) == 80
        and int(obj_gap.get("source_horizon_gap", 0)) == 8
        and int(obj_gap.get("current_evidence_genuine_extension_flag", -1)) == 0
    )
    tens_ok = int(
        certified(reports["long_tens"]) == 1
        and int(tens_horizons.get("gap_component_path_count", 0)) == 64_560_240
        and int(tens_horizons.get("total_component_path_count", 0)) == 64_570_080
        and int(tens_current.get("materialized_component_path_object_count", -1)) == 0
        and int(tens_current.get("current_horizon16_sum_profunctor_flag", -1)) == 0
    )
    lift_ok = int(
        certified(reports["long_lift"]) == 1
        and int(lift_components.get("active_owner_total", 0)) == 51
        and int(lift_components.get("owner_cell_total", 0)) == 749_239
        and int(lift_current.get("current_materialized_owner_path_flag", -1)) == 0
        and int(lift_current.get("current_raw_line_address_lift_flag", -1)) == 0
    )
    raw_ok = int(
        certified(reports["long_raw"]) == 1
        and int(raw_owner.get("raw_tensor_support_count", 0)) == 1_414_965
        and int(raw_owner.get("raw_tensor_coeff_sum", 0)) == 2_537_360
        and int(raw_current.get("current_materialized_raw_path_flag", -1)) == 0
        and int(raw_fibers.get("raw_support_lift_positive_count", 0)) == 288
    )
    path_ok = int(
        certified(reports["long_path"]) == 1
        and int(path_paths.get("path_row_count", 0)) == 288
        and int(path_paths.get("gap_path_count", 0)) == 208
        and int(path_current.get("current_single_witness_per_fiber_flag", 0)) == 1
        and int(path_current.get("current_all_raw_paths_materialized_flag", -1)) == 0
        and int(path_current.get("current_composable_raw_address_path_flag", -1)) == 0
    )
    paths_ok = int(
        certified(reports["long_paths"]) == 1
        and int(paths_summary.get("component_path_total", 0)) == 64_570_080
        and int(paths_summary.get("component_path_gap_total", 0)) == 64_560_240
        and int(paths_summary.get("compressed_raw_product_family_flag", 0)) == 1
        and int(paths_summary.get("materialized_raw_path_family_flag", -1)) == 0
        and int(paths_summary.get("exact_composable_raw_path_family_flag", -1)) == 0
    )
    measure_ok = int(
        certified(reports["long_measure"]) == 1
        and int(measure_summary.get("scoped_probability_law_flag", 0)) == 1
        and int(measure_summary.get("full_raw_measure_certified_flag", -1)) == 0
        and int(measure_summary.get("full_raw_scope_gap_flag", 0)) == 1
        and int(measure_summary.get("conditional_normalization_flag_count", 0)) == 32
        and int(measure_summary.get("variance_decomp_flag_count", 0)) == 2
    )
    orientation_ok = int(
        certified(reports["long_orient"]) == 1
        and int(orient_moments.get("raw_section_count", 0)) == 1_414_965
        and int(orient_moments.get("positive_section_count", 0)) == 477_589
        and int(orient_moments.get("reverse_section_count", 0)) == 937_376
        and int(orient_mobius.get("mobius_roundtrip_flag_count", 0)) == 12
    )
    dual_ok = int(
        certified(reports["long_dual"]) == 1
        and int(dual_path.get("dual_path_coeff_nonzero_count", 0)) == 288
        and int(dual_path.get("dual_path_count_nonzero_count", 0)) == 16
        and int(dual_transition.get("dual_transition_compose_count", 0)) == 2_840
    )
    prob_ok = int(
        certified(reports["long_prob"]) == 1
        and int(prob_measure.get("path_count", 0)) == 288
        and int(prob_curve.get("variance_shrink_flag_count", 0)) == 16
        and prob_decomp.get("variance_decomp_flag") is True
    )
    mart_ok = int(
        certified(reports["long_mart"]) == 1
        and mart_current.get("transport_operator") is True
        and mart_current.get("global_martingale") is False
        and mart_current.get("eventual_submartingale") is True
        and mart_current.get("variance_supermartingale") is True
        and int(mart_drift.get("negative_count", -1)) == 1
    )
    stop_ok = int(
        certified(reports["long_stop"]) == 1
        and int(stop_tail.get("row_count", 0)) == 48
        and int(stop_tail.get("gap_nonnegative_count", 0)) == 48
        and int(stop_stopped.get("row_count", 0)) == 48
        and int(stop_stopped.get("gap_nonnegative_count", 0)) == 48
        and stop_comparison.get("grammar_match_flag") is True
    )
    dlim_ok = int(
        certified(reports["long_dlim"]) == 1
        and int(dlim_defect.get("defect_count", 0)) == 1
        and int(dlim_defect.get("sample_count", 0)) == 1
        and str(dlim_defect.get("drift", "")) == "-3/214"
        and int(dlim_cone.get("negative_count", -1)) == 0
        and int(dlim_cone.get("level_count", 0)) == 14
    )

    status_rows = [
        {
            "surface_id": 0,
            "surface_code": 0,
            "input_certified_flag": c985_ok,
            "resolved_flag": c985_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 0,
            "next_action_code": 0,
        },
        {
            "surface_id": 1,
            "surface_code": 1,
            "input_certified_flag": gap_ok,
            "resolved_flag": gap_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 0,
            "next_action_code": 1,
        },
        {
            "surface_id": 2,
            "surface_code": 2,
            "input_certified_flag": prof_sample_ok,
            "resolved_flag": prof_sample_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 2,
        },
        {
            "surface_id": 3,
            "surface_code": 3,
            "input_certified_flag": linf_ok,
            "resolved_flag": linf_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 3,
        },
        {
            "surface_id": 4,
            "surface_code": 4,
            "input_certified_flag": matrix_ok,
            "resolved_flag": matrix_ok,
            "open_boundary_flag": 0,
            "proof_gap_count": 0,
            "next_action_code": 4,
        },
        {
            "surface_id": 5,
            "surface_code": 5,
            "input_certified_flag": character_ok,
            "resolved_flag": character_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 5,
        },
        {
            "surface_id": 6,
            "surface_code": 6,
            "input_certified_flag": sector11_ok,
            "resolved_flag": sector11_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 6,
        },
        {
            "surface_id": 7,
            "surface_code": 7,
            "input_certified_flag": c2_ok,
            "resolved_flag": c2_ok,
            "open_boundary_flag": 0,
            "proof_gap_count": 0,
            "next_action_code": 7,
        },
        {
            "surface_id": 8,
            "surface_code": 8,
            "input_certified_flag": certified(reports["long_inv"]),
            "resolved_flag": 1 - inventory_update_needed,
            "open_boundary_flag": inventory_update_needed,
            "proof_gap_count": inventory_update_needed,
            "next_action_code": 8,
        },
        {
            "surface_id": 9,
            "surface_code": 9,
            "input_certified_flag": h16_ok,
            "resolved_flag": h16_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 9,
        },
        {
            "surface_id": 10,
            "surface_code": 10,
            "input_certified_flag": orientation_ok,
            "resolved_flag": orientation_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 10,
        },
        {
            "surface_id": 11,
            "surface_code": 11,
            "input_certified_flag": dual_ok,
            "resolved_flag": dual_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 11,
        },
        {
            "surface_id": 12,
            "surface_code": 12,
            "input_certified_flag": prob_ok,
            "resolved_flag": prob_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 12,
        },
        {
            "surface_id": 13,
            "surface_code": 13,
            "input_certified_flag": mart_ok,
            "resolved_flag": mart_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 13,
        },
        {
            "surface_id": 14,
            "surface_code": 14,
            "input_certified_flag": stop_ok,
            "resolved_flag": stop_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 14,
        },
        {
            "surface_id": 15,
            "surface_code": 15,
            "input_certified_flag": dlim_ok,
            "resolved_flag": dlim_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 15,
        },
        {
            "surface_id": 16,
            "surface_code": 16,
            "input_certified_flag": prof_ok,
            "resolved_flag": prof_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 16,
        },
        {
            "surface_id": 17,
            "surface_code": 17,
            "input_certified_flag": ext_ok,
            "resolved_flag": ext_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 17,
        },
        {
            "surface_id": 18,
            "surface_code": 18,
            "input_certified_flag": obj_ok,
            "resolved_flag": obj_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 18,
        },
        {
            "surface_id": 19,
            "surface_code": 19,
            "input_certified_flag": tens_ok,
            "resolved_flag": tens_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 19,
        },
        {
            "surface_id": 20,
            "surface_code": 20,
            "input_certified_flag": lift_ok,
            "resolved_flag": lift_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 20,
        },
        {
            "surface_id": 21,
            "surface_code": 21,
            "input_certified_flag": raw_ok,
            "resolved_flag": raw_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 21,
        },
        {
            "surface_id": 22,
            "surface_code": 22,
            "input_certified_flag": path_ok,
            "resolved_flag": path_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 22,
        },
        {
            "surface_id": 23,
            "surface_code": 23,
            "input_certified_flag": paths_ok,
            "resolved_flag": paths_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 1,
            "next_action_code": 23,
        },
        {
            "surface_id": 24,
            "surface_code": 24,
            "input_certified_flag": measure_ok,
            "resolved_flag": measure_ok,
            "open_boundary_flag": 1,
            "proof_gap_count": 0,
            "next_action_code": 24,
        },
        {
            "surface_id": 25,
            "surface_code": 25,
            "input_certified_flag": inv_exhaust_ok,
            "resolved_flag": inv_exhaust_ok,
            "open_boundary_flag": 0,
            "proof_gap_count": 0,
            "next_action_code": 25,
        },
        {
            "surface_id": 26,
            "surface_code": 26,
            "input_certified_flag": anom_ok,
            "resolved_flag": anom_ok,
            "open_boundary_flag": 0,
            "proof_gap_count": 0,
            "next_action_code": 26,
        },
        {
            "surface_id": 27,
            "surface_code": 27,
            "input_certified_flag": auto_ok,
            "resolved_flag": auto_ok,
            "open_boundary_flag": 0,
            "proof_gap_count": 0,
            "next_action_code": 27,
        },
        {
            "surface_id": 28,
            "surface_code": 28,
            "input_certified_flag": mat_ok,
            "resolved_flag": mat_ok,
            "open_boundary_flag": 0,
            "proof_gap_count": 0,
            "next_action_code": 28,
        },
    ]
    obs = {
        "input_report_count": len(reports),
        "input_certified_count": input_certified_count,
        "status_row_count": len(status_rows),
        "resolved_surface_count": sum(row["resolved_flag"] for row in status_rows),
        "open_boundary_count": sum(row["open_boundary_flag"] for row in status_rows),
        "inventory_update_needed_flag": inventory_update_needed,
        "c985_final_certified_flag": c985_ok,
        "matrix_unit_count": int(matrix_derived.get("matrix_unit_count", 0)),
        "source_sector_count": int(matrix_derived.get("source_sector_count", 0)),
        "sector_character_row_count": int(char_derived.get("character_table_shape", [0, 0])[0])
        * int(char_derived.get("character_table_shape", [0, 0])[1]),
        "sector11_transition_mass": int(sector11_obstruction.get("missing_state_pair_count", 0)),
        "sector11_valid_nonempty_extension_count": valid_nonempty_extensions,
        "support_gap_check_count": int(gapind.get("finite_gap_check_count", 0)),
        "support_gap_nonnegative_count": int(gapind.get("finite_gap_nonnegative_count", 0)),
        "sheaf_section_count": int(sheaf_sections.get("global_section_count", 0)),
        "lift_horizon": int(linf_lift.get("lift_horizon", 0)),
        "h16_materialized_profunctor_flag": int(
            h16_summary.get("materialized_h16_profunctor_flag", -1)
        ),
        "h16_boundary_decision_code": int(h16_summary.get("boundary_decision_code", 0)),
        "h16_current_model_obstruction_flag": int(
            h16_summary.get("current_model_obstruction_flag", 0)
        ),
        "h16_active_frontier_flag": int(
            h16_summary.get("active_h16_frontier_flag", -1)
        ),
        "long_prof_object_count": int(prof_objects.get("count", 0)),
        "long_prof_profunctor_count": int(prof_profunctors.get("count", 0)),
        "long_prof_compose_violation_count": int(
            prof_composition.get("violation_count", -1)
        ),
        "long_ext_formal_added_row_count": int(
            ext_extension.get("formal_added_row_count", 0)
        ),
        "long_ext_genuine_tensor_lookup_flag": int(
            ext_flags.get("current_evidence_genuine_tensor_lookup_flag", -1)
        ),
        "long_ext_convolution_shadow_flag": int(
            ext_flags.get("current_evidence_convolution_shadow_flag", 0)
        ),
        "long_obj_gap_row_count": int(obj_comparison.get("object_gap_row_count", 0)),
        "long_obj_source_horizon_gap": int(obj_gap.get("source_horizon_gap", 0)),
        "long_obj_genuine_extension_flag": int(
            obj_gap.get("current_evidence_genuine_extension_flag", -1)
        ),
        "long_tens_gap_component_path_count": int(
            tens_horizons.get("gap_component_path_count", 0)
        ),
        "long_tens_total_component_path_count": int(
            tens_horizons.get("total_component_path_count", 0)
        ),
        "long_tens_materialized_path_object_count": int(
            tens_current.get("materialized_component_path_object_count", -1)
        ),
        "long_tens_sum_profunctor_flag": int(
            tens_current.get("current_horizon16_sum_profunctor_flag", -1)
        ),
        "long_lift_active_owner_total": int(lift_components.get("active_owner_total", 0)),
        "long_lift_owner_cell_total": int(lift_components.get("owner_cell_total", 0)),
        "long_lift_materialized_owner_path_flag": int(
            lift_current.get("current_materialized_owner_path_flag", -1)
        ),
        "long_lift_raw_line_address_lift_flag": int(
            lift_current.get("current_raw_line_address_lift_flag", -1)
        ),
        "long_raw_support_count": int(raw_owner.get("raw_tensor_support_count", 0)),
        "long_raw_coeff_sum": int(raw_owner.get("raw_tensor_coeff_sum", 0)),
        "long_raw_materialized_path_flag": int(
            raw_current.get("current_materialized_raw_path_flag", -1)
        ),
        "long_raw_fiber_positive_count": int(
            raw_fibers.get("raw_support_lift_positive_count", 0)
        ),
        "long_path_path_count": int(path_paths.get("path_row_count", 0)),
        "long_path_gap_path_count": int(path_paths.get("gap_path_count", 0)),
        "long_path_single_witness_flag": int(
            path_current.get("current_single_witness_per_fiber_flag", 0)
        ),
        "long_path_all_raw_paths_flag": int(
            path_current.get("current_all_raw_paths_materialized_flag", -1)
        ),
        "long_path_composable_raw_address_flag": int(
            path_current.get("current_composable_raw_address_path_flag", -1)
        ),
        "long_paths_component_path_total": int(
            paths_summary.get("component_path_total", 0)
        ),
        "long_paths_gap_component_path_total": int(
            paths_summary.get("component_path_gap_total", 0)
        ),
        "long_paths_selected_witness_count": int(
            paths_summary.get("selected_witness_count", 0)
        ),
        "long_paths_compressed_family_flag": int(
            paths_summary.get("compressed_raw_product_family_flag", 0)
        ),
        "long_paths_materialized_family_flag": int(
            paths_summary.get("materialized_raw_path_family_flag", -1)
        ),
        "long_paths_exact_composable_family_flag": int(
            paths_summary.get("exact_composable_raw_path_family_flag", -1)
        ),
        "long_measure_scoped_law_flag": int(
            measure_summary.get("scoped_probability_law_flag", 0)
        ),
        "long_measure_full_raw_certified_flag": int(
            measure_summary.get("full_raw_measure_certified_flag", -1)
        ),
        "long_measure_full_raw_scope_gap_flag": int(
            measure_summary.get("full_raw_scope_gap_flag", 0)
        ),
        "long_measure_conditional_normalization_count": int(
            measure_summary.get("conditional_normalization_flag_count", 0)
        ),
        "long_measure_variance_decomp_count": int(
            measure_summary.get("variance_decomp_flag_count", 0)
        ),
        "orientation_positive_section_count": int(
            orient_moments.get("positive_section_count", 0)
        ),
        "orientation_reverse_section_count": int(
            orient_moments.get("reverse_section_count", 0)
        ),
        "orientation_mobius_roundtrip_count": int(
            orient_mobius.get("mobius_roundtrip_flag_count", 0)
        ),
        "dual_coeff_path_nonzero_count": int(
            dual_path.get("dual_path_coeff_nonzero_count", 0)
        ),
        "dual_count_path_nonzero_count": int(
            dual_path.get("dual_path_count_nonzero_count", 0)
        ),
        "dual_transition_compose_count": int(
            dual_transition.get("dual_transition_compose_count", 0)
        ),
        "prob_path_count": int(prob_measure.get("path_count", 0)),
        "prob_variance_shrink_count": int(
            prob_curve.get("variance_shrink_flag_count", 0)
        ),
        "prob_variance_decomp_flag": int(prob_decomp.get("variance_decomp_flag") is True),
        "mart_global_martingale_flag": int(mart_current.get("global_martingale") is True),
        "mart_eventual_submartingale_flag": int(
            mart_current.get("eventual_submartingale") is True
        ),
        "mart_negative_drift_count": int(mart_drift.get("negative_count", 0)),
        "stop_tail_gap_nonnegative_count": int(stop_tail.get("gap_nonnegative_count", 0)),
        "stop_stopped_gap_nonnegative_count": int(
            stop_stopped.get("gap_nonnegative_count", 0)
        ),
        "stop_grammar_match_flag": int(stop_comparison.get("grammar_match_flag") is True),
        "dlim_defect_count": int(dlim_defect.get("defect_count", 0)),
        "dlim_eventual_cone_negative_count": int(dlim_cone.get("negative_count", -1)),
        "dlim_eventual_cone_level_count": int(dlim_cone.get("level_count", 0)),
        "c2_anomaly_counterterm_flag": c2_ok,
        "long_inv_exhaust_current_inventory_flag": int(
            inv_exhaust_summary.get("current_inventory_exhaustive_flag", 0)
        ),
        "long_inv_exhaust_active_frontier_remaining_count": int(
            inv_exhaust_summary.get("active_frontier_remaining_count", -1)
        ),
        "long_anom_resolved_surface_count": int(
            anom_summary.get("resolved_surface_count", 0)
        ),
        "long_anom_residual_boundary_count": int(
            anom_summary.get("residual_anomaly_boundary_count", -1)
        ),
        "long_anom_current_suite_closed_flag": int(
            anom_summary.get("current_anomaly_suite_closed_flag", 0)
        ),
        "long_auto_resolved_surface_count": int(
            auto_summary.get("resolved_surface_count", 0)
        ),
        "long_auto_residual_boundary_count": int(
            auto_summary.get("residual_auto_boundary_count", -1)
        ),
        "long_auto_current_boundary_closed_flag": int(
            auto_summary.get("current_automorphic_boundary_closed_flag", 0)
        ),
        "long_mat_resolved_surface_count": int(
            mat_summary.get("resolved_surface_count", 0)
        ),
        "long_mat_residual_boundary_count": int(
            mat_summary.get("residual_current_model_matrix_boundary_count", -1)
        ),
        "long_mat_current_boundary_closed_flag": int(
            mat_summary.get("current_matrix_boundary_closed_flag", 0)
        ),
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    status_hash = hashlib.sha256(
        digest_text(STATUS_COLUMNS, status_rows).encode("ascii")
    ).hexdigest()
    return {
        "reports": reports,
        "status_rows": status_rows,
        "obs_rows": obs_rows,
        "status_table": table_from_rows(STATUS_COLUMNS, status_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "status_hash": status_hash,
        "obs": obs,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": obs["input_certified_count"] == obs["input_report_count"] == 31,
        "c985_oracle_reproducible": obs["c985_final_certified_flag"] == 1,
        "matrix_surface_closed": (
            obs["matrix_unit_count"],
            obs["source_sector_count"],
            obs["sector_character_row_count"],
        )
        == (985, 39, 38_415),
        "sector11_obstruction_closed": (
            obs["sector11_transition_mass"],
            obs["sector11_valid_nonempty_extension_count"],
        )
        == (420, 0),
        "form_gapind_closed": (
            obs["support_gap_check_count"],
            obs["support_gap_nonnegative_count"],
        )
        == (131_586, 131_586),
        "profunctor_witness_sheaf_present": (
            obs["sheaf_section_count"],
            obs["lift_horizon"],
        )
        == (3_128, 128),
        "h16_boundary_recorded": (
            obs["h16_materialized_profunctor_flag"],
            obs["h16_boundary_decision_code"],
            obs["h16_current_model_obstruction_flag"],
            obs["h16_active_frontier_flag"],
        )
        == (0, 3, 1, 0),
        "finite_prof_boundary_recorded": (
            obs["long_prof_object_count"],
            obs["long_prof_profunctor_count"],
            obs["long_prof_compose_violation_count"],
        )
        == (9, 8, 0),
        "formal_extension_shadow_recorded": (
            obs["long_ext_formal_added_row_count"],
            obs["long_ext_genuine_tensor_lookup_flag"],
            obs["long_ext_convolution_shadow_flag"],
        )
        == (208, 0, 1),
        "object_gap_recorded": (
            obs["long_obj_gap_row_count"],
            obs["long_obj_source_horizon_gap"],
            obs["long_obj_genuine_extension_flag"],
        )
        == (208, 8, 0),
        "component_tensor_gap_recorded": (
            obs["long_tens_gap_component_path_count"],
            obs["long_tens_total_component_path_count"],
            obs["long_tens_materialized_path_object_count"],
            obs["long_tens_sum_profunctor_flag"],
        )
        == (64_560_240, 64_570_080, 0, 0),
        "owner_lift_boundary_recorded": (
            obs["long_lift_active_owner_total"],
            obs["long_lift_owner_cell_total"],
            obs["long_lift_materialized_owner_path_flag"],
            obs["long_lift_raw_line_address_lift_flag"],
        )
        == (51, 749_239, 0, 0),
        "raw_lift_boundary_recorded": (
            obs["long_raw_support_count"],
            obs["long_raw_coeff_sum"],
            obs["long_raw_materialized_path_flag"],
            obs["long_raw_fiber_positive_count"],
        )
        == (1_414_965, 2_537_360, 0, 288),
        "single_path_boundary_recorded": (
            obs["long_path_path_count"],
            obs["long_path_gap_path_count"],
            obs["long_path_single_witness_flag"],
            obs["long_path_all_raw_paths_flag"],
            obs["long_path_composable_raw_address_flag"],
        )
        == (288, 208, 1, 0, 0),
        "compressed_paths_recorded": (
            obs["long_paths_component_path_total"],
            obs["long_paths_gap_component_path_total"],
            obs["long_paths_selected_witness_count"],
            obs["long_paths_compressed_family_flag"],
            obs["long_paths_materialized_family_flag"],
            obs["long_paths_exact_composable_family_flag"],
        )
        == (64_570_080, 64_560_240, 288, 1, 0, 0),
        "scoped_measure_boundary_recorded": (
            obs["long_measure_scoped_law_flag"],
            obs["long_measure_full_raw_certified_flag"],
            obs["long_measure_full_raw_scope_gap_flag"],
            obs["long_measure_conditional_normalization_count"],
            obs["long_measure_variance_decomp_count"],
        )
        == (1, 0, 1, 32, 2),
        "orientation_duality_recorded": (
            obs["orientation_positive_section_count"],
            obs["orientation_reverse_section_count"],
            obs["orientation_mobius_roundtrip_count"],
        )
        == (477_589, 937_376, 12),
        "dual_kernel_recorded": (
            obs["dual_coeff_path_nonzero_count"],
            obs["dual_count_path_nonzero_count"],
            obs["dual_transition_compose_count"],
        )
        == (288, 16, 2_840),
        "dual_probability_recorded": (
            obs["prob_path_count"],
            obs["prob_variance_shrink_count"],
            obs["prob_variance_decomp_flag"],
        )
        == (288, 16, 1),
        "martingale_boundary_recorded": (
            obs["mart_global_martingale_flag"],
            obs["mart_eventual_submartingale_flag"],
            obs["mart_negative_drift_count"],
        )
        == (0, 1, 1),
        "stopped_tail_recorded": (
            obs["stop_tail_gap_nonnegative_count"],
            obs["stop_stopped_gap_nonnegative_count"],
            obs["stop_grammar_match_flag"],
        )
        == (48, 48, 1),
        "drift_limit_recorded": (
            obs["dlim_defect_count"],
            obs["dlim_eventual_cone_negative_count"],
            obs["dlim_eventual_cone_level_count"],
        )
        == (1, 0, 14),
        "inventory_exhaust_recorded": (
            obs["long_inv_exhaust_current_inventory_flag"],
            obs["long_inv_exhaust_active_frontier_remaining_count"],
        )
        == (1, 0),
        "anomaly_suite_recorded": (
            obs["long_anom_resolved_surface_count"],
            obs["long_anom_residual_boundary_count"],
            obs["long_anom_current_suite_closed_flag"],
        )
        == (14, 0, 1),
        "automorphic_boundary_recorded": (
            obs["long_auto_resolved_surface_count"],
            obs["long_auto_residual_boundary_count"],
            obs["long_auto_current_boundary_closed_flag"],
        )
        == (18, 0, 1),
        "matrix_boundary_recorded": (
            obs["long_mat_resolved_surface_count"],
            obs["long_mat_residual_boundary_count"],
            obs["long_mat_current_boundary_closed_flag"],
        )
        == (37, 0, 1),
        "inventory_synchronized": obs["inventory_update_needed_flag"] == 0,
        "table_shapes_match": (
            tuple(rows["status_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == ((29, len(STATUS_COLUMNS)), (len(OBS_CODES), len(OBS_COLUMNS))),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "oracle_anomaly_status_split",
        "summary": {
            "input_report_count": obs["input_report_count"],
            "input_certified_count": obs["input_certified_count"],
            "resolved_surface_count": obs["resolved_surface_count"],
            "open_boundary_count": obs["open_boundary_count"],
            "inventory_update_needed_flag": obs["inventory_update_needed_flag"],
        },
        "surface_code_map": {
            "0": "c985_multifusion_oracle",
            "1": "global_support_gap_form",
            "2": "zeta_composable_sample_sheaf",
            "3": "horizon128_witness_lift",
            "4": "canonical_a985_matrix_units",
            "5": "canonical_a985_sector_characters",
            "6": "screen12_11_support_obstruction",
            "7": "c2_quotient_anomaly_counterterm",
            "8": "long_inv_inventory_synchronized",
            "9": "horizon16_profunctor_boundary",
            "10": "orientation_duality_mobius_split",
            "11": "coefficient_dual_witness_kernel",
            "12": "dual_probability_lln_curve",
            "13": "finite_transport_martingale_boundary",
            "14": "stopped_tail_transport_bounds",
            "15": "drift_limit_obstruction",
            "16": "finite_horizon8_alexandrov_profunctor",
            "17": "formal_horizon16_extension_shadow",
            "18": "horizon16_tensor_object_gap",
            "19": "component_path_tensor_expansion_gap",
            "20": "owner_component_lift_boundary",
            "21": "raw_owner_support_lift_boundary",
            "22": "single_raw_product_path_witness",
            "23": "compressed_active_raw_product_path_family",
            "24": "scoped_active_raw_product_probability_boundary",
            "25": "bounded_invariant_family_inventory_cover",
            "26": "finite_anomaly_correction_suite",
            "27": "finite_automorphic_fourier_string_kernel_boundary",
            "28": "finite_matrix_theoretic_charge_wall_boundary",
        },
        "next_action_code_map": {
            "0": "optional pivotal/spherical/unitary/braided C985 refinements",
            "1": "keep full component-word measure out of theorem claims unless separately certified",
            "2": "extend interval sheaf to full raw tensor support if needed",
            "3": "build long_ind for symbolic induction beyond horizon 128",
            "4": "use canonical matrix units as the default sector-local gauge",
            "5": "test Fourier candidates against canonical block traces",
            "6": "stop current support refinement or build a genuine extended model before using state 11",
            "7": "treat C2 quotient anomaly through the certified exact counterterm",
            "8": "keep long_inv synchronized with focused oracle retirements",
            "9": "use the current-model h16 obstruction as a guardrail; reserve absolute nonexistence for changed models",
            "10": "use the signed orientation split as a finite dual-kernel seam; do not claim the reversed component is removable",
            "11": "use the coefficient kernel, not signed counts, on current witness paths",
            "12": "keep the witness dual probability separate from full raw-support measure claims",
            "13": "record the single first-level negative drift and keep martingale claims eventual",
            "14": "keep stopped-tail bounds finite and dual-transport scoped",
            "15": "bridge the finite drift defect through long_linf before any infinite-horizon claim",
            "16": "do not treat the horizon-eight long_prof chain as the missing horizon-sixteen profunctor",
            "17": "separate formal convolution shadows from genuine tensor-lookup objects",
            "18": "target the 208 object-gap rows before claiming horizon-sixteen closure",
            "19": "materialize component paths or keep the 64560240 gap words compressed",
            "20": "materialize owner or owner-cell paths before claiming owner-level profunctoriality",
            "21": "materialize raw tensor-address paths before claiming raw-line profunctoriality",
            "22": "upgrade single witnesses to exhaustive raw path families if long_paths is targeted",
            "23": "use compressed active-product counts for long_measure; do not claim materialized or exact-composable raw paths",
            "24": "use the scoped measure boundary for h16; do not treat it as a full raw-support measure independent of current active products",
            "25": "treat the focused theorem-debt frontier as empty until broad gates are permitted",
            "26": "use long_anom as the finite anomaly correction guardrail; do not claim continuum anomaly freedom",
            "27": "use long_auto as the finite automorphic/Fourier guardrail; do not claim continuum automorphic classification",
            "28": "use long_mat as the finite Matrix-theoretic charge-wall guardrail; do not claim a full A985-to-packet Matrix model",
        },
        "status_text_sha256": rows["status_hash"],
        "status_table_sha256": sha_array(rows["status_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    status_payload = {
        "schema": "long.orac@1",
        "object": "oracle_anomaly_status_split",
        "status": STATUS if all(checks.values()) else "LONG_ORAC_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.orac.report@1",
        "status": status_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_orac certifies the current local oracle/anomaly status split: "
            "the C985 oracle chain is reproducible, A985 matrix units and sector "
            "characters are certified, screen12=11 is a support-level obstruction "
            "under current constraints, and the profunctor/form surfaces have "
            "explicit certified boundaries including orientation-duality, "
            "dual-kernel probability, martingale/stopped-tail drift limits, "
            "the formal horizon-16 object/profunctor gap chain, and the current-model horizon-16 "
            "profunctor obstruction, plus compressed active raw product-path "
            "accounting and a scoped active-product probability boundary, "
            "with long_inv synchronized to the retired C985 associator debt, "
            "long_inv_exhaust closing the focused inventory frontier, and "
            "long_anom recording finite anomaly correction, and long_auto "
            "recording the finite automorphic/Fourier/string-kernel boundary, "
            "with long_mat recording the finite Matrix-theoretic charge-wall "
            "boundary, "
            "without claiming a "
            "materialized horizon-16 profunctor, continuum anomaly freedom, or "
            "infinite-horizon closure."
        ),
        "stage_protocol": {
            "draft": "read focused oracle, profunctor, matrix, character, sector-11, formal-extension, object-gap, tensor-lift, raw/path, dual-probability, martingale, stopped-tail, drift-limit, anomaly, automorphic, and matrix-boundary reports",
            "witness": "emit numeric status rows and observable counts",
            "coherence": "check statuses, counts, current boundaries, hashes, and table shapes",
            "closure": "certify the status split without closing the broader active objective",
            "emit": "write long_orac artifacts and verifier hook",
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
            "orac": relpath(OUT_DIR / "orac.json"),
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
                "C985 oracle reproducibility through the final multi-fusion certificate",
                "canonical A985 source-sector matrix-unit and character-table availability",
                "screen12=11 as a residue-visible state obstructed by current six-object/109-piece support constraints",
                "zeta-composable sample-path sheaf and horizon-128 witness lift status",
                "the current horizon-16 boundary as a raw-backed quotient/sample-path obstruction without a materialized long_prof profunctor",
                "the finite horizon-eight long_prof chain and the formal horizon-sixteen convolution-shadow extension boundary",
                "the 208-row tensor-object gap, 64,560,240-word component-path gap, owner/component lift boundary, raw-support lift boundary, and single-witness raw path boundary",
                "compressed active raw product-path family accounting for the 64,570,080 component paths",
                "scoped active raw product-family probability laws with the full raw-support gap preserved",
                "orientation-duality Mobius split, coefficient-dual witness kernel, and finite dual path probability curve",
                "finite transport martingale boundary, stopped-tail bounds, and single-defect drift-limit obstruction",
                "long_inv synchronization with the now-passing C985 final certificate",
                "bounded finite-line inventory cover through long_inv_exhaust",
                "finite anomaly correction suite through long_anom",
                "finite automorphic/Fourier/string-kernel boundary through long_auto",
                "finite Matrix-theoretic charge-wall boundary through long_mat",
            ],
            "does_not_certify_because_out_of_scope": [
                "the full trinomial component-word measure",
                "absolute nonexistence of a genuine horizon-16 long_prof profunctor under a changed object/support model",
                "a probability measure on the full raw tensor support independent of the current active-product boundary",
                "full raw-path composition beyond selected witnesses",
                "materialized rows for every compressed active raw product path",
                "a genuine tensor-lookup object for the formal horizon-sixteen extension rows",
                "a materialized owner-cell or raw-address horizon-sixteen path object",
                "a nonempty support-level realization of screen12=11",
                "infinite-horizon induction beyond the focused certificates",
                "broad bundle integration without running the broad certificate gate",
                "continuum anomaly cancellation outside the finite d20 oracle",
                "continuum automorphic-form classification outside the finite d20 oracle",
                "a full A985-to-packet Matrix model outside the finite charge-wall shadow",
            ],
        },
        "next_highest_yield_item": (
            "Focused theorem-debt frontier is empty; defer broad integration "
            "gates until the operator permits long gates."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.orac.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.orac.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "orac": status_payload,
        "status_csv": csv_text(STATUS_COLUMNS, rows["status_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "status_table": rows["status_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    write_json(OUT_DIR / "orac.json", payloads["orac"])
    (OUT_DIR / "status.csv").write_text(payloads["status_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        status_table=payloads["status_table"],
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
