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
        sha_array,
        write_json,
    )
    from .derive_long_orac import OBS_CODES as ORAC_OBS_CODES
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
    from derive_long_orac import OBS_CODES as ORAC_OBS_CODES
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_frontier"
STATUS = "LONG_FRONTIER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_ORAC_REPORT = PROOF_ROOT / "long_orac" / "report.json"
LONG_ORAC_OBS = PROOF_ROOT / "long_orac" / "obs.csv"
LONG_ORAC_TABLES = PROOF_ROOT / "long_orac" / "tables.npz"
LONG_INV_REPORT = PROOF_ROOT / "long_inv" / "report.json"
LONG_POBJ_REPORT = PROOF_ROOT / "long_pobj" / "report.json"
LONG_PATHS_REPORT = PROOF_ROOT / "long_paths" / "report.json"
LONG_MEASURE_REPORT = PROOF_ROOT / "long_measure" / "report.json"
LONG_INV_EXHAUST_REPORT = PROOF_ROOT / "long_inv_exhaust" / "report.json"
LONG_ANOM_REPORT = PROOF_ROOT / "long_anom" / "report.json"
LONG_AUTO_REPORT = PROOF_ROOT / "long_auto" / "report.json"
LONG_MAT_REPORT = PROOF_ROOT / "long_mat" / "report.json"
LONG_CLUSTER_REPORT = PROOF_ROOT / "long_cluster" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_frontier.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_frontier.py"

CARD_COLUMNS = [
    "card_id",
    "target_code",
    "status_code",
    "rank_code",
    "source_surface_code",
    "operator_code",
    "witness_code",
    "verifier_code",
    "dependency_code",
    "token_reduction_code",
    "goal_speedup_code",
    "proof_gap_count",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "card_count",
    "guardrail_closed_count",
    "frontier_open_count",
    "next_card_count",
    "oracle_input_count",
    "oracle_certified_input_count",
    "oracle_resolved_surface_count",
    "oracle_open_boundary_count",
    "oracle_inventory_update_needed_flag",
    "matrix_guardrail_closed_flag",
    "sector11_guardrail_closed_flag",
    "c2_guardrail_closed_flag",
    "anomaly_guardrail_closed_flag",
    "automorphic_guardrail_closed_flag",
    "matrix_boundary_guardrail_closed_flag",
    "cluster_reopened_count",
    "cluster_seam_candidate_count",
    "cluster_top_cluster_code",
    "path_object_decided_flag",
    "path_object_closed_flag",
    "raw_product_family_decided_flag",
    "measure_boundary_decided_flag",
    "scoped_measure_law_flag",
    "raw_product_family_materialized_flag",
    "h16_materialized_profunctor_flag",
    "h16_current_model_obstruction_flag",
    "raw_paths_exhaustive_flag",
    "full_raw_measure_certified_flag",
    "highest_yield_target_code",
    "highest_token_reduction_code",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_obs_csv(path: Path) -> dict[str, int]:
    rows = path.read_text(encoding="utf-8").strip().splitlines()
    if not rows or rows[0] != "observable_id,observable_code,value":
        raise AssertionError(f"{path} has unexpected observable header")
    by_code: dict[int, int] = {}
    for row in rows[1:]:
        _, code_text, value_text = row.split(",")
        by_code[int(code_text)] = int(value_text)
    return {name: by_code[code] for name, code in ORAC_OBS_CODES.items()}


def certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def build_rows() -> dict[str, Any]:
    orac_report = load_json(LONG_ORAC_REPORT)
    inv_report = load_json(LONG_INV_REPORT)
    pobj_report = load_json(LONG_POBJ_REPORT)
    paths_report = load_json(LONG_PATHS_REPORT)
    measure_report = load_json(LONG_MEASURE_REPORT)
    inv_exhaust_report = load_json(LONG_INV_EXHAUST_REPORT)
    anom_report = load_json(LONG_ANOM_REPORT)
    auto_report = load_json(LONG_AUTO_REPORT)
    mat_report = load_json(LONG_MAT_REPORT)
    cluster_report = load_json(LONG_CLUSTER_REPORT)
    orac_obs = read_obs_csv(LONG_ORAC_OBS)
    orac_summary = orac_report.get("witness", {}).get("summary", {})
    pobj_summary = pobj_report.get("witness", {}).get("summary", {})
    paths_summary = paths_report.get("witness", {}).get("summary", {})
    measure_summary = measure_report.get("witness", {}).get("summary", {})
    inv_exhaust_summary = inv_exhaust_report.get("witness", {}).get("summary", {})
    anom_summary = anom_report.get("witness", {}).get("summary", {})
    auto_summary = auto_report.get("witness", {}).get("summary", {})
    mat_summary = mat_report.get("witness", {}).get("summary", {})
    cluster_summary = cluster_report.get("witness", {}).get("summary", {})

    orac_ok = certified(orac_report, "LONG_ORAC_CERTIFIED")
    inv_ok = certified(inv_report, "LONG_INV_CERTIFIED")
    pobj_ok = certified(pobj_report, "LONG_POBJ_CERTIFIED")
    paths_ok = certified(paths_report, "LONG_PATHS_CERTIFIED")
    measure_ok = certified(measure_report, "LONG_MEASURE_CERTIFIED")
    inv_exhaust_ok = int(
        certified(inv_exhaust_report, "LONG_INV_EXHAUST_CERTIFIED")
        and int(inv_exhaust_summary.get("current_inventory_exhaustive_flag", 0)) == 1
        and int(inv_exhaust_summary.get("active_frontier_remaining_count", -1)) == 0
        and int(inv_exhaust_summary.get("absolute_exhaustiveness_claim_flag", -1))
        == 0
    )
    anom_ok = int(
        certified(anom_report, "LONG_ANOM_CERTIFIED")
        and int(anom_summary.get("current_anomaly_suite_closed_flag", 0)) == 1
        and int(anom_summary.get("residual_anomaly_boundary_count", -1)) == 0
        and int(anom_summary.get("resolved_surface_count", 0)) == 14
    )
    auto_ok = int(
        certified(auto_report, "LONG_AUTO_CERTIFIED")
        and int(auto_summary.get("current_automorphic_boundary_closed_flag", 0)) == 1
        and int(auto_summary.get("residual_auto_boundary_count", -1)) == 0
        and int(auto_summary.get("resolved_surface_count", 0)) == 18
    )
    mat_ok = int(
        certified(mat_report, "LONG_MAT_CERTIFIED")
        and int(mat_summary.get("current_matrix_boundary_closed_flag", 0)) == 1
        and int(
            mat_summary.get("residual_current_model_matrix_boundary_count", -1)
        )
        == 0
        and int(mat_summary.get("resolved_surface_count", 0)) == 37
    )
    cluster_ok = int(
        certified(cluster_report, "LONG_CLUSTER_CERTIFIED")
        and int(cluster_summary.get("reopened_cluster_count", 0)) > 0
        and int(cluster_summary.get("seam_candidate_count", 0)) > 0
        and int(cluster_summary.get("complete_goal_claim_flag", -1)) == 0
    )
    matrix_guardrail = int(
        (
            orac_obs["matrix_unit_count"],
            orac_obs["source_sector_count"],
            orac_obs["sector_character_row_count"],
        )
        == (985, 39, 38_415)
    )
    sector11_guardrail = int(
        (
            orac_obs["sector11_transition_mass"],
            orac_obs["sector11_valid_nonempty_extension_count"],
        )
        == (420, 0)
    )
    c2_guardrail = int(orac_obs["c2_anomaly_counterterm_flag"] == 1)
    path_object_decided = int(
        pobj_ok
        and int(pobj_summary.get("closed_path_object_flag", -1)) == 0
        and int(pobj_summary.get("sample_zeta_section_flag", 0)) == 1
        and str(pobj_summary.get("next_target")) == "long_paths"
    )
    raw_product_family_decided = int(
        paths_ok
        and int(paths_summary.get("compressed_raw_product_family_flag", 0)) == 1
        and int(paths_summary.get("component_path_total", 0)) == 64_570_080
        and str(paths_summary.get("next_target")) == "long_measure"
    )
    measure_boundary_decided = int(
        measure_ok
        and int(measure_summary.get("scoped_probability_law_flag", 0)) == 1
        and int(measure_summary.get("full_raw_scope_gap_flag", 0)) == 1
        and int(measure_summary.get("full_raw_measure_certified_flag", -1)) == 0
        and str(measure_summary.get("next_target")) == "long_h16"
    )
    h16_current_model_obstruction = int(
        orac_obs["h16_current_model_obstruction_flag"] == 1
        and orac_obs["h16_active_frontier_flag"] == 0
    )
    frontier_refresh_guardrail = int(
        orac_ok
        and inv_ok
        and pobj_ok
        and paths_ok
        and measure_ok
        and inv_exhaust_ok
        and anom_ok
        and auto_ok
        and mat_ok
        and cluster_ok
        and int(orac_summary.get("inventory_update_needed_flag", -1)) == 0
    )

    card_rows = [
        {
            "card_id": 0,
            "target_code": 0,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 4,
            "operator_code": 0,
            "witness_code": 0,
            "verifier_code": 0,
            "dependency_code": 0,
            "token_reduction_code": 2,
            "goal_speedup_code": 1,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 1,
            "target_code": 1,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 6,
            "operator_code": 0,
            "witness_code": 0,
            "verifier_code": 0,
            "dependency_code": 0,
            "token_reduction_code": 2,
            "goal_speedup_code": 1,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 2,
            "target_code": 2,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 7,
            "operator_code": 0,
            "witness_code": 0,
            "verifier_code": 0,
            "dependency_code": 0,
            "token_reduction_code": 2,
            "goal_speedup_code": 1,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 3,
            "target_code": 8,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 8,
            "operator_code": 6,
            "witness_code": 6,
            "verifier_code": 6,
            "dependency_code": 0,
            "token_reduction_code": 3,
            "goal_speedup_code": 2,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 4,
            "target_code": 3,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 22,
            "operator_code": 1,
            "witness_code": 1,
            "verifier_code": 1,
            "dependency_code": 0,
            "token_reduction_code": 3,
            "goal_speedup_code": 3,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 5,
            "target_code": 4,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 21,
            "operator_code": 2,
            "witness_code": 2,
            "verifier_code": 2,
            "dependency_code": 1,
            "token_reduction_code": 3,
            "goal_speedup_code": 3,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 6,
            "target_code": 5,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 24,
            "operator_code": 3,
            "witness_code": 3,
            "verifier_code": 3,
            "dependency_code": 2,
            "token_reduction_code": 3,
            "goal_speedup_code": 3,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 7,
            "target_code": 6,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 9,
            "operator_code": 4,
            "witness_code": 4,
            "verifier_code": 4,
            "dependency_code": 5,
            "token_reduction_code": 2,
            "goal_speedup_code": 2,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 8,
            "target_code": 7,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 8,
            "operator_code": 5,
            "witness_code": 5,
            "verifier_code": 5,
            "dependency_code": 5,
            "token_reduction_code": 1,
            "goal_speedup_code": 1,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 9,
            "target_code": 9,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 26,
            "operator_code": 0,
            "witness_code": 0,
            "verifier_code": 7,
            "dependency_code": 0,
            "token_reduction_code": 2,
            "goal_speedup_code": 1,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 10,
            "target_code": 10,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 27,
            "operator_code": 0,
            "witness_code": 0,
            "verifier_code": 8,
            "dependency_code": 0,
            "token_reduction_code": 2,
            "goal_speedup_code": 1,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 11,
            "target_code": 11,
            "status_code": 0,
            "rank_code": 99,
            "source_surface_code": 28,
            "operator_code": 0,
            "witness_code": 0,
            "verifier_code": 9,
            "dependency_code": 0,
            "token_reduction_code": 2,
            "goal_speedup_code": 1,
            "proof_gap_count": 0,
            "next_flag": 0,
        },
        {
            "card_id": 12,
            "target_code": 12,
            "status_code": 1,
            "rank_code": 0,
            "source_surface_code": 29,
            "operator_code": 7,
            "witness_code": 7,
            "verifier_code": 10,
            "dependency_code": 6,
            "token_reduction_code": 4,
            "goal_speedup_code": 4,
            "proof_gap_count": int(cluster_ok),
            "next_flag": int(cluster_ok),
        },
    ]
    open_rows = [row for row in card_rows if row["status_code"] == 1]
    next_rows = [row for row in card_rows if row["next_flag"] == 1]
    obs = {
        "card_count": len(card_rows),
        "guardrail_closed_count": sum(row["status_code"] == 0 for row in card_rows),
        "frontier_open_count": len(open_rows),
        "next_card_count": len(next_rows),
        "oracle_input_count": int(orac_summary.get("input_report_count", 0)),
        "oracle_certified_input_count": int(
            orac_summary.get("input_certified_count", 0)
        ),
        "oracle_resolved_surface_count": int(
            orac_summary.get("resolved_surface_count", 0)
        ),
        "oracle_open_boundary_count": int(orac_summary.get("open_boundary_count", 0)),
        "oracle_inventory_update_needed_flag": int(
            orac_summary.get("inventory_update_needed_flag", -1)
        ),
        "matrix_guardrail_closed_flag": matrix_guardrail,
        "sector11_guardrail_closed_flag": sector11_guardrail,
        "c2_guardrail_closed_flag": c2_guardrail,
        "anomaly_guardrail_closed_flag": anom_ok,
        "automorphic_guardrail_closed_flag": auto_ok,
        "matrix_boundary_guardrail_closed_flag": mat_ok,
        "cluster_reopened_count": int(cluster_summary.get("reopened_cluster_count", 0)),
        "cluster_seam_candidate_count": int(
            cluster_summary.get("seam_candidate_count", 0)
        ),
        "cluster_top_cluster_code": int(cluster_summary.get("top_cluster_code", -1)),
        "path_object_decided_flag": path_object_decided,
        "path_object_closed_flag": int(
            pobj_summary.get("closed_path_object_flag", -1)
        ),
        "raw_product_family_decided_flag": raw_product_family_decided,
        "measure_boundary_decided_flag": measure_boundary_decided,
        "scoped_measure_law_flag": int(
            measure_summary.get("scoped_probability_law_flag", 0)
        ),
        "raw_product_family_materialized_flag": int(
            paths_summary.get("materialized_raw_path_family_flag", -1)
        ),
        "h16_materialized_profunctor_flag": int(
            orac_obs["h16_materialized_profunctor_flag"]
        ),
        "h16_current_model_obstruction_flag": h16_current_model_obstruction,
        "raw_paths_exhaustive_flag": int(orac_obs["long_path_all_raw_paths_flag"]),
        "full_raw_measure_certified_flag": 0,
        "highest_yield_target_code": int(next_rows[0]["target_code"])
        if next_rows
        else -1,
        "highest_token_reduction_code": max(
            row["token_reduction_code"] for row in open_rows
        )
        if open_rows
        else 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "orac_report": orac_report,
        "inv_report": inv_report,
        "pobj_report": pobj_report,
        "paths_report": paths_report,
        "measure_report": measure_report,
        "inv_exhaust_report": inv_exhaust_report,
        "anom_report": anom_report,
        "auto_report": auto_report,
        "mat_report": mat_report,
        "cluster_report": cluster_report,
        "card_rows": card_rows,
        "obs_rows": obs_rows,
        "card_table": table_from_rows(CARD_COLUMNS, card_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "card_text_hash": hashlib.sha256(
            digest_text(CARD_COLUMNS, card_rows).encode("ascii")
        ).hexdigest(),
        "obs": obs,
        "guardrails": {
            "matrix": matrix_guardrail,
            "sector11": sector11_guardrail,
            "c2": c2_guardrail,
            "path_object": path_object_decided,
            "raw_product_family": raw_product_family_decided,
            "measure_boundary": measure_boundary_decided,
            "h16_current_model_obstruction": h16_current_model_obstruction,
            "inventory_exhaust": inv_exhaust_ok,
            "anomaly_suite": anom_ok,
            "automorphic_boundary": auto_ok,
            "matrix_boundary": mat_ok,
            "frontier_refresh": frontier_refresh_guardrail,
        },
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    card_rows = rows["card_rows"]
    open_order = [
        row["target_code"]
        for row in sorted(
            [row for row in card_rows if row["status_code"] == 1],
            key=lambda row: row["rank_code"],
        )
    ]
    checks = {
        "inputs_certified": (
            rows["orac_report"].get("status") == "LONG_ORAC_CERTIFIED"
            and rows["orac_report"].get("all_checks_pass") is True
            and rows["inv_report"].get("status") == "LONG_INV_CERTIFIED"
            and rows["inv_report"].get("all_checks_pass") is True
            and rows["pobj_report"].get("status") == "LONG_POBJ_CERTIFIED"
            and rows["pobj_report"].get("all_checks_pass") is True
            and rows["paths_report"].get("status") == "LONG_PATHS_CERTIFIED"
            and rows["paths_report"].get("all_checks_pass") is True
            and rows["measure_report"].get("status") == "LONG_MEASURE_CERTIFIED"
            and rows["measure_report"].get("all_checks_pass") is True
            and rows["inv_exhaust_report"].get("status")
            == "LONG_INV_EXHAUST_CERTIFIED"
            and rows["inv_exhaust_report"].get("all_checks_pass") is True
            and rows["anom_report"].get("status") == "LONG_ANOM_CERTIFIED"
            and rows["anom_report"].get("all_checks_pass") is True
            and rows["auto_report"].get("status") == "LONG_AUTO_CERTIFIED"
            and rows["auto_report"].get("all_checks_pass") is True
            and rows["mat_report"].get("status") == "LONG_MAT_CERTIFIED"
            and rows["mat_report"].get("all_checks_pass") is True
            and rows["cluster_report"].get("status") == "LONG_CLUSTER_CERTIFIED"
            and rows["cluster_report"].get("all_checks_pass") is True
        ),
        "oracle_summary_exact": (
            obs["oracle_input_count"],
            obs["oracle_certified_input_count"],
            obs["oracle_resolved_surface_count"],
            obs["oracle_open_boundary_count"],
            obs["oracle_inventory_update_needed_flag"],
        )
        == (31, 31, 29, 22, 0),
        "guardrails_closed": (
            rows["guardrails"]["matrix"],
            rows["guardrails"]["sector11"],
            rows["guardrails"]["c2"],
            rows["guardrails"]["path_object"],
            rows["guardrails"]["raw_product_family"],
            rows["guardrails"]["measure_boundary"],
            rows["guardrails"]["h16_current_model_obstruction"],
            rows["guardrails"]["inventory_exhaust"],
            rows["guardrails"]["anomaly_suite"],
            rows["guardrails"]["automorphic_boundary"],
            rows["guardrails"]["matrix_boundary"],
            rows["guardrails"]["frontier_refresh"],
        )
        == (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        "cluster_reopen_recorded": (
            obs["cluster_reopened_count"] > 0
            and obs["cluster_seam_candidate_count"] > 0
            and obs["cluster_top_cluster_code"] >= 0
        ),
        "frontier_order_exact": open_order == [12],
        "single_next_target": (
            obs["next_card_count"],
            obs["highest_yield_target_code"],
        )
        == (1, 12),
        "token_reduction_frontloaded": obs["highest_token_reduction_code"] == 4,
        "open_debt_not_overclaimed": (
            obs["frontier_open_count"],
            obs["path_object_decided_flag"],
            obs["path_object_closed_flag"],
            obs["raw_product_family_decided_flag"],
            obs["measure_boundary_decided_flag"],
            obs["anomaly_guardrail_closed_flag"],
            obs["automorphic_guardrail_closed_flag"],
            obs["matrix_boundary_guardrail_closed_flag"],
            obs["scoped_measure_law_flag"],
            obs["raw_product_family_materialized_flag"],
            obs["h16_materialized_profunctor_flag"],
            obs["h16_current_model_obstruction_flag"],
            obs["raw_paths_exhaustive_flag"],
            obs["full_raw_measure_certified_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0),
        "table_shapes_match": (
            tuple(rows["card_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == ((13, len(CARD_COLUMNS)), (len(OBS_CODES), len(OBS_COLUMNS))),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "certificate_frontier_planner",
        "process_ontology": {
            "0": "certified_surface",
            "1": "open_boundary",
            "2": "candidate_operator",
            "3": "witness_artifact",
            "4": "focused_verifier",
            "5": "oracle_refresh",
        },
        "target_code_map": {
            "0": "matrix_sector_gauge_guardrail",
            "1": "screen12_11_support_obstruction_guardrail",
            "2": "c2_counterterm_guardrail",
            "3": "long_pobj",
            "4": "long_paths",
            "5": "long_measure",
            "6": "long_h16",
            "7": "long_inv_exhaust",
            "8": "long_frontier_refresh",
            "9": "finite_anomaly_correction_suite_guardrail",
            "10": "finite_automorphic_boundary_guardrail",
            "11": "finite_matrix_theoretic_charge_wall_guardrail",
            "12": "long_cluster_reopen_audit",
        },
        "operator_code_map": {
            "0": "closed_guardrail",
            "1": "path_object_upgrade_test",
            "2": "raw_path_exhaustion",
            "3": "raw_support_measure_kernel",
            "4": "genuine_h16_owner_raw_profunctor_materialization",
            "5": "invariant_family_exhaustiveness_cover",
            "6": "oracle_frontier_refresh",
            "7": "clustered_reopen_seam_materialization",
        },
        "witness_code_map": {
            "0": "existing_certificate",
            "1": "path_object_closure_rows",
            "2": "raw_path_family_rows",
            "3": "raw_support_measure_rows",
            "4": "owner_raw_path_profunctor_rows",
            "5": "invariant_family_cover_rows",
            "6": "frontier_card_rows",
            "7": "cluster_seam_rows",
        },
        "verifier_code_map": {
            "0": "current_focused_verifier",
            "1": "long-pobj",
            "2": "long-paths",
            "3": "long-measure",
            "4": "long-h16",
            "5": "long-inv-exhaust",
            "6": "long-frontier",
            "7": "long-anom",
            "8": "long-auto",
            "9": "long-mat",
            "10": "long-cluster",
        },
        "dependency_code_map": {
            "0": "none",
            "1": "after_long_pobj_decision",
            "2": "after_long_paths_partition",
            "4": "after_paths_measure_h16_frontier",
            "5": "after_long_measure_boundary",
            "6": "after_cluster_reopen_audit",
        },
        "summary": {
            "card_count": obs["card_count"],
            "guardrail_closed_count": obs["guardrail_closed_count"],
            "frontier_open_count": obs["frontier_open_count"],
            "next_target": "long_cluster_top_seam",
            "highest_yield_target_code": obs["highest_yield_target_code"],
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "card_text_sha256": rows["card_text_hash"],
        "card_table_sha256": sha_array(rows["card_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    frontier_payload = {
        "schema": "long.frontier@1",
        "object": "certificate_frontier_planner",
        "status": STATUS if all(checks.values()) else "LONG_FRONTIER_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.frontier.report@1",
        "status": frontier_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_frontier certifies the operational point of long_orac: it turns "
            "the oracle/anomaly status split into a ranked certificate frontier. "
            "Matrix-sector gauge, screen12=11, C2, the long_pobj decision, "
            "compressed long_paths accounting, scoped long_measure laws, the "
            "current-model h16 obstruction, bounded long_inv_exhaust cover, "
            "finite long_anom correction suite, and oracle synchronization are "
            "closed guardrails; the finite long_auto automorphic/Fourier boundary "
            "and finite long_mat matrix-theory boundary are also closed guardrails; "
            "long_cluster reopens the next focused target by clustering certified "
            "reports outside the current oracle inputs."
        ),
        "stage_protocol": {
            "draft": "read long_orac and long_inv reports plus oracle observable rows",
            "witness": "emit ranked frontier cards and observable counts",
            "coherence": "check guardrails, oracle counts, frontier order, next target, table shapes, and hashes",
            "closure": "certify a planning frontier without claiming open theorem debt is solved",
            "emit": "write long_frontier artifacts and verifier hook",
        },
        "inputs": {
            "long_orac_report": input_entry(
                LONG_ORAC_REPORT,
                {
                    "status": rows["orac_report"].get("status"),
                    "certificate_sha256": rows["orac_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_orac_obs": input_entry(LONG_ORAC_OBS),
            "long_orac_tables": input_entry(LONG_ORAC_TABLES),
            "long_inv_report": input_entry(
                LONG_INV_REPORT,
                {
                    "status": rows["inv_report"].get("status"),
                    "certificate_sha256": rows["inv_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_pobj_report": input_entry(
                LONG_POBJ_REPORT,
                {
                    "status": rows["pobj_report"].get("status"),
                    "certificate_sha256": rows["pobj_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_paths_report": input_entry(
                LONG_PATHS_REPORT,
                {
                    "status": rows["paths_report"].get("status"),
                    "certificate_sha256": rows["paths_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_measure_report": input_entry(
                LONG_MEASURE_REPORT,
                {
                    "status": rows["measure_report"].get("status"),
                    "certificate_sha256": rows["measure_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_inv_exhaust_report": input_entry(
                LONG_INV_EXHAUST_REPORT,
                {
                    "status": rows["inv_exhaust_report"].get("status"),
                    "certificate_sha256": rows["inv_exhaust_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_anom_report": input_entry(
                LONG_ANOM_REPORT,
                {
                    "status": rows["anom_report"].get("status"),
                    "certificate_sha256": rows["anom_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_auto_report": input_entry(
                LONG_AUTO_REPORT,
                {
                    "status": rows["auto_report"].get("status"),
                    "certificate_sha256": rows["auto_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_mat_report": input_entry(
                LONG_MAT_REPORT,
                {
                    "status": rows["mat_report"].get("status"),
                    "certificate_sha256": rows["mat_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_cluster_report": input_entry(
                LONG_CLUSTER_REPORT,
                {
                    "status": rows["cluster_report"].get("status"),
                    "certificate_sha256": rows["cluster_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "frontier": relpath(OUT_DIR / "frontier.json"),
            "cards_csv": relpath(OUT_DIR / "cards.csv"),
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
                "the oracle has an actionable process ontology: certified surface -> open boundary -> candidate operator -> witness artifact -> focused verifier -> oracle refresh",
                "matrix-sector gauge, screen12=11, C2, the long_pobj decision, compressed long_paths accounting, scoped long_measure laws, the current-model h16 obstruction, bounded long_inv_exhaust cover, finite long_anom correction, finite long_auto automorphic/Fourier closure, finite long_mat matrix-theory closure, and oracle synchronization are guardrails rather than current search targets",
                "long_cluster reopens the current focused frontier with ranked multi-theme seam candidates",
                "focused token reduction now comes from avoiding broad integration gates until the operator permits them",
            ],
            "does_not_certify_because_out_of_scope": [
                "materialized rows for every raw address path",
                "exact C985 source/target composability of all raw paths",
                "a probability measure on the full raw tensor support independent of the current active-product boundary",
                "a genuine horizon-16 profunctor",
                "absolute invariant-family exhaustiveness outside the current oracle ontology",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Materialize the top long_cluster seam as a dedicated focused proof "
            "obligation, then feed its decision back into long_orac and "
            "long_frontier."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.frontier.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.frontier.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "frontier": frontier_payload,
        "cards_csv": csv_text(CARD_COLUMNS, rows["card_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "card_table": rows["card_table"],
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
    write_json(OUT_DIR / "frontier.json", payloads["frontier"])
    (OUT_DIR / "cards.csv").write_text(payloads["cards_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        card_table=payloads["card_table"],
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
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
