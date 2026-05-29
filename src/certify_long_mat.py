from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_mat import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        REPORTS,
        STATUS,
        STATUS_TEXT_HASH,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_mat import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        REPORTS,
        STATUS,
        STATUS_TEXT_HASH,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
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


def validate_long_mat() -> dict[str, Any]:
    expected = build_payloads()
    mat_payload = load_json(OUT_DIR / "mat.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if mat_payload != expected["mat"]:
        raise AssertionError("long_mat JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_mat cert mismatch")
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, key, columns, row_count in [
        ("status.csv", "status_csv", SURFACE_COLUMNS, 37),
        ("obs.csv", "obs_csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_mat {filename} mismatch")
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_mat {filename} shape mismatch")
    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_mat table mismatch: {key}")

    if report.get("schema") != "long.mat.report@1":
        raise AssertionError("long_mat report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_mat report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_mat all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_mat checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_mat report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_mat report hash mismatch")

    if tuple(np.asarray(tables["surface_table"]).shape) != (
        37,
        len(SURFACE_COLUMNS),
    ):
        raise AssertionError("long_mat surface table shape mismatch")
    if tuple(np.asarray(tables["observable_table"]).shape) != (
        len(OBS_CODES),
        len(OBS_COLUMNS),
    ):
        raise AssertionError("long_mat observable table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 37,
        "input_certified_count": 37,
        "status_row_count": 37,
        "resolved_surface_count": 37,
        "residual_current_model_matrix_boundary_count": 0,
        "current_matrix_boundary_closed_flag": 1,
        "rooted_flux_rank": 20,
        "augmented_ledger_stabilizer_order": 1,
        "ward_scalar_sum": 0,
        "pi33_residual_integral": -374_784,
        "finite_flux_cycle_rank": 11,
        "finite_flux_residue_class_count": 2048,
        "typed_update_count": 2048,
        "typed_nonzero_update_count": 2047,
        "fourier_screen_rank": 3,
        "fourier_common_kernel_count": 256,
        "closed_loop_basis_count": 297,
        "closed_loop_commutator_failure_count": 0,
        "full_a985_commutator_failure_count": 304,
        "pointer_manifest_row_count": 1011,
        "pointer_open_boundary_count": 1,
        "full_matrix_unit_count": 985,
        "full_orbital_coo_row_count": 76_703,
        "support_projector_count": 7,
        "contour_quotient_order": 52,
        "raw_compatible_pair_count": 0,
        "row_scalar_divisibility": 6,
        "projective_packet_count": 512,
        "projective_charge_frame_class_count": 47,
        "hidden_packet_row_count": 2048,
        "propagator_kernel_residue_row_count": 6,
        "propagator_source_packet": 239,
        "propagator_partner_packet": 238,
        "surviving_symmetry_order": 1,
        "selected_ward_mask": 288,
        "selected_ward_height": 1_065_984,
        "matrix_shadow_registered_flag": 1,
        "minimal_charge_kernel_lift_flag": 1,
        "full_packet_block_dimension": 40,
        "full_a985_packet_operator_map_flag": 0,
        "minimum_packet_map_kernel_dimension": 945,
        "packet_bridge_raw_columns_available_flag": 0,
        "packet_bridge_candidate_count": 3,
        "packet_bridge_rank": 20,
        "full_exposure_packet_count": 20,
        "packet_propagation_component_count": 10,
        "packet_propagation_edge_count": 40,
        "packet239_charge_seed_flag": 1,
        "packet239_active_partner_packet": 238,
        "packet239_stabilizer_unique_flag": 0,
        "packet239_arithmetic_twin_successor": 241,
        "quotient_positive_packet_action_count": 3,
        "quotient_a985_or_tube_packet_operator_found_flag": 0,
        "explicit_packet_restriction_mode_count": 40,
        "explicit_packet_missing_bridge_count": 3,
        "loop_step_packet_snf_tested_column_count": 25,
        "loop_step_packet_snf_passing_column_count": 0,
        "low_support_even_candidate_count": 12,
        "low_support_compatible_doublet_count": 6,
        "low_support_full_doublet_map_available_flag": 0,
        "prime_alignment_union_prime_count": 3,
        "prime_alignment_common_prime_count": 1,
        "complete_goal_claim_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_mat observable {key} mismatch")

    if hashlib.sha256(
        digest_text(SURFACE_COLUMNS, csv_rows["status.csv"]).encode("ascii")
    ).hexdigest() != STATUS_TEXT_HASH:
        raise AssertionError("long_mat status hash mismatch")
    if hashlib.sha256(
        digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")
    ).hexdigest() != OBS_TEXT_HASH:
        raise AssertionError("long_mat observable hash mismatch")

    inputs = report.get("inputs", {})
    for name, path in REPORTS.items():
        assert_file_hash(inputs.get(name, {}), path, f"{name} input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.mat.manifest@1":
        raise AssertionError("long_mat manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_mat manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_mat manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_mat missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_mat proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_mat proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.mat.verification@1",
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
    print(json.dumps(validate_long_mat(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
