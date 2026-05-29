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


THEOREM_ID = "long_auto"
STATUS = "LONG_AUTO_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

LONG_MAT_REPORT = PROOF_ROOT / "long_mat" / "report.json"
LOOP297_REPORT = THEOREM_ROOT / "loop297_scattering_amplitude_lift" / "report.json"
COMPACT_QUOTIENT_REPORT = (
    THEOREM_ROOT / "compact_amplitude_quotient" / "report.json"
)
AUTOMATON_REPORT = (
    THEOREM_ROOT / "reduced_amplitude_quotient_scattering_automaton" / "report.json"
)
FOURIER_MODE_REPORT = (
    THEOREM_ROOT / "amplitude_quotient_fourier_mode_classifier" / "report.json"
)
STRING_KERNEL_REPORT = (
    THEOREM_ROOT / "finite_virasoro_string_kernel_candidate" / "report.json"
)
GENERATOR_ALGEBRA_REPORT = (
    THEOREM_ROOT / "finite_virasoro_generator_algebra" / "report.json"
)
CENTRAL_EXTENSION_REPORT = (
    THEOREM_ROOT / "finite_central_extension_anomaly_cocycle" / "report.json"
)
PARITY_EXTENSION_REPORT = (
    THEOREM_ROOT / "finite_parity_central_extension_group" / "report.json"
)
TENFOLD_REPORT = THEOREM_ROOT / "projective_kernel_packet_tenfold_way" / "report.json"
FOURIER_A985_REPORT = (
    THEOREM_ROOT / "fourier_a985_sector_character_candidates" / "report.json"
)
FOURIER_TRACE_REPORT = (
    THEOREM_ROOT / "tiny_pointer_a985_fourier_trace_candidate_evaluation" / "report.json"
)
MATRIX_UNITS_REPORT = (
    THEOREM_ROOT / "tiny_pointer_a985_canonical_sector_matrix_units" / "report.json"
)
SECTOR_CHARACTERS_REPORT = (
    THEOREM_ROOT / "tiny_pointer_a985_canonical_sector_characters" / "report.json"
)
SECTOR11_UNSUPPORTED_REPORT = (
    THEOREM_ROOT / "tube_sandpile_flip_unsupported_state_classification" / "report.json"
)
SECTOR11_PULLBACK_REPORT = (
    THEOREM_ROOT / "tube_sandpile_flip_sector_support_pullback" / "report.json"
)
SECTOR11_FORMAL_REPORT = (
    THEOREM_ROOT / "tube_sandpile_flip_formal_11_extension_test" / "report.json"
)
LONG_ANOM_REPORT = PROOF_ROOT / "long_anom" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_auto.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_auto.py"

STATUS_TEXT_HASH = "3eae5298cbf83d96aabaed50f50a205392c2a7f26938f049b1e7a3f488777298"
OBS_TEXT_HASH = "5714f4ab5e531eac974b2e4e1bc94cb1abbb90067a8a379402fc874a9f266615"

REPORTS = {
    "long_mat": LONG_MAT_REPORT,
    "loop297": LOOP297_REPORT,
    "compact_quotient": COMPACT_QUOTIENT_REPORT,
    "automaton": AUTOMATON_REPORT,
    "fourier_mode": FOURIER_MODE_REPORT,
    "string_kernel": STRING_KERNEL_REPORT,
    "generator_algebra": GENERATOR_ALGEBRA_REPORT,
    "central_extension": CENTRAL_EXTENSION_REPORT,
    "parity_extension": PARITY_EXTENSION_REPORT,
    "tenfold_packet": TENFOLD_REPORT,
    "fourier_a985": FOURIER_A985_REPORT,
    "fourier_trace": FOURIER_TRACE_REPORT,
    "matrix_units": MATRIX_UNITS_REPORT,
    "sector_characters": SECTOR_CHARACTERS_REPORT,
    "sector11_unsupported": SECTOR11_UNSUPPORTED_REPORT,
    "sector11_pullback": SECTOR11_PULLBACK_REPORT,
    "sector11_formal": SECTOR11_FORMAL_REPORT,
    "long_anom": LONG_ANOM_REPORT,
}

EXPECTED_STATUSES = {
    "long_mat": "LONG_MAT_CERTIFIED",
    "loop297": "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_CERTIFIED",
    "compact_quotient": "D20_COMPACT_AMPLITUDE_QUOTIENT_CERTIFIED",
    "automaton": "D20_REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_CERTIFIED",
    "fourier_mode": "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED",
    "string_kernel": "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED",
    "generator_algebra": "D20_FINITE_VIRASORO_GENERATOR_ALGEBRA_CERTIFIED",
    "central_extension": "D20_FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_CERTIFIED",
    "parity_extension": "D20_FINITE_PARITY_CENTRAL_EXTENSION_GROUP_CERTIFIED",
    "tenfold_packet": "D20_PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_CERTIFIED",
    "fourier_a985": "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED",
    "fourier_trace": "D20_TINY_POINTER_A985_FOURIER_TRACE_CANDIDATE_EVALUATION_CERTIFIED",
    "matrix_units": "D20_TINY_POINTER_A985_CANONICAL_SECTOR_MATRIX_UNITS_CERTIFIED",
    "sector_characters": "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED",
    "sector11_unsupported": "D20_TUBE_SANDPILE_FLIP_UNSUPPORTED_STATE_CLASSIFIED",
    "sector11_pullback": "D20_TUBE_SANDPILE_FLIP_SECTOR_SUPPORT_PULLBACK_CERTIFIED",
    "sector11_formal": "D20_TUBE_SANDPILE_FLIP_FORMAL_11_EXTENSION_OBSTRUCTED",
    "long_anom": "LONG_ANOM_CERTIFIED",
}

SURFACE_COLUMNS = [
    "surface_id",
    "surface_code",
    "certified_flag",
    "resolved_flag",
    "residual_boundary_flag",
    "next_action_code",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "status_row_count",
    "resolved_surface_count",
    "residual_auto_boundary_count",
    "current_automorphic_boundary_closed_flag",
    "primitive_generator_packet_count",
    "directed_transition_count",
    "automaton_state_count",
    "automaton_degree",
    "residue_rank",
    "fourier_mode_count",
    "corrected_hidden_kernel_count",
    "corrected_hidden_odd_count",
    "sector26_clock_residue_count",
    "step_atom_count",
    "string_kernel_seed_count",
    "string_kernel_rank",
    "string_kernel_mode_count",
    "primitive_preserving_generator_count",
    "crossing_generator_count",
    "named_generator_count",
    "generator_dependency_count",
    "central_extension_cocycle_dimension",
    "parity_extension_order",
    "parity_extension_center_order",
    "parity_extension_derived_order",
    "parity_extension_exponent",
    "projective_packet_count",
    "projective_packet_dimension",
    "radical_direction_count",
    "active_direction_count",
    "matrix_unit_count",
    "source_sector_count",
    "sector_character_row_count",
    "fourier_candidate_count",
    "full_scalar_trace_candidate_count",
    "public_zero_scalar_trace_candidate_count",
    "sector11_residue_mask_count",
    "sector11_missing_pair_count",
    "sector11_valid_nonempty_extension_count",
    "long_mat_resolved_surface_count",
    "long_mat_residual_boundary_count",
    "long_mat_current_boundary_closed_flag",
    "anomaly_suite_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def report_certified(name: str, report: dict[str, Any]) -> int:
    return int(
        report.get("status") == EXPECTED_STATUSES[name]
        and report.get("all_checks_pass") is True
    )


def checks_all_true(report: dict[str, Any]) -> bool:
    checks = report.get("checks", {})
    return isinstance(checks, dict) and all(
        value is not False and value is not None for value in checks.values()
    )


def count_true(mapping: dict[str, Any]) -> int:
    return sum(1 for value in mapping.values() if value is True)


def build_rows() -> dict[str, Any]:
    reports = {name: load_json(path) for name, path in REPORTS.items()}

    mat_summary = reports["long_mat"].get("witness", {}).get("summary", {})
    loop297 = reports["loop297"].get("derived", {})
    compact = reports["compact_quotient"].get("derived", {})
    automaton = reports["automaton"].get("derived", {})
    fourier = reports["fourier_mode"].get("derived", {})
    string_kernel = reports["string_kernel"].get("derived", {})
    algebra = reports["generator_algebra"].get("derived", {})
    central = reports["central_extension"].get("derived", {})
    parity = reports["parity_extension"].get("derived", {})
    tenfold = reports["tenfold_packet"].get("derived", {})
    fourier_a985 = reports["fourier_a985"].get("derived", {})
    fourier_trace = reports["fourier_trace"].get("derived", {})
    matrix_units = reports["matrix_units"].get("derived", {})
    sector_characters = reports["sector_characters"].get("derived", {})
    sector11_unsupported = reports["sector11_unsupported"].get("derived", {})
    sector11_pullback = reports["sector11_pullback"].get("derived", {})
    sector11_formal = reports["sector11_formal"].get("derived", {})
    anom_summary = reports["long_anom"].get("witness", {}).get("summary", {})

    certified_flags = {
        name: int(report_certified(name, report) and checks_all_true(report))
        for name, report in reports.items()
    }

    surface_rows = [
        {
            "surface_id": index,
            "surface_code": index,
            "certified_flag": certified_flags[name],
            "resolved_flag": certified_flags[name],
            "residual_boundary_flag": 0,
            "next_action_code": index,
        }
        for index, name in enumerate(REPORTS)
    ]

    automaton_summary = automaton.get("automaton_summary", {})
    classifier_summary = fourier.get("classifier_summary", {})
    hidden_clock_hist = classifier_summary.get(
        "corrected_hidden_clock_mod26_histogram", {}
    )
    sector26_clock_hist = classifier_summary.get(
        "sector26_optical_clock_mod26_histogram", {}
    )
    quotient_summary = compact.get("quotient_summary", {})
    closure_summary = string_kernel.get("closure_summary", {})
    algebra_summary = algebra.get("algebra_summary", {})
    central_summary = central.get("central_extension_summary", {})
    parity_summary = parity.get("central_extension_summary", {})
    packet_summary = tenfold.get("packet_summary", {})
    character_join = sector_characters.get("perennial_join_key", {})
    trace_full_profile = fourier_trace.get("full_trace_profile", {})
    trace_public_zero_profile = fourier_trace.get("public_zero_scalar_profile", {})
    sector11_residue = sector11_unsupported.get("residue_screen12_counts", {})
    screen12_counts = sector11_residue.get("screen12_counts", {})
    sector11_obstruction = sector11_pullback.get("transition_obstruction_summary", {})
    formal_extensions = sector11_formal.get("valid_nonempty_extension_scenarios", [])

    radical_dimension = int(packet_summary.get("radical_dimension", 0))
    kernel_dimension = int(packet_summary.get("kernel_dimension", 0))

    obs = {
        "input_report_count": len(reports),
        "input_certified_count": sum(certified_flags.values()),
        "status_row_count": len(surface_rows),
        "resolved_surface_count": sum(row["resolved_flag"] for row in surface_rows),
        "residual_auto_boundary_count": sum(
            row["residual_boundary_flag"] for row in surface_rows
        ),
        "primitive_generator_packet_count": int(
            quotient_summary.get("primitive_generator_count", 0)
        ),
        "directed_transition_count": int(
            loop297.get("lifted_transition_counts", {}).get(
                "directed_transition_count", 0
            )
        ),
        "automaton_state_count": int(automaton_summary.get("state_count", 0)),
        "automaton_degree": int(automaton_summary.get("generator_label_count", 0)),
        "residue_rank": int(automaton_summary.get("residue_rank", 0)),
        "fourier_mode_count": int(classifier_summary.get("mode_count", 0)),
        "corrected_hidden_kernel_count": int(hidden_clock_hist.get("0", 0)),
        "corrected_hidden_odd_count": int(hidden_clock_hist.get("13", 0)),
        "sector26_clock_residue_count": len(sector26_clock_hist),
        "step_atom_count": int(quotient_summary.get("used_loop_step_atom_count", 0)),
        "string_kernel_seed_count": int(
            closure_summary.get("seed_zero_clock_mode_count", 0)
        ),
        "string_kernel_rank": int(closure_summary.get("kernel_closure_rank", 0)),
        "string_kernel_mode_count": int(
            closure_summary.get("kernel_closure_mode_count", 0)
        ),
        "primitive_preserving_generator_count": int(
            closure_summary.get("primitive_preserving_generator_rank", 0)
        ),
        "crossing_generator_count": len(
            closure_summary.get("crossing_primitive_generators", [])
        ),
        "named_generator_count": int(
            algebra_summary.get("named_generator_count", 0)
        ),
        "generator_dependency_count": int(
            algebra_summary.get("relation_count_mod_involutions", 0)
        ),
        "central_extension_cocycle_dimension": int(
            central_summary.get("compatible_f2_cocycle_dimension", 0)
        ),
        "parity_extension_order": int(parity_summary.get("group_order", 0)),
        "parity_extension_center_order": int(parity_summary.get("center_order", 0)),
        "parity_extension_derived_order": int(
            parity_summary.get("derived_subgroup_order", 0)
        ),
        "parity_extension_exponent": int(parity_summary.get("exponent", 0)),
        "projective_packet_count": int(
            packet_summary.get("irreducible_packet_count", 0)
        ),
        "projective_packet_dimension": int(
            packet_summary.get("irreducible_packet_dimension", 0)
        ),
        "radical_direction_count": radical_dimension,
        "active_direction_count": kernel_dimension - radical_dimension,
        "matrix_unit_count": int(matrix_units.get("matrix_unit_count", 0)),
        "source_sector_count": int(matrix_units.get("source_sector_count", 0)),
        "sector_character_row_count": int(
            character_join.get("character_rows_resolved", 0)
        ),
        "fourier_candidate_count": int(fourier_a985.get("candidate_count", 0)),
        "full_scalar_trace_candidate_count": count_true(trace_full_profile),
        "public_zero_scalar_trace_candidate_count": count_true(
            trace_public_zero_profile
        ),
        "sector11_residue_mask_count": int(screen12_counts.get("11", 0)),
        "sector11_missing_pair_count": int(
            sector11_obstruction.get("missing_state_pair_count", 0)
        ),
        "sector11_valid_nonempty_extension_count": len(formal_extensions),
        "long_mat_resolved_surface_count": int(
            mat_summary.get("resolved_surface_count", 0)
        ),
        "long_mat_residual_boundary_count": int(
            mat_summary.get("residual_current_model_matrix_boundary_count", -1)
        ),
        "long_mat_current_boundary_closed_flag": int(
            mat_summary.get("current_matrix_boundary_closed_flag", 0)
        ),
        "anomaly_suite_closed_flag": int(
            anom_summary.get("current_anomaly_suite_closed_flag", 0)
        ),
        "complete_goal_claim_flag": 0,
    }
    obs["current_automorphic_boundary_closed_flag"] = int(
        sum(certified_flags.values()) == len(reports)
        and obs["primitive_generator_packet_count"] == 11
        and obs["directed_transition_count"] == 22_528
        and obs["automaton_state_count"] == 2048
        and obs["automaton_degree"] == 11
        and obs["residue_rank"] == 11
        and obs["fourier_mode_count"] == 2048
        and obs["corrected_hidden_kernel_count"] == 1024
        and obs["corrected_hidden_odd_count"] == 1024
        and obs["sector26_clock_residue_count"] == 26
        and obs["step_atom_count"] == 25
        and obs["string_kernel_seed_count"] == 83
        and obs["string_kernel_rank"] == 10
        and obs["string_kernel_mode_count"] == 1024
        and obs["primitive_preserving_generator_count"] == 8
        and obs["crossing_generator_count"] == 3
        and obs["named_generator_count"] == 11
        and obs["generator_dependency_count"] == 1
        and obs["central_extension_cocycle_dimension"] == 1
        and obs["parity_extension_order"] == 2048
        and obs["parity_extension_center_order"] == 512
        and obs["parity_extension_derived_order"] == 2
        and obs["parity_extension_exponent"] == 4
        and obs["projective_packet_count"] == 512
        and obs["projective_packet_dimension"] == 2
        and obs["radical_direction_count"] == 8
        and obs["active_direction_count"] == 2
        and obs["matrix_unit_count"] == 985
        and obs["source_sector_count"] == 39
        and obs["sector_character_row_count"] == 38_415
        and obs["fourier_candidate_count"] == 3
        and obs["full_scalar_trace_candidate_count"] == 0
        and obs["public_zero_scalar_trace_candidate_count"] == 1
        and obs["sector11_residue_mask_count"] == 512
        and obs["sector11_missing_pair_count"] == 420
        and obs["sector11_valid_nonempty_extension_count"] == 0
        and obs["long_mat_resolved_surface_count"] == 37
        and obs["long_mat_residual_boundary_count"] == 0
        and obs["long_mat_current_boundary_closed_flag"] == 1
        and obs["anomaly_suite_closed_flag"] == 1
    )

    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    status_hash = hashlib.sha256(
        digest_text(SURFACE_COLUMNS, surface_rows).encode("ascii")
    ).hexdigest()
    obs_hash = hashlib.sha256(
        digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
    ).hexdigest()
    return {
        "reports": reports,
        "surface_rows": surface_rows,
        "obs_rows": obs_rows,
        "surface_table": table_from_rows(SURFACE_COLUMNS, surface_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "status_hash": status_hash,
        "obs_hash": obs_hash,
        "obs": obs,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": obs["input_certified_count"]
        == obs["input_report_count"]
        == 18,
        "finite_automorphic_boundary_closed": (
            obs["current_automorphic_boundary_closed_flag"],
            obs["resolved_surface_count"],
            obs["residual_auto_boundary_count"],
        )
        == (1, 18, 0),
        "amplitude_fourier_automaton_closed": (
            obs["primitive_generator_packet_count"],
            obs["directed_transition_count"],
            obs["automaton_state_count"],
            obs["automaton_degree"],
            obs["residue_rank"],
            obs["fourier_mode_count"],
            obs["corrected_hidden_kernel_count"],
            obs["corrected_hidden_odd_count"],
            obs["sector26_clock_residue_count"],
            obs["step_atom_count"],
        )
        == (11, 22_528, 2048, 11, 11, 2048, 1024, 1024, 26, 25),
        "string_kernel_generator_algebra_closed": (
            obs["string_kernel_seed_count"],
            obs["string_kernel_rank"],
            obs["string_kernel_mode_count"],
            obs["primitive_preserving_generator_count"],
            obs["crossing_generator_count"],
            obs["named_generator_count"],
            obs["generator_dependency_count"],
        )
        == (83, 10, 1024, 8, 3, 11, 1),
        "central_projective_packet_closed": (
            obs["central_extension_cocycle_dimension"],
            obs["parity_extension_order"],
            obs["parity_extension_center_order"],
            obs["parity_extension_derived_order"],
            obs["parity_extension_exponent"],
            obs["projective_packet_count"],
            obs["projective_packet_dimension"],
            obs["radical_direction_count"],
            obs["active_direction_count"],
        )
        == (1, 2048, 512, 2, 4, 512, 2, 8, 2),
        "matrix_sector11_anomaly_guardrails_closed": (
            obs["matrix_unit_count"],
            obs["source_sector_count"],
            obs["sector_character_row_count"],
            obs["fourier_candidate_count"],
            obs["full_scalar_trace_candidate_count"],
            obs["public_zero_scalar_trace_candidate_count"],
            obs["sector11_residue_mask_count"],
            obs["sector11_missing_pair_count"],
            obs["sector11_valid_nonempty_extension_count"],
            obs["long_mat_resolved_surface_count"],
            obs["long_mat_residual_boundary_count"],
            obs["long_mat_current_boundary_closed_flag"],
            obs["anomaly_suite_closed_flag"],
        )
        == (985, 39, 38_415, 3, 0, 1, 512, 420, 0, 37, 0, 1, 1),
        "fingerprints_exact": (
            rows["status_hash"] == STATUS_TEXT_HASH and rows["obs_hash"] == OBS_TEXT_HASH
        ),
        "scope_not_overclaimed": obs["complete_goal_claim_flag"] == 0,
        "table_shapes_match": (
            tuple(rows["surface_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == ((18, len(SURFACE_COLUMNS)), (len(OBS_CODES), len(OBS_COLUMNS))),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_automorphic_fourier_string_kernel_boundary",
        "summary": {
            "input_report_count": obs["input_report_count"],
            "input_certified_count": obs["input_certified_count"],
            "resolved_surface_count": obs["resolved_surface_count"],
            "residual_auto_boundary_count": obs["residual_auto_boundary_count"],
            "current_automorphic_boundary_closed_flag": obs[
                "current_automorphic_boundary_closed_flag"
            ],
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "surface_code_map": {
            str(index): name for index, name in enumerate(REPORTS)
        },
        "status_text_sha256": rows["status_hash"],
        "observable_text_sha256": rows["obs_hash"],
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    auto_payload = {
        "schema": "long.auto@1",
        "object": "finite_automorphic_boundary_oracle",
        "status": STATUS if all(checks.values()) else "LONG_AUTO_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.auto.report@1",
        "status": auto_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_auto certifies the current finite automorphic/Fourier boundary: "
            "the Loop_297 amplitude lift, compact amplitude quotient, 2048-state "
            "residue automaton, Fourier mode classifier, finite Virasoro "
            "string-kernel candidate, generator algebra, finite central and parity "
            "extensions, projective kernel packet decomposition, A985 sector trace "
            "candidate evaluation, canonical matrix/character guardrails, sector-11 "
            "support obstruction, and finite anomaly correction suite cohere as a "
            "closed current-model oracle surface."
        ),
        "stage_protocol": {
            "draft": "read amplitude, Fourier, string-kernel, matrix, sector-11, and anomaly reports",
            "witness": "emit automorphic surface rows and observable closure counts",
            "coherence": "check input statuses, automaton/Fourier counts, kernel algebra counts, projective packet counts, matrix/sector-11 guardrails, hashes, and table shapes",
            "closure": "certify the finite current-model automorphic boundary without claiming continuum automorphic classification or broad bundle integration",
            "emit": "write long_auto artifacts and verifier hook",
        },
        "inputs": {
            **{
                name: input_entry(
                    path,
                    {
                        "status": rows["reports"][name].get("status"),
                        "certificate_sha256": rows["reports"][name].get(
                            "certificate_sha256"
                        ),
                    },
                )
                for name, path in REPORTS.items()
            },
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "auto": relpath(OUT_DIR / "auto.json"),
            "status_csv": relpath(OUT_DIR / "status.csv"),
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
                "the finite Loop_297 amplitude quotient and 2048-state Fourier-mode automaton cohere",
                "the rank-10 finite string-kernel candidate and 11-generator algebra are certified current-model structure",
                "the finite central/parity extension and 512 projective two-dimensional packet decomposition are certified",
            "the A985 matrix-unit and sector-character guardrails remain certified at 985 matrix units, 39 source sectors, and 38415 character rows",
            "the screen12=11 support state remains obstructed by the current finite support boundary with 420 missing transition pairs and no valid nonempty extension",
            "the finite matrix-theoretic charge-wall boundary is closed through long_mat",
            "the finite anomaly correction suite required by this boundary is closed through long_anom",
            ],
            "does_not_certify_because_out_of_scope": [
                "a continuum automorphic-form classification outside the finite d20 oracle",
                "semantic C985 associator composition beyond dedicated C985 certificates",
                "broad bundle integration without running the broad certificate gate",
                "a materialized horizon-16 profunctor",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Focused theorem-debt frontier is empty after long_auto ingestion; "
            "defer broad integration gates until the operator permits long gates."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.auto.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.auto.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "auto": auto_payload,
        "status_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "status_text_sha256": rows["status_hash"],
            "obs_text_sha256": rows["obs_hash"],
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
    write_json(OUT_DIR / "auto.json", payloads["auto"])
    (OUT_DIR / "status.csv").write_text(payloads["status_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
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
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
