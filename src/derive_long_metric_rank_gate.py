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


THEOREM_ID = "long_metric_rank_gate"
STATUS = "LONG_METRIC_RANK_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_LOR = PROOF_ROOT / "long_lor" / "report.json"
LONG_TIME_MAP = PROOF_ROOT / "long_time_map" / "report.json"
LONG_METRIC_GATE = PROOF_ROOT / "long_metric_gate" / "report.json"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_COUPLE = PROOF_ROOT / "long_stress_couple" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_metric_rank_gate.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_metric_rank_gate.py"

RANK_COLUMNS = [
    "rank_row_id",
    "rank_code",
    "ambient_rank",
    "certified_rank",
    "kernel_rank",
    "quotient_rank",
    "count_value",
    "certified_flag",
    "obstruction_flag",
]
DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "pass_flag",
    "certified_flag",
    "obstruction_flag",
    "value",
]
GAP_COLUMNS = ["gap_id", "gap_code", "open_flag", "obstruction_flag", "next_flag"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

RANK_NAMES = [
    "operation_integral_trace_rank",
    "public_integral_trace_rank",
    "public_kernel_residual_rank",
    "rho_public_readout_rank",
    "recurrence_time_line_rank",
    "finite_stress_readout_rank",
    "four_dimensional_reduction_candidate",
    "smooth_lorentzian_signature_candidate",
]
RANK_CODES = {name: index for index, name in enumerate(RANK_NAMES)}

DECISION_NAMES = [
    "finite_rank_split_survives",
    "one_plus_nineteen_formal_split",
    "four_dimensional_reduction_certified",
    "smooth_lorentzian_signature_certified",
    "stress_energy_source_certified",
    "gr_derivation_certified",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}

GAP_NAMES = [
    "finite_rank_split",
    "four_dimensional_spacetime_reduction",
    "nondegenerate_smooth_lorentzian_metric",
    "physical_stress_energy_tensor",
    "curvature_and_einstein_tensor",
    "gr_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "operation_algebra_dimension",
    "integrity_kernel_dimension",
    "time_rank",
    "public_rank",
    "public_kernel_dimension",
    "public_quotient_dimension",
    "rho_rank",
    "normal_form_tick_count",
    "transition_row_count",
    "finite_stress_node_count",
    "finite_stress_edge_count",
    "finite_rank_split_flag",
    "one_plus_nineteen_formal_split_flag",
    "three_spatial_rank_flag",
    "four_dimensional_spacetime_flag",
    "smooth_metric_signature_flag",
    "stress_energy_flag",
    "curvature_einstein_flag",
    "gr_derivation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    summary = witness.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary missing")
    return summary


def build_rows() -> dict[str, Any]:
    long_lor = load_json(LONG_LOR)
    long_time_map = load_json(LONG_TIME_MAP)
    long_metric_gate = load_json(LONG_METRIC_GATE)
    long_transition_sem = load_json(LONG_TRANSITION_SEM)
    long_stress_gate = load_json(LONG_STRESS_GATE)
    long_stress_couple = load_json(LONG_STRESS_COUPLE)

    lor = _summary(long_lor)
    time_map = _summary(long_time_map)
    metric_gate = _summary(long_metric_gate)
    transition_sem = _summary(long_transition_sem)
    stress_gate = _summary(long_stress_gate)
    stress_couple = _summary(long_stress_couple)

    operation_dim = int(lor["operation_algebra_dimension"])
    time_rank = int(lor["time_rank"])
    public_rank = int(lor["public_rank"])
    public_kernel = int(lor["public_kernel_dimension"])
    public_quotient = int(lor["public_quotient_dimension"])
    rho_rank = int(time_map["rho_rank"])
    ticks = int(time_map["time_tick_total"])
    transition_count = int(transition_sem["transition_row_count"])
    stress_nodes = int(stress_gate["stress_node_count"])
    stress_edges = int(stress_gate["stress_directed_edge_count"])
    finite_rank_split_flag = 1
    one_plus_nineteen_flag = int(time_rank == 1 and public_kernel == 19)
    three_spatial_rank_flag = int(public_kernel == 3)
    four_dimensional_flag = int(time_rank == 1 and public_kernel == 3)
    smooth_metric_flag = int(metric_gate["smooth_lorentzian_metric_flag"])
    stress_energy_flag = int(stress_couple["physical_stress_energy_flag"])
    curvature_flag = int(stress_couple.get("curvature_einstein_tensor_flag", 0))
    gr_flag = int(stress_couple["gr_derivation_flag"])

    obs = {
        "input_report_count": 6,
        "input_certified_count": 6,
        "operation_algebra_dimension": operation_dim,
        "integrity_kernel_dimension": operation_dim - time_rank,
        "time_rank": time_rank,
        "public_rank": public_rank,
        "public_kernel_dimension": public_kernel,
        "public_quotient_dimension": public_quotient,
        "rho_rank": rho_rank,
        "normal_form_tick_count": ticks,
        "transition_row_count": transition_count,
        "finite_stress_node_count": stress_nodes,
        "finite_stress_edge_count": stress_edges,
        "finite_rank_split_flag": finite_rank_split_flag,
        "one_plus_nineteen_formal_split_flag": one_plus_nineteen_flag,
        "three_spatial_rank_flag": three_spatial_rank_flag,
        "four_dimensional_spacetime_flag": four_dimensional_flag,
        "smooth_metric_signature_flag": smooth_metric_flag,
        "stress_energy_flag": stress_energy_flag,
        "curvature_einstein_flag": curvature_flag,
        "gr_derivation_flag": gr_flag,
        "open_gap_count": 5,
        "next_gap_code": GAP_CODES["four_dimensional_spacetime_reduction"],
    }

    rank_rows = [
        {
            "rank_row_id": RANK_CODES["operation_integral_trace_rank"],
            "rank_code": RANK_CODES["operation_integral_trace_rank"],
            "ambient_rank": operation_dim,
            "certified_rank": time_rank,
            "kernel_rank": operation_dim - time_rank,
            "quotient_rank": time_rank,
            "count_value": time_rank,
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "rank_row_id": RANK_CODES["public_integral_trace_rank"],
            "rank_code": RANK_CODES["public_integral_trace_rank"],
            "ambient_rank": public_rank,
            "certified_rank": public_quotient,
            "kernel_rank": public_kernel,
            "quotient_rank": public_quotient,
            "count_value": public_quotient,
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "rank_row_id": RANK_CODES["public_kernel_residual_rank"],
            "rank_code": RANK_CODES["public_kernel_residual_rank"],
            "ambient_rank": public_rank,
            "certified_rank": public_kernel,
            "kernel_rank": public_kernel,
            "quotient_rank": public_quotient,
            "count_value": public_kernel,
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "rank_row_id": RANK_CODES["rho_public_readout_rank"],
            "rank_code": RANK_CODES["rho_public_readout_rank"],
            "ambient_rank": operation_dim,
            "certified_rank": rho_rank,
            "kernel_rank": operation_dim - rho_rank,
            "quotient_rank": -1,
            "count_value": rho_rank,
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "rank_row_id": RANK_CODES["recurrence_time_line_rank"],
            "rank_code": RANK_CODES["recurrence_time_line_rank"],
            "ambient_rank": ticks,
            "certified_rank": time_rank,
            "kernel_rank": ticks - time_rank,
            "quotient_rank": time_rank,
            "count_value": ticks,
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "rank_row_id": RANK_CODES["finite_stress_readout_rank"],
            "rank_code": RANK_CODES["finite_stress_readout_rank"],
            "ambient_rank": stress_nodes,
            "certified_rank": stress_nodes,
            "kernel_rank": 0,
            "quotient_rank": -1,
            "count_value": stress_edges,
            "certified_flag": int(stress_gate["finite_stress_readout_flag"]),
            "obstruction_flag": 0,
        },
        {
            "rank_row_id": RANK_CODES["four_dimensional_reduction_candidate"],
            "rank_code": RANK_CODES["four_dimensional_reduction_candidate"],
            "ambient_rank": public_rank,
            "certified_rank": 0,
            "kernel_rank": public_kernel,
            "quotient_rank": 4,
            "count_value": four_dimensional_flag,
            "certified_flag": four_dimensional_flag,
            "obstruction_flag": int(four_dimensional_flag == 0),
        },
        {
            "rank_row_id": RANK_CODES["smooth_lorentzian_signature_candidate"],
            "rank_code": RANK_CODES["smooth_lorentzian_signature_candidate"],
            "ambient_rank": 0,
            "certified_rank": 0,
            "kernel_rank": -1,
            "quotient_rank": -1,
            "count_value": smooth_metric_flag,
            "certified_flag": smooth_metric_flag,
            "obstruction_flag": int(smooth_metric_flag == 0),
        },
    ]
    decision_rows = [
        {
            "decision_id": DECISION_CODES["finite_rank_split_survives"],
            "decision_code": DECISION_CODES["finite_rank_split_survives"],
            "pass_flag": 1,
            "certified_flag": finite_rank_split_flag,
            "obstruction_flag": 0,
            "value": finite_rank_split_flag,
        },
        {
            "decision_id": DECISION_CODES["one_plus_nineteen_formal_split"],
            "decision_code": DECISION_CODES["one_plus_nineteen_formal_split"],
            "pass_flag": 1,
            "certified_flag": one_plus_nineteen_flag,
            "obstruction_flag": 0,
            "value": public_kernel,
        },
        {
            "decision_id": DECISION_CODES["four_dimensional_reduction_certified"],
            "decision_code": DECISION_CODES["four_dimensional_reduction_certified"],
            "pass_flag": 1,
            "certified_flag": four_dimensional_flag,
            "obstruction_flag": int(four_dimensional_flag == 0),
            "value": four_dimensional_flag,
        },
        {
            "decision_id": DECISION_CODES["smooth_lorentzian_signature_certified"],
            "decision_code": DECISION_CODES["smooth_lorentzian_signature_certified"],
            "pass_flag": 1,
            "certified_flag": smooth_metric_flag,
            "obstruction_flag": int(smooth_metric_flag == 0),
            "value": smooth_metric_flag,
        },
        {
            "decision_id": DECISION_CODES["stress_energy_source_certified"],
            "decision_code": DECISION_CODES["stress_energy_source_certified"],
            "pass_flag": 1,
            "certified_flag": stress_energy_flag,
            "obstruction_flag": int(stress_energy_flag == 0),
            "value": stress_energy_flag,
        },
        {
            "decision_id": DECISION_CODES["gr_derivation_certified"],
            "decision_code": DECISION_CODES["gr_derivation_certified"],
            "pass_flag": 1,
            "certified_flag": gr_flag,
            "obstruction_flag": int(gr_flag == 0),
            "value": gr_flag,
        },
    ]
    gap_rows = [
        {
            "gap_id": code,
            "gap_code": code,
            "open_flag": int(name != "finite_rank_split"),
            "obstruction_flag": int(name != "finite_rank_split"),
            "next_flag": int(name == "four_dimensional_spacetime_reduction"),
        }
        for name, code in GAP_CODES.items()
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "long_lor": long_lor,
        "long_time_map": long_time_map,
        "long_metric_gate": long_metric_gate,
        "long_transition_sem": long_transition_sem,
        "long_stress_gate": long_stress_gate,
        "long_stress_couple": long_stress_couple,
        "rank_rows": rank_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "rank_table": table_from_rows(RANK_COLUMNS, rank_rows),
        "decision_table": table_from_rows(DECISION_COLUMNS, decision_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "rank_text_hash": sha_text(digest_text(RANK_COLUMNS, rank_rows)),
        "decision_text_hash": sha_text(digest_text(DECISION_COLUMNS, decision_rows)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    long_lor = rows["long_lor"]
    long_time_map = rows["long_time_map"]
    long_metric_gate = rows["long_metric_gate"]
    long_transition_sem = rows["long_transition_sem"]
    long_stress_gate = rows["long_stress_gate"]
    long_stress_couple = rows["long_stress_couple"]
    checks = {
        "all_input_reports_certified": long_lor.get("status") == "LONG_LOR_CERTIFIED"
        and long_lor.get("all_checks_pass") is True
        and long_time_map.get("status") == "LONG_TIME_MAP_CERTIFIED"
        and long_time_map.get("all_checks_pass") is True
        and long_metric_gate.get("status") == "LONG_METRIC_GATE_CERTIFIED"
        and long_metric_gate.get("all_checks_pass") is True
        and long_transition_sem.get("status")
        == "LONG_TRANSITION_SEM_OBSTRUCTION_CERTIFIED"
        and long_transition_sem.get("all_checks_pass") is True
        and long_stress_gate.get("status") == "LONG_STRESS_GATE_CERTIFIED"
        and long_stress_gate.get("all_checks_pass") is True
        and long_stress_couple.get("status")
        == "LONG_STRESS_COUPLE_OBSTRUCTION_CERTIFIED"
        and long_stress_couple.get("all_checks_pass") is True,
        "finite_rank_split_exact": obs["operation_algebra_dimension"] == 36
        and obs["integrity_kernel_dimension"] == 35
        and obs["time_rank"] == 1
        and obs["public_rank"] == 20
        and obs["public_kernel_dimension"] == 19
        and obs["public_quotient_dimension"] == 1
        and obs["rho_rank"] == 20,
        "finite_surfaces_exact": obs["normal_form_tick_count"] == 642
        and obs["transition_row_count"] == 642
        and obs["finite_stress_node_count"] == 20
        and obs["finite_stress_edge_count"] == 100,
        "rank_gate_obstructions_exact": obs["finite_rank_split_flag"] == 1
        and obs["one_plus_nineteen_formal_split_flag"] == 1
        and obs["three_spatial_rank_flag"] == 0
        and obs["four_dimensional_spacetime_flag"] == 0
        and obs["smooth_metric_signature_flag"] == 0
        and obs["stress_energy_flag"] == 0
        and obs["curvature_einstein_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "table_shapes_match": rows["rank_table"].shape
        == (len(RANK_CODES), len(RANK_COLUMNS))
        and rows["decision_table"].shape
        == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_metric_rank_gate",
        "summary": {
            "operation_algebra_dimension": obs["operation_algebra_dimension"],
            "time_rank": obs["time_rank"],
            "public_rank": obs["public_rank"],
            "public_kernel_dimension": obs["public_kernel_dimension"],
            "public_quotient_dimension": obs["public_quotient_dimension"],
            "rho_rank": obs["rho_rank"],
            "normal_form_tick_count": obs["normal_form_tick_count"],
            "transition_row_count": obs["transition_row_count"],
            "finite_stress_node_count": obs["finite_stress_node_count"],
            "finite_stress_edge_count": obs["finite_stress_edge_count"],
            "finite_rank_split_flag": obs["finite_rank_split_flag"],
            "one_plus_nineteen_formal_split_flag": obs[
                "one_plus_nineteen_formal_split_flag"
            ],
            "four_dimensional_spacetime_flag": obs["four_dimensional_spacetime_flag"],
            "smooth_metric_signature_flag": obs["smooth_metric_signature_flag"],
            "stress_energy_flag": obs["stress_energy_flag"],
            "gr_derivation_flag": obs["gr_derivation_flag"],
            "next_gap": "four_dimensional_spacetime_reduction",
        },
        "rank_code_map": {str(value): key for key, value in RANK_CODES.items()},
        "decision_code_map": {str(value): key for key, value in DECISION_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "rank_table_sha256": sha_array(rows["rank_table"]),
        "rank_text_sha256": rows["rank_text_hash"],
        "decision_table_sha256": sha_array(rows["decision_table"]),
        "decision_text_sha256": rows["decision_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    metric_rank_gate = {
        "schema": "long.metric_rank_gate@1",
        "object": "finite_metric_rank_gate",
        "status": STATUS
        if all(checks.values())
        else "LONG_METRIC_RANK_GATE_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.metric_rank_gate.report@1",
        "status": metric_rank_gate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_metric_rank_gate certifies the finite rank statement that "
            "survives the current d20 pathway: a one-dimensional time quotient, "
            "a 20-rank public boundary, a 19-dimensional public kernel, rho "
            "rank 20, 642 normal-form ticks, and a finite stress readout. It "
            "does not certify a 3+1 spacetime reduction, a nondegenerate smooth "
            "Lorentzian metric signature, a physical stress-energy source, or "
            "Einstein equations."
        ),
        "stage_protocol": {
            "draft": "read long_lor, long_time_map, long_metric_gate, long_transition_sem, long_stress_gate, and long_stress_couple",
            "witness": "emit rank rows, decision rows, gap rows, and observables",
            "coherence": "check quotient ranks, rho rank, transition/stress counts, obstruction flags, and table hashes",
            "closure": "certify the finite 1+19 rank boundary while preserving 3+1 and smooth metric gaps",
            "emit": "write long_metric_rank_gate artifacts and verifier hook",
        },
        "inputs": {
            "long_lor": input_entry(
                LONG_LOR,
                {
                    "status": long_lor.get("status"),
                    "certificate_sha256": long_lor.get("certificate_sha256"),
                },
            ),
            "long_time_map": input_entry(
                LONG_TIME_MAP,
                {
                    "status": long_time_map.get("status"),
                    "certificate_sha256": long_time_map.get("certificate_sha256"),
                },
            ),
            "long_metric_gate": input_entry(
                LONG_METRIC_GATE,
                {
                    "status": long_metric_gate.get("status"),
                    "certificate_sha256": long_metric_gate.get("certificate_sha256"),
                },
            ),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": long_transition_sem.get("status"),
                    "certificate_sha256": long_transition_sem.get("certificate_sha256"),
                },
            ),
            "long_stress_gate": input_entry(
                LONG_STRESS_GATE,
                {
                    "status": long_stress_gate.get("status"),
                    "certificate_sha256": long_stress_gate.get("certificate_sha256"),
                },
            ),
            "long_stress_couple": input_entry(
                LONG_STRESS_COUPLE,
                {
                    "status": long_stress_couple.get("status"),
                    "certificate_sha256": long_stress_couple.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "metric_rank_gate": relpath(OUT_DIR / "metric_rank_gate.json"),
            "rank_csv": relpath(OUT_DIR / "rank.csv"),
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
                "the finite rank split T_1 plus public kernel rank 19",
                "the public boundary rank 20 and rho readout rank 20",
                "642 normal-form time ticks and 642 guarded transitions remain rank-compatible readouts",
                "a finite 20-node, 100-directed-edge stress readout remains available",
                "the current rank boundary is 1+19, not certified as 3+1",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a 3+1 spacetime reduction from the 1+19 public split",
                "a nondegenerate smooth Lorentzian metric tensor or metric signature",
                "a physical stress-energy tensor source",
                "Riemann/Ricci curvature, Einstein tensor, or Einstein field equations",
                "a completed derivation of general relativity",
            ],
        },
        "next_highest_yield_item": (
            "Build long_dim4_gate: decide whether any certified quotient, "
            "subboundary, or sector selection reduces the 1+19 rank split to a "
            "1+3 spacetime boundary, or certify that obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.metric_rank_gate.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.metric_rank_gate.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "metric_rank_gate": metric_rank_gate,
        "rank_csv": csv_text(RANK_COLUMNS, rows["rank_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "rank_table": rows["rank_table"],
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
    write_json(OUT_DIR / "metric_rank_gate.json", payloads["metric_rank_gate"])
    (OUT_DIR / "rank.csv").write_text(payloads["rank_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        rank_table=payloads["rank_table"],
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
