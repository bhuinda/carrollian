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


THEOREM_ID = "long_metric_gate"
STATUS = "LONG_METRIC_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_GR = PROOF_ROOT / "long_gr" / "report.json"
LONG_LOR = PROOF_ROOT / "long_lor" / "report.json"
LONG_TIME_MAP = PROOF_ROOT / "long_time_map" / "report.json"
LONG_TIME_SEM = PROOF_ROOT / "long_time_sem" / "report.json"
ATLAS = PROOF_ROOT / "c985_d20_boundary_invariant_atlas" / "report.json"
HYPERBOLIC = PROOF_ROOT / "c985_d20_hyperbolic_boundary_graph" / "report.json"
POINCARE = PROOF_ROOT / "c985_d20_poincare_embedding" / "report.json"
STRESS = PROOF_ROOT / "c985_d20_boundary_neighborhood_stress_graph" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_metric_gate.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_metric_gate.py"

SURFACE_COLUMNS = [
    "surface_id",
    "role_code",
    "certified_flag",
    "formal_metric_input_flag",
    "semantic_metric_input_flag",
    "obstruction_flag",
    "guard_required_flag",
    "gr_claim_flag",
]
DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "value",
    "expected_value",
    "pass_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "obligation_code",
    "required_for_gr_flag",
    "certified_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SURFACE_NAMES = [
    "a985_gr_pathway",
    "lorentzian_time_quotient",
    "normal_form_time_map",
    "semantic_edge_obstruction",
    "d20_boundary_atlas",
    "hyperbolic_boundary_graph",
    "poincare_disk_chart",
    "stress_neighborhood_graph",
]
SURFACE_CODES = {name: index for index, name in enumerate(SURFACE_NAMES)}

ROLE_NAMES = [
    "gr_pathway_boundary",
    "time_scaffold",
    "normal_form_clock",
    "semantic_guard",
    "boundary_geometry",
    "finite_metric_readout",
    "finite_chart_readout",
    "finite_stress_readout",
]
ROLE_CODES = {name: index for index, name in enumerate(ROLE_NAMES)}

DECISION_NAMES = [
    "input_report_count",
    "input_certified_count",
    "formal_metric_surface_count",
    "semantic_metric_surface_count",
    "obstruction_surface_count",
    "recurrence_edge_count",
    "normal_form_tick_total",
    "semantic_edge_operation_flag",
    "semantic_obstruction_flag",
    "boundary_atom_count",
    "hyperbolic_johnson_edge_count",
    "poincare_atom_count",
    "stress_graph_node_count",
    "guarded_finite_metric_gate_flag",
    "a985_semantic_metric_gate_flag",
    "contact_lift_required_flag",
    "smooth_lorentzian_metric_flag",
    "gr_derivation_flag",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}

GAP_NAMES = [
    "semantic_edge_operation_realization_from_a985",
    "owner_boundary_contact_lift",
    "physical_stress_energy_tensor",
    "nondegenerate_smooth_lorentzian_metric",
    "four_dimensional_spacetime_reduction",
    "curvature_and_einstein_tensor",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "surface_count",
    "formal_metric_surface_count",
    "semantic_metric_surface_count",
    "obstruction_surface_count",
    "guard_required_surface_count",
    "recurrence_edge_count",
    "normal_form_tick_total",
    "semantic_edge_operation_flag",
    "semantic_obstruction_flag",
    "boundary_atom_count",
    "hyperbolic_johnson_edge_count",
    "poincare_atom_count",
    "stress_graph_node_count",
    "guarded_finite_metric_gate_flag",
    "a985_semantic_metric_gate_flag",
    "contact_lift_required_flag",
    "smooth_lorentzian_metric_flag",
    "physical_stress_energy_flag",
    "gr_derivation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

EXPECTED_STATUSES = {
    "long_gr": "LONG_GR_PATHWAY_CERTIFIED",
    "long_lor": "LONG_LOR_CERTIFIED",
    "long_time_map": "LONG_TIME_MAP_CERTIFIED",
    "long_time_sem": "LONG_TIME_SEM_OBSTRUCTION_CERTIFIED",
    "atlas": "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
    "hyperbolic": "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_CERTIFIED",
    "poincare": "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
    "stress": "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED",
}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require_dict(payload: Any, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AssertionError(f"{label} is not a JSON object")
    return payload


def _status_ok(report: dict[str, Any], expected_status: str) -> int:
    return int(report.get("status") == expected_status and report.get("all_checks_pass") is True)


def _stress_graph_node_count(stress: dict[str, Any]) -> int:
    witness = _require_dict(stress.get("witness"), "stress.witness")
    rows = witness.get("graph_rows")
    if not isinstance(rows, list):
        raise AssertionError("stress graph_rows missing")
    return len(rows)


def _stress_neighbor_count(stress: dict[str, Any]) -> int:
    witness = _require_dict(stress.get("witness"), "stress.witness")
    rows = witness.get("graph_rows")
    if not isinstance(rows, list):
        raise AssertionError("stress graph_rows missing")
    return sum(len(row.get("neighbors", [])) for row in rows if isinstance(row, dict))


def build_rows() -> dict[str, Any]:
    long_gr = load_json(LONG_GR)
    long_lor = load_json(LONG_LOR)
    long_time_map = load_json(LONG_TIME_MAP)
    long_time_sem = load_json(LONG_TIME_SEM)
    atlas = load_json(ATLAS)
    hyperbolic = load_json(HYPERBOLIC)
    poincare = load_json(POINCARE)
    stress = load_json(STRESS)

    reports = {
        "long_gr": long_gr,
        "long_lor": long_lor,
        "long_time_map": long_time_map,
        "long_time_sem": long_time_sem,
        "atlas": atlas,
        "hyperbolic": hyperbolic,
        "poincare": poincare,
        "stress": stress,
    }
    input_ok = {
        name: _status_ok(report, EXPECTED_STATUSES[name])
        for name, report in reports.items()
    }

    time_map_summary = _require_dict(
        _require_dict(long_time_map.get("witness"), "long_time_map.witness").get(
            "summary"
        ),
        "long_time_map.summary",
    )
    time_sem_summary = _require_dict(
        _require_dict(long_time_sem.get("witness"), "long_time_sem.witness").get(
            "summary"
        ),
        "long_time_sem.summary",
    )
    hyperbolic_witness = _require_dict(hyperbolic.get("witness"), "hyperbolic.witness")
    poincare_witness = _require_dict(poincare.get("witness"), "poincare.witness")
    stress_checks = _require_dict(stress.get("checks"), "stress.checks")

    recurrence_edge_count = int(time_map_summary["recurrence_edge_count"])
    normal_form_tick_total = int(time_map_summary["time_tick_total"])
    semantic_edge_operation_flag = int(time_sem_summary["semantic_edge_operation_flag"])
    semantic_obstruction_flag = int(time_sem_summary["obstruction_certified_flag"])
    boundary_atom_count = int(hyperbolic_witness["atom_count"])
    hyperbolic_johnson_edge_count = int(hyperbolic_witness["johnson_edge_count"])
    poincare_atom_count = int(poincare_witness["atom_count"])
    stress_graph_node_count = _stress_graph_node_count(stress)

    surface_rows = [
        {
            "surface_id": SURFACE_CODES["a985_gr_pathway"],
            "role_code": ROLE_CODES["gr_pathway_boundary"],
            "certified_flag": input_ok["long_gr"],
            "formal_metric_input_flag": 0,
            "semantic_metric_input_flag": 0,
            "obstruction_flag": 0,
            "guard_required_flag": 1,
            "gr_claim_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["lorentzian_time_quotient"],
            "role_code": ROLE_CODES["time_scaffold"],
            "certified_flag": input_ok["long_lor"],
            "formal_metric_input_flag": 1,
            "semantic_metric_input_flag": 0,
            "obstruction_flag": 0,
            "guard_required_flag": 1,
            "gr_claim_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["normal_form_time_map"],
            "role_code": ROLE_CODES["normal_form_clock"],
            "certified_flag": input_ok["long_time_map"],
            "formal_metric_input_flag": 1,
            "semantic_metric_input_flag": 0,
            "obstruction_flag": 0,
            "guard_required_flag": 1,
            "gr_claim_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["semantic_edge_obstruction"],
            "role_code": ROLE_CODES["semantic_guard"],
            "certified_flag": input_ok["long_time_sem"],
            "formal_metric_input_flag": 0,
            "semantic_metric_input_flag": 0,
            "obstruction_flag": 1,
            "guard_required_flag": 1,
            "gr_claim_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["d20_boundary_atlas"],
            "role_code": ROLE_CODES["boundary_geometry"],
            "certified_flag": input_ok["atlas"],
            "formal_metric_input_flag": 1,
            "semantic_metric_input_flag": 0,
            "obstruction_flag": 0,
            "guard_required_flag": 0,
            "gr_claim_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["hyperbolic_boundary_graph"],
            "role_code": ROLE_CODES["finite_metric_readout"],
            "certified_flag": input_ok["hyperbolic"],
            "formal_metric_input_flag": 1,
            "semantic_metric_input_flag": 0,
            "obstruction_flag": 0,
            "guard_required_flag": 0,
            "gr_claim_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["poincare_disk_chart"],
            "role_code": ROLE_CODES["finite_chart_readout"],
            "certified_flag": input_ok["poincare"],
            "formal_metric_input_flag": 1,
            "semantic_metric_input_flag": 0,
            "obstruction_flag": 0,
            "guard_required_flag": 0,
            "gr_claim_flag": 0,
        },
        {
            "surface_id": SURFACE_CODES["stress_neighborhood_graph"],
            "role_code": ROLE_CODES["finite_stress_readout"],
            "certified_flag": input_ok["stress"],
            "formal_metric_input_flag": 1,
            "semantic_metric_input_flag": 0,
            "obstruction_flag": 0,
            "guard_required_flag": 1,
            "gr_claim_flag": 0,
        },
    ]

    guarded_finite_metric_gate_flag = int(
        sum(input_ok.values()) == len(input_ok)
        and semantic_obstruction_flag == 1
        and semantic_edge_operation_flag == 0
        and recurrence_edge_count == 642
        and normal_form_tick_total == 642
        and boundary_atom_count == 20
        and hyperbolic_johnson_edge_count == 90
        and poincare_atom_count == 20
        and stress_graph_node_count == 20
    )
    a985_semantic_metric_gate_flag = 0
    contact_lift_required_flag = 1
    smooth_lorentzian_metric_flag = 0
    physical_stress_energy_flag = 0
    gr_derivation_flag = 0

    decision_expectations = [
        ("input_report_count", len(input_ok), 8),
        ("input_certified_count", sum(input_ok.values()), 8),
        (
            "formal_metric_surface_count",
            sum(row["formal_metric_input_flag"] for row in surface_rows),
            6,
        ),
        (
            "semantic_metric_surface_count",
            sum(row["semantic_metric_input_flag"] for row in surface_rows),
            0,
        ),
        (
            "obstruction_surface_count",
            sum(row["obstruction_flag"] for row in surface_rows),
            1,
        ),
        ("recurrence_edge_count", recurrence_edge_count, 642),
        ("normal_form_tick_total", normal_form_tick_total, 642),
        ("semantic_edge_operation_flag", semantic_edge_operation_flag, 0),
        ("semantic_obstruction_flag", semantic_obstruction_flag, 1),
        ("boundary_atom_count", boundary_atom_count, 20),
        ("hyperbolic_johnson_edge_count", hyperbolic_johnson_edge_count, 90),
        ("poincare_atom_count", poincare_atom_count, 20),
        ("stress_graph_node_count", stress_graph_node_count, 20),
        ("guarded_finite_metric_gate_flag", guarded_finite_metric_gate_flag, 1),
        ("a985_semantic_metric_gate_flag", a985_semantic_metric_gate_flag, 0),
        ("contact_lift_required_flag", contact_lift_required_flag, 1),
        ("smooth_lorentzian_metric_flag", smooth_lorentzian_metric_flag, 0),
        ("gr_derivation_flag", gr_derivation_flag, 0),
    ]
    decision_rows = [
        {
            "decision_id": index,
            "decision_code": DECISION_CODES[name],
            "value": int(value),
            "expected_value": int(expected),
            "pass_flag": int(value == expected),
        }
        for index, (name, value, expected) in enumerate(decision_expectations)
    ]

    gap_rows = [
        {
            "gap_id": 0,
            "obligation_code": GAP_CODES["semantic_edge_operation_realization_from_a985"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": 1,
            "obligation_code": GAP_CODES["owner_boundary_contact_lift"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": 2,
            "obligation_code": GAP_CODES["physical_stress_energy_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 3,
            "obligation_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 4,
            "obligation_code": GAP_CODES["four_dimensional_spacetime_reduction"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 5,
            "obligation_code": GAP_CODES["curvature_and_einstein_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
    ]

    obs = {
        "input_report_count": len(input_ok),
        "input_certified_count": sum(input_ok.values()),
        "surface_count": len(surface_rows),
        "formal_metric_surface_count": sum(
            row["formal_metric_input_flag"] for row in surface_rows
        ),
        "semantic_metric_surface_count": sum(
            row["semantic_metric_input_flag"] for row in surface_rows
        ),
        "obstruction_surface_count": sum(row["obstruction_flag"] for row in surface_rows),
        "guard_required_surface_count": sum(
            row["guard_required_flag"] for row in surface_rows
        ),
        "recurrence_edge_count": recurrence_edge_count,
        "normal_form_tick_total": normal_form_tick_total,
        "semantic_edge_operation_flag": semantic_edge_operation_flag,
        "semantic_obstruction_flag": semantic_obstruction_flag,
        "boundary_atom_count": boundary_atom_count,
        "hyperbolic_johnson_edge_count": hyperbolic_johnson_edge_count,
        "poincare_atom_count": poincare_atom_count,
        "stress_graph_node_count": stress_graph_node_count,
        "guarded_finite_metric_gate_flag": guarded_finite_metric_gate_flag,
        "a985_semantic_metric_gate_flag": a985_semantic_metric_gate_flag,
        "contact_lift_required_flag": contact_lift_required_flag,
        "smooth_lorentzian_metric_flag": smooth_lorentzian_metric_flag,
        "physical_stress_energy_flag": physical_stress_energy_flag,
        "gr_derivation_flag": gr_derivation_flag,
        "open_gap_count": sum(1 - row["certified_flag"] for row in gap_rows),
        "next_gap_code": GAP_CODES["owner_boundary_contact_lift"],
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
        "reports": reports,
        "input_ok": input_ok,
        "time_map_summary": time_map_summary,
        "time_sem_summary": time_sem_summary,
        "hyperbolic_witness": hyperbolic_witness,
        "poincare_witness": poincare_witness,
        "stress_checks": stress_checks,
        "stress_neighbor_count": _stress_neighbor_count(stress),
        "surface_rows": surface_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "surface_table": table_from_rows(SURFACE_COLUMNS, surface_rows),
        "decision_table": table_from_rows(DECISION_COLUMNS, decision_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "surface_text_hash": sha_text(digest_text(SURFACE_COLUMNS, surface_rows)),
        "decision_text_hash": sha_text(digest_text(DECISION_COLUMNS, decision_rows)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    reports = rows["reports"]
    obs = rows["obs"]
    checks = {
        "all_input_reports_certified": obs["input_report_count"] == 8
        and obs["input_certified_count"] == 8,
        "time_chain_guard_preserved": obs["recurrence_edge_count"] == 642
        and obs["normal_form_tick_total"] == 642
        and obs["semantic_edge_operation_flag"] == 0
        and rows["time_sem_summary"].get("obstruction_certified_flag") == 1,
        "finite_metric_readouts_certified": obs["boundary_atom_count"] == 20
        and obs["hyperbolic_johnson_edge_count"] == 90
        and obs["poincare_atom_count"] == 20
        and obs["stress_graph_node_count"] == 20
        and rows["stress_neighbor_count"] == 100
        and rows["stress_checks"].get("all_nodes_have_five_neighbors") is True,
        "guarded_gate_decision_exact": obs["guarded_finite_metric_gate_flag"] == 1
        and obs["a985_semantic_metric_gate_flag"] == 0
        and obs["contact_lift_required_flag"] == 1
        and obs["smooth_lorentzian_metric_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "no_surface_claims_gr": all(row["gr_claim_flag"] == 0 for row in rows["surface_rows"]),
        "decision_rows_pass": all(row["pass_flag"] == 1 for row in rows["decision_rows"]),
        "table_shapes_match": rows["surface_table"].shape
        == (len(SURFACE_NAMES), len(SURFACE_COLUMNS))
        and rows["decision_table"].shape
        == (len(DECISION_NAMES), len(DECISION_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_NAMES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_NAMES), len(OBS_COLUMNS)),
    }

    witness = {
        "name": THEOREM_ID,
        "classification": "guarded_finite_metric_pathway_gate",
        "surface_code_map": {str(value): key for key, value in SURFACE_CODES.items()},
        "role_code_map": {str(value): key for key, value in ROLE_CODES.items()},
        "decision_code_map": {str(value): key for key, value in DECISION_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "summary": {
            "input_report_count": obs["input_report_count"],
            "input_certified_count": obs["input_certified_count"],
            "formal_metric_surface_count": obs["formal_metric_surface_count"],
            "semantic_metric_surface_count": obs["semantic_metric_surface_count"],
            "recurrence_edge_count": obs["recurrence_edge_count"],
            "normal_form_tick_total": obs["normal_form_tick_total"],
            "boundary_atom_count": obs["boundary_atom_count"],
            "hyperbolic_johnson_edge_count": obs["hyperbolic_johnson_edge_count"],
            "poincare_atom_count": obs["poincare_atom_count"],
            "stress_graph_node_count": obs["stress_graph_node_count"],
            "guarded_finite_metric_gate_flag": obs[
                "guarded_finite_metric_gate_flag"
            ],
            "a985_semantic_metric_gate_flag": obs[
                "a985_semantic_metric_gate_flag"
            ],
            "contact_lift_required_flag": obs["contact_lift_required_flag"],
            "smooth_lorentzian_metric_flag": obs["smooth_lorentzian_metric_flag"],
            "gr_derivation_flag": obs["gr_derivation_flag"],
            "next_gap": "owner_boundary_contact_lift",
        },
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "surface_text_sha256": rows["surface_text_hash"],
        "decision_table_sha256": sha_array(rows["decision_table"]),
        "decision_text_sha256": rows["decision_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    metric_gate = {
        "schema": "long.metric_gate@1",
        "object": "guarded_finite_metric_pathway_gate",
        "status": STATUS if all(checks.values()) else "LONG_METRIC_GATE_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.metric_gate.report@1",
        "status": metric_gate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_metric_gate unites the certified finite time chain with the "
            "certified finite d20 metric readouts under an explicit guard. The "
            "normal-form time map, Lorentzian quotient scaffold, boundary atlas, "
            "hyperbolic graph, Poincare chart, and stress-neighborhood graph may "
            "be used together as a guarded finite metric pathway. The semantic "
            "edge-operation obstruction from long_time_sem remains active, so "
            "this gate forbids treating the normal-form ticks as A985-alone "
            "semantic transition operations and does not certify a smooth "
            "Lorentzian metric or GR."
        ),
        "stage_protocol": {
            "draft": "read long_gr, long_lor, long_time_map, long_time_sem, atlas, hyperbolic, Poincare, and stress reports",
            "witness": "emit metric-surface rows, gate-decision rows, and open metric/GR gap rows",
            "coherence": "check input statuses, time obstruction guard, finite metric counts, stress-neighborhood shape, and table hashes",
            "closure": "certify a guarded finite metric pathway gate without claiming A985 semantic metric closure or GR",
            "emit": "write long_metric_gate artifacts and verifier hook",
        },
        "inputs": {
            "long_gr": input_entry(
                LONG_GR,
                {
                    "status": reports["long_gr"].get("status"),
                    "certificate_sha256": reports["long_gr"].get("certificate_sha256"),
                },
            ),
            "long_lor": input_entry(
                LONG_LOR,
                {
                    "status": reports["long_lor"].get("status"),
                    "certificate_sha256": reports["long_lor"].get("certificate_sha256"),
                },
            ),
            "long_time_map": input_entry(
                LONG_TIME_MAP,
                {
                    "status": reports["long_time_map"].get("status"),
                    "certificate_sha256": reports["long_time_map"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_time_sem": input_entry(
                LONG_TIME_SEM,
                {
                    "status": reports["long_time_sem"].get("status"),
                    "certificate_sha256": reports["long_time_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "atlas": input_entry(
                ATLAS,
                {
                    "status": reports["atlas"].get("status"),
                    "certificate_sha256": reports["atlas"].get("certificate_sha256"),
                },
            ),
            "hyperbolic": input_entry(
                HYPERBOLIC,
                {
                    "status": reports["hyperbolic"].get("status"),
                    "certificate_sha256": reports["hyperbolic"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "poincare": input_entry(
                POINCARE,
                {
                    "status": reports["poincare"].get("status"),
                    "certificate_sha256": reports["poincare"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "stress": input_entry(
                STRESS,
                {
                    "status": reports["stress"].get("status"),
                    "certificate_sha256": reports["stress"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "metric_gate": relpath(OUT_DIR / "metric_gate.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
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
                "the finite time quotient and normal-form clock can be combined with finite boundary metric readouts only under the long_time_sem guard",
                "the certified d20 boundary atlas, hyperbolic graph, Poincare chart, and stress graph form a guarded finite metric pathway surface",
                "normal-form ticks are not accepted as A985 semantic transition operations",
                "semantic edge-operation realization remains obstructed in the current artifact boundary",
                "an owner-boundary contact lift is the next required semantic bridge before an A985-alone metric certificate",
            ],
            "does_not_certify_because_guarded_or_open": [
                "a semantic A985 operation for each recurrence edge",
                "a physical stress-energy tensor",
                "a nondegenerate smooth Lorentzian metric tensor",
                "a 3+1 spacetime reduction from the 1+19 public split",
                "Riemann/Ricci curvature, Einstein tensor, or Einstein field equations",
            ],
        },
        "next_highest_yield_item": (
            "Build long_contact_lift: materialize owner-boundary contact rows "
            "for each recurrence edge, relating the graph adjacency event to "
            "explicit A985-backed endpoint/contact data before any stronger "
            "semantic metric claim."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.metric_gate.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.metric_gate.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "metric_gate": metric_gate,
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "decision_table": rows["decision_table"],
        "gap_table": rows["gap_table"],
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
    write_json(OUT_DIR / "metric_gate.json", payloads["metric_gate"])
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(payloads["decision_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
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
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
