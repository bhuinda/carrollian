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


THEOREM_ID = "long_c59p3s"
STATUS = "LONG_C59P3S_NONPRINCIPAL_PLANE_SELECTOR_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59NP3 = PROOF_ROOT / "long_c59np3" / "report.json"
LONG_TIME_MAP = PROOF_ROOT / "long_time_map" / "report.json"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_STRESS_COUPLE = PROOF_ROOT / "long_stress_couple" / "report.json"
LONG_SEL = PROOF_ROOT / "long_sel" / "report.json"
LONG_DIM4_GATE = PROOF_ROOT / "long_dim4_gate" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3s.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3s.py"

CANDIDATE_COLUMNS = [
    "candidate_id",
    "plane_code",
    "candidate_a",
    "candidate_b",
    "candidate_c",
    "inertia_positive",
    "inertia_negative",
    "formal_candidate_flag",
    "normal_form_time_flag",
    "guarded_transition_flag",
    "semantic_transition_operation_flag",
    "stress_coupling_map_flag",
    "physical_selector_axiom_flag",
    "selected_physical_flag",
]
CONTRACT_COLUMNS = [
    "clause_id",
    "clause_code",
    "pass_flag",
    "fail_flag",
    "first_failure_flag",
    "downstream_blocked_flag",
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

PLANE_NAMES = ["positive_definite_plane", "negative_definite_plane"]
PLANE_CODES = {name: index for index, name in enumerate(PLANE_NAMES)}
CLAUSE_NAMES = [
    "nonprincipal_definite_plane_domain_present",
    "normal_form_time_trace_present",
    "guarded_transition_surface_present",
    "physical_selector_axiom_present",
    "semantic_transition_operation_present",
    "stress_transition_coupling_map_present",
    "four_dimensional_metric_reduction_present",
    "physical_source_tensor_ready",
]
CLAUSE_CODES = {name: index for index, name in enumerate(CLAUSE_NAMES)}
DECISION_NAMES = [
    "algebraic_plane_domain_certified",
    "normal_form_time_coherence_certified",
    "guarded_transition_coherence_certified",
    "physical_selector_axiom_available",
    "semantic_transition_operation_available",
    "stress_coupling_map_available",
    "canonical_physical_plane_selected",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}
GAP_NAMES = [
    "nonprincipal_plane_witnesses",
    "physical_selector_axiom",
    "semantic_transition_operation",
    "stress_coupling_map",
    "four_dimensional_metric_reduction",
    "physical_source_tensor",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "candidate_count",
    "selected_candidate_count",
    "formal_plane_selector_candidate_count",
    "nonprincipal_definite_plane_count",
    "positive_plane_candidate_a",
    "positive_plane_candidate_b",
    "positive_plane_candidate_c",
    "negative_plane_candidate_a",
    "negative_plane_candidate_b",
    "negative_plane_candidate_c",
    "normal_form_time_map_flag",
    "semantic_edge_operation_flag",
    "finite_guard_transition_flag",
    "semantic_transition_operation_flag",
    "stress_coupling_map_certified_flag",
    "shared_stress_coupling_key_count",
    "physical_selector_axiom_flag",
    "dim4_reduction_certified_flag",
    "physical_stress_energy_flag",
    "contract_clause_count",
    "contract_pass_count",
    "contract_fail_count",
    "first_failure_clause_code",
    "downstream_blocked_clause_count",
    "canonical_physical_selection_flag",
    "four_dimensional_metric_flag",
    "thermal_gravity_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def build_rows() -> dict[str, Any]:
    c59np3 = load_json(LONG_C59NP3)
    time_map = load_json(LONG_TIME_MAP)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    stress_couple = load_json(LONG_STRESS_COUPLE)
    long_sel = load_json(LONG_SEL)
    dim4_gate = load_json(LONG_DIM4_GATE)

    c59np3_summary = summary(c59np3)
    time_summary = summary(time_map)
    transition_summary = summary(transition_sem)
    stress_summary = summary(stress_couple)
    selector_summary = summary(long_sel)
    dim4_summary = dim4_gate["witness"]["summary"]

    positive_triple = c59np3_summary["positive_plane_candidate_triple"]
    negative_triple = c59np3_summary["negative_plane_candidate_triple"]
    normal_time_flag = int(time_summary["normal_form_time_map_flag"])
    semantic_edge_flag = int(time_summary["semantic_edge_operation_flag"])
    guarded_transition_flag = int(transition_summary["finite_guard_transition_flag"])
    semantic_transition_flag = int(
        transition_summary["semantic_transition_operation_flag"]
    )
    stress_coupling_flag = int(stress_summary["coupling_map_certified_flag"])
    shared_coupling_key_count = int(stress_summary["shared_certified_coupling_key_count"])
    physical_selector_flag = int(selector_summary["physical_selector_axiom_flag"])
    dim4_flag = int(dim4_summary["dim4_reduction_certified_flag"])
    physical_stress_flag = int(stress_summary["physical_stress_energy_flag"])

    candidate_specs = [
        (0, PLANE_CODES["positive_definite_plane"], positive_triple, 3, 0),
        (1, PLANE_CODES["negative_definite_plane"], negative_triple, 0, 3),
    ]
    candidate_rows = [
        {
            "candidate_id": candidate_id,
            "plane_code": plane_code,
            "candidate_a": triple[0],
            "candidate_b": triple[1],
            "candidate_c": triple[2],
            "inertia_positive": inertia_positive,
            "inertia_negative": inertia_negative,
            "formal_candidate_flag": 1,
            "normal_form_time_flag": normal_time_flag,
            "guarded_transition_flag": guarded_transition_flag,
            "semantic_transition_operation_flag": semantic_transition_flag,
            "stress_coupling_map_flag": stress_coupling_flag,
            "physical_selector_axiom_flag": physical_selector_flag,
            "selected_physical_flag": 0,
        }
        for candidate_id, plane_code, triple, inertia_positive, inertia_negative in candidate_specs
    ]
    clause_values = {
        "nonprincipal_definite_plane_domain_present": int(
            c59np3_summary["nonprincipal_definite_plane_count"] == 2
        ),
        "normal_form_time_trace_present": normal_time_flag,
        "guarded_transition_surface_present": guarded_transition_flag,
        "physical_selector_axiom_present": physical_selector_flag,
        "semantic_transition_operation_present": semantic_transition_flag,
        "stress_transition_coupling_map_present": stress_coupling_flag,
        "four_dimensional_metric_reduction_present": dim4_flag,
        "physical_source_tensor_ready": physical_stress_flag,
    }
    first_failure_code = next(
        CLAUSE_CODES[name] for name in CLAUSE_NAMES if clause_values[name] == 0
    )
    contract_rows = []
    for name in CLAUSE_NAMES:
        clause_code = CLAUSE_CODES[name]
        pass_flag = clause_values[name]
        contract_rows.append(
            {
                "clause_id": clause_code,
                "clause_code": clause_code,
                "pass_flag": pass_flag,
                "fail_flag": int(pass_flag == 0),
                "first_failure_flag": int(clause_code == first_failure_code),
                "downstream_blocked_flag": int(
                    pass_flag == 0 and clause_code > first_failure_code
                ),
            }
        )

    obs = {
        "input_report_count": 6,
        "input_certified_count": int(certified(c59np3))
        + int(certified(time_map))
        + int(certified(transition_sem))
        + int(certified(stress_couple))
        + int(certified(long_sel))
        + int(certified(dim4_gate)),
        "candidate_count": len(candidate_rows),
        "selected_candidate_count": sum(
            row["selected_physical_flag"] for row in candidate_rows
        ),
        "formal_plane_selector_candidate_count": sum(
            row["formal_candidate_flag"] for row in candidate_rows
        ),
        "nonprincipal_definite_plane_count": int(
            c59np3_summary["nonprincipal_definite_plane_count"]
        ),
        "positive_plane_candidate_a": positive_triple[0],
        "positive_plane_candidate_b": positive_triple[1],
        "positive_plane_candidate_c": positive_triple[2],
        "negative_plane_candidate_a": negative_triple[0],
        "negative_plane_candidate_b": negative_triple[1],
        "negative_plane_candidate_c": negative_triple[2],
        "normal_form_time_map_flag": normal_time_flag,
        "semantic_edge_operation_flag": semantic_edge_flag,
        "finite_guard_transition_flag": guarded_transition_flag,
        "semantic_transition_operation_flag": semantic_transition_flag,
        "stress_coupling_map_certified_flag": stress_coupling_flag,
        "shared_stress_coupling_key_count": shared_coupling_key_count,
        "physical_selector_axiom_flag": physical_selector_flag,
        "dim4_reduction_certified_flag": dim4_flag,
        "physical_stress_energy_flag": physical_stress_flag,
        "contract_clause_count": len(contract_rows),
        "contract_pass_count": sum(row["pass_flag"] for row in contract_rows),
        "contract_fail_count": sum(row["fail_flag"] for row in contract_rows),
        "first_failure_clause_code": first_failure_code,
        "downstream_blocked_clause_count": sum(
            row["downstream_blocked_flag"] for row in contract_rows
        ),
        "canonical_physical_selection_flag": 0,
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["physical_selector_axiom"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES["algebraic_plane_domain_certified"],
            "decision_code": DECISION_CODES["algebraic_plane_domain_certified"],
            "value": obs["nonprincipal_definite_plane_count"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["normal_form_time_coherence_certified"],
            "decision_code": DECISION_CODES["normal_form_time_coherence_certified"],
            "value": normal_time_flag,
            "certified_flag": normal_time_flag,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES[
                "guarded_transition_coherence_certified"
            ],
            "decision_code": DECISION_CODES[
                "guarded_transition_coherence_certified"
            ],
            "value": guarded_transition_flag,
            "certified_flag": guarded_transition_flag,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["physical_selector_axiom_available"],
            "decision_code": DECISION_CODES["physical_selector_axiom_available"],
            "value": physical_selector_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES[
                "semantic_transition_operation_available"
            ],
            "decision_code": DECISION_CODES[
                "semantic_transition_operation_available"
            ],
            "value": semantic_transition_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["stress_coupling_map_available"],
            "decision_code": DECISION_CODES["stress_coupling_map_available"],
            "value": stress_coupling_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["canonical_physical_plane_selected"],
            "decision_code": DECISION_CODES["canonical_physical_plane_selected"],
            "value": obs["canonical_physical_selection_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["nonprincipal_plane_witnesses"],
            "gap_code": GAP_CODES["nonprincipal_plane_witnesses"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["physical_selector_axiom"],
            "gap_code": GAP_CODES["physical_selector_axiom"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
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
            "gap_id": GAP_CODES["stress_coupling_map"],
            "gap_code": GAP_CODES["stress_coupling_map"],
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
            "gap_id": GAP_CODES["physical_source_tensor"],
            "gap_code": GAP_CODES["physical_source_tensor"],
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
        "c59np3": c59np3,
        "time_map": time_map,
        "transition_sem": transition_sem,
        "stress_couple": stress_couple,
        "long_sel": long_sel,
        "dim4_gate": dim4_gate,
        "candidate_rows": candidate_rows,
        "contract_rows": contract_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    contract_table = table_from_rows(CONTRACT_COLUMNS, rows["contract_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "formal_candidate_domain_present": obs["candidate_count"] == 2
        and obs["formal_plane_selector_candidate_count"] == 2
        and obs["nonprincipal_definite_plane_count"] == 2,
        "time_and_guarded_transition_prefix_passes": obs["normal_form_time_map_flag"]
        == 1
        and obs["finite_guard_transition_flag"] == 1
        and obs["contract_pass_count"] == 3,
        "first_failure_is_physical_selector_axiom": obs[
            "first_failure_clause_code"
        ]
        == CLAUSE_CODES["physical_selector_axiom_present"]
        and obs["physical_selector_axiom_flag"] == 0,
        "downstream_failures_preserved": obs["semantic_edge_operation_flag"] == 0
        and obs["semantic_transition_operation_flag"] == 0
        and obs["stress_coupling_map_certified_flag"] == 0
        and obs["shared_stress_coupling_key_count"] == 0
        and obs["dim4_reduction_certified_flag"] == 0
        and obs["physical_stress_energy_flag"] == 0
        and obs["downstream_blocked_clause_count"] == 4,
        "no_physical_selection_or_metric_promotion": obs[
            "selected_candidate_count"
        ]
        == 0
        and obs["canonical_physical_selection_flag"] == 0
        and obs["four_dimensional_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": candidate_table.shape == (2, len(CANDIDATE_COLUMNS))
        and contract_table.shape == (len(CLAUSE_CODES), len(CONTRACT_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "nonprincipal_three_plane_selector_gate",
        "summary": {
            "candidate_count": obs["candidate_count"],
            "formal_plane_selector_candidate_count": obs[
                "formal_plane_selector_candidate_count"
            ],
            "nonprincipal_definite_plane_count": obs[
                "nonprincipal_definite_plane_count"
            ],
            "normal_form_time_map_flag": obs["normal_form_time_map_flag"],
            "finite_guard_transition_flag": obs["finite_guard_transition_flag"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "stress_coupling_map_certified_flag": obs[
                "stress_coupling_map_certified_flag"
            ],
            "first_failure_clause_code": obs["first_failure_clause_code"],
            "downstream_blocked_clause_count": obs[
                "downstream_blocked_clause_count"
            ],
            "selected_candidate_count": obs["selected_candidate_count"],
            "canonical_physical_selection_flag": obs[
                "canonical_physical_selection_flag"
            ],
            "four_dimensional_metric_flag": obs["four_dimensional_metric_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "plane_code_map": {str(value): key for key, value in PLANE_CODES.items()},
        "clause_code_map": {str(value): key for key, value in CLAUSE_CODES.items()},
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "candidate_table_sha256": sha_array(candidate_table),
        "candidate_text_sha256": sha_text(
            csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"])
        ),
        "contract_table_sha256": sha_array(contract_table),
        "contract_text_sha256": sha_text(
            csv_text(CONTRACT_COLUMNS, rows["contract_rows"])
        ),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3s = {
        "schema": "long.c59p3s@1",
        "object": "nonprincipal_three_plane_selector_gate",
        "status": STATUS if all(checks.values()) else "LONG_C59P3S_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3s.report@1",
        "status": c59p3s["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3s promotes the long_c59np3 witnesses only to formal "
            "finite 3-plane selector candidates. The algebraic plane domain, "
            "normal-form time trace, and guarded transition surface pass. The "
            "first failing clause is still the unaccepted physical selector "
            "axiom; semantic transition operations, stress coupling, and metric "
            "reduction remain downstream blocked."
        ),
        "stage_protocol": {
            "draft": "read long_c59np3, long_time_map, long_transition_sem, long_stress_couple, long_sel, and long_dim4_gate",
            "witness": "emit formal plane-selector candidates, ordered selector-gate clauses, decisions, gaps, and observables",
            "coherence": "check the passing prefix, first failure, downstream blocks, and absence of physical selector or metric promotion",
            "closure": "certify the current-boundary selector gate over the non-principal 3-plane witnesses",
            "emit": "write long_c59p3s artifacts and verifier hook",
        },
        "inputs": {
            "long_c59np3": input_entry(
                LONG_C59NP3,
                {
                    "status": rows["c59np3"].get("status"),
                    "certificate_sha256": rows["c59np3"].get("certificate_sha256"),
                },
            ),
            "long_time_map": input_entry(
                LONG_TIME_MAP,
                {
                    "status": rows["time_map"].get("status"),
                    "certificate_sha256": rows["time_map"].get("certificate_sha256"),
                },
            ),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_stress_couple": input_entry(
                LONG_STRESS_COUPLE,
                {
                    "status": rows["stress_couple"].get("status"),
                    "certificate_sha256": rows["stress_couple"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_sel": input_entry(
                LONG_SEL,
                {
                    "status": rows["long_sel"].get("status"),
                    "certificate_sha256": rows["long_sel"].get("certificate_sha256"),
                },
            ),
            "long_dim4_gate": input_entry(
                LONG_DIM4_GATE,
                {
                    "status": rows["dim4_gate"].get("status"),
                    "certificate_sha256": rows["dim4_gate"].get(
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
            "c59p3s": relpath(OUT_DIR / "c59p3s.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
            "contract_csv": relpath(OUT_DIR / "contract.csv"),
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
                "two formal non-principal 3-plane selector candidates are present",
                "the normal-form time trace and guarded finite transition surface are available for the selector gate",
                "the first failing selector-gate clause is the unaccepted physical selector axiom",
                "semantic transition operation, stress coupling, and metric-reduction clauses remain downstream blocked",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "acceptance of a physical selector axiom",
                "a canonical physical choice between the positive and negative 3-plane candidates",
                "semantic A985 transition-operation realization",
                "a transition-to-stress coupling map",
                "a four-dimensional metric reduction",
                "a physical source tensor or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Attack the first failed selector-gate clause: either accept an "
            "explicit physical selector axiom, or avoid that extra axiom by "
            "constructing semantic transition operation rows that select one "
            "of the witnessed 3-planes."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3s.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3s.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3s": c59p3s,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "contract_csv": csv_text(CONTRACT_COLUMNS, rows["contract_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": candidate_table,
        "contract_table": contract_table,
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
    write_json(OUT_DIR / "c59p3s.json", payloads["c59p3s"])
    (OUT_DIR / "candidate.csv").write_text(
        payloads["candidate_csv"], encoding="utf-8"
    )
    (OUT_DIR / "contract.csv").write_text(
        payloads["contract_csv"], encoding="utf-8"
    )
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        contract_table=payloads["contract_table"],
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
