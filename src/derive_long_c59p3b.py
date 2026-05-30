from __future__ import annotations

import csv
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
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_c59p3b"
STATUS = "LONG_C59P3B_BASIS_STRESS_ATOM_BRIDGE_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3T = PROOF_ROOT / "long_c59p3t" / "report.json"
LONG_C59P3T_JOIN = PROOF_ROOT / "long_c59p3t" / "join.csv"
LONG_C59P3T_OBS = PROOF_ROOT / "long_c59p3t" / "obs.csv"
LONG_ABMAP = PROOF_ROOT / "long_abmap" / "report.json"
LONG_ABMAP_CSP = PROOF_ROOT / "long_abmap" / "csp.csv"
LONG_ABMAP_MATCH = PROOF_ROOT / "long_abmap" / "match.csv"
LONG_ABMAP_OBS = PROOF_ROOT / "long_abmap" / "obs.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_CONTACT_LIFT = PROOF_ROOT / "long_contact_lift" / "report.json"
LONG_C59P3A = PROOF_ROOT / "long_c59p3a" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3b.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3b.py"

SURFACE_COLUMNS = [
    "surface_id",
    "surface_code",
    "row_count",
    "certified_flag",
    "relation_cover_flag",
    "functorial_map_flag",
    "schema_atom_key_flag",
    "stress_atom_key_flag",
]
BRIDGE_COLUMNS = [
    "bridge_id",
    "bridge_code",
    "source_surface_code",
    "target_surface_code",
    "relation_cover_flag",
    "single_valued_flag",
    "schema_key_flag",
    "candidate_count",
    "certified_map_flag",
    "obstruction_flag",
]
DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "value",
    "certified_flag",
    "obstruction_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SURFACE_NAMES = [
    "atom_overlap_stress_score",
    "stress_edge_surface",
    "guarded_transition_surface",
    "contact_lift_surface",
    "raw_endpoint_surface",
    "atom_basis_relation_cover",
    "atom_basis_csp",
]
SURFACE_CODES = {name: index for index, name in enumerate(SURFACE_NAMES)}

BRIDGE_NAMES = [
    "directed_atom_basis_relation",
    "undirected_atom_basis_relation",
    "contact_endpoint_basis_bridge",
    "endpoint_atom_schema_key",
    "raw_endpoint_stress_atom_bridge",
    "transition_overlap_score_consumption",
    "basis_stress_atom_bridge",
]
BRIDGE_CODES = {name: index for index, name in enumerate(BRIDGE_NAMES)}

DECISION_NAMES = [
    "relation_level_cover_available",
    "directed_cover_complete",
    "undirected_cover_functorial",
    "endpoint_atom_key_available",
    "basis_stress_atom_bridge_available",
    "transition_stress_map_available",
    "semantic_transition_operation_available",
    "current_boundary_lift_ready",
    "current_boundary_obstruction_certified",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}

GAP_NAMES = [
    "relation_level_atom_basis_cover",
    "functorial_atom_basis_map",
    "endpoint_atom_schema_key",
    "raw_endpoint_stress_atom_bridge",
    "transition_stress_coupling_map",
    "semantic_transition_operation",
    "physical_selector_axiom",
    "four_dimensional_metric_reduction",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "transition_row_count",
    "contact_row_count",
    "endpoint_row_count",
    "stress_edge_row_count",
    "atom_overlap_row_count",
    "atom_basis_domain_row_count",
    "atom_basis_match_row_count",
    "directed_edge_covered_count",
    "directed_candidate_pair_count",
    "directed_cover_complete_flag",
    "directed_functorial_map_exists_flag",
    "undirected_edge_covered_count",
    "undirected_candidate_pair_count",
    "undirected_max_pair_multiplicity",
    "undirected_relation_cover_flag",
    "undirected_functorial_map_exists_flag",
    "atom_to_basis_function_certified_flag",
    "contact_endpoint_bridge_flag",
    "endpoint_atom_column_count",
    "endpoint_overlap_shared_key_count",
    "transition_overlap_shared_key_count",
    "atom_transition_bridge_flag",
    "basis_stress_atom_bridge_flag",
    "raw_endpoint_stress_atom_bridge_flag",
    "transition_stress_map_certified_flag",
    "current_schema_consumes_atom_score_flag",
    "semantic_transition_operation_flag",
    "physical_selector_axiom_flag",
    "four_dimensional_metric_flag",
    "thermal_gravity_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

C59P3T_OBS_CODES = {
    "contact_row_count": 4,
    "endpoint_row_count": 5,
    "contact_endpoint_bridge_flag": 9,
    "endpoint_overlap_shared_key_count": 13,
    "transition_overlap_shared_key_count": 11,
    "endpoint_atom_column_count": 17,
}

ABMAP_OBS_CODES = {
    "directed_functorial_map_exists_flag": 9,
}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and (
        "CERTIFIED" in str(report.get("status", ""))
        or "OBSTRUCTION_CERTIFIED" in str(report.get("status", ""))
    )


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    value = witness.get("summary", {})
    if not isinstance(value, dict):
        raise AssertionError("report witness summary is not an object")
    return value


def obs_from_rows(rows: list[dict[str, str]]) -> dict[int, int]:
    return {int(row["observable_code"]): int(row["value"]) for row in rows}


def build_rows() -> dict[str, Any]:
    c59p3t = load_json(LONG_C59P3T)
    abmap = load_json(LONG_ABMAP)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    contact_lift = load_json(LONG_CONTACT_LIFT)
    c59p3a = load_json(LONG_C59P3A)

    _, c59p3t_join_rows = read_csv_rows(LONG_C59P3T_JOIN)
    _, c59p3t_obs_rows = read_csv_rows(LONG_C59P3T_OBS)
    _, abmap_csp_rows = read_csv_rows(LONG_ABMAP_CSP)
    _, abmap_match_rows = read_csv_rows(LONG_ABMAP_MATCH)
    _, abmap_obs_rows = read_csv_rows(LONG_ABMAP_OBS)

    t_summary = summary(c59p3t)
    a_summary = summary(abmap)
    c59p3a_summary = summary(c59p3a)
    c59p3t_obs = obs_from_rows(c59p3t_obs_rows)
    abmap_obs = obs_from_rows(abmap_obs_rows)

    directed_cover_complete_flag = int(a_summary["directed_edge_covered_count"] == 20)
    basis_stress_atom_bridge_flag = int(
        a_summary["atom_to_basis_function_certified_flag"] == 1
        and t_summary["transition_stress_map_certified_flag"] == 1
    )
    raw_endpoint_stress_atom_bridge_flag = int(
        c59p3t_obs[C59P3T_OBS_CODES["contact_endpoint_bridge_flag"]] == 1
        and c59p3t_obs[C59P3T_OBS_CODES["endpoint_atom_column_count"]] > 0
        and basis_stress_atom_bridge_flag == 1
    )
    current_boundary_lift_ready_flag = int(
        raw_endpoint_stress_atom_bridge_flag == 1
        and t_summary["current_schema_consumes_atom_score_flag"] == 1
        and t_summary["semantic_transition_operation_flag"] == 1
    )
    obstruction_certified_flag = int(current_boundary_lift_ready_flag == 0)
    obs = {
        "input_report_count": 5,
        "input_certified_count": int(certified(c59p3t))
        + int(certified(abmap))
        + int(certified(transition_sem))
        + int(certified(contact_lift))
        + int(certified(c59p3a)),
        "transition_row_count": int(t_summary["transition_row_count"]),
        "contact_row_count": c59p3t_obs[C59P3T_OBS_CODES["contact_row_count"]],
        "endpoint_row_count": c59p3t_obs[C59P3T_OBS_CODES["endpoint_row_count"]],
        "stress_edge_row_count": int(t_summary["stress_edge_row_count"]),
        "atom_overlap_row_count": int(t_summary["overlap_row_count"]),
        "atom_basis_domain_row_count": int(a_summary["domain_row_count"]),
        "atom_basis_match_row_count": len(abmap_match_rows),
        "directed_edge_covered_count": int(a_summary["directed_edge_covered_count"]),
        "directed_candidate_pair_count": int(a_summary["directed_candidate_pair_count"]),
        "directed_cover_complete_flag": directed_cover_complete_flag,
        "directed_functorial_map_exists_flag": abmap_obs[
            ABMAP_OBS_CODES["directed_functorial_map_exists_flag"]
        ],
        "undirected_edge_covered_count": int(a_summary["undirected_edge_covered_count"]),
        "undirected_candidate_pair_count": int(
            a_summary["undirected_candidate_pair_count"]
        ),
        "undirected_max_pair_multiplicity": int(
            a_summary["undirected_max_pair_multiplicity"]
        ),
        "undirected_relation_cover_flag": int(
            a_summary["undirected_relation_cover_flag"]
        ),
        "undirected_functorial_map_exists_flag": int(
            a_summary["undirected_functorial_map_exists_flag"]
        ),
        "atom_to_basis_function_certified_flag": int(
            a_summary["atom_to_basis_function_certified_flag"]
        ),
        "contact_endpoint_bridge_flag": c59p3t_obs[
            C59P3T_OBS_CODES["contact_endpoint_bridge_flag"]
        ],
        "endpoint_atom_column_count": c59p3t_obs[
            C59P3T_OBS_CODES["endpoint_atom_column_count"]
        ],
        "endpoint_overlap_shared_key_count": c59p3t_obs[
            C59P3T_OBS_CODES["endpoint_overlap_shared_key_count"]
        ],
        "transition_overlap_shared_key_count": c59p3t_obs[
            C59P3T_OBS_CODES["transition_overlap_shared_key_count"]
        ],
        "atom_transition_bridge_flag": int(t_summary["atom_transition_bridge_flag"]),
        "basis_stress_atom_bridge_flag": basis_stress_atom_bridge_flag,
        "raw_endpoint_stress_atom_bridge_flag": raw_endpoint_stress_atom_bridge_flag,
        "transition_stress_map_certified_flag": int(
            t_summary["transition_stress_map_certified_flag"]
        ),
        "current_schema_consumes_atom_score_flag": int(
            t_summary["current_schema_consumes_atom_score_flag"]
        ),
        "semantic_transition_operation_flag": int(
            t_summary["semantic_transition_operation_flag"]
        ),
        "physical_selector_axiom_flag": int(
            c59p3a_summary["physical_selector_axiom_flag"]
        ),
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["functorial_atom_basis_map"],
    }
    surface_rows = [
        {
            "surface_id": SURFACE_CODES["atom_overlap_stress_score"],
            "surface_code": SURFACE_CODES["atom_overlap_stress_score"],
            "row_count": obs["atom_overlap_row_count"],
            "certified_flag": 1,
            "relation_cover_flag": 0,
            "functorial_map_flag": 0,
            "schema_atom_key_flag": 1,
            "stress_atom_key_flag": 1,
        },
        {
            "surface_id": SURFACE_CODES["stress_edge_surface"],
            "surface_code": SURFACE_CODES["stress_edge_surface"],
            "row_count": obs["stress_edge_row_count"],
            "certified_flag": 1,
            "relation_cover_flag": 0,
            "functorial_map_flag": 0,
            "schema_atom_key_flag": 1,
            "stress_atom_key_flag": 1,
        },
        {
            "surface_id": SURFACE_CODES["guarded_transition_surface"],
            "surface_code": SURFACE_CODES["guarded_transition_surface"],
            "row_count": obs["transition_row_count"],
            "certified_flag": 1,
            "relation_cover_flag": 0,
            "functorial_map_flag": 0,
            "schema_atom_key_flag": 0,
            "stress_atom_key_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["contact_lift_surface"],
            "surface_code": SURFACE_CODES["contact_lift_surface"],
            "row_count": obs["contact_row_count"],
            "certified_flag": 1,
            "relation_cover_flag": 0,
            "functorial_map_flag": 0,
            "schema_atom_key_flag": 0,
            "stress_atom_key_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["raw_endpoint_surface"],
            "surface_code": SURFACE_CODES["raw_endpoint_surface"],
            "row_count": obs["endpoint_row_count"],
            "certified_flag": 1,
            "relation_cover_flag": 0,
            "functorial_map_flag": 0,
            "schema_atom_key_flag": 0,
            "stress_atom_key_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["atom_basis_relation_cover"],
            "surface_code": SURFACE_CODES["atom_basis_relation_cover"],
            "row_count": obs["atom_basis_match_row_count"],
            "certified_flag": 1,
            "relation_cover_flag": obs["undirected_relation_cover_flag"],
            "functorial_map_flag": obs["atom_to_basis_function_certified_flag"],
            "schema_atom_key_flag": 1,
            "stress_atom_key_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["atom_basis_csp"],
            "surface_code": SURFACE_CODES["atom_basis_csp"],
            "row_count": len(abmap_csp_rows),
            "certified_flag": 1,
            "relation_cover_flag": obs["undirected_relation_cover_flag"],
            "functorial_map_flag": obs["atom_to_basis_function_certified_flag"],
            "schema_atom_key_flag": 1,
            "stress_atom_key_flag": 0,
        },
    ]
    bridge_rows = [
        {
            "bridge_id": BRIDGE_CODES["directed_atom_basis_relation"],
            "bridge_code": BRIDGE_CODES["directed_atom_basis_relation"],
            "source_surface_code": SURFACE_CODES["atom_basis_relation_cover"],
            "target_surface_code": SURFACE_CODES["guarded_transition_surface"],
            "relation_cover_flag": obs["directed_cover_complete_flag"],
            "single_valued_flag": obs["directed_functorial_map_exists_flag"],
            "schema_key_flag": 1,
            "candidate_count": obs["directed_candidate_pair_count"],
            "certified_map_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "bridge_id": BRIDGE_CODES["undirected_atom_basis_relation"],
            "bridge_code": BRIDGE_CODES["undirected_atom_basis_relation"],
            "source_surface_code": SURFACE_CODES["atom_basis_relation_cover"],
            "target_surface_code": SURFACE_CODES["guarded_transition_surface"],
            "relation_cover_flag": obs["undirected_relation_cover_flag"],
            "single_valued_flag": obs["undirected_functorial_map_exists_flag"],
            "schema_key_flag": 1,
            "candidate_count": obs["undirected_candidate_pair_count"],
            "certified_map_flag": obs["atom_to_basis_function_certified_flag"],
            "obstruction_flag": 1,
        },
        {
            "bridge_id": BRIDGE_CODES["contact_endpoint_basis_bridge"],
            "bridge_code": BRIDGE_CODES["contact_endpoint_basis_bridge"],
            "source_surface_code": SURFACE_CODES["contact_lift_surface"],
            "target_surface_code": SURFACE_CODES["raw_endpoint_surface"],
            "relation_cover_flag": obs["contact_endpoint_bridge_flag"],
            "single_valued_flag": 1,
            "schema_key_flag": 1,
            "candidate_count": obs["endpoint_row_count"],
            "certified_map_flag": obs["contact_endpoint_bridge_flag"],
            "obstruction_flag": 0,
        },
        {
            "bridge_id": BRIDGE_CODES["endpoint_atom_schema_key"],
            "bridge_code": BRIDGE_CODES["endpoint_atom_schema_key"],
            "source_surface_code": SURFACE_CODES["raw_endpoint_surface"],
            "target_surface_code": SURFACE_CODES["atom_overlap_stress_score"],
            "relation_cover_flag": 0,
            "single_valued_flag": 0,
            "schema_key_flag": int(obs["endpoint_atom_column_count"] > 0),
            "candidate_count": obs["endpoint_overlap_shared_key_count"],
            "certified_map_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "bridge_id": BRIDGE_CODES["raw_endpoint_stress_atom_bridge"],
            "bridge_code": BRIDGE_CODES["raw_endpoint_stress_atom_bridge"],
            "source_surface_code": SURFACE_CODES["raw_endpoint_surface"],
            "target_surface_code": SURFACE_CODES["stress_edge_surface"],
            "relation_cover_flag": 0,
            "single_valued_flag": 0,
            "schema_key_flag": 0,
            "candidate_count": 0,
            "certified_map_flag": obs["raw_endpoint_stress_atom_bridge_flag"],
            "obstruction_flag": 1,
        },
        {
            "bridge_id": BRIDGE_CODES["transition_overlap_score_consumption"],
            "bridge_code": BRIDGE_CODES["transition_overlap_score_consumption"],
            "source_surface_code": SURFACE_CODES["guarded_transition_surface"],
            "target_surface_code": SURFACE_CODES["atom_overlap_stress_score"],
            "relation_cover_flag": 0,
            "single_valued_flag": 0,
            "schema_key_flag": 0,
            "candidate_count": obs["transition_overlap_shared_key_count"],
            "certified_map_flag": obs["current_schema_consumes_atom_score_flag"],
            "obstruction_flag": 1,
        },
        {
            "bridge_id": BRIDGE_CODES["basis_stress_atom_bridge"],
            "bridge_code": BRIDGE_CODES["basis_stress_atom_bridge"],
            "source_surface_code": SURFACE_CODES["atom_basis_csp"],
            "target_surface_code": SURFACE_CODES["stress_edge_surface"],
            "relation_cover_flag": obs["undirected_relation_cover_flag"],
            "single_valued_flag": obs["undirected_functorial_map_exists_flag"],
            "schema_key_flag": 0,
            "candidate_count": 0,
            "certified_map_flag": obs["basis_stress_atom_bridge_flag"],
            "obstruction_flag": 1,
        },
    ]
    decision_values = {
        "relation_level_cover_available": obs["undirected_relation_cover_flag"],
        "directed_cover_complete": obs["directed_cover_complete_flag"],
        "undirected_cover_functorial": obs["undirected_functorial_map_exists_flag"],
        "endpoint_atom_key_available": int(obs["endpoint_atom_column_count"] > 0),
        "basis_stress_atom_bridge_available": obs["basis_stress_atom_bridge_flag"],
        "transition_stress_map_available": obs["transition_stress_map_certified_flag"],
        "semantic_transition_operation_available": obs[
            "semantic_transition_operation_flag"
        ],
        "current_boundary_lift_ready": current_boundary_lift_ready_flag,
        "current_boundary_obstruction_certified": obstruction_certified_flag,
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES[name],
            "decision_code": DECISION_CODES[name],
            "value": decision_values[name],
            "certified_flag": int(name in {
                "relation_level_cover_available",
                "current_boundary_obstruction_certified",
            }),
            "obstruction_flag": int(
                name not in {
                    "relation_level_cover_available",
                    "current_boundary_obstruction_certified",
                }
            ),
        }
        for name in DECISION_NAMES
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["relation_level_atom_basis_cover"],
            "gap_code": GAP_CODES["relation_level_atom_basis_cover"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["functorial_atom_basis_map"],
            "gap_code": GAP_CODES["functorial_atom_basis_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["endpoint_atom_schema_key"],
            "gap_code": GAP_CODES["endpoint_atom_schema_key"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["raw_endpoint_stress_atom_bridge"],
            "gap_code": GAP_CODES["raw_endpoint_stress_atom_bridge"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["transition_stress_coupling_map"],
            "gap_code": GAP_CODES["transition_stress_coupling_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_transition_operation"],
            "gap_code": GAP_CODES["semantic_transition_operation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["physical_selector_axiom"],
            "gap_code": GAP_CODES["physical_selector_axiom"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["four_dimensional_metric_reduction"],
            "gap_code": GAP_CODES["four_dimensional_metric_reduction"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59p3t": c59p3t,
        "abmap": abmap,
        "transition_sem": transition_sem,
        "contact_lift": contact_lift,
        "c59p3a": c59p3a,
        "c59p3t_join_rows": c59p3t_join_rows,
        "abmap_csp_rows": abmap_csp_rows,
        "surface_rows": surface_rows,
        "bridge_rows": bridge_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    surface_table = table_from_rows(SURFACE_COLUMNS, rows["surface_rows"])
    bridge_table = table_from_rows(BRIDGE_COLUMNS, rows["bridge_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "source_counts_match": obs["transition_row_count"] == 642
        and obs["contact_row_count"] == 642
        and obs["endpoint_row_count"] == 259
        and obs["stress_edge_row_count"] == 100
        and obs["atom_overlap_row_count"] == 14
        and obs["atom_basis_domain_row_count"] == 90
        and obs["atom_basis_match_row_count"] == 83,
        "relation_cover_is_not_functorial": obs["directed_edge_covered_count"] == 15
        and obs["directed_candidate_pair_count"] == 24
        and obs["directed_cover_complete_flag"] == 0
        and obs["directed_functorial_map_exists_flag"] == 0
        and obs["undirected_edge_covered_count"] == 20
        and obs["undirected_candidate_pair_count"] == 59
        and obs["undirected_max_pair_multiplicity"] == 6
        and obs["undirected_relation_cover_flag"] == 1
        and obs["undirected_functorial_map_exists_flag"] == 0
        and obs["atom_to_basis_function_certified_flag"] == 0,
        "endpoint_atom_key_absent": obs["contact_endpoint_bridge_flag"] == 1
        and obs["endpoint_atom_column_count"] == 0
        and obs["endpoint_overlap_shared_key_count"] == 0,
        "stress_lift_absent": obs["atom_transition_bridge_flag"] == 0
        and obs["basis_stress_atom_bridge_flag"] == 0
        and obs["raw_endpoint_stress_atom_bridge_flag"] == 0
        and obs["transition_stress_map_certified_flag"] == 0
        and obs["current_schema_consumes_atom_score_flag"] == 0,
        "physical_boundaries_preserved": obs["semantic_transition_operation_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["four_dimensional_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": surface_table.shape == (len(SURFACE_CODES), len(SURFACE_COLUMNS))
        and bridge_table.shape == (len(BRIDGE_CODES), len(BRIDGE_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "basis_to_stress_atom_bridge_obstruction",
        "summary": {
            "undirected_relation_cover_flag": obs["undirected_relation_cover_flag"],
            "undirected_candidate_pair_count": obs["undirected_candidate_pair_count"],
            "undirected_max_pair_multiplicity": obs[
                "undirected_max_pair_multiplicity"
            ],
            "atom_to_basis_function_certified_flag": obs[
                "atom_to_basis_function_certified_flag"
            ],
            "endpoint_atom_column_count": obs["endpoint_atom_column_count"],
            "endpoint_overlap_shared_key_count": obs[
                "endpoint_overlap_shared_key_count"
            ],
            "basis_stress_atom_bridge_flag": obs["basis_stress_atom_bridge_flag"],
            "raw_endpoint_stress_atom_bridge_flag": obs[
                "raw_endpoint_stress_atom_bridge_flag"
            ],
            "transition_stress_map_certified_flag": obs[
                "transition_stress_map_certified_flag"
            ],
            "current_schema_consumes_atom_score_flag": obs[
                "current_schema_consumes_atom_score_flag"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
        },
        "surface_code_map": {
            str(value): key for key, value in SURFACE_CODES.items()
        },
        "bridge_code_map": {str(value): key for key, value in BRIDGE_CODES.items()},
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "surface_table_sha256": sha_array(surface_table),
        "bridge_table_sha256": sha_array(bridge_table),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "bridge_text_sha256": sha_text(csv_text(BRIDGE_COLUMNS, rows["bridge_rows"])),
    }
    c59p3b = {
        "schema": "long.c59p3b@1",
        "object": "basis_to_stress_atom_bridge_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_C59P3B_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3b.report@1",
        "status": c59p3b["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3b composes the transition-stress lift gate with the "
            "atom-to-basis relation test. The current evidence has an "
            "undirected relation cover over all 20 ticks, but it has no "
            "single-valued atom-to-basis map, no endpoint atom key, and no "
            "raw-endpoint-to-stress-atom bridge. Therefore the atom-overlap "
            "orientation score still cannot be consumed by guarded transitions "
            "under the current artifact boundary."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3t, long_abmap, long_transition_sem, long_contact_lift, and long_c59p3a",
            "witness": "emit surface rows, bridge clauses, decisions, gaps, and observables",
            "coherence": "check relation-cover counts, functorial-map collapse, endpoint atom-key absence, and preserved physical exclusions",
            "closure": "certify the current-boundary obstruction to a basis/raw-endpoint-to-stress-atom bridge",
            "emit": "write long_c59p3b artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3t": input_entry(
                LONG_C59P3T,
                {
                    "status": rows["c59p3t"].get("status"),
                    "certificate_sha256": rows["c59p3t"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3t_join": input_entry(LONG_C59P3T_JOIN),
            "long_c59p3t_obs": input_entry(LONG_C59P3T_OBS),
            "long_abmap": input_entry(
                LONG_ABMAP,
                {
                    "status": rows["abmap"].get("status"),
                    "certificate_sha256": rows["abmap"].get("certificate_sha256"),
                },
            ),
            "long_abmap_csp": input_entry(LONG_ABMAP_CSP),
            "long_abmap_match": input_entry(LONG_ABMAP_MATCH),
            "long_abmap_obs": input_entry(LONG_ABMAP_OBS),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_contact_lift": input_entry(
                LONG_CONTACT_LIFT,
                {
                    "status": rows["contact_lift"].get("status"),
                    "certificate_sha256": rows["contact_lift"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3a": input_entry(
                LONG_C59P3A,
                {
                    "status": rows["c59p3a"].get("status"),
                    "certificate_sha256": rows["c59p3a"].get(
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
            "c59p3b": relpath(OUT_DIR / "c59p3b.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
            "bridge_csv": relpath(OUT_DIR / "bridge.csv"),
            "decision_csv": relpath(OUT_DIR / "decision.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "the strongest current atom-to-basis evidence is relation-level rather than functorial",
                "the undirected relation covers all 20 ticks but is nonunique with maximum multiplicity 6",
                "the raw endpoint surface has no certified atom key into the atom-overlap score",
                "the current boundary has no basis/raw-endpoint-to-stress-atom bridge",
                "the atom-overlap orientation score remains unavailable to guarded transitions",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a new Loop-step-to-endpoint-basis identification outside the tested identity candidate",
                "a relation-valued stress-transition law that explicitly accepts multivalued tick witnesses",
                "semantic transition-operation realization",
                "a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Test whether the existing relation-valued tick semantics can be "
            "extended to stress scoring, since the single-valued atom/basis "
            "route is obstructed under the current boundary."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3b.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3b.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3b": c59p3b,
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": surface_table,
        "bridge_table": bridge_table,
        "decision_table": decision_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
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
    write_json(OUT_DIR / "c59p3b.json", payloads["c59p3b"])
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
        bridge_table=payloads["bridge_table"],
        decision_table=payloads["decision_table"],
        gap_table=payloads["gap_table"],
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
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
