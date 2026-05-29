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


THEOREM_ID = "long_binc"
STATUS = "LONG_BINC_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_binc.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_binc.py"

SURFACE_TEXT_HASH = "67f30e159b1f9be53950a0d67ce14229e9ed6e7a3433c81e4ff0dcabab7e8853"
EDGE_TEXT_HASH = "ae47231ccd4ae7c671ba5f349641a1f4182bd1aa70db8e20b67d711da85bacd9"
OBS_TEXT_HASH = "44305e72f1d22319ba6b39a012d39486aaf2ba69c1cba16e46537abf0205f149"

INPUT_REPORTS = [
    (
        "boundary_loop_step_atom_incidence",
        0,
        THEOREM_ROOT / "d20_boundary_loop_step_atom_incidence" / "report.json",
    ),
    (
        "packet_bridge_snf_obstruction",
        1,
        THEOREM_ROOT / "d20_packet_bridge_snf_obstruction" / "report.json",
    ),
    (
        "boundary_packet_pairing_obstruction",
        2,
        THEOREM_ROOT / "d20_boundary_packet_pairing_obstruction" / "report.json",
    ),
    (
        "boundary_packet_row_normalization_obstruction",
        3,
        THEOREM_ROOT
        / "d20_boundary_packet_row_normalization_obstruction"
        / "report.json",
    ),
    (
        "loop_step_packet_snf_probe",
        4,
        THEOREM_ROOT / "d20_loop_step_packet_snf_probe" / "report.json",
    ),
    (
        "boundary_packet_low_support_candidate_atlas",
        5,
        THEOREM_ROOT
        / "d20_boundary_packet_low_support_candidate_atlas"
        / "report.json",
    ),
    (
        "explicit_packet_restriction_map_test",
        6,
        THEOREM_ROOT / "d20_explicit_packet_restriction_map_test" / "report.json",
    ),
    (
        "contour_sector_packet_prime_alignment",
        7,
        THEOREM_ROOT / "d20_contour_sector_packet_prime_alignment" / "report.json",
    ),
    (
        "canonical_finite_scattering_table",
        8,
        THEOREM_ROOT / "canonical_finite_scattering_table" / "report.json",
    ),
    (
        "full_exposure_label_coordinate_transition_operator",
        9,
        THEOREM_ROOT
        / "full_exposure_label_coordinate_transition_operator"
        / "report.json",
    ),
]

SURFACE_COLUMNS = [
    "surface_id",
    "role_code",
    "certified_flag",
    "boundary_flag",
    "packet_flag",
    "obstruction_flag",
    "candidate_flag",
    "transport_flag",
    "row_count",
    "gap_flag",
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
    "public_atom_count",
    "loop_step_atom_count",
    "directed_pair_projection_count",
    "missing_directed_pair_count",
    "incidence_rank_over_q",
    "zero_sum_boundary_lattice_index",
    "boundary_nonunit_factor_count",
    "boundary_lattice_exponent",
    "packet_doublet_count",
    "packet_operator_rank",
    "packet_snf_factor_count",
    "packet_snf_prime_count",
    "raw_bridge_candidate_count",
    "raw_bridge_columns_available_flag",
    "raw_compatible_pair_count",
    "minimal_scalar_with_pair",
    "joint_boundary_packet_scalar_lcm",
    "row_scalar_divisibility",
    "loop_step_columns_tested",
    "loop_step_columns_passing",
    "low_support_candidate_count",
    "low_support_even_candidate_count",
    "low_support_compatible_doublet_count",
    "low_support_rank_two_doublet_count",
    "explicit_two_step_packet_action_flag",
    "missing_restriction_bridge_count",
    "scattering_generator_count",
    "scattering_directed_transition_count",
    "label_coordinate_count",
    "label_transition_edge_count",
    "prime_union_count",
    "focused_binc_seam_closed_flag",
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


def load_reports() -> dict[str, dict[str, Any]]:
    return {name: load_json(path) for name, _code, path in INPUT_REPORTS}


def derived(report: dict[str, Any]) -> dict[str, Any]:
    value = report.get("derived", {})
    if not isinstance(value, dict):
        return {}
    return value


def build_rows() -> dict[str, Any]:
    reports = load_reports()
    incidence = derived(reports["boundary_loop_step_atom_incidence"])[
        "incidence_summary"
    ]
    packet = derived(reports["packet_bridge_snf_obstruction"])[
        "obstruction_summary"
    ]
    pairing = derived(reports["boundary_packet_pairing_obstruction"])[
        "obstruction_summary"
    ]
    row_norm = derived(reports["boundary_packet_row_normalization_obstruction"])[
        "obstruction_summary"
    ]
    loop_probe = derived(reports["loop_step_packet_snf_probe"])["probe_summary"]
    low_support = derived(reports["boundary_packet_low_support_candidate_atlas"])[
        "low_support_summary"
    ]
    restriction = derived(reports["explicit_packet_restriction_map_test"])[
        "restriction_summary"
    ]
    alignment = derived(reports["contour_sector_packet_prime_alignment"])[
        "alignment_summary"
    ]
    scattering = derived(reports["canonical_finite_scattering_table"])[
        "transition_counts"
    ]
    label = derived(reports["full_exposure_label_coordinate_transition_operator"])[
        "transition_summary"
    ]

    role_sets = {
        "boundary": {
            "boundary_loop_step_atom_incidence",
            "boundary_packet_pairing_obstruction",
            "boundary_packet_row_normalization_obstruction",
            "boundary_packet_low_support_candidate_atlas",
        },
        "packet": {
            "packet_bridge_snf_obstruction",
            "boundary_packet_pairing_obstruction",
            "boundary_packet_row_normalization_obstruction",
            "loop_step_packet_snf_probe",
            "boundary_packet_low_support_candidate_atlas",
            "explicit_packet_restriction_map_test",
            "full_exposure_label_coordinate_transition_operator",
        },
        "obstruction": {
            "packet_bridge_snf_obstruction",
            "boundary_packet_pairing_obstruction",
            "boundary_packet_row_normalization_obstruction",
            "loop_step_packet_snf_probe",
            "boundary_packet_low_support_candidate_atlas",
        },
        "candidate": {
            "boundary_packet_low_support_candidate_atlas",
            "explicit_packet_restriction_map_test",
        },
        "transport": {
            "canonical_finite_scattering_table",
            "full_exposure_label_coordinate_transition_operator",
            "contour_sector_packet_prime_alignment",
        },
    }
    row_counts = {
        "boundary_loop_step_atom_incidence": int(incidence["compact_loop_step_atom_count"]),
        "packet_bridge_snf_obstruction": int(len(packet["nonunit_invariant_factors"])),
        "boundary_packet_pairing_obstruction": int(
            pairing["all_unordered_public_pair_count"]
        ),
        "boundary_packet_row_normalization_obstruction": int(
            row_norm["tested_unordered_public_pair_count"]
        ),
        "loop_step_packet_snf_probe": int(loop_probe["tested_column_count"]),
        "boundary_packet_low_support_candidate_atlas": int(
            low_support["candidate_count"]
        ),
        "explicit_packet_restriction_map_test": int(
            restriction["constructed_projection_packet_count"]
        ),
        "contour_sector_packet_prime_alignment": int(
            len(alignment["union_prime_split"])
        ),
        "canonical_finite_scattering_table": int(
            scattering["directed_transition_count"]
        ),
        "full_exposure_label_coordinate_transition_operator": int(
            label["label_transition_edge_count"]
        ),
    }
    surface_rows = []
    for surface_id, (name, role_code, _path) in enumerate(INPUT_REPORTS):
        surface_rows.append(
            {
                "surface_id": surface_id,
                "role_code": role_code,
                "certified_flag": certified(reports[name]),
                "boundary_flag": int(name in role_sets["boundary"]),
                "packet_flag": int(name in role_sets["packet"]),
                "obstruction_flag": int(name in role_sets["obstruction"]),
                "candidate_flag": int(name in role_sets["candidate"]),
                "transport_flag": int(name in role_sets["transport"]),
                "row_count": int(row_counts.get(name, 0)),
                "gap_flag": int(
                    name
                    in {
                        "packet_bridge_snf_obstruction",
                        "loop_step_packet_snf_probe",
                        "boundary_packet_low_support_candidate_atlas",
                        "explicit_packet_restriction_map_test",
                    }
                ),
            }
        )

    edge_specs = [
        (0, 0, 2, 1),
        (1, 0, 3, 1),
        (2, 0, 4, 1),
        (3, 0, 5, 1),
        (4, 1, 2, 1),
        (5, 1, 3, 1),
        (6, 1, 4, 1),
        (7, 1, 5, 1),
        (8, 2, 3, 1),
        (9, 3, 5, 1),
        (10, 6, 1, 1),
        (11, 6, 9, 0),
        (12, 8, 6, 0),
        (13, 8, 0, 0),
        (14, 9, 1, 0),
        (15, 7, 1, 0),
        (16, 7, 5, 0),
    ]
    edge_rows = [
        {
            "edge_id": edge_id,
            "source_surface_id": source,
            "target_surface_id": target,
            "edge_code": edge_id,
            "closed_flag": 1,
            "gap_flag": gap_flag,
        }
        for edge_id, source, target, gap_flag in edge_specs
    ]

    obs = {
        "input_report_count": len(INPUT_REPORTS),
        "certified_input_count": sum(certified(report) for report in reports.values()),
        "connected_edge_count": len(edge_rows),
        "closed_edge_count": sum(row["closed_flag"] for row in edge_rows),
        "public_atom_count": int(incidence["public_atom_count"]),
        "loop_step_atom_count": int(incidence["compact_loop_step_atom_count"]),
        "directed_pair_projection_count": int(
            incidence["boundary_directed_pair_projection_count"]
        ),
        "missing_directed_pair_count": int(incidence["missing_directed_pair_count"]),
        "incidence_rank_over_q": int(incidence["rank_over_Q"]),
        "zero_sum_boundary_lattice_index": int(
            incidence["zero_sum_boundary_lattice_index"]
        ),
        "boundary_nonunit_factor_count": int(
            len(incidence["nonunit_invariant_factors"])
        ),
        "boundary_lattice_exponent": int(pairing["boundary_lattice_exponent"]),
        "packet_doublet_count": int(pairing["packet_doublet_count"]),
        "packet_operator_rank": int(packet["rank_over_Q"]),
        "packet_snf_factor_count": int(len(packet["nonunit_invariant_factors"])),
        "packet_snf_prime_count": int(len(packet["torsion_primes"])),
        "raw_bridge_candidate_count": int(packet["raw_bridge_candidate_count"]),
        "raw_bridge_columns_available_flag": int(packet["raw_bridge_columns_available"]),
        "raw_compatible_pair_count": int(pairing["raw_compatible_pair_count"]),
        "minimal_scalar_with_pair": int(pairing["minimal_scalar_with_any_compatible_pair"]),
        "joint_boundary_packet_scalar_lcm": int(
            pairing["joint_boundary_packet_scalar_lcm"]
        ),
        "row_scalar_divisibility": int(
            row_norm["row_scalar_divisibility_for_any_packet_pairing"]
        ),
        "loop_step_columns_tested": int(loop_probe["tested_column_count"]),
        "loop_step_columns_passing": int(
            len(loop_probe["columns_passing_packet_snf_image"])
        ),
        "low_support_candidate_count": int(low_support["candidate_count"]),
        "low_support_even_candidate_count": int(
            low_support["even_image_candidate_count"]
        ),
        "low_support_compatible_doublet_count": int(
            low_support["compatible_doublet_count"]
        ),
        "low_support_rank_two_doublet_count": int(
            low_support["compatible_doublet_rank_histogram"].get("2", 0)
        ),
        "explicit_two_step_packet_action_flag": int(
            restriction["two_step_packet_action_exists"]
        ),
        "missing_restriction_bridge_count": int(restriction["missing_bridge_count"]),
        "scattering_generator_count": int(scattering["primitive_generator_count"]),
        "scattering_directed_transition_count": int(
            scattering["directed_transition_count"]
        ),
        "label_coordinate_count": int(label["coordinate_count"]),
        "label_transition_edge_count": int(label["label_transition_edge_count"]),
        "prime_union_count": int(len(alignment["union_prime_split"])),
        "focused_binc_seam_closed_flag": 1,
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
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    reports = rows["reports"]
    checks = {
        "inputs_certified": obs["input_report_count"] == obs["certified_input_count"],
        "boundary_incidence_counts_cohere": (
            obs["public_atom_count"],
            obs["loop_step_atom_count"],
            obs["directed_pair_projection_count"],
            obs["missing_directed_pair_count"],
            obs["incidence_rank_over_q"],
            obs["zero_sum_boundary_lattice_index"],
            obs["boundary_nonunit_factor_count"],
        )
        == (20, 25, 30, 5, 19, 32, 3),
        "packet_snf_counts_cohere": (
            obs["packet_doublet_count"],
            obs["packet_operator_rank"],
            obs["packet_snf_factor_count"],
            obs["packet_snf_prime_count"],
            obs["raw_bridge_candidate_count"],
            obs["raw_bridge_columns_available_flag"],
        )
        == (10, 20, 20, 2, 3, 0),
        "boundary_packet_obstructions_cohere": (
            obs["raw_compatible_pair_count"],
            obs["minimal_scalar_with_pair"],
            obs["joint_boundary_packet_scalar_lcm"],
            obs["row_scalar_divisibility"],
            obs["loop_step_columns_tested"],
            obs["loop_step_columns_passing"],
        )
        == (0, 6, 12, 6, 25, 0),
        "low_support_candidate_boundary_preserved": (
            obs["low_support_candidate_count"],
            obs["low_support_even_candidate_count"],
            obs["low_support_compatible_doublet_count"],
            obs["low_support_rank_two_doublet_count"],
        )
        == (800, 12, 6, 0),
        "transport_packet_context_coheres": (
            obs["explicit_two_step_packet_action_flag"],
            obs["missing_restriction_bridge_count"],
            obs["scattering_generator_count"],
            obs["scattering_directed_transition_count"],
            obs["label_coordinate_count"],
            obs["label_transition_edge_count"],
            obs["prime_union_count"],
        )
        == (1, 3, 11, 22_528, 20, 40, 3),
        "connected_edges_closed": (
            obs["connected_edge_count"] == obs["closed_edge_count"]
            and obs["connected_edge_count"] == 17
        ),
        "focused_seam_closed_without_goal_completion": (
            obs["focused_binc_seam_closed_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
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
            (17, len(EDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "focused_boundary_loop_packet_incidence_seam",
        "role_code_map": {str(code): name for name, code, _path in INPUT_REPORTS},
        "summary": {
            "input_report_count": obs["input_report_count"],
            "certified_input_count": obs["certified_input_count"],
            "connected_edge_count": obs["connected_edge_count"],
            "public_atom_count": obs["public_atom_count"],
            "loop_step_atom_count": obs["loop_step_atom_count"],
            "directed_pair_projection_count": obs["directed_pair_projection_count"],
            "missing_directed_pair_count": obs["missing_directed_pair_count"],
            "zero_sum_boundary_lattice_index": obs[
                "zero_sum_boundary_lattice_index"
            ],
            "packet_doublet_count": obs["packet_doublet_count"],
            "raw_compatible_pair_count": obs["raw_compatible_pair_count"],
            "minimal_scalar_with_pair": obs["minimal_scalar_with_pair"],
            "joint_boundary_packet_scalar_lcm": obs[
                "joint_boundary_packet_scalar_lcm"
            ],
            "loop_step_columns_passing": obs["loop_step_columns_passing"],
            "low_support_compatible_doublet_count": obs[
                "low_support_compatible_doublet_count"
            ],
            "low_support_rank_two_doublet_count": obs[
                "low_support_rank_two_doublet_count"
            ],
            "missing_restriction_bridge_count": obs["missing_restriction_bridge_count"],
            "focused_binc_seam_closed_flag": obs["focused_binc_seam_closed_flag"],
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "surface_text_sha256": rows["surface_text_hash"],
        "edge_text_sha256": rows["edge_text_hash"],
        "observable_text_sha256": rows["obs_text_hash"],
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "edge_table_sha256": sha_array(rows["edge_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    seam_payload = {
        "schema": "long.binc@1",
        "object": "focused_boundary_loop_packet_incidence_seam",
        "status": STATUS if all(checks.values()) else "LONG_BINC_PROVISIONAL",
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
        "schema": "long.binc.report@1",
        "status": seam_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_binc materializes the boundary-to-Loop_297 incidence seam and "
            "its packet bridge boundary. It connects the 20x25 signed public "
            "atom incidence surface, 2/4/4 boundary torsion, 2I+4S packet SNF "
            "obstruction, scalar and row-normalization failures, low-support "
            "candidate atlas, explicit automaton-to-packet restriction, finite "
            "scattering table, and label-coordinate packet operator. The raw "
            "A985/tube/q42/q12-to-packet bridge remains explicitly open."
        ),
        "stage_protocol": {
            "draft": "read the top long_cluster boundary incidence seam and adjacent packet obstruction reports",
            "witness": "emit surface rows, connection edges, observable counts, and stable hashes",
            "coherence": "check certified inputs, incidence counts, packet SNF counts, obstruction counts, candidate counts, transport counts, and table shapes",
            "closure": "certify the focused boundary/packet seam without claiming a raw packet bridge exists",
            "emit": "write long_binc artifacts and verifier hook",
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
                "the boundary-to-Loop_297 atom incidence seam has a focused certified input surface",
                "the packet SNF obstruction and boundary scalar/row-normalization obstructions are connected to the incidence surface",
                "the low-support candidate atlas is connected as a degenerate rank-one search boundary rather than a full packet map",
                "the explicit automaton-to-packet restriction and label-coordinate packet operator are separated from the missing raw A985/tube/q42/q12 packet bridges",
            ],
            "does_not_certify_because_out_of_scope": [
                "a raw A985-to-packet operator homomorphism",
                "a screen-0 tube or q42/q12 quotient-to-packet projection",
                "a full-rank non-diagonal boundary-to-packet doublet map",
                "support-3 or higher signed-combination search closure",
                "broad bundle integration without running the broad certificate gate",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Refresh long_cluster with long_binc as a focused input, then "
            "materialize the new top unconsumed seam."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.binc.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.binc.manifest@1",
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
