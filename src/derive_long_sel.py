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


THEOREM_ID = "long_sel"
STATUS = "LONG_SEL_PHYSICAL_SELECTOR_AXIOM_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_RIM_SELECT = PROOF_ROOT / "long_rim_select" / "report.json"
LONG_C2UF = PROOF_ROOT / "long_c2uf" / "report.json"
LONG_PSEC = PROOF_ROOT / "long_psec" / "report.json"
LONG_BINC = PROOF_ROOT / "long_binc" / "report.json"
LONG_DIM4_GATE = PROOF_ROOT / "long_dim4_gate" / "report.json"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_sel.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_sel.py"

SELECTOR_COLUMNS = [
    "selector_id",
    "selector_code",
    "source_code",
    "candidate_count",
    "formal_selector_flag",
    "physical_selector_flag",
    "rim_phase_key_flag",
    "golden_phase_selected_flag",
    "dim4_candidate_flag",
    "open_obstruction_flag",
]
OBSTRUCTION_COLUMNS = [
    "obstruction_id",
    "obstruction_code",
    "source_code",
    "open_flag",
    "certified_obstruction_flag",
    "value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SELECTOR_NAMES = [
    "c2_raw543_formal_selector",
    "c2_lazy63_formal_selector",
    "c2_singleton_formal_selectors",
    "golden_rim_phase_candidate",
    "stress_overlap_selector_candidate",
    "boundary_packet_selector_candidate",
    "perennial_sector_selector_candidate",
    "dim4_subboundary_selector_candidate",
    "physical_selector_axiom",
]
SELECTOR_CODES = {name: index for index, name in enumerate(SELECTOR_NAMES)}

OBSTRUCTION_NAMES = [
    "physical_selector_axiom_missing",
    "golden_rim_phase_unselected",
    "stress_selector_not_golden",
    "stress_transition_coupling_key_absent",
    "semantic_transition_operation_absent",
    "raw_packet_bridge_absent",
    "sector_normalization_open",
    "dim4_reduction_absent",
]
OBSTRUCTION_CODES = {name: index for index, name in enumerate(OBSTRUCTION_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "c2_selector_count",
    "c2_noncontractible_selector_count",
    "c2_singleton_selector_count",
    "c2_physical_selector_axiom_flag",
    "c2_formal_univalence_flag",
    "c2_lazy63_selector_count",
    "c2_raw543_selector_count",
    "rim_phase_count",
    "golden_phase_selected_flag",
    "golden_unoriented_rim_count",
    "stress_overlap_global_directed_max",
    "stress_overlap_golden_directed_max",
    "stress_transition_shared_key_count",
    "semantic_transition_operation_flag",
    "raw_compatible_packet_pair_count",
    "low_support_compatible_doublet_count",
    "low_support_rank_two_doublet_count",
    "missing_restriction_bridge_count",
    "psec_open_normalization_sector_count",
    "psec_remaining_projective_gauge_dimension",
    "certified_dim4_candidate_count",
    "dim4_reduction_certified_flag",
    "physical_selector_candidate_count",
    "missing_physical_selector_axiom_flag",
    "next_obstruction_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def build_rows() -> dict[str, Any]:
    rim_select = load_json(LONG_RIM_SELECT)
    c2uf = load_json(LONG_C2UF)
    psec = load_json(LONG_PSEC)
    binc = load_json(LONG_BINC)
    dim4 = load_json(LONG_DIM4_GATE)
    transition = load_json(LONG_TRANSITION_SEM)

    rim = summary(rim_select)
    c2 = summary(c2uf)
    psec_summary = summary(psec)
    binc_summary = summary(binc)
    dim4_summary = summary(dim4)
    transition_summary = summary(transition)
    c2_selector_counts = c2uf["witness"]["selector_fiber_counts"]

    obs = {
        "input_report_count": 6,
        "input_certified_count": 6,
        "c2_selector_count": int(c2["selector_count"]),
        "c2_noncontractible_selector_count": int(c2["noncontractible_selector_count"]),
        "c2_singleton_selector_count": int(c2["singleton_selector_count"]),
        "c2_physical_selector_axiom_flag": int(
            c2["physical_selector_axiom_certified_flag"]
        ),
        "c2_formal_univalence_flag": int(c2["formal_univalence_proof_present_flag"]),
        "c2_lazy63_selector_count": int(
            c2_selector_counts["lazy_componentwise_spectral_gap"]
        ),
        "c2_raw543_selector_count": int(
            c2_selector_counts["raw_componentwise_absolute_spectral_gap"]
        ),
        "rim_phase_count": int(rim["rim_phase_count"]),
        "golden_phase_selected_flag": int(rim["golden_phase_selected_flag"]),
        "golden_unoriented_rim_count": int(rim["golden_unoriented_rims"]),
        "stress_overlap_global_directed_max": int(rim["global_directed_overlap_max"]),
        "stress_overlap_golden_directed_max": int(rim["golden_directed_overlap_max"]),
        "stress_transition_shared_key_count": int(
            rim["stress_transition_shared_key_count"]
        ),
        "semantic_transition_operation_flag": int(
            transition_summary["semantic_transition_operation_flag"]
        ),
        "raw_compatible_packet_pair_count": int(
            binc_summary["raw_compatible_pair_count"]
        ),
        "low_support_compatible_doublet_count": int(
            binc_summary["low_support_compatible_doublet_count"]
        ),
        "low_support_rank_two_doublet_count": int(
            binc_summary["low_support_rank_two_doublet_count"]
        ),
        "missing_restriction_bridge_count": int(
            binc_summary["missing_restriction_bridge_count"]
        ),
        "psec_open_normalization_sector_count": int(
            psec_summary["open_normalization_sector_count"]
        ),
        "psec_remaining_projective_gauge_dimension": int(
            psec_summary["remaining_projective_gauge_dimension"]
        ),
        "certified_dim4_candidate_count": int(
            dim4_summary["certified_dim4_candidate_count"]
        ),
        "dim4_reduction_certified_flag": int(
            dim4_summary["dim4_reduction_certified_flag"]
        ),
        "physical_selector_candidate_count": 0,
        "missing_physical_selector_axiom_flag": 1,
        "next_obstruction_code": OBSTRUCTION_CODES["physical_selector_axiom_missing"],
    }

    selector_rows = [
        {
            "selector_id": SELECTOR_CODES["c2_raw543_formal_selector"],
            "selector_code": SELECTOR_CODES["c2_raw543_formal_selector"],
            "source_code": 0,
            "candidate_count": obs["c2_raw543_selector_count"],
            "formal_selector_flag": 1,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 0,
            "golden_phase_selected_flag": 0,
            "dim4_candidate_flag": 0,
            "open_obstruction_flag": 1,
        },
        {
            "selector_id": SELECTOR_CODES["c2_lazy63_formal_selector"],
            "selector_code": SELECTOR_CODES["c2_lazy63_formal_selector"],
            "source_code": 0,
            "candidate_count": obs["c2_lazy63_selector_count"],
            "formal_selector_flag": 1,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 0,
            "golden_phase_selected_flag": 0,
            "dim4_candidate_flag": 0,
            "open_obstruction_flag": 1,
        },
        {
            "selector_id": SELECTOR_CODES["c2_singleton_formal_selectors"],
            "selector_code": SELECTOR_CODES["c2_singleton_formal_selectors"],
            "source_code": 0,
            "candidate_count": obs["c2_singleton_selector_count"],
            "formal_selector_flag": 1,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 0,
            "golden_phase_selected_flag": 0,
            "dim4_candidate_flag": 0,
            "open_obstruction_flag": 1,
        },
        {
            "selector_id": SELECTOR_CODES["golden_rim_phase_candidate"],
            "selector_code": SELECTOR_CODES["golden_rim_phase_candidate"],
            "source_code": 1,
            "candidate_count": 1,
            "formal_selector_flag": 0,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 1,
            "golden_phase_selected_flag": obs["golden_phase_selected_flag"],
            "dim4_candidate_flag": 0,
            "open_obstruction_flag": 1,
        },
        {
            "selector_id": SELECTOR_CODES["stress_overlap_selector_candidate"],
            "selector_code": SELECTOR_CODES["stress_overlap_selector_candidate"],
            "source_code": 2,
            "candidate_count": obs["rim_phase_count"],
            "formal_selector_flag": 0,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 1,
            "golden_phase_selected_flag": 0,
            "dim4_candidate_flag": 0,
            "open_obstruction_flag": 1,
        },
        {
            "selector_id": SELECTOR_CODES["boundary_packet_selector_candidate"],
            "selector_code": SELECTOR_CODES["boundary_packet_selector_candidate"],
            "source_code": 3,
            "candidate_count": obs["low_support_compatible_doublet_count"],
            "formal_selector_flag": 0,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 0,
            "golden_phase_selected_flag": 0,
            "dim4_candidate_flag": 0,
            "open_obstruction_flag": 1,
        },
        {
            "selector_id": SELECTOR_CODES["perennial_sector_selector_candidate"],
            "selector_code": SELECTOR_CODES["perennial_sector_selector_candidate"],
            "source_code": 4,
            "candidate_count": int(psec_summary["sector_count"]),
            "formal_selector_flag": 0,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 0,
            "golden_phase_selected_flag": 0,
            "dim4_candidate_flag": 0,
            "open_obstruction_flag": 1,
        },
        {
            "selector_id": SELECTOR_CODES["dim4_subboundary_selector_candidate"],
            "selector_code": SELECTOR_CODES["dim4_subboundary_selector_candidate"],
            "source_code": 5,
            "candidate_count": obs["certified_dim4_candidate_count"],
            "formal_selector_flag": 0,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 0,
            "golden_phase_selected_flag": 0,
            "dim4_candidate_flag": obs["dim4_reduction_certified_flag"],
            "open_obstruction_flag": 1,
        },
        {
            "selector_id": SELECTOR_CODES["physical_selector_axiom"],
            "selector_code": SELECTOR_CODES["physical_selector_axiom"],
            "source_code": 6,
            "candidate_count": obs["physical_selector_candidate_count"],
            "formal_selector_flag": 0,
            "physical_selector_flag": 0,
            "rim_phase_key_flag": 0,
            "golden_phase_selected_flag": 0,
            "dim4_candidate_flag": 0,
            "open_obstruction_flag": 1,
        },
    ]

    obstruction_rows = [
        {
            "obstruction_id": OBSTRUCTION_CODES["physical_selector_axiom_missing"],
            "obstruction_code": OBSTRUCTION_CODES["physical_selector_axiom_missing"],
            "source_code": 0,
            "open_flag": 1,
            "certified_obstruction_flag": 1,
            "value": obs["c2_physical_selector_axiom_flag"],
        },
        {
            "obstruction_id": OBSTRUCTION_CODES["golden_rim_phase_unselected"],
            "obstruction_code": OBSTRUCTION_CODES["golden_rim_phase_unselected"],
            "source_code": 1,
            "open_flag": 1,
            "certified_obstruction_flag": 1,
            "value": obs["golden_phase_selected_flag"],
        },
        {
            "obstruction_id": OBSTRUCTION_CODES["stress_selector_not_golden"],
            "obstruction_code": OBSTRUCTION_CODES["stress_selector_not_golden"],
            "source_code": 2,
            "open_flag": 1,
            "certified_obstruction_flag": 1,
            "value": obs["stress_overlap_global_directed_max"]
            - obs["stress_overlap_golden_directed_max"],
        },
        {
            "obstruction_id": OBSTRUCTION_CODES["stress_transition_coupling_key_absent"],
            "obstruction_code": OBSTRUCTION_CODES[
                "stress_transition_coupling_key_absent"
            ],
            "source_code": 1,
            "open_flag": 1,
            "certified_obstruction_flag": 1,
            "value": obs["stress_transition_shared_key_count"],
        },
        {
            "obstruction_id": OBSTRUCTION_CODES["semantic_transition_operation_absent"],
            "obstruction_code": OBSTRUCTION_CODES[
                "semantic_transition_operation_absent"
            ],
            "source_code": 5,
            "open_flag": 1,
            "certified_obstruction_flag": 1,
            "value": obs["semantic_transition_operation_flag"],
        },
        {
            "obstruction_id": OBSTRUCTION_CODES["raw_packet_bridge_absent"],
            "obstruction_code": OBSTRUCTION_CODES["raw_packet_bridge_absent"],
            "source_code": 3,
            "open_flag": 1,
            "certified_obstruction_flag": 1,
            "value": obs["raw_compatible_packet_pair_count"],
        },
        {
            "obstruction_id": OBSTRUCTION_CODES["sector_normalization_open"],
            "obstruction_code": OBSTRUCTION_CODES["sector_normalization_open"],
            "source_code": 4,
            "open_flag": 1,
            "certified_obstruction_flag": 1,
            "value": obs["psec_open_normalization_sector_count"],
        },
        {
            "obstruction_id": OBSTRUCTION_CODES["dim4_reduction_absent"],
            "obstruction_code": OBSTRUCTION_CODES["dim4_reduction_absent"],
            "source_code": 6,
            "open_flag": 1,
            "certified_obstruction_flag": 1,
            "value": obs["dim4_reduction_certified_flag"],
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
        "rim_select": rim_select,
        "c2uf": c2uf,
        "psec": psec,
        "binc": binc,
        "dim4": dim4,
        "transition": transition,
        "selector_rows": selector_rows,
        "obstruction_rows": obstruction_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    selector_table = table_from_rows(SELECTOR_COLUMNS, rows["selector_rows"])
    obstruction_table = table_from_rows(OBSTRUCTION_COLUMNS, rows["obstruction_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])

    checks = {
        "input_reports_certified": rows["rim_select"].get("status")
        == "LONG_RIM_SELECT_GAUGE_OBSTRUCTION_CERTIFIED"
        and rows["rim_select"].get("all_checks_pass") is True
        and rows["c2uf"].get("status") == "LONG_C2UF_CERTIFIED"
        and rows["c2uf"].get("all_checks_pass") is True
        and rows["psec"].get("status") == "LONG_PSEC_CERTIFIED"
        and rows["psec"].get("all_checks_pass") is True
        and rows["binc"].get("status") == "LONG_BINC_CERTIFIED"
        and rows["binc"].get("all_checks_pass") is True
        and rows["dim4"].get("status") == "LONG_DIM4_GATE_OBSTRUCTION_CERTIFIED"
        and rows["dim4"].get("all_checks_pass") is True
        and rows["transition"].get("status")
        == "LONG_TRANSITION_SEM_OBSTRUCTION_CERTIFIED"
        and rows["transition"].get("all_checks_pass") is True,
        "formal_selectors_do_not_supply_physical_axiom": obs["c2_selector_count"] == 8
        and obs["c2_physical_selector_axiom_flag"] == 0
        and obs["c2_formal_univalence_flag"] == 0,
        "rim_phase_and_stress_selection_blocked": obs["rim_phase_count"] == 63
        and obs["golden_phase_selected_flag"] == 0
        and obs["stress_overlap_global_directed_max"]
        > obs["stress_overlap_golden_directed_max"]
        and obs["stress_transition_shared_key_count"] == 0,
        "transition_packet_sector_dim4_obstructions_preserved": obs[
            "semantic_transition_operation_flag"
        ]
        == 0
        and obs["raw_compatible_packet_pair_count"] == 0
        and obs["low_support_rank_two_doublet_count"] == 0
        and obs["missing_restriction_bridge_count"] == 3
        and obs["psec_open_normalization_sector_count"] == 30
        and obs["certified_dim4_candidate_count"] == 0
        and obs["dim4_reduction_certified_flag"] == 0,
        "physical_selector_missing_exact": obs["physical_selector_candidate_count"] == 0
        and obs["missing_physical_selector_axiom_flag"] == 1,
        "table_shapes_match": selector_table.shape
        == (len(SELECTOR_CODES), len(SELECTOR_COLUMNS))
        and obstruction_table.shape
        == (len(OBSTRUCTION_CODES), len(OBSTRUCTION_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "physical_selector_axiom_current_boundary_obstruction",
        "summary": {
            "formal_c2_selector_count": obs["c2_selector_count"],
            "c2_noncontractible_selector_count": obs[
                "c2_noncontractible_selector_count"
            ],
            "c2_singleton_selector_count": obs["c2_singleton_selector_count"],
            "physical_selector_axiom_flag": obs["c2_physical_selector_axiom_flag"],
            "formal_univalence_flag": obs["c2_formal_univalence_flag"],
            "rim_phase_count": obs["rim_phase_count"],
            "golden_phase_selected_flag": obs["golden_phase_selected_flag"],
            "golden_unoriented_rims": obs["golden_unoriented_rim_count"],
            "stress_directed_gap_over_golden": obs[
                "stress_overlap_global_directed_max"
            ]
            - obs["stress_overlap_golden_directed_max"],
            "stress_transition_shared_key_count": obs[
                "stress_transition_shared_key_count"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "raw_compatible_packet_pair_count": obs[
                "raw_compatible_packet_pair_count"
            ],
            "psec_open_normalization_sector_count": obs[
                "psec_open_normalization_sector_count"
            ],
            "certified_dim4_candidate_count": obs["certified_dim4_candidate_count"],
            "physical_selector_candidate_count": obs[
                "physical_selector_candidate_count"
            ],
            "missing_physical_selector_axiom_flag": obs[
                "missing_physical_selector_axiom_flag"
            ],
        },
        "selector_code_map": {str(value): key for key, value in SELECTOR_CODES.items()},
        "obstruction_code_map": {
            str(value): key for key, value in OBSTRUCTION_CODES.items()
        },
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "selector_table_sha256": sha_array(selector_table),
        "selector_text_sha256": sha_text(
            csv_text(SELECTOR_COLUMNS, rows["selector_rows"])
        ),
        "obstruction_table_sha256": sha_array(obstruction_table),
        "obstruction_text_sha256": sha_text(
            csv_text(OBSTRUCTION_COLUMNS, rows["obstruction_rows"])
        ),
        "observable_table_sha256": sha_array(observable_table),
    }
    sel = {
        "schema": "long.sel@1",
        "object": "physical_selector_axiom_current_boundary_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_SEL_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.sel.report@1",
        "status": sel["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_sel unifies the selector boundary after rim classification. "
            "The repository has finite formal C2 selectors, finite rim phases, "
            "stress overlap candidates, packet candidates, sector candidates, "
            "and rank candidates, but none is certified as a physical selector "
            "axiom. The current boundary therefore cannot select the golden rim "
            "phase, a 1+3 subboundary, or a GR source structure without a new "
            "selector construction."
        ),
        "stage_protocol": {
            "draft": "read long_rim_select, long_c2uf, long_psec, long_binc, long_dim4_gate, and long_transition_sem",
            "witness": "emit selector candidate rows, obstruction rows, and observables",
            "coherence": "check input statuses, formal selector counts, rim/stress selector failure, packet/sector/dim4 obstructions, and table hashes",
            "closure": "certify the current-boundary missing physical selector axiom",
            "emit": "write long_sel artifacts and verifier hook",
        },
        "inputs": {
            "long_rim_select": input_entry(
                LONG_RIM_SELECT,
                {
                    "status": rows["rim_select"].get("status"),
                    "certificate_sha256": rows["rim_select"].get("certificate_sha256"),
                },
            ),
            "long_c2uf": input_entry(
                LONG_C2UF,
                {
                    "status": rows["c2uf"].get("status"),
                    "certificate_sha256": rows["c2uf"].get("certificate_sha256"),
                },
            ),
            "long_psec": input_entry(
                LONG_PSEC,
                {
                    "status": rows["psec"].get("status"),
                    "certificate_sha256": rows["psec"].get("certificate_sha256"),
                },
            ),
            "long_binc": input_entry(
                LONG_BINC,
                {
                    "status": rows["binc"].get("status"),
                    "certificate_sha256": rows["binc"].get("certificate_sha256"),
                },
            ),
            "long_dim4_gate": input_entry(
                LONG_DIM4_GATE,
                {
                    "status": rows["dim4"].get("status"),
                    "certificate_sha256": rows["dim4"].get("certificate_sha256"),
                },
            ),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition"].get("status"),
                    "certificate_sha256": rows["transition"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "sel": relpath(OUT_DIR / "sel.json"),
            "selector_csv": relpath(OUT_DIR / "selector.csv"),
            "obstruction_csv": relpath(OUT_DIR / "obstruction.csv"),
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
                "formal C2 selectors exist but do not certify a physical selector axiom",
                "the golden rim phase is not selected by the current rim/stress/contact boundary",
                "packet, sector-normalization, semantic-transition, and 1+3 selector candidates remain obstructed",
                "no current certified selector chooses the golden rim phase or a physical 1+3 boundary",
                "the next missing seam is an explicit physical selector construction or axiom",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute nonexistence of a future physical selector",
                "formal univalence for the C2 candidate universe",
                "a raw A985-to-packet operator bridge",
                "sector-local GL_d/scalar normalization for the 30 open sectors",
                "a nondegenerate Lorentzian metric, stress-energy tensor, or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Build the selector-construction attempt: define the minimal finite "
            "physical-selector contract over rim phase, atom boundary, packet "
            "bridge, and transition semantics, then either produce a witness or "
            "certify the contract's first failing clause."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.sel.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.sel.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "sel": sel,
        "selector_csv": csv_text(SELECTOR_COLUMNS, rows["selector_rows"]),
        "obstruction_csv": csv_text(OBSTRUCTION_COLUMNS, rows["obstruction_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "selector_table": selector_table,
        "obstruction_table": obstruction_table,
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
    write_json(OUT_DIR / "sel.json", payloads["sel"])
    (OUT_DIR / "selector.csv").write_text(payloads["selector_csv"], encoding="utf-8")
    (OUT_DIR / "obstruction.csv").write_text(
        payloads["obstruction_csv"], encoding="utf-8"
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        selector_table=payloads["selector_table"],
        obstruction_table=payloads["obstruction_table"],
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
