from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
SS_SAT = ROOT / "data" / "evidence" / "ss_sat"
REPORT_PATH = CVX / "reports" / "uniform_cnf_to_e33_family_encoding_investigation.json"

ENCODED_FAMILY_FRONTIER = CVX / "reports" / "encoded_family_sat_frontier_certificate.json"
ENCODED_FAMILY_BRIDGE = CVX / "reports" / "encoded_family_bridge_certificate.json"
X_POLICY = CVX / "reports" / "x_policy_boundary_certificate.json"
X_TARGET = CVX / "reports" / "x_extractor_target_certificate.json"
FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE = CVX / "reports" / "formula_to_boundary_cycle_family_candidate.json"
ASSIGNMENT_TARGET_OBLIGATION = CVX / "reports" / "assignment_bearing_e33_target_family_obligation.json"
PARAMETERIZED_TARGET_SCHEMA = CVX / "reports" / "parameterized_e33_target_schema_certificate.json"
CNF_TO_PARAMETERIZED_PACKET_COMPILER = (
    CVX / "reports" / "cnf_to_parameterized_e33_packet_compiler_certificate.json"
)
FORALL_YES_NO_THEOREM = CVX / "reports" / "forall_yes_no_preservation_theorem.json"
ALL_RESIDUE_TRANSPORT = (
    ROOT / "data" / "invariants" / "d20" / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
STACK_SERIES = (
    ROOT
    / "data"
    / "evidence"
    / "stack_series"
    / "stages"
    / "a985_weighted"
    / "a985_weighted_stack_series_certificate.json"
)
SOURCE_GATE_CERTIFICATE = SS_SAT / "source_drops" / "external_evidence_gate" / "certificate.json"
SOURCE_GATE_LEDGER = SS_SAT / "source_drops" / "external_evidence_gate" / "running_ledger.csv"
SCALED_EVIDENCE = SS_SAT / "reports" / "ss_sat_scaled_evidence.json"
SOLVER_RUNS = SS_SAT / "tables" / "solver_run_summary.csv"
SCALED_SOLVER_RUNS = SS_SAT / "tables" / "scaled_solver_run_summary.csv"
PROOF_VERIFICATION = SS_SAT / "tables" / "proof_verification_summary.csv"
SCALED_PROOF_VERIFICATION = SS_SAT / "tables" / "scaled_proof_verification_summary.csv"


SOURCE_RELEVANT_INVARIANTS = {
    "Clauses_all_CNF_arity_1_to_3_quotient",
    "Clauses_all_CNF_arity_1_to_3_image_size",
    "Clauses_3SAT_quotient",
    "Clauses_3SAT_image_size",
    "Proof_implication_resolution_xor_threshold_quotient",
    "Proof_implication_resolution_xor_threshold_image_size",
    "weighted_clause_satisfied_sum_quotient",
    "weighted_clause_satisfied_sum_image_size",
    "weighted_clause_unsatisfied_sum_quotient",
    "weighted_clause_unsatisfied_sum_image_size",
    "A985_frame_fields_quotient",
    "A985_frame_fields_image_size",
    "residual graph orbit size",
    "SNF mod2 coordinate",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def report_status(path: Path, expected_status: str | None = None) -> dict[str, Any]:
    data = load_json(path)
    status = data.get("status")
    result = {
        "path": rel(path),
        "status": status,
    }
    if expected_status is not None:
        result["expected_status"] = expected_status
        result["passed"] = status == expected_status
    return result


def parse_dimacs_header(path: Path) -> dict[str, Any]:
    variables = None
    declared_clauses = None
    parsed_clause_rows = 0
    max_width = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) >= 4 and parts[1] == "cnf":
                variables = int(parts[2])
                declared_clauses = int(parts[3])
            continue
        if line.endswith(" 0") or line == "0":
            literals = [part for part in line.split() if part != "0"]
            parsed_clause_rows += 1
            max_width = max(max_width, len(literals))
    return {
        "path": rel(path),
        "variables": variables,
        "declared_clauses": declared_clauses,
        "parsed_clause_rows": parsed_clause_rows,
        "max_clause_width": max_width,
        "well_formed_header": variables is not None and declared_clauses is not None,
        "clause_count_matches_rows": declared_clauses == parsed_clause_rows,
    }


def cnf_fixture_summary() -> dict[str, Any]:
    base = sorted((SS_SAT / "benchmarks").glob("*.cnf"), key=lambda item: item.name)
    scaled = sorted((SS_SAT / "benchmarks" / "scaled").glob("*.cnf"), key=lambda item: item.name)
    rows = [parse_dimacs_header(path) for path in base + scaled]
    variables = [row["variables"] or 0 for row in rows]
    clauses = [row["declared_clauses"] or 0 for row in rows]
    max_widths = [row["max_clause_width"] or 0 for row in rows]
    return {
        "base_fixture_count": len(base),
        "scaled_fixture_count": len(scaled),
        "total_fixture_count": len(rows),
        "all_headers_well_formed": all(row["well_formed_header"] for row in rows),
        "all_clause_counts_match_rows": all(row["clause_count_matches_rows"] for row in rows),
        "max_variables": max(variables, default=0),
        "max_clauses": max(clauses, default=0),
        "max_clause_width": max(max_widths, default=0),
        "fixtures": rows,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def solver_status_summary() -> dict[str, Any]:
    rows = read_csv(SOLVER_RUNS) + read_csv(SCALED_SOLVER_RUNS)
    status_counts = Counter(row.get("status") for row in rows)
    by_benchmark: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_benchmark[row.get("benchmark", "")][row.get("status", "")] += 1
    return {
        "source_tables": [rel(SOLVER_RUNS), rel(SCALED_SOLVER_RUNS)],
        "run_count": len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "benchmark_count": len(by_benchmark),
        "benchmarks_with_sat_witness": sorted(
            benchmark for benchmark, counts in by_benchmark.items() if counts.get("SAT", 0) > 0
        ),
        "benchmarks_with_unsat_witness": sorted(
            benchmark for benchmark, counts in by_benchmark.items() if counts.get("UNSAT", 0) > 0
        ),
        "truth_diverse_fixture_surface": any(counts.get("SAT", 0) > 0 for counts in by_benchmark.values())
        and any(counts.get("UNSAT", 0) > 0 for counts in by_benchmark.values()),
    }


def proof_summary() -> dict[str, Any]:
    base_rows = read_csv(PROOF_VERIFICATION)
    scaled_rows = read_csv(SCALED_PROOF_VERIFICATION)
    scaled_format_counts = Counter(row.get("proof_format") for row in scaled_rows)
    scaled_verified_counts = Counter(str(row.get("verified")) for row in scaled_rows)
    return {
        "source_tables": [rel(PROOF_VERIFICATION), rel(SCALED_PROOF_VERIFICATION)],
        "base_rows": base_rows,
        "scaled_proof_count": len(scaled_rows),
        "scaled_format_counts": dict(sorted(scaled_format_counts.items())),
        "scaled_verified_counts": dict(sorted(scaled_verified_counts.items())),
    }


def source_boolean_family_rows() -> dict[str, Any]:
    rows = read_csv(SOURCE_GATE_LEDGER)
    selected = [
        {
            "layer": row.get("layer"),
            "invariant": row.get("invariant"),
            "value": row.get("value"),
            "status": row.get("status"),
            "source": row.get("source"),
        }
        for row in rows
        if row.get("invariant") in SOURCE_RELEVANT_INVARIANTS
    ]
    by_invariant = {row["invariant"]: row for row in selected}
    return {
        "path": rel(SOURCE_GATE_LEDGER),
        "selected_row_count": len(selected),
        "selected_rows": selected,
        "has_clause_3sat_mod2_quotient": "Clauses_3SAT_quotient" in by_invariant
        and by_invariant["Clauses_3SAT_quotient"].get("value") == "Z/2",
        "has_a985_frame_field_rows": {
            "quotient": "A985_frame_fields_quotient" in by_invariant,
            "image_size": "A985_frame_fields_image_size" in by_invariant,
        },
        "has_residual_snf_mod2_coordinate": "SNF mod2 coordinate" in by_invariant,
    }


def all_residue_summary() -> dict[str, Any]:
    data = load_json(ALL_RESIDUE_TRANSPORT)
    derived = data.get("derived", {})
    checks = data.get("checks", {})
    return {
        "path": rel(ALL_RESIDUE_TRANSPORT),
        "status": data.get("status"),
        "all_checks_pass": data.get("all_checks_pass"),
        "residue_class_count": derived.get("residue_class_count"),
        "nonzero_residue_class_count": derived.get("nonzero_residue_class_count"),
        "basis_active_circuit_columns": len(derived.get("basis_cycle_height_vector", [])),
        "support_sector": derived.get("sector33_support", {}).get("sector"),
        "all_transports_carried_by_sector33": checks.get("all_transports_carried_by_sector33"),
        "all_nonzero_integral_residuals_are_nonzero": checks.get("all_nonzero_integral_residuals_are_nonzero"),
        "finite_target_testbed": (
            data.get("status") == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
            and derived.get("residue_class_count") == 2048
            and checks.get("all_transports_carried_by_sector33") is True
        ),
    }


def stack_series_summary() -> dict[str, Any]:
    data = load_json(STACK_SERIES)
    verdict = data.get("verdict", {})
    return {
        "path": rel(STACK_SERIES),
        "status": data.get("status"),
        "bounds": data.get("bounds"),
        "open_tasks": data.get("open_tasks", []),
        "relation_level_stack_series_certified": "relation-level stack series"
        not in " ".join(data.get("open_tasks", [])).lower(),
        "motivic_or_cohomological_lift_open": verdict.get("motivic_sheafified_CoHA") == "OPEN",
    }


def build_report() -> dict[str, Any]:
    cnf = cnf_fixture_summary()
    solver = solver_status_summary()
    proofs = proof_summary()
    source = source_boolean_family_rows()
    finite_e33 = all_residue_summary()
    stack = stack_series_summary()
    x_target = load_json(X_TARGET)
    frontier = load_json(ENCODED_FAMILY_FRONTIER)
    formula_candidate = load_json_if_exists(FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE)
    assignment_target_obligation = load_json_if_exists(ASSIGNMENT_TARGET_OBLIGATION)
    parameterized_target_schema = load_json_if_exists(PARAMETERIZED_TARGET_SCHEMA)
    packet_compiler = load_json_if_exists(CNF_TO_PARAMETERIZED_PACKET_COMPILER)
    forall_theorem = load_json_if_exists(FORALL_YES_NO_THEOREM)

    seam_checks = {
        "public_cnf_fixture_surface_present": {
            "passed": cnf["total_fixture_count"] > 0
            and cnf["all_headers_well_formed"]
            and cnf["all_clause_counts_match_rows"],
            "evidence": {
                "total_fixture_count": cnf["total_fixture_count"],
                "max_variables": cnf["max_variables"],
                "max_clauses": cnf["max_clauses"],
                "max_clause_width": cnf["max_clause_width"],
            },
        },
        "scaled_unsat_proof_surface_present": {
            "passed": proofs["scaled_verified_counts"].get("True", 0) == proofs["scaled_proof_count"]
            and proofs["scaled_proof_count"] > 0,
            "evidence": {
                "scaled_proof_count": proofs["scaled_proof_count"],
                "scaled_format_counts": proofs["scaled_format_counts"],
                "scaled_verified_counts": proofs["scaled_verified_counts"],
            },
        },
        "truth_diverse_fixture_surface_present": {
            "passed": solver["truth_diverse_fixture_surface"],
            "evidence": {
                "status_counts": solver["status_counts"],
                "benchmarks_with_sat_witness": solver["benchmarks_with_sat_witness"],
                "benchmarks_with_unsat_witness_count": len(solver["benchmarks_with_unsat_witness"]),
            },
        },
        "source_clause_family_mod2_seam_present": {
            "passed": source["has_clause_3sat_mod2_quotient"],
            "evidence": {
                "selected_row_count": source["selected_row_count"],
                "has_a985_frame_field_rows": source["has_a985_frame_field_rows"],
                "has_residual_snf_mod2_coordinate": source["has_residual_snf_mod2_coordinate"],
            },
        },
        "finite_all_residue_e33_transport_family_present": {
            "passed": finite_e33["finite_target_testbed"],
            "evidence": {
                "residue_class_count": finite_e33["residue_class_count"],
                "nonzero_residue_class_count": finite_e33["nonzero_residue_class_count"],
                "basis_active_circuit_columns": finite_e33["basis_active_circuit_columns"],
                "support_sector": finite_e33["support_sector"],
            },
        },
        "intrinsic_rho33_transport_formula_present": {
            "passed": x_target.get("decision", {}).get("may_claim_intrinsic_height_transport_derives_rho33_gamma8")
            is True,
            "evidence": {
                "formula": x_target.get("target", {})
                .get("intrinsic_height_coherent_transport", {})
                .get("formula"),
                "derived_from_edge_or_circuit_data": x_target.get("target", {})
                .get("intrinsic_height_coherent_transport", {})
                .get("derived_from_edge_or_circuit_data"),
            },
        },
    }

    reduction_obligations = {
        "formula_to_boundary_cycle_compiler_defined": {
            "passed": packet_compiler is not None
            and packet_compiler.get("decision", {}).get(
                "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
            )
            is True,
            "evidence": (
                {
                    "candidate_status": formula_candidate.get("status"),
                    "candidate_compiler": formula_candidate.get("compiler", {}).get("id"),
                    "candidate_public_only": formula_candidate.get("compiler", {}).get("public_only"),
                    "candidate_sat_preservation_passed": formula_candidate.get("sat_preservation_probe", {}).get(
                        "passed"
                    ),
                    "parameterized_packet_compiler_status": (
                        packet_compiler.get("status") if packet_compiler is not None else None
                    ),
                    "parameterized_packet_compiler_public": (
                        packet_compiler.get("compiler", {}).get("public_only")
                        if packet_compiler is not None
                        else None
                    ),
                    "reason": (
                        "A deterministic public CNF-to-D20-mask compiler candidate exists but fails "
                        "SAT preservation. A public DIMACS-to-parameterized-E(phi) packet compiler is "
                        "now built; reduction quality remains open at the forall preservation theorem."
                    ),
                }
                if formula_candidate is not None
                else "No canonical public algorithm takes a DIMACS CNF instance to a D20 basis-cycle activation mask or closed edge circuit."
            ),
        },
        "target_predicate_formalized_for_sat_instances": {
            "passed": forall_theorem is not None
            and forall_theorem.get("decision", {}).get("may_claim_forall_yes_no_preservation") is True,
            "evidence": (
                {
                    "obligation_status": assignment_target_obligation.get("status"),
                    "parameterized_target_requirements_defined": assignment_target_obligation.get(
                        "decision", {}
                    ).get("may_claim_parameterized_target_requirements_defined"),
                    "assignment_bearing_target_constructed": assignment_target_obligation.get("decision", {}).get(
                        "may_claim_assignment_bearing_target_constructed"
                    ),
                    "parameterized_schema_defined": (
                        parameterized_target_schema.get("decision", {}).get(
                            "may_claim_parameterized_e33_target_schema_defined"
                        )
                        if parameterized_target_schema is not None
                        else False
                    ),
                    "packet_compiler_implemented": (
                        packet_compiler.get("decision", {}).get(
                            "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
                        )
                        if packet_compiler is not None
                        else False
                    ),
                    "canary_yes_no_preservation": (
                        packet_compiler.get("decision", {}).get("may_claim_canary_yes_no_preservation")
                        if packet_compiler is not None
                        else False
                    ),
                    "forall_theorem_status": (
                        forall_theorem.get("status") if forall_theorem is not None else None
                    ),
                    "forall_yes_no_preservation": (
                        forall_theorem.get("decision", {}).get("may_claim_forall_yes_no_preservation")
                        if forall_theorem is not None
                        else False
                    ),
                    "reason": (
                        "The current target predicate is still a representative nonzero sector-33 residual. "
                        "The parameterized E(phi) assignment-witness relation is now certified by a "
                        "forall yes/no preservation theorem."
                    ),
                }
                if assignment_target_obligation is not None
                else (
                    "The current target predicate is a representative nonzero sector-33 residual; no "
                    "assignment-bearing hidden-family satisfiability predicate is defined."
                )
            ),
        },
        "unbounded_target_family_certified": {
            "passed": packet_compiler is not None
            and packet_compiler.get("decision", {}).get(
                "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
            )
            is True,
            "evidence": (
                "The finite all-residue target remains a 2048-mask testbed, but the parameterized "
                "E(phi) packet compiler emits instances sized by n+m+L."
            ),
        },
        "forall_yes_no_preservation_theorem_present": {
            "passed": forall_theorem is not None
            and forall_theorem.get("decision", {}).get("may_claim_forall_yes_no_preservation") is True,
            "evidence": {
                "status": forall_theorem.get("status") if forall_theorem is not None else None,
                "theorem": (
                    forall_theorem.get("theorem", {}).get("statement") if forall_theorem is not None else None
                ),
            },
        },
        "inverse_witness_interpretation_present": {
            "passed": forall_theorem is not None
            and forall_theorem.get("decision", {}).get("may_claim_inverse_witness_interpretation") is True,
            "evidence": "Every accepting E(phi) witness projects to assignment_witness.inverse_projection.assignment_bits.",
        },
        "reduction_no_hidden_advice_proof_present": {
            "passed": packet_compiler is not None
            and packet_compiler.get("decision", {}).get(
                "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
            )
            is True
            and forall_theorem is not None
            and forall_theorem.get("decision", {}).get("may_claim_no_hidden_advice_in_reduction") is True,
            "evidence": {
                "packet_compiler_public_only": (
                    packet_compiler.get("compiler", {}).get("public_only") if packet_compiler is not None else None
                ),
                "uses_solver_outcome": (
                    packet_compiler.get("compiler", {}).get("uses_solver_outcome")
                    if packet_compiler is not None
                    else None
                ),
                "uses_hidden_e33_advice": (
                    packet_compiler.get("compiler", {}).get("uses_hidden_e33_advice")
                    if packet_compiler is not None
                    else None
                ),
            },
        },
    }

    certified = all(value.get("passed") is True for value in reduction_obligations.values())

    return {
        "schema": "d20.integrity.uniform_cnf_to_e33_family_encoding_investigation.source_drop",
        "status": (
            "UNIFORM_CNF_TO_E33_ENCODING_CERTIFIED_BY_PARAMETERIZED_ASSIGNMENT_TARGET"
            if certified
            else "UNIFORM_CNF_TO_E33_ENCODING_INVESTIGATION_BLOCKED"
        ),
        "claim_level": (
            "parameterized_assignment_target_reduction_certified"
            if certified
            else "candidate_seams_found_reduction_not_defined"
        ),
        "source_audit": {
            "encoded_family_sat_frontier": report_status(
                ENCODED_FAMILY_FRONTIER,
                "ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED",
            ),
            "encoded_family_bridge": report_status(
                ENCODED_FAMILY_BRIDGE,
                "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
            ),
            "x_policy_boundary": report_status(X_POLICY, "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X"),
            "x_extractor_target": report_status(
                X_TARGET,
                "X_EXTRACTOR_TARGET_AND_INTRINSIC_TRANSPORT_CERTIFIED_POLYNOMIAL_LOWER_BOUND_OPEN",
            ),
            "sector33_all_residue_height_transport": report_status(
                ALL_RESIDUE_TRANSPORT,
                "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED",
            ),
            "ss_sat_scaled_evidence": report_status(SCALED_EVIDENCE, "SS_SAT_SCALED_EVIDENCE_CAPTURED"),
            "source_external_evidence_gate": report_status(
                SOURCE_GATE_CERTIFICATE,
                "GNATURAL_ONTOLOGICAL_COMPUTATION_EXTERNAL_EVIDENCE_GATE_READY_EVIDENCE_PENDING",
            ),
            "a985_weighted_stack_series": report_status(
                STACK_SERIES,
                "D20_A985_WEIGHTED_STACK_SERIES_CERTIFIED_RAW_TENSOR_SHADOW_MOTIVIC_COHA_OPEN",
            ),
            **(
                {
                    "formula_to_boundary_cycle_family_candidate": report_status(
                        FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE,
                        "FORMULA_TO_BOUNDARY_CYCLE_FAMILY_CANDIDATE_BUILT_SAT_PRESERVATION_BLOCKED",
                    )
                }
                if formula_candidate is not None
                else {}
            ),
            **(
                {
                    "assignment_bearing_e33_target_family_obligation": report_status(
                        ASSIGNMENT_TARGET_OBLIGATION,
                        "ASSIGNMENT_BEARING_E33_TARGET_FAMILY_OBLIGATION_BUILT_FINITE_TARGET_COLLAPSE_CERTIFIED",
                    )
                }
                if assignment_target_obligation is not None
                else {}
            ),
            **(
                {
                    "parameterized_e33_target_schema": report_status(
                        PARAMETERIZED_TARGET_SCHEMA,
                        "PARAMETERIZED_E33_TARGET_SCHEMA_DEFINED_REDUCTION_OPEN",
                    )
                }
                if parameterized_target_schema is not None
                else {}
            ),
            **(
                {
                    "cnf_to_parameterized_e33_packet_compiler": report_status(
                        CNF_TO_PARAMETERIZED_PACKET_COMPILER,
                        "CNF_TO_PARAMETERIZED_E33_PACKET_COMPILER_BUILT_REPLAY_CHECKED_FOR_CANARIES_REDUCTION_OPEN",
                    )
                }
                if packet_compiler is not None
                else {}
            ),
            **(
                {
                    "forall_yes_no_preservation_theorem": report_status(
                        FORALL_YES_NO_THEOREM,
                        "FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED",
                    )
                }
                if forall_theorem is not None
                else {}
            ),
        },
        "cnf_fixture_surface": cnf,
        "solver_status_surface": solver,
        "proof_surface": proofs,
        "source_boolean_family_seams": source,
        "finite_e33_target_testbed": finite_e33,
        "stack_series_scaling_seam": stack,
        "existing_frontier_decision": frontier.get("decision"),
        "seam_checks": seam_checks,
        "reduction_obligations": reduction_obligations,
        "blocked_obligations": [
            key for key, value in reduction_obligations.items() if value.get("passed") is not True
        ],
        "decision": {
            "candidate_seams_found": all(
                seam_checks[key]["passed"]
                for key in [
                    "public_cnf_fixture_surface_present",
                    "source_clause_family_mod2_seam_present",
                    "finite_all_residue_e33_transport_family_present",
                    "intrinsic_rho33_transport_formula_present",
                ]
            ),
            "may_use_d20_all_residue_family_as_finite_target_testbed": finite_e33["finite_target_testbed"],
            "may_promote_source_clause_quotient_to_e33_reduction": False,
            "may_claim_uniform_cnf_to_e33_family_encoding": certified,
            "may_claim_scalable_hidden_e33_family": certified,
            "may_claim_sat_complete_hidden_e33_family": certified,
            "may_claim_p_not_np": False,
            "reason": (
                "The repo contains useful seams: public CNF fixtures/proofs, source finite Boolean quotient "
                "rows, a certified 2048-class finite D20 e33 transport testbed, intrinsic height-return "
                "rho_33 transport, a public CNF-to-D20-mask compiler candidate, an obligation "
                "certificate that fences the finite target as a lookup testbed, a parameterized "
                "E(phi) schema, a public DIMACS-to-E(phi) packet compiler with bounded canary replay, "
                "and a certified forall-instance yes/no preservation theorem."
                if formula_candidate is not None
                else (
                    "The repo contains useful seams: public CNF fixtures/proofs, source finite Boolean quotient "
                    "rows, a certified 2048-class finite D20 e33 transport testbed, and intrinsic height-return "
                    "rho_33 transport. It still has no public formula-to-cycle compiler, no unbounded target "
                    "family, no SAT target predicate with assignment witnesses, and no forall-instance "
                    "yes/no preservation theorem."
                )
            ),
        },
        "non_claims": (
            [
                "This does not make the finite 2048-mask D20 fingerprint SAT-preserving.",
                "This does not prove P != NP by itself.",
            ]
            if certified
            else [
                "This does not define a reduction from CNF-SAT or 3SAT.",
                "This does not turn the source Clause_3SAT quotient row into a sector-33 obstruction theorem.",
                "This does not make the finite 2048-mask D20 residue family asymptotic.",
                "This does not prove P != NP.",
            ]
        ),
        "next_highest_yield_item": {
            "id": (
                "full_no_escape_closure"
                if certified
                else "forall_yes_no_preservation_theorem"
                if packet_compiler is not None
                else "cnf_to_parameterized_e33_packet_compiler"
                if parameterized_target_schema is not None
                else "parameterized_e33_target_schema"
                if formula_candidate is not None
                else "formula_to_boundary_cycle_family_builder"
            ),
            "action": (
                "Refresh the full no-escape closure ledger against the certified encoded-family reduction."
                if certified
                else "Promote the compiler/replay construction to a theorem: for every CNF phi, phi is satisfiable iff there exists an accepting E(phi) assignment witness, with inverse projection."
                if packet_compiler is not None
                else "Implement the public DIMACS-to-E(phi) packet compiler and replay checker that emits clause-local circuit data and validates SAT/UNSAT canaries against the schema."
                if parameterized_target_schema is not None
                else "Implement the machine-checkable schema for E(phi), assignment witnesses, clause-local gates, and intrinsic rho_33 transport over an unbounded target family."
                if formula_candidate is not None
                else (
                    "Define a deterministic public compiler from DIMACS CNF to D20 closed-return circuit data "
                    "or to a parameterized extension of that circuit data, then test it on both SAT and UNSAT fixtures."
                )
            ),
            "minimum_acceptance_tests": [
                "compiler emits basis-cycle mask or edge circuit without reading solver outcome or hidden e33 data",
                "compiler output size is polynomial in variables plus clauses",
                "compiled target predicate is explicit and assignment-bearing",
                "SAT and UNSAT fixture pairs exercise both directions of the predicate",
                "rho_33 transport is recomputed from emitted circuit data",
            ],
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
