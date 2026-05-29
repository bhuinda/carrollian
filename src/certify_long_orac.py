from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_orac import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REPORTS,
        STATUS,
        STATUS_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_orac import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REPORTS,
        STATUS,
        STATUS_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from derive_long_raw import rows_from_table


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_orac() -> dict[str, Any]:
    expected = build_payloads()
    orac_payload = load_json(OUT_DIR / "orac.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if orac_payload != expected["orac"]:
        raise AssertionError("long_orac orac JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_orac cert mismatch")
    for filename, key in {
        "status.csv": "status_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_orac {filename} mismatch")

    for key, expected_array in {
        "status_table": expected["status_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_orac table mismatch: {key}")

    if report.get("schema") != "long.orac.report@1":
        raise AssertionError("long_orac report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_orac report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_orac all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_orac checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_orac report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_orac report hash mismatch")

    csv_shapes = [
        ("status.csv", STATUS_COLUMNS, 29),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_orac {filename} shape mismatch")

    table_shapes = {
        "status_table": (29, len(STATUS_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_orac {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 31,
        "input_certified_count": 31,
        "status_row_count": 29,
        "resolved_surface_count": 29,
        "open_boundary_count": 22,
        "inventory_update_needed_flag": 0,
        "c985_final_certified_flag": 1,
        "matrix_unit_count": 985,
        "source_sector_count": 39,
        "sector_character_row_count": 38_415,
        "sector11_transition_mass": 420,
        "sector11_valid_nonempty_extension_count": 0,
        "support_gap_check_count": 131_586,
        "support_gap_nonnegative_count": 131_586,
        "sheaf_section_count": 3_128,
        "lift_horizon": 128,
        "h16_materialized_profunctor_flag": 0,
        "h16_boundary_decision_code": 3,
        "h16_current_model_obstruction_flag": 1,
        "h16_active_frontier_flag": 0,
        "long_prof_object_count": 9,
        "long_prof_profunctor_count": 8,
        "long_prof_compose_violation_count": 0,
        "long_ext_formal_added_row_count": 208,
        "long_ext_genuine_tensor_lookup_flag": 0,
        "long_ext_convolution_shadow_flag": 1,
        "long_obj_gap_row_count": 208,
        "long_obj_source_horizon_gap": 8,
        "long_obj_genuine_extension_flag": 0,
        "long_tens_gap_component_path_count": 64_560_240,
        "long_tens_total_component_path_count": 64_570_080,
        "long_tens_materialized_path_object_count": 0,
        "long_tens_sum_profunctor_flag": 0,
        "long_lift_active_owner_total": 51,
        "long_lift_owner_cell_total": 749_239,
        "long_lift_materialized_owner_path_flag": 0,
        "long_lift_raw_line_address_lift_flag": 0,
        "long_raw_support_count": 1_414_965,
        "long_raw_coeff_sum": 2_537_360,
        "long_raw_materialized_path_flag": 0,
        "long_raw_fiber_positive_count": 288,
        "long_path_path_count": 288,
        "long_path_gap_path_count": 208,
        "long_path_single_witness_flag": 1,
        "long_path_all_raw_paths_flag": 0,
        "long_path_composable_raw_address_flag": 0,
        "long_paths_component_path_total": 64_570_080,
        "long_paths_gap_component_path_total": 64_560_240,
        "long_paths_selected_witness_count": 288,
        "long_paths_compressed_family_flag": 1,
        "long_paths_materialized_family_flag": 0,
        "long_paths_exact_composable_family_flag": 0,
        "long_measure_scoped_law_flag": 1,
        "long_measure_full_raw_certified_flag": 0,
        "long_measure_full_raw_scope_gap_flag": 1,
        "long_measure_conditional_normalization_count": 32,
        "long_measure_variance_decomp_count": 2,
        "orientation_positive_section_count": 477_589,
        "orientation_reverse_section_count": 937_376,
        "orientation_mobius_roundtrip_count": 12,
        "dual_coeff_path_nonzero_count": 288,
        "dual_count_path_nonzero_count": 16,
        "dual_transition_compose_count": 2_840,
        "prob_path_count": 288,
        "prob_variance_shrink_count": 16,
        "prob_variance_decomp_flag": 1,
        "mart_global_martingale_flag": 0,
        "mart_eventual_submartingale_flag": 1,
        "mart_negative_drift_count": 1,
        "stop_tail_gap_nonnegative_count": 48,
        "stop_stopped_gap_nonnegative_count": 48,
        "stop_grammar_match_flag": 1,
        "dlim_defect_count": 1,
        "dlim_eventual_cone_negative_count": 0,
        "dlim_eventual_cone_level_count": 14,
        "c2_anomaly_counterterm_flag": 1,
        "long_inv_exhaust_current_inventory_flag": 1,
        "long_inv_exhaust_active_frontier_remaining_count": 0,
        "long_anom_resolved_surface_count": 14,
        "long_anom_residual_boundary_count": 0,
        "long_anom_current_suite_closed_flag": 1,
        "long_auto_resolved_surface_count": 18,
        "long_auto_residual_boundary_count": 0,
        "long_auto_current_boundary_closed_flag": 1,
        "long_mat_resolved_surface_count": 37,
        "long_mat_residual_boundary_count": 0,
        "long_mat_current_boundary_closed_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_orac observable {key} mismatch")

    inputs = report.get("inputs", {})
    for name, path in REPORTS.items():
        assert_file_hash(inputs.get(name, {}), path, f"{name} input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.orac.manifest@1":
        raise AssertionError("long_orac manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_orac manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_orac manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_orac missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_orac proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_orac proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.orac.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "surface_code_map": witness.get("surface_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_orac(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
