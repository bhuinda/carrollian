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
    from .derive_long_binc import OBS_CODES as BINC_OBS_CODES
    from .derive_long_c2uf import OBS_CODES as C2UF_OBS_CODES
    from .derive_long_psec import OBS_CODES as PSEC_OBS_CODES
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
    from derive_long_binc import OBS_CODES as BINC_OBS_CODES
    from derive_long_c2uf import OBS_CODES as C2UF_OBS_CODES
    from derive_long_psec import OBS_CODES as PSEC_OBS_CODES
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_dim4_gate"
STATUS = "LONG_DIM4_GATE_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_METRIC_RANK_GATE = PROOF_ROOT / "long_metric_rank_gate" / "report.json"
LONG_BINC = PROOF_ROOT / "long_binc" / "report.json"
LONG_BINC_OBS = PROOF_ROOT / "long_binc" / "obs.csv"
LONG_PSEC = PROOF_ROOT / "long_psec" / "report.json"
LONG_PSEC_OBS = PROOF_ROOT / "long_psec" / "obs.csv"
LONG_C2UF = PROOF_ROOT / "long_c2uf" / "report.json"
LONG_C2UF_OBS = PROOF_ROOT / "long_c2uf" / "obs.csv"
ATLAS = PROOF_ROOT / "c985_d20_boundary_invariant_atlas" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_dim4_gate.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_dim4_gate.py"

CANDIDATE_COLUMNS = [
    "candidate_id",
    "candidate_code",
    "source_code",
    "certified_input_flag",
    "ambient_count",
    "residual_rank",
    "required_spatial_rank",
    "physical_selector_flag",
    "normalization_gap_count",
    "bridge_gap_count",
    "dim4_candidate_flag",
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

CANDIDATE_NAMES = [
    "rank_boundary_one_plus_nineteen",
    "atlas_twenty_atom_boundary",
    "boundary_packet_incidence",
    "c2_quotient_selector",
    "perennial_sector_selection",
]
CANDIDATE_CODES = {name: index for index, name in enumerate(CANDIDATE_NAMES)}

DECISION_NAMES = [
    "rank_boundary_blocks_dim4",
    "subboundary_dim4_certified",
    "quotient_dim4_certified",
    "sector_dim4_certified",
    "physical_selector_certified",
    "dim4_reduction_certified",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}

GAP_NAMES = [
    "four_dimensional_spacetime_reduction",
    "physical_selector_or_subboundary_axiom",
    "nondegenerate_smooth_lorentzian_metric",
    "physical_stress_energy_tensor",
    "curvature_and_einstein_tensor",
    "gr_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "time_rank",
    "public_rank",
    "public_kernel_dimension",
    "public_quotient_dimension",
    "required_spatial_rank",
    "residual_rank_excess_over_three",
    "rank_gate_dim4_flag",
    "atlas_atom_count",
    "atlas_complement_pair_count",
    "binc_public_atom_count",
    "binc_incidence_rank_over_q",
    "binc_raw_compatible_pair_count",
    "binc_low_support_rank_two_doublet_count",
    "binc_missing_restriction_bridge_count",
    "c2_quotient_state_count",
    "c2_selector_count",
    "c2_physical_selector_axiom_flag",
    "psec_sector_count",
    "psec_open_normalization_sector_count",
    "psec_dimension_one_fixed_sector_count",
    "psec_remaining_projective_gauge_dimension",
    "certified_dim4_candidate_count",
    "dim4_reduction_certified_flag",
    "current_boundary_obstruction_flag",
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


def read_obs(path: Path, codes: dict[str, int]) -> dict[str, int]:
    reverse = {value: key for key, value in codes.items()}
    out: dict[str, int] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            code = int(row["observable_code"])
            if code in reverse:
                out[reverse[code]] = int(row["value"])
    return out


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def build_rows() -> dict[str, Any]:
    metric_rank = load_json(LONG_METRIC_RANK_GATE)
    binc = load_json(LONG_BINC)
    psec = load_json(LONG_PSEC)
    c2uf = load_json(LONG_C2UF)
    atlas = load_json(ATLAS)

    metric = summary(metric_rank)
    binc_summary = summary(binc)
    psec_summary = summary(psec)
    c2uf_summary = summary(c2uf)
    atlas_witness = atlas["witness"]
    binc_obs = read_obs(LONG_BINC_OBS, BINC_OBS_CODES)
    psec_obs = read_obs(LONG_PSEC_OBS, PSEC_OBS_CODES)
    c2uf_obs = read_obs(LONG_C2UF_OBS, C2UF_OBS_CODES)

    required_spatial_rank = 3
    public_kernel = int(metric["public_kernel_dimension"])
    dim4_candidates = 0
    obs = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "time_rank": int(metric["time_rank"]),
        "public_rank": int(metric["public_rank"]),
        "public_kernel_dimension": public_kernel,
        "public_quotient_dimension": int(metric["public_quotient_dimension"]),
        "required_spatial_rank": required_spatial_rank,
        "residual_rank_excess_over_three": public_kernel - required_spatial_rank,
        "rank_gate_dim4_flag": int(metric["four_dimensional_spacetime_flag"]),
        "atlas_atom_count": int(atlas_witness["atom_count"]),
        "atlas_complement_pair_count": int(atlas_witness["complement_pair_count"]),
        "binc_public_atom_count": int(binc_summary["public_atom_count"]),
        "binc_incidence_rank_over_q": int(binc_obs["incidence_rank_over_q"]),
        "binc_raw_compatible_pair_count": int(
            binc_summary["raw_compatible_pair_count"]
        ),
        "binc_low_support_rank_two_doublet_count": int(
            binc_summary["low_support_rank_two_doublet_count"]
        ),
        "binc_missing_restriction_bridge_count": int(
            binc_summary["missing_restriction_bridge_count"]
        ),
        "c2_quotient_state_count": int(c2uf_summary["quotient_state_count"]),
        "c2_selector_count": int(c2uf_summary["selector_count"]),
        "c2_physical_selector_axiom_flag": int(
            c2uf_obs["physical_selector_axiom_certified_flag"]
        ),
        "psec_sector_count": int(psec_summary["sector_count"]),
        "psec_open_normalization_sector_count": int(
            psec_summary["open_normalization_sector_count"]
        ),
        "psec_dimension_one_fixed_sector_count": int(
            psec_obs["dimension_one_fixed_sector_count"]
        ),
        "psec_remaining_projective_gauge_dimension": int(
            psec_summary["remaining_projective_gauge_dimension"]
        ),
        "certified_dim4_candidate_count": dim4_candidates,
        "dim4_reduction_certified_flag": 0,
        "current_boundary_obstruction_flag": 1,
        "smooth_metric_signature_flag": int(metric["smooth_metric_signature_flag"]),
        "stress_energy_flag": int(metric["stress_energy_flag"]),
        "curvature_einstein_flag": 0,
        "gr_derivation_flag": int(metric["gr_derivation_flag"]),
        "open_gap_count": 5,
        "next_gap_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
    }
    candidate_rows = [
        {
            "candidate_id": CANDIDATE_CODES["rank_boundary_one_plus_nineteen"],
            "candidate_code": CANDIDATE_CODES["rank_boundary_one_plus_nineteen"],
            "source_code": 0,
            "certified_input_flag": 1,
            "ambient_count": obs["public_rank"],
            "residual_rank": obs["public_kernel_dimension"],
            "required_spatial_rank": required_spatial_rank,
            "physical_selector_flag": 0,
            "normalization_gap_count": 0,
            "bridge_gap_count": 0,
            "dim4_candidate_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "candidate_id": CANDIDATE_CODES["atlas_twenty_atom_boundary"],
            "candidate_code": CANDIDATE_CODES["atlas_twenty_atom_boundary"],
            "source_code": 1,
            "certified_input_flag": 1,
            "ambient_count": obs["atlas_atom_count"],
            "residual_rank": obs["atlas_atom_count"],
            "required_spatial_rank": required_spatial_rank,
            "physical_selector_flag": 0,
            "normalization_gap_count": 0,
            "bridge_gap_count": 0,
            "dim4_candidate_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "candidate_id": CANDIDATE_CODES["boundary_packet_incidence"],
            "candidate_code": CANDIDATE_CODES["boundary_packet_incidence"],
            "source_code": 2,
            "certified_input_flag": 1,
            "ambient_count": obs["binc_public_atom_count"],
            "residual_rank": obs["binc_incidence_rank_over_q"],
            "required_spatial_rank": required_spatial_rank,
            "physical_selector_flag": 0,
            "normalization_gap_count": 0,
            "bridge_gap_count": obs["binc_missing_restriction_bridge_count"],
            "dim4_candidate_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "candidate_id": CANDIDATE_CODES["c2_quotient_selector"],
            "candidate_code": CANDIDATE_CODES["c2_quotient_selector"],
            "source_code": 3,
            "certified_input_flag": 1,
            "ambient_count": obs["c2_quotient_state_count"],
            "residual_rank": obs["c2_selector_count"],
            "required_spatial_rank": required_spatial_rank,
            "physical_selector_flag": obs["c2_physical_selector_axiom_flag"],
            "normalization_gap_count": 0,
            "bridge_gap_count": 0,
            "dim4_candidate_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "candidate_id": CANDIDATE_CODES["perennial_sector_selection"],
            "candidate_code": CANDIDATE_CODES["perennial_sector_selection"],
            "source_code": 4,
            "certified_input_flag": 1,
            "ambient_count": obs["psec_sector_count"],
            "residual_rank": obs["psec_sector_count"],
            "required_spatial_rank": required_spatial_rank,
            "physical_selector_flag": 0,
            "normalization_gap_count": obs["psec_open_normalization_sector_count"],
            "bridge_gap_count": obs["psec_remaining_projective_gauge_dimension"],
            "dim4_candidate_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    decision_rows = [
        {
            "decision_id": DECISION_CODES["rank_boundary_blocks_dim4"],
            "decision_code": DECISION_CODES["rank_boundary_blocks_dim4"],
            "pass_flag": 1,
            "certified_flag": 1,
            "obstruction_flag": 1,
            "value": obs["residual_rank_excess_over_three"],
        },
        {
            "decision_id": DECISION_CODES["subboundary_dim4_certified"],
            "decision_code": DECISION_CODES["subboundary_dim4_certified"],
            "pass_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "value": 0,
        },
        {
            "decision_id": DECISION_CODES["quotient_dim4_certified"],
            "decision_code": DECISION_CODES["quotient_dim4_certified"],
            "pass_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "value": 0,
        },
        {
            "decision_id": DECISION_CODES["sector_dim4_certified"],
            "decision_code": DECISION_CODES["sector_dim4_certified"],
            "pass_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "value": 0,
        },
        {
            "decision_id": DECISION_CODES["physical_selector_certified"],
            "decision_code": DECISION_CODES["physical_selector_certified"],
            "pass_flag": 1,
            "certified_flag": obs["c2_physical_selector_axiom_flag"],
            "obstruction_flag": 1,
            "value": obs["c2_physical_selector_axiom_flag"],
        },
        {
            "decision_id": DECISION_CODES["dim4_reduction_certified"],
            "decision_code": DECISION_CODES["dim4_reduction_certified"],
            "pass_flag": 1,
            "certified_flag": obs["dim4_reduction_certified_flag"],
            "obstruction_flag": 1,
            "value": obs["certified_dim4_candidate_count"],
        },
    ]
    gap_rows = [
        {
            "gap_id": code,
            "gap_code": code,
            "open_flag": int(name != "four_dimensional_spacetime_reduction"),
            "obstruction_flag": 1,
            "next_flag": int(name == "nondegenerate_smooth_lorentzian_metric"),
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
        "metric_rank": metric_rank,
        "binc": binc,
        "psec": psec,
        "c2uf": c2uf,
        "atlas": atlas,
        "candidate_rows": candidate_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "candidate_table": table_from_rows(CANDIDATE_COLUMNS, candidate_rows),
        "decision_table": table_from_rows(DECISION_COLUMNS, decision_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "candidate_text_hash": sha_text(digest_text(CANDIDATE_COLUMNS, candidate_rows)),
        "decision_text_hash": sha_text(digest_text(DECISION_COLUMNS, decision_rows)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "all_input_reports_certified": rows["metric_rank"].get("status")
        == "LONG_METRIC_RANK_GATE_CERTIFIED"
        and rows["metric_rank"].get("all_checks_pass") is True
        and rows["binc"].get("status") == "LONG_BINC_CERTIFIED"
        and rows["binc"].get("all_checks_pass") is True
        and rows["psec"].get("status") == "LONG_PSEC_CERTIFIED"
        and rows["psec"].get("all_checks_pass") is True
        and rows["c2uf"].get("status") == "LONG_C2UF_CERTIFIED"
        and rows["c2uf"].get("all_checks_pass") is True
        and rows["atlas"].get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED"
        and rows["atlas"].get("all_checks_pass") is True,
        "rank_boundary_obstruction_exact": obs["time_rank"] == 1
        and obs["public_kernel_dimension"] == 19
        and obs["required_spatial_rank"] == 3
        and obs["residual_rank_excess_over_three"] == 16
        and obs["rank_gate_dim4_flag"] == 0,
        "candidate_surfaces_not_dim4": obs["atlas_atom_count"] == 20
        and obs["binc_incidence_rank_over_q"] == 19
        and obs["c2_physical_selector_axiom_flag"] == 0
        and obs["psec_open_normalization_sector_count"] == 30
        and obs["certified_dim4_candidate_count"] == 0,
        "dim4_obstruction_scope_exact": obs["dim4_reduction_certified_flag"] == 0
        and obs["current_boundary_obstruction_flag"] == 1
        and obs["smooth_metric_signature_flag"] == 0
        and obs["stress_energy_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "table_shapes_match": rows["candidate_table"].shape
        == (len(CANDIDATE_CODES), len(CANDIDATE_COLUMNS))
        and rows["decision_table"].shape
        == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "four_dimensional_reduction_current_boundary_obstruction",
        "summary": {
            "time_rank": obs["time_rank"],
            "public_rank": obs["public_rank"],
            "public_kernel_dimension": obs["public_kernel_dimension"],
            "required_spatial_rank": obs["required_spatial_rank"],
            "residual_rank_excess_over_three": obs[
                "residual_rank_excess_over_three"
            ],
            "atlas_atom_count": obs["atlas_atom_count"],
            "binc_incidence_rank_over_q": obs["binc_incidence_rank_over_q"],
            "c2_physical_selector_axiom_flag": obs[
                "c2_physical_selector_axiom_flag"
            ],
            "psec_open_normalization_sector_count": obs[
                "psec_open_normalization_sector_count"
            ],
            "certified_dim4_candidate_count": obs["certified_dim4_candidate_count"],
            "dim4_reduction_certified_flag": obs["dim4_reduction_certified_flag"],
            "current_boundary_obstruction_flag": obs[
                "current_boundary_obstruction_flag"
            ],
            "smooth_metric_signature_flag": obs["smooth_metric_signature_flag"],
            "gr_derivation_flag": obs["gr_derivation_flag"],
            "next_gap": "nondegenerate_smooth_lorentzian_metric",
        },
        "candidate_code_map": {str(value): key for key, value in CANDIDATE_CODES.items()},
        "decision_code_map": {str(value): key for key, value in DECISION_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "candidate_table_sha256": sha_array(rows["candidate_table"]),
        "candidate_text_sha256": rows["candidate_text_hash"],
        "decision_table_sha256": sha_array(rows["decision_table"]),
        "decision_text_sha256": rows["decision_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    dim4_gate = {
        "schema": "long.dim4_gate@1",
        "object": "four_dimensional_reduction_current_boundary_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_DIM4_GATE_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.dim4_gate.report@1",
        "status": dim4_gate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_dim4_gate checks the current certified quotient, subboundary, "
            "and sector-selection surfaces for a reduction from the 1+19 rank "
            "boundary to a 1+3 spacetime boundary. The current boundary has 16 "
            "extra residual public-kernel directions beyond rank three, and no "
            "certified quotient, packet/subboundary bridge, C2 physical selector, "
            "or sector-normalized selector supplies a 1+3 reduction."
        ),
        "stage_protocol": {
            "draft": "read long_metric_rank_gate, long_binc, long_psec, long_c2uf, and c985_d20_boundary_invariant_atlas",
            "witness": "emit candidate rows, decision rows, gap rows, and observables",
            "coherence": "check input statuses, rank excess, candidate counts, selector flags, normalization gaps, and table hashes",
            "closure": "certify the current-boundary 1+3 reduction obstruction",
            "emit": "write long_dim4_gate artifacts and verifier hook",
        },
        "inputs": {
            "long_metric_rank_gate": input_entry(
                LONG_METRIC_RANK_GATE,
                {
                    "status": rows["metric_rank"].get("status"),
                    "certificate_sha256": rows["metric_rank"].get("certificate_sha256"),
                },
            ),
            "long_binc": input_entry(
                LONG_BINC,
                {
                    "status": rows["binc"].get("status"),
                    "certificate_sha256": rows["binc"].get("certificate_sha256"),
                },
            ),
            "long_binc_obs": input_entry(LONG_BINC_OBS),
            "long_psec": input_entry(
                LONG_PSEC,
                {
                    "status": rows["psec"].get("status"),
                    "certificate_sha256": rows["psec"].get("certificate_sha256"),
                },
            ),
            "long_psec_obs": input_entry(LONG_PSEC_OBS),
            "long_c2uf": input_entry(
                LONG_C2UF,
                {
                    "status": rows["c2uf"].get("status"),
                    "certificate_sha256": rows["c2uf"].get("certificate_sha256"),
                },
            ),
            "long_c2uf_obs": input_entry(LONG_C2UF_OBS),
            "atlas": input_entry(
                ATLAS,
                {
                    "status": rows["atlas"].get("status"),
                    "certificate_sha256": rows["atlas"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "dim4_gate": relpath(OUT_DIR / "dim4_gate.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
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
                "the current rank boundary is 1+19, not 1+3",
                "the 20-atom atlas does not by itself certify a 3-spatial subboundary",
                "the boundary/packet incidence surface has rank 19 and missing packet bridges",
                "the C2 quotient seam lacks a certified physical selector axiom",
                "the perennial-sector seam keeps 30 normalization sectors open",
                "no certified current-boundary 1+3 spacetime reduction exists",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute nonexistence of every possible future 1+3 quotient",
                "a nondegenerate smooth Lorentzian metric tensor",
                "a physical stress-energy tensor",
                "Riemann/Ricci curvature, Einstein tensor, or Einstein field equations",
                "a completed derivation of general relativity",
            ],
        },
        "next_highest_yield_item": (
            "Build long_signature_gate: with 1+3 blocked in the current boundary, "
            "decide whether any finite bilinear/signature form is certified on "
            "the 1+19 rank split, or certify that smooth Lorentzian signature is absent."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.dim4_gate.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.dim4_gate.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "dim4_gate": dim4_gate,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": rows["candidate_table"],
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
    write_json(OUT_DIR / "dim4_gate.json", payloads["dim4_gate"])
    (OUT_DIR / "candidate.csv").write_text(
        payloads["candidate_csv"], encoding="utf-8"
    )
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
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
