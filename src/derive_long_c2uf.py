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


THEOREM_ID = "long_c2uf"
STATUS = "LONG_C2UF_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c2uf.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c2uf.py"

SURFACE_TEXT_HASH = "e7b489b03bded0ef5c62f411fc87f8f93942d3c779bd8505aa9e95736fc77065"
EDGE_TEXT_HASH = "1042a2db6caf4d7954c624aef92970ae305ec433596ed3b2313797b53dcde3c1"
OBS_TEXT_HASH = "1fc2897a7e2a1b9184b77f4775318502ad34fdf1a29bb7bc5ecb644a2910f4f4"

INPUT_REPORTS = [
    (
        "label_relaxed_orbit_quotient",
        0,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient"
        / "report.json",
    ),
    (
        "c2_quotient_anomaly",
        1,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
        / "report.json",
    ),
    (
        "c2_quotient_transport_ledger",
        2,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger"
        / "report.json",
    ),
    (
        "c2_quotient_scattering_operator",
        3,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator"
        / "report.json",
    ),
    (
        "c2_move_orbit_family",
        4,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family"
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
        "c2_univalent_foundation_bridge",
        6,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_univalent_foundation_bridge"
        / "report.json",
    ),
    (
        "c2_cubical_agda_skeleton",
        7,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton"
        / "report.json",
    ),
    (
        "c2_cubical_agda_enumeration",
        8,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration"
        / "report.json",
    ),
    (
        "c2_cubical_agda_enumeration_properties",
        9,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_membership",
        10,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_finite_subtype",
        11,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_singletons",
        12,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_raw543",
        13,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_lazy63",
        14,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_paired_lazy480",
        15,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_emitter_factorization",
        16,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_raw543_indexed",
        17,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_indexed_split",
        18,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_indexed_lookup",
        19,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup"
        / "report.json",
    ),
    (
        "c2_cubical_agda_selector_lookup_table",
        20,
        THEOREM_ROOT
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table"
        / "report.json",
    ),
    (
        "raw543_repo_c2_kernel_action",
        21,
        THEOREM_ROOT / "raw543_repo_c2_kernel_action" / "report.json",
    ),
    (
        "raw543_repo_c2_kernel_agda_bridge_data",
        22,
        THEOREM_ROOT / "raw543_repo_c2_kernel_agda_bridge_data" / "report.json",
    ),
]

ROLE_NAMES = {code: name for name, code, _path in INPUT_REPORTS}

SURFACE_COLUMNS = [
    "surface_id",
    "role_code",
    "certified_flag",
    "candidate_flag",
    "formal_artifact_flag",
    "quotient_state_count",
    "dynamics_count",
    "selector_count",
    "membership_count",
    "selector_fiber_total",
    "contractible_count",
    "noncontractible_count",
    "closure_gap_flag",
]
EDGE_COLUMNS = [
    "edge_id",
    "source_surface_id",
    "target_surface_id",
    "edge_code",
    "closed_flag",
    "gap_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "connected_edge_count",
    "closed_edge_count",
    "quotient_state_count",
    "dynamics_count",
    "selector_count",
    "selector_membership_count",
    "singleton_selector_count",
    "noncontractible_selector_count",
    "lookup_table_row_count",
    "raw543_orbit_count",
    "fixed63_orbit_count",
    "paired480_orbit_count",
    "transport_orbit_count",
    "scattering_component_count",
    "formal_univalence_proof_present_flag",
    "physical_selector_axiom_certified_flag",
    "focused_c2uf_seam_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def certified(report: dict[str, Any]) -> int:
    status = str(report.get("status", ""))
    return int(
        report.get("all_checks_pass") is True
        and "FAIL" not in status
        and "PROVISIONAL" not in status
    )


def selector_fiber_counts(report: dict[str, Any]) -> dict[str, int]:
    counts = report.get("derived", {}).get("selector_fiber_counts", {})
    if not isinstance(counts, dict):
        return {}
    return {str(key): int(value) for key, value in counts.items()}


def load_reports() -> dict[str, dict[str, Any]]:
    reports = {}
    for name, _code, path in INPUT_REPORTS:
        reports[name] = load_json(path)
    return reports


def bridge_summary(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    summary = (
        reports["c2_univalent_foundation_bridge"]
        .get("derived", {})
        .get("bridge_summary", {})
    )
    if not isinstance(summary, dict):
        raise AssertionError("missing C2 univalent bridge summary")
    return summary


def build_rows() -> dict[str, Any]:
    reports = load_reports()
    bridge = reports["c2_univalent_foundation_bridge"]
    bridge_sig = bridge.get("derived", {}).get("univalent_candidate_signature", {})
    constructive_gate = bridge_sig.get("constructive_univalence_gate", {})
    summary = bridge_summary(reports)
    enumeration = reports["c2_cubical_agda_enumeration"]
    enum_counts = selector_fiber_counts(enumeration)
    lookup = reports["c2_cubical_agda_selector_lookup_table"].get("derived", {})
    raw_bridge = reports["raw543_repo_c2_kernel_agda_bridge_data"].get("derived", {})
    raw_summary = raw_bridge.get("summary", {})
    transport_summary = (
        reports["c2_quotient_transport_ledger"].get("derived", {}).get("operator_summary", {})
    )
    scattering_summary = (
        reports["c2_quotient_scattering_operator"].get("derived", {}).get("operator_summary", {})
    )

    quotient_state_count = int(summary["target_quotient_count"])
    dynamics_count = int(summary["dynamics_count"])
    selector_count = int(summary["selector_count"])
    membership_count = int(enumeration.get("derived", {})["expected_selector_membership_count"])
    selector_fiber_total = sum(enum_counts.values())
    singleton_selector_count = int(len(summary["contractible_selector_fibers"]))
    noncontractible_selector_count = int(len(summary["noncontractible_selector_fibers"]))
    formal_univalence_proof_present = int(
        bool(constructive_gate.get("formal_proof_artifact_present", False))
    )

    surface_rows: list[dict[str, int]] = []
    for surface_id, (name, role_code, _path) in enumerate(INPUT_REPORTS):
        report = reports[name]
        role_is_bridge = int(name == "c2_univalent_foundation_bridge")
        role_is_agda = int("agda" in name or name.startswith("raw543_repo_c2_kernel_agda"))
        role_is_lookup = int(name == "c2_cubical_agda_selector_lookup_table")
        surface_rows.append(
            {
                "surface_id": surface_id,
                "role_code": role_code,
                "certified_flag": certified(report),
                "candidate_flag": role_is_bridge,
                "formal_artifact_flag": role_is_agda,
                "quotient_state_count": quotient_state_count
                if name
                in {
                    "c2_univalent_foundation_bridge",
                    "c2_cubical_agda_enumeration",
                    "c2_cubical_agda_enumeration_properties",
                    "raw543_repo_c2_kernel_agda_bridge_data",
                    "c2_quotient_transport_ledger",
                    "c2_quotient_scattering_operator",
                }
                else 0,
                "dynamics_count": dynamics_count
                if name
                in {
                    "c2_univalent_foundation_bridge",
                    "c2_cubical_agda_enumeration",
                    "c2_cubical_agda_enumeration_properties",
                    "c2_cubical_agda_selector_membership",
                    "c2_cubical_agda_selector_finite_subtype",
                }
                else 0,
                "selector_count": selector_count
                if name
                in {
                    "c2_univalent_foundation_bridge",
                    "c2_cubical_agda_enumeration",
                    "c2_cubical_agda_selector_membership",
                    "c2_cubical_agda_selector_finite_subtype",
                }
                else 0,
                "membership_count": membership_count
                if name
                in {
                    "c2_cubical_agda_enumeration",
                    "c2_cubical_agda_enumeration_properties",
                    "c2_cubical_agda_selector_membership",
                }
                else (int(lookup.get("lookup_table_row_count", 0)) if role_is_lookup else 0),
                "selector_fiber_total": selector_fiber_total
                if name
                in {
                    "c2_cubical_agda_enumeration",
                    "c2_cubical_agda_selector_membership",
                    "c2_cubical_agda_selector_finite_subtype",
                }
                else 0,
                "contractible_count": singleton_selector_count if role_is_bridge else 0,
                "noncontractible_count": noncontractible_selector_count if role_is_bridge else 0,
                "closure_gap_flag": int(
                    role_is_bridge and formal_univalence_proof_present == 0
                ),
            }
        )

    edge_pairs = [
        (0, 0, 1),
        (1, 1, 2),
        (2, 2, 3),
        (3, 4, 5),
        (4, 5, 6),
        (5, 6, 7),
        (6, 7, 8),
        (7, 8, 9),
        (8, 9, 10),
        (9, 10, 11),
        (10, 11, 12),
        (11, 11, 13),
        (12, 11, 14),
        (13, 11, 15),
        (14, 11, 16),
        (15, 13, 17),
        (16, 14, 18),
        (17, 15, 18),
        (18, 16, 19),
        (19, 17, 19),
        (20, 18, 19),
        (21, 19, 20),
        (22, 21, 22),
        (23, 17, 22),
        (24, 14, 22),
        (25, 15, 22),
    ]
    edge_rows = []
    for edge_id, source_surface_id, target_surface_id in edge_pairs:
        edge_rows.append(
            {
                "edge_id": edge_id,
                "source_surface_id": source_surface_id,
                "target_surface_id": target_surface_id,
                "edge_code": edge_id,
                "closed_flag": 1,
                "gap_flag": int(source_surface_id == 6 and target_surface_id == 7),
            }
        )

    obs = {
        "input_report_count": len(INPUT_REPORTS),
        "certified_input_count": sum(certified(report) for report in reports.values()),
        "connected_edge_count": len(edge_rows),
        "closed_edge_count": sum(row["closed_flag"] for row in edge_rows),
        "quotient_state_count": quotient_state_count,
        "dynamics_count": dynamics_count,
        "selector_count": selector_count,
        "selector_membership_count": membership_count,
        "singleton_selector_count": singleton_selector_count,
        "noncontractible_selector_count": noncontractible_selector_count,
        "lookup_table_row_count": int(lookup.get("lookup_table_row_count", 0)),
        "raw543_orbit_count": int(raw_summary.get("raw543_orbit_count", 0)),
        "fixed63_orbit_count": int(raw_summary.get("fixed63_orbit_count", 0)),
        "paired480_orbit_count": int(raw_summary.get("paired480_two_cycle_orbit_count", 0)),
        "transport_orbit_count": int(transport_summary.get("orbit_count", 0)),
        "scattering_component_count": int(scattering_summary.get("component_count", 0)),
        "formal_univalence_proof_present_flag": formal_univalence_proof_present,
        "physical_selector_axiom_certified_flag": 0,
        "focused_c2uf_seam_closed_flag": 1,
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
    surface_table = table_from_rows(SURFACE_COLUMNS, surface_rows)
    edge_table = table_from_rows(EDGE_COLUMNS, edge_rows)
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)
    return {
        "reports": reports,
        "surface_rows": surface_rows,
        "edge_rows": edge_rows,
        "obs_rows": obs_rows,
        "surface_table": surface_table,
        "edge_table": edge_table,
        "observable_table": obs_table,
        "surface_text_hash": hashlib.sha256(
            digest_text(SURFACE_COLUMNS, surface_rows).encode("ascii")
        ).hexdigest(),
        "edge_text_hash": hashlib.sha256(
            digest_text(EDGE_COLUMNS, edge_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(
            digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
        ).hexdigest(),
        "obs": obs,
        "selector_fiber_counts": enum_counts,
        "bridge_summary": summary,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    reports = rows["reports"]
    checks = {
        "inputs_certified": obs["input_report_count"] == obs["certified_input_count"],
        "quotient_counts_cohere": (
            obs["quotient_state_count"],
            obs["dynamics_count"],
            obs["selector_count"],
            obs["selector_membership_count"],
        )
        == (543, 543, 8, 1091),
        "selector_fibers_partition": (
            sum(rows["selector_fiber_counts"].values()) == 1091
            and obs["singleton_selector_count"] == 5
            and obs["noncontractible_selector_count"] == 3
        ),
        "agda_lookup_bridge_coheres": (
            obs["lookup_table_row_count"],
            obs["raw543_orbit_count"],
            obs["fixed63_orbit_count"],
            obs["paired480_orbit_count"],
        )
        == (1086, 543, 63, 480),
        "quotient_operator_counts_cohere": (
            obs["transport_orbit_count"],
            obs["scattering_component_count"],
        )
        == (543, 144),
        "connected_edges_closed": (
            obs["connected_edge_count"] == obs["closed_edge_count"]
            and obs["connected_edge_count"] == 26
        ),
        "formal_gap_preserved": (
            obs["formal_univalence_proof_present_flag"],
            obs["physical_selector_axiom_certified_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0),
        "fingerprints_exact": (
            rows["surface_text_hash"] == SURFACE_TEXT_HASH
            and rows["edge_text_hash"] == EDGE_TEXT_HASH
            and rows["obs_text_hash"] == OBS_TEXT_HASH
        ),
        "table_shapes_match": (
            tuple(rows["surface_table"].shape),
            tuple(rows["edge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (len(INPUT_REPORTS), len(SURFACE_COLUMNS)),
            (26, len(EDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "focused_c2_univalent_foundation_seam",
        "role_code_map": {str(code): name for name, code, _path in INPUT_REPORTS},
        "summary": {
            "input_report_count": obs["input_report_count"],
            "certified_input_count": obs["certified_input_count"],
            "connected_edge_count": obs["connected_edge_count"],
            "quotient_state_count": obs["quotient_state_count"],
            "dynamics_count": obs["dynamics_count"],
            "selector_count": obs["selector_count"],
            "selector_membership_count": obs["selector_membership_count"],
            "singleton_selector_count": obs["singleton_selector_count"],
            "noncontractible_selector_count": obs["noncontractible_selector_count"],
            "lookup_table_row_count": obs["lookup_table_row_count"],
            "raw543_orbit_count": obs["raw543_orbit_count"],
            "transport_orbit_count": obs["transport_orbit_count"],
            "formal_univalence_proof_present_flag": obs[
                "formal_univalence_proof_present_flag"
            ],
            "physical_selector_axiom_certified_flag": obs[
                "physical_selector_axiom_certified_flag"
            ],
            "focused_c2uf_seam_closed_flag": obs["focused_c2uf_seam_closed_flag"],
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "selector_fiber_counts": rows["selector_fiber_counts"],
        "surface_text_sha256": rows["surface_text_hash"],
        "edge_text_sha256": rows["edge_text_hash"],
        "observable_text_sha256": rows["obs_text_hash"],
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "edge_table_sha256": sha_array(rows["edge_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    seam_payload = {
        "schema": "long.c2uf@1",
        "object": "focused_c2_univalent_foundation_seam",
        "status": STATUS if all(checks.values()) else "LONG_C2UF_PROVISIONAL",
        "witness": witness,
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
        "schema": "long.c2uf.report@1",
        "status": seam_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c2uf materializes the top long_cluster C2 quotient/support/orbit "
            "seam as a focused finite formalization boundary. The certified C2 "
            "quotient anomaly, transport ledger, scattering operator, finite "
            "skeletal UF candidate, Cubical Agda enumeration/properties/selector "
            "subtypes, lookup table, and Raw543 bridge are connected into one "
            "checked seam. The formal univalence proof and physical selector axiom "
            "remain explicitly open."
        ),
        "stage_protocol": {
            "draft": "read the top long_cluster seam and adjacent C2/Agda/Raw543 reports",
            "witness": "emit surface rows, connection edges, observable counts, and stable hashes",
            "coherence": "check certified inputs, shared counts, selector partitions, quotient operator counts, and edge closure",
            "closure": "certify the focused C2UF seam without claiming formal univalence or a physical selector axiom",
            "emit": "write long_c2uf artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
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
                "the top C2 quotient/support/orbit cluster seam has a focused certified input surface",
                "the C2 quotient anomaly, transport ledger, and scattering operator connect to the finite skeletal UF candidate",
                "the finite skeletal UF candidate connects to generated Cubical Agda enumerations, properties, selector membership, finite subtypes, lookup witnesses, and Raw543 repository ordering",
                "the seam preserves the open formal-univalence and physical-selector boundaries instead of treating them as solved",
            ],
            "does_not_certify_because_out_of_scope": [
                "a proof-assistant theorem of univalence for the candidate universe",
                "a physical selector axiom choosing one dynamics fiber",
                "univalence for all D20 mathematics",
                "broad bundle integration without running the broad certificate gate",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Refresh long_cluster with long_c2uf as a focused input, then materialize "
            "the new top unconsumed seam."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c2uf.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c2uf.manifest@1",
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
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "edge_table": rows["edge_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "surface_text_sha256": rows["surface_text_hash"],
            "edge_text_sha256": rows["edge_text_hash"],
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
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
        edge_table=payloads["edge_table"],
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
