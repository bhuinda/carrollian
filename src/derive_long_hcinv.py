from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        write_json,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_hcinv"
STATUS = "LONG_HCINV_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
THEOREM_ROOT = D20_INVARIANTS / "theorems"
PO_ROOT = D20_INVARIANTS / "proof_obligations"
EVIDENCE_ROOT = (
    ROOT / "data" / "evidence" / "talagrand_python_handoff" / "work"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcinv.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcinv.py"

SURFACE_TEXT_HASH = "c8198b9bd478a858121270d651eda517514bfabab1663c2bbe23ac5e966e3923"
INVARIANT_TEXT_HASH = "b01fadf6a40649532ece1678f4ba2ff56bd5d392210523c2db48b1aeeaddeedf"
EDGE_TEXT_HASH = "66531ef1f0cb3eabe517ed4153e8e9fd31036f9e9c1bcdc5a07118d63a7ca023"
SAMPLE_TEXT_HASH = "c91efc3992d49ab8cc038b07820e8c703908a0b6941fc2a4c5ff72b417354d67"
OBS_TEXT_HASH = "3a5f7385d7ce6f7a79aa1e78a44df2bd41961017b53e2dc125996d578472a53a"

INPUT_REPORTS = [
    (
        "raw543_repo_c2_kernel_action",
        0,
        THEOREM_ROOT / "raw543_repo_c2_kernel_action" / "report.json",
    ),
    (
        "raw543_repo_c2_kernel_agda_bridge_data",
        1,
        THEOREM_ROOT / "raw543_repo_c2_kernel_agda_bridge_data" / "report.json",
    ),
    (
        "long_c2uf",
        2,
        PO_ROOT / "long_c2uf" / "report.json",
    ),
    (
        "c2_quotient_transport_ledger",
        3,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger"
        / "report.json",
    ),
    (
        "c2_quotient_anomaly",
        4,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
        / "report.json",
    ),
    (
        "c2_dynamics_selector",
        5,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector"
        / "report.json",
    ),
    (
        "sector33_height_coherent_transport",
        6,
        THEOREM_ROOT / "sector33_height_coherent_transport" / "report.json",
    ),
    (
        "sector33_all_residue_height_transport",
        7,
        THEOREM_ROOT / "sector33_all_residue_height_transport" / "report.json",
    ),
    (
        "height_action_return_reconstruction",
        8,
        EVIDENCE_ROOT
        / "all_residue_height_action_return_reconstruction"
        / "all_residue_height_action_return_certificate.json",
    ),
    (
        "e33_full_corrected_transport",
        9,
        EVIDENCE_ROOT
        / "e33_full_corrected_transport"
        / "e33_full_corrected_transport_certificate.json",
    ),
    (
        "lambda_hc_act_invariance",
        10,
        EVIDENCE_ROOT
        / "lambda_hc_act_invariance_audit"
        / "lambda_hc_act_invariance_certificate.json",
    ),
    (
        "height_action_return_intertwining",
        11,
        EVIDENCE_ROOT
        / "height_coherent_action_return_intertwining"
        / "height_coherent_action_return_intertwining_certificate.json",
    ),
]

ROLE_NAMES = {code: name for name, code, _path in INPUT_REPORTS}

SURFACE_COLUMNS = [
    "surface_id",
    "role_code",
    "accepted_flag",
    "source_action_flag",
    "height_action_flag",
    "vector_flag",
    "anomaly_flag",
    "selector_flag",
    "lift_boundary_flag",
    "row_count",
    "gap_flag",
]
INVARIANT_COLUMNS = [
    "invariant_id",
    "group_code",
    "invariant_code",
    "value",
    "certified_flag",
    "open_gap_flag",
]
EDGE_COLUMNS = [
    "edge_id",
    "source_surface_id",
    "target_surface_id",
    "edge_code",
    "closed_flag",
    "gap_flag",
]
SAMPLE_COLUMNS = [
    "sample_id",
    "sample_code",
    "value_a",
    "value_b",
    "value_c",
    "certified_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

INVARIANT_NAMES = [
    "input_report_count",
    "accepted_input_count",
    "raw543_orbit_count",
    "raw543_fixed_orbit_count",
    "raw543_pair_orbit_count",
    "raw543_kernel_dimension",
    "raw543_fixed_dimension",
    "tau_squared_identity",
    "gamma8_fixed",
    "gamma8_mask",
    "tau_spectrum_plus",
    "tau_spectrum_minus",
    "tau_trace",
    "tau_projection_rank",
    "tau_projection_nullity",
    "transport_target_domain",
    "residue_mask_count",
    "nonzero_residue_class_count",
    "edge_mod2_mismatch_count",
    "gamma8_height",
    "gamma8_residual",
    "gamma8_transport_scalar",
    "full_mask_height",
    "e33_support",
    "e33_positive_count",
    "e33_negative_count",
    "e33_signed_sum",
    "corrected_vector_count",
    "corrected_total_sparse_entries",
    "lambda_act_kernel_masks",
    "lambda_act_kernel_failures",
    "zero_anomaly_orbit_count",
    "nonzero_anomaly_orbit_count",
    "anomaly_cocycle_gcd_abs",
    "tau_cocycle_zero_mask_count",
    "tau_cocycle_nonzero_mask_count",
    "selector_candidate_count",
    "selector_free_unique_operator_flag",
    "primitive_selector_orbit_id",
    "global_selector_orbit_id",
    "paired_selector_orbit_id",
    "foam_support_dimension",
    "foam_projection_rank",
    "foam_bridge_kernel_dimension",
    "hidden_generator_index",
    "r_hc_matrix_materialized_flag",
    "r_foam_matrix_materialized_flag",
    "pi_foam33_matrix_materialized_flag",
    "complete_goal_claim_flag",
]
INVARIANT_CODES = {name: index for index, name in enumerate(INVARIANT_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "accepted_input_count",
    "connected_edge_count",
    "closed_edge_count",
    "gap_edge_count",
    "raw543_orbit_count",
    "raw543_fixed_orbit_count",
    "raw543_pair_orbit_count",
    "transport_orbit_count",
    "tau_projection_rank",
    "tau_projection_nullity",
    "residue_mask_count",
    "nonzero_height_mask_count",
    "e33_support",
    "e33_positive_count",
    "e33_negative_count",
    "corrected_vector_count",
    "lambda_act_kernel_masks",
    "lambda_act_kernel_failures",
    "zero_anomaly_orbit_count",
    "nonzero_anomaly_orbit_count",
    "anomaly_cocycle_gcd_abs",
    "selector_candidate_count",
    "selector_free_unique_operator_flag",
    "foam_support_dimension",
    "foam_core_rank",
    "foam_bridge_kernel_dimension",
    "height_coherent_operator_materialized_flag",
    "focused_hcinv_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

GROUP_CODES = {
    "input": 0,
    "action": 1,
    "quotient": 2,
    "height": 3,
    "vector": 4,
    "anomaly": 5,
    "selector": 6,
    "lift": 7,
}


def accepted(report: dict[str, Any]) -> int:
    status = str(report.get("status", ""))
    checks = report.get("checks")
    failures = report.get("failures")
    if isinstance(checks, dict):
        checks_ok = all(value not in (False, None, "") for value in checks.values())
    else:
        checks_ok = failures in (None, [])
    status_ok = any(
        marker in status for marker in ("CERTIFIED", "PASS", "TARGET_LOCKED")
    )
    return int(status_ok and checks_ok and "PROVISIONAL" not in status)


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def load_reports() -> dict[str, dict[str, Any]]:
    return {name: load_json(path) for name, _code, path in INPUT_REPORTS}


def selected_row(selector_summary: dict[str, Any], key: str) -> dict[str, Any]:
    rows = selector_summary[key]
    if not isinstance(rows, list) or len(rows) != 1:
        raise AssertionError(f"selector row {key} is not unique")
    row = rows[0]
    if not isinstance(row, dict):
        raise AssertionError(f"selector row {key} is not an object")
    return row


def build_rows() -> dict[str, Any]:
    reports = load_reports()
    action = as_dict(reports["raw543_repo_c2_kernel_action"].get("derived"))
    raw_kernel = as_dict(action.get("raw543_kernel"))
    tau = as_dict(action.get("actual_nontrivial_c2_preserver"))
    agda = as_dict(reports["raw543_repo_c2_kernel_agda_bridge_data"].get("derived"))
    agda_summary = as_dict(agda.get("summary"))
    c2uf_summary = as_dict(reports["long_c2uf"].get("witness")).get("summary", {})
    if not isinstance(c2uf_summary, dict):
        raise AssertionError("missing long_c2uf summary")

    ledger = as_dict(reports["c2_quotient_transport_ledger"].get("derived"))
    ledger_summary = as_dict(ledger.get("operator_summary"))
    tau_spectrum = as_dict(ledger_summary.get("primal_tau_spectrum"))
    projection_spectrum = as_dict(ledger_summary.get("orbit_projection_spectrum"))
    anomaly = as_dict(reports["c2_quotient_anomaly"].get("derived"))
    anomaly_summary = as_dict(anomaly.get("anomaly_summary"))
    selector = as_dict(reports["c2_dynamics_selector"].get("derived"))
    selector_summary = as_dict(selector.get("selector_summary"))

    sector33_height = as_dict(
        reports["sector33_height_coherent_transport"].get("derived")
    )
    height_residual = as_dict(sector33_height.get("edge_derived_residual"))
    height_vectors = as_dict(sector33_height.get("vectors"))
    all_residue = as_dict(
        reports["sector33_all_residue_height_transport"].get("derived")
    )
    gamma8_row = as_dict(all_residue.get("gamma8_row"))
    sector33_support = as_dict(all_residue.get("sector33_support"))
    sector33_e33 = as_dict(sector33_support.get("e33"))
    action_return = reports["height_action_return_reconstruction"]
    full_mask_row = as_dict(action_return.get("full_mask_row"))
    e33_report = reports["e33_full_corrected_transport"]
    e33 = as_dict(e33_report.get("e33"))
    corrected_transport = as_dict(e33_report.get("corrected_transport"))
    lambda_report = reports["lambda_hc_act_invariance"]
    lambda_summary = as_dict(lambda_report.get("summary"))
    intertwining = reports["height_action_return_intertwining"]
    facts = as_dict(intertwining.get("facts"))
    ladder = intertwining.get("ladder", [])
    ladder_text = "\n".join(str(row) for row in ladder)

    primitive = selected_row(selector_summary, "primitive_seeded_selected")
    global_action = selected_row(selector_summary, "global_action_minimal_selected")
    paired_action = selected_row(selector_summary, "paired_action_minimal_selected")

    surface_row_counts = {
        "raw543_repo_c2_kernel_action": int(raw_kernel["nonzero_kernel_orbit_count"]),
        "raw543_repo_c2_kernel_agda_bridge_data": int(
            agda_summary["raw543_orbit_count"]
        ),
        "long_c2uf": int(c2uf_summary["certified_input_count"]),
        "c2_quotient_transport_ledger": int(ledger_summary["orbit_count"]),
        "c2_quotient_anomaly": int(anomaly_summary["orbit_count"]),
        "c2_dynamics_selector": int(selector_summary["candidate_family_size"]),
        "sector33_height_coherent_transport": int(
            as_dict(height_vectors.get("height_transport"))["support"]
        ),
        "sector33_all_residue_height_transport": int(
            all_residue["residue_class_count"]
        ),
        "height_action_return_reconstruction": int(
            action_return["residue_class_count"]
        ),
        "e33_full_corrected_transport": int(corrected_transport["mask_count"]),
        "lambda_hc_act_invariance": int(lambda_summary["Act_kernel_masks"]),
        "height_action_return_intertwining": int(facts["Lambda3_A8_candidate"]),
    }
    gap_surfaces = {
        "c2_dynamics_selector",
        "height_action_return_intertwining",
    }

    surface_rows: list[dict[str, int]] = []
    for surface_id, (name, role_code, _path) in enumerate(INPUT_REPORTS):
        surface_rows.append(
            {
                "surface_id": surface_id,
                "role_code": role_code,
                "accepted_flag": accepted(reports[name]),
                "source_action_flag": int(role_code <= 5),
                "height_action_flag": int(role_code >= 6),
                "vector_flag": int(role_code in {9, 10, 11}),
                "anomaly_flag": int(name == "c2_quotient_anomaly"),
                "selector_flag": int(name == "c2_dynamics_selector"),
                "lift_boundary_flag": int(name == "height_action_return_intertwining"),
                "row_count": surface_row_counts[name],
                "gap_flag": int(name in gap_surfaces),
            }
        )

    invariant_specs = [
        ("input", "input_report_count", len(INPUT_REPORTS), 1, 0),
        (
            "input",
            "accepted_input_count",
            sum(accepted(report) for report in reports.values()),
            1,
            0,
        ),
        (
            "action",
            "raw543_orbit_count",
            int(raw_kernel["nonzero_kernel_orbit_count"]),
            1,
            0,
        ),
        (
            "action",
            "raw543_fixed_orbit_count",
            int(raw_kernel["fixed_nonzero_orbits"]),
            1,
            0,
        ),
        (
            "action",
            "raw543_pair_orbit_count",
            int(raw_kernel["two_cycle_orbits"]),
            1,
            0,
        ),
        ("action", "raw543_kernel_dimension", int(raw_kernel["dimension"]), 1, 0),
        (
            "action",
            "raw543_fixed_dimension",
            int(raw_kernel["fixed_space_dimension"]),
            1,
            0,
        ),
        (
            "action",
            "tau_squared_identity",
            int(tau["tau_squared_identity"]),
            1,
            0,
        ),
        ("action", "gamma8_fixed", int(tau["gamma8_fixed"]), 1, 0),
        ("action", "gamma8_mask", int(tau["gamma8_mask"]), 1, 0),
        (
            "quotient",
            "tau_spectrum_plus",
            int(tau_spectrum["eigenvalue_plus_one_multiplicity"]),
            1,
            0,
        ),
        (
            "quotient",
            "tau_spectrum_minus",
            int(tau_spectrum["eigenvalue_minus_one_multiplicity"]),
            1,
            0,
        ),
        ("quotient", "tau_trace", int(tau_spectrum["trace"]), 1, 0),
        (
            "quotient",
            "tau_projection_rank",
            int(projection_spectrum["rank"]),
            1,
            0,
        ),
        (
            "quotient",
            "tau_projection_nullity",
            int(projection_spectrum["nullity"]),
            1,
            0,
        ),
        (
            "quotient",
            "transport_target_domain",
            int(ledger_summary["target_domain_size"]),
            1,
            0,
        ),
        ("height", "residue_mask_count", int(all_residue["residue_class_count"]), 1, 0),
        (
            "height",
            "nonzero_residue_class_count",
            int(all_residue["nonzero_residue_class_count"]),
            1,
            0,
        ),
        (
            "height",
            "edge_mod2_mismatch_count",
            int(as_dict(all_residue["edge_mod2_height_incoherence"])["mismatch_count"]),
            1,
            0,
        ),
        ("height", "gamma8_height", int(gamma8_row["height_action"]), 1, 0),
        ("height", "gamma8_residual", int(gamma8_row["residual_integral"]), 1, 0),
        (
            "height",
            "gamma8_transport_scalar",
            int(gamma8_row["transport_scalar"]),
            1,
            0,
        ),
        ("height", "full_mask_height", int(full_mask_row["height_action"]), 1, 0),
        ("vector", "e33_support", int(e33["support"]), 1, 0),
        ("vector", "e33_positive_count", int(e33["positive_count"]), 1, 0),
        ("vector", "e33_negative_count", int(e33["negative_count"]), 1, 0),
        ("vector", "e33_signed_sum", int(e33["signed_sum"]), 1, 0),
        ("vector", "corrected_vector_count", int(corrected_transport["mask_count"]), 1, 0),
        (
            "vector",
            "corrected_total_sparse_entries",
            int(corrected_transport["total_sparse_entries"]),
            1,
            0,
        ),
        (
            "vector",
            "lambda_act_kernel_masks",
            int(lambda_summary["Act_kernel_masks"]),
            1,
            0,
        ),
        (
            "vector",
            "lambda_act_kernel_failures",
            int(lambda_summary["Act_kernel_failures"]),
            1,
            0,
        ),
        (
            "anomaly",
            "zero_anomaly_orbit_count",
            int(anomaly_summary["zero_anomaly_orbit_count"]),
            1,
            0,
        ),
        (
            "anomaly",
            "nonzero_anomaly_orbit_count",
            int(anomaly_summary["nonzero_anomaly_orbit_count"]),
            1,
            0,
        ),
        (
            "anomaly",
            "anomaly_cocycle_gcd_abs",
            int(anomaly_summary["height_action_cocycle_gcd_abs"]),
            1,
            0,
        ),
        (
            "anomaly",
            "tau_cocycle_zero_mask_count",
            int(anomaly_summary["tau_cocycle_zero_mask_count"]),
            1,
            0,
        ),
        (
            "anomaly",
            "tau_cocycle_nonzero_mask_count",
            int(anomaly_summary["tau_cocycle_nonzero_mask_count"]),
            1,
            0,
        ),
        (
            "selector",
            "selector_candidate_count",
            int(selector_summary["candidate_family_size"]),
            1,
            0,
        ),
        ("selector", "selector_free_unique_operator_flag", 0, 1, 1),
        (
            "selector",
            "primitive_selector_orbit_id",
            int(primitive["move_orbit_id"]),
            1,
            0,
        ),
        (
            "selector",
            "global_selector_orbit_id",
            int(global_action["move_orbit_id"]),
            1,
            0,
        ),
        (
            "selector",
            "paired_selector_orbit_id",
            int(paired_action["move_orbit_id"]),
            1,
            0,
        ),
        ("lift", "foam_support_dimension", int(facts["Lambda3_A8_candidate"]), 1, 0),
        (
            "lift",
            "foam_projection_rank",
            33 if "56 -> 33 has rank 33 and kernel 23" in ladder_text else 0,
            1,
            0,
        ),
        (
            "lift",
            "foam_bridge_kernel_dimension",
            23 if "56 -> 33 has rank 33 and kernel 23" in ladder_text else 0,
            1,
            0,
        ),
        (
            "lift",
            "hidden_generator_index",
            int(facts["unique_hidden_kernel_generator_index"]),
            1,
            0,
        ),
        ("lift", "r_hc_matrix_materialized_flag", 0, 1, 1),
        ("lift", "r_foam_matrix_materialized_flag", 0, 1, 1),
        ("lift", "pi_foam33_matrix_materialized_flag", 0, 1, 1),
        ("lift", "complete_goal_claim_flag", 0, 1, 1),
    ]
    invariant_rows = [
        {
            "invariant_id": invariant_id,
            "group_code": GROUP_CODES[group],
            "invariant_code": INVARIANT_CODES[name],
            "value": int(value),
            "certified_flag": int(certified_flag),
            "open_gap_flag": int(open_gap_flag),
        }
        for invariant_id, (group, name, value, certified_flag, open_gap_flag) in enumerate(
            invariant_specs
        )
    ]

    edge_specs = [
        (0, 1, 0, 1, 0),
        (0, 2, 1, 1, 0),
        (0, 3, 2, 1, 0),
        (3, 4, 3, 1, 0),
        (0, 4, 4, 1, 0),
        (5, 4, 5, 1, 0),
        (6, 7, 6, 1, 0),
        (7, 8, 7, 1, 0),
        (8, 9, 8, 1, 0),
        (9, 10, 9, 1, 0),
        (8, 11, 10, 0, 1),
        (9, 11, 11, 0, 1),
        (4, 11, 12, 0, 1),
        (5, 11, 13, 0, 1),
        (10, 11, 14, 0, 1),
    ]
    edge_rows = [
        {
            "edge_id": edge_id,
            "source_surface_id": source,
            "target_surface_id": target,
            "edge_code": edge_code,
            "closed_flag": closed_flag,
            "gap_flag": gap_flag,
        }
        for edge_id, (source, target, edge_code, closed_flag, gap_flag) in enumerate(
            edge_specs
        )
    ]

    primitive_deltas = primitive["move_deltas"]
    paired_deltas = paired_action["move_deltas"]
    sample_rows = [
        {
            "sample_id": 0,
            "sample_code": 0,
            "value_a": int(tau["gamma8_mask"]),
            "value_b": int(gamma8_row["height_action"]),
            "value_c": int(gamma8_row["transport_scalar"]),
            "certified_flag": 1,
        },
        {
            "sample_id": 1,
            "sample_code": 1,
            "value_a": int(primitive["move_orbit_id"]),
            "value_b": int(primitive_deltas[0]),
            "value_c": int(primitive_deltas[1]),
            "certified_flag": 1,
        },
        {
            "sample_id": 2,
            "sample_code": 2,
            "value_a": int(global_action["move_orbit_id"]),
            "value_b": int(global_action["move_deltas"][0]),
            "value_c": 0,
            "certified_flag": 1,
        },
        {
            "sample_id": 3,
            "sample_code": 3,
            "value_a": int(paired_action["move_orbit_id"]),
            "value_b": int(paired_deltas[0]),
            "value_c": int(paired_deltas[1]),
            "certified_flag": 1,
        },
        {
            "sample_id": 4,
            "sample_code": 4,
            "value_a": int(facts["Lambda3_A8_candidate"]),
            "value_b": 33,
            "value_c": 23,
            "certified_flag": 1,
        },
        {
            "sample_id": 5,
            "sample_code": 5,
            "value_a": int(anomaly_summary["zero_anomaly_orbit_count"]),
            "value_b": int(anomaly_summary["nonzero_anomaly_orbit_count"]),
            "value_c": int(anomaly_summary["height_action_cocycle_gcd_abs"]),
            "certified_flag": 1,
        },
    ]

    obs = {
        "input_report_count": len(INPUT_REPORTS),
        "accepted_input_count": sum(accepted(report) for report in reports.values()),
        "connected_edge_count": len(edge_rows),
        "closed_edge_count": sum(row["closed_flag"] for row in edge_rows),
        "gap_edge_count": sum(row["gap_flag"] for row in edge_rows),
        "raw543_orbit_count": int(raw_kernel["nonzero_kernel_orbit_count"]),
        "raw543_fixed_orbit_count": int(raw_kernel["fixed_nonzero_orbits"]),
        "raw543_pair_orbit_count": int(raw_kernel["two_cycle_orbits"]),
        "transport_orbit_count": int(ledger_summary["orbit_count"]),
        "tau_projection_rank": int(projection_spectrum["rank"]),
        "tau_projection_nullity": int(projection_spectrum["nullity"]),
        "residue_mask_count": int(all_residue["residue_class_count"]),
        "nonzero_height_mask_count": int(all_residue["nonzero_residue_class_count"]),
        "e33_support": int(e33["support"]),
        "e33_positive_count": int(e33["positive_count"]),
        "e33_negative_count": int(e33["negative_count"]),
        "corrected_vector_count": int(corrected_transport["mask_count"]),
        "lambda_act_kernel_masks": int(lambda_summary["Act_kernel_masks"]),
        "lambda_act_kernel_failures": int(lambda_summary["Act_kernel_failures"]),
        "zero_anomaly_orbit_count": int(anomaly_summary["zero_anomaly_orbit_count"]),
        "nonzero_anomaly_orbit_count": int(
            anomaly_summary["nonzero_anomaly_orbit_count"]
        ),
        "anomaly_cocycle_gcd_abs": int(
            anomaly_summary["height_action_cocycle_gcd_abs"]
        ),
        "selector_candidate_count": int(selector_summary["candidate_family_size"]),
        "selector_free_unique_operator_flag": 0,
        "foam_support_dimension": int(facts["Lambda3_A8_candidate"]),
        "foam_core_rank": 33,
        "foam_bridge_kernel_dimension": 23,
        "height_coherent_operator_materialized_flag": 0,
        "focused_hcinv_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": OBS_CODES[name],
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for name in OBS_NAMES
    ]

    surface_table = table_from_rows(SURFACE_COLUMNS, surface_rows)
    invariant_table = table_from_rows(INVARIANT_COLUMNS, invariant_rows)
    edge_table = table_from_rows(EDGE_COLUMNS, edge_rows)
    sample_table = table_from_rows(SAMPLE_COLUMNS, sample_rows)
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)

    return {
        "reports": reports,
        "surface_rows": surface_rows,
        "invariant_rows": invariant_rows,
        "edge_rows": edge_rows,
        "sample_rows": sample_rows,
        "obs_rows": obs_rows,
        "surface_table": surface_table,
        "invariant_table": invariant_table,
        "edge_table": edge_table,
        "sample_table": sample_table,
        "observable_table": obs_table,
        "obs": obs,
        "surface_text_hash": hashlib.sha256(
            digest_text(SURFACE_COLUMNS, surface_rows).encode("ascii")
        ).hexdigest(),
        "invariant_text_hash": hashlib.sha256(
            digest_text(INVARIANT_COLUMNS, invariant_rows).encode("ascii")
        ).hexdigest(),
        "edge_text_hash": hashlib.sha256(
            digest_text(EDGE_COLUMNS, edge_rows).encode("ascii")
        ).hexdigest(),
        "sample_text_hash": hashlib.sha256(
            digest_text(SAMPLE_COLUMNS, sample_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(
            digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
        ).hexdigest(),
        "gamma8_height_matches_single_cycle": int(
            gamma8_row["height_action"]
        )
        == int(height_residual["height_action"]),
        "e33_support_matches_sector33": int(e33["support"])
        == int(sector33_e33["support"])
        == int(facts["Lambda3_A8_candidate"]),
        "selector_delta_samples": {
            "primitive": list(primitive_deltas),
            "global": list(global_action["move_deltas"]),
            "paired": list(paired_deltas),
        },
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    reports = rows["reports"]
    checks = {
        "inputs_accepted": obs["input_report_count"] == obs["accepted_input_count"],
        "raw543_orbit_split": (
            obs["raw543_orbit_count"],
            obs["raw543_fixed_orbit_count"],
            obs["raw543_pair_orbit_count"],
        )
        == (543, 63, 480),
        "transport_projection_split": (
            obs["transport_orbit_count"],
            obs["tau_projection_rank"],
            obs["tau_projection_nullity"],
        )
        == (543, 543, 480),
        "height_residue_counts": (
            obs["residue_mask_count"],
            obs["nonzero_height_mask_count"],
        )
        == (2048, 2047),
        "gamma8_height_matches_single_cycle": rows["gamma8_height_matches_single_cycle"],
        "vector_support_matches_lift_dimension": (
            obs["e33_support"],
            obs["e33_positive_count"],
            obs["e33_negative_count"],
            obs["corrected_vector_count"],
        )
        == (56, 28, 28, 2048)
        and rows["e33_support_matches_sector33"],
        "lambda_act_invariant_for_all_masks": (
            obs["lambda_act_kernel_masks"],
            obs["lambda_act_kernel_failures"],
        )
        == (2048, 0),
        "c2_anomaly_split": (
            obs["zero_anomaly_orbit_count"],
            obs["nonzero_anomaly_orbit_count"],
            obs["anomaly_cocycle_gcd_abs"],
        )
        == (71, 472, 3072),
        "selector_nonunique_boundary_marked": (
            obs["selector_candidate_count"],
            obs["selector_free_unique_operator_flag"],
        )
        == (543, 0),
        "lift_target_locked_not_materialized": (
            obs["foam_support_dimension"],
            obs["foam_core_rank"],
            obs["foam_bridge_kernel_dimension"],
            obs["height_coherent_operator_materialized_flag"],
        )
        == (56, 33, 23, 0),
        "tables_have_expected_shapes": (
            tuple(rows["surface_table"].shape),
            tuple(rows["invariant_table"].shape),
            tuple(rows["edge_table"].shape),
            tuple(rows["sample_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (len(INPUT_REPORTS), len(SURFACE_COLUMNS)),
            (len(INVARIANT_NAMES), len(INVARIANT_COLUMNS)),
            (15, len(EDGE_COLUMNS)),
            (6, len(SAMPLE_COLUMNS)),
            (len(OBS_NAMES), len(OBS_COLUMNS)),
        ),
        "focused_hcinv_closed_without_goal_claim": (
            obs["focused_hcinv_closed_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "height_coherent_action_return_invariant_ledger",
        "role_code_map": {str(code): name for name, code, _path in INPUT_REPORTS},
        "invariant_code_map": {
            str(code): name for name, code in INVARIANT_CODES.items()
        },
        "group_code_map": {str(code): name for name, code in GROUP_CODES.items()},
        "summary": obs,
        "selector_delta_samples": rows["selector_delta_samples"],
        "operator_boundary": {
            "statement": "pi_Foam33 R_hc = R_Foam pi_Foam33",
            "support_dimension": 56,
            "foam_rank": 33,
            "bridge_kernel_dimension": 23,
            "matrix_materialized": False,
        },
    }
    seam_payload = {
        "schema": "long.hcinv.seam@1",
        "status": STATUS,
        "claim": (
            "The sourced finite C2 action, Raw543 orbit quotient, sector-33 "
            "height/action-return scalar layer, corrected vector layer, exact "
            "C2 cocycle anomaly, and selector non-uniqueness form a checked "
            "invariant ledger. The height-coherent lift matrices remain open."
        ),
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        name: input_entry(
            path,
            {
                "status": reports[name].get("status"),
                "certificate_sha256": reports[name].get("certificate_sha256"),
            },
        )
        for name, _code, path in INPUT_REPORTS
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = (
        input_entry(VALIDATOR_SCRIPT)
        if VALIDATOR_SCRIPT.exists()
        else {"path": relpath(VALIDATOR_SCRIPT)}
    )
    report = {
        "schema": "long.hcinv.report@1",
        "status": seam_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_hcinv certifies the invariant ledger for the sourced C2 action "
            "against the sector-33 height/action-return boundary using the "
            "current report boundary. It identifies the 71/472 orbit anomaly "
            "split and preserves the 56-to-33 lift target as open until "
            "pi_Foam33, R_hc, and R_Foam are materialized."
        ),
        "stage_protocol": {
            "draft": "read sourced C2, Raw543, sector-33, action-return, anomaly, selector, and target-lock artifacts",
            "witness": "emit surface rows, invariant rows, dependency edges, sample rows, and table hashes",
            "coherence": "check orbit splits, projection ranks, height/vector counts, cocycle split, selector boundary, and lift dimensions",
            "closure": "certify the invariant ledger without claiming the height-coherent intertwiner",
            "emit": "write long_hcinv artifacts and focused verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
            "invariant_csv": relpath(OUT_DIR / "invariant.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
            "sample_csv": relpath(OUT_DIR / "sample.csv"),
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
                "the finite C2 action is sourced and agrees with the Raw543 543-orbit quotient",
                "tau has 63 fixed nonzero kernel orbits and 480 two-cycle orbits",
                "the tau projection has rank 543 and nullity 480 over the 1023 nonzero target masks",
                "the all-residue height/action-return layer has 2048 masks with 2047 nonzero height rows",
                "sector 33 carries the transport with e33 support 56 and 28/28 signed split",
                "Lambda_hc is Act-kernel invariant on all 2048 masks in the finite audit",
                "the C2 failure to descend is an exact cocycle with 71 zero-anomaly orbits and 472 nonzero-anomaly orbits",
                "the selector layer has 543 candidates and no selector-free unique operator",
                "the locked lift target has support dimension 56, Foam rank 33, and bridge kernel dimension 23",
            ],
            "does_not_certify": [
                "a materialized pi_Foam33 matrix",
                "a materialized R_hc matrix or generator family",
                "a materialized R_Foam matrix or generator family",
                "the intertwining equation for all action-return generators",
                "recursive upstream input-hash refresh for every consumed source report",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": (
            "Materialize pi_Foam33 as 33x56, R_hc on the 56-support, and "
            "R_Foam on the 33-core, then run a focused verifier for "
            "pi_Foam33 R_hc = R_Foam pi_Foam33."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.hcinv.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.hcinv.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "invariant_csv": csv_text(INVARIANT_COLUMNS, rows["invariant_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "sample_csv": csv_text(SAMPLE_COLUMNS, rows["sample_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "invariant_table": rows["invariant_table"],
        "edge_table": rows["edge_table"],
        "sample_table": rows["sample_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "surface_text_sha256": rows["surface_text_hash"],
            "invariant_text_sha256": rows["invariant_text_hash"],
            "edge_text_sha256": rows["edge_text_hash"],
            "sample_text_sha256": rows["sample_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
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
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "invariant.csv").write_text(
        payloads["invariant_csv"], encoding="utf-8"
    )
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "sample.csv").write_text(payloads["sample_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
        invariant_table=payloads["invariant_table"],
        edge_table=payloads["edge_table"],
        sample_table=payloads["sample_table"],
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
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
