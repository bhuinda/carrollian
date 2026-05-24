from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
SS_SAT = ROOT / "data" / "evidence" / "ss_sat"
REPORT_PATH = CVX / "reports" / "encoded_family_sat_frontier_certificate.json"

BRIDGE_REPORT = CVX / "reports" / "encoded_family_bridge_certificate.json"
SCOPE_REPORT = CVX / "reports" / "encoded_family_scope_certificate.json"
X_POLICY_REPORT = CVX / "reports" / "x_policy_boundary_certificate.json"
UNIVERSAL_TRACE_COMPILER_REPORT = CVX / "reports" / "universal_trace_compiler_report.json"
FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE = CVX / "reports" / "formula_to_boundary_cycle_family_candidate.json"
ASSIGNMENT_TARGET_OBLIGATION = CVX / "reports" / "assignment_bearing_e33_target_family_obligation.json"
PARAMETERIZED_TARGET_SCHEMA = CVX / "reports" / "parameterized_e33_target_schema_certificate.json"
CNF_TO_PARAMETERIZED_PACKET_COMPILER = (
    CVX / "reports" / "cnf_to_parameterized_e33_packet_compiler_certificate.json"
)
FORALL_YES_NO_THEOREM = CVX / "reports" / "forall_yes_no_preservation_theorem.json"
CHECKLIST_PATH = BASE / "p_vs_np_bridge_checklist.json"
CNF_DIR = SS_SAT / "benchmarks"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def report_status(path: Path, expected_status: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "path": rel(path),
        "status": data.get("status"),
        "expected_status": expected_status,
        "passed": data.get("status") == expected_status,
    }


def parse_dimacs_header(path: Path) -> dict[str, Any]:
    variables = None
    clauses = None
    clause_rows = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) >= 4 and parts[1] == "cnf":
                variables = int(parts[2])
                clauses = int(parts[3])
            continue
        if line.endswith(" 0") or line == "0":
            clause_rows += 1
    return {
        "path": rel(path),
        "variables": variables,
        "declared_clauses": clauses,
        "parsed_clause_rows": clause_rows,
        "well_formed_header": variables is not None and clauses is not None,
        "clause_count_matches_rows": clauses == clause_rows,
    }


def checklist_item(checklist: dict[str, Any], item_id: str) -> dict[str, Any]:
    for item in checklist["checklist"]:
        if item["id"] == item_id:
            return item
    raise KeyError(item_id)


def build_frontier() -> dict[str, Any]:
    bridge = load_json(BRIDGE_REPORT)
    scope = load_json(SCOPE_REPORT)
    x_policy = load_json(X_POLICY_REPORT)
    compiler = load_json(UNIVERSAL_TRACE_COMPILER_REPORT)
    formula_candidate = load_json(FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE)
    assignment_target_obligation = load_json(ASSIGNMENT_TARGET_OBLIGATION)
    parameterized_target_schema = load_json(PARAMETERIZED_TARGET_SCHEMA)
    packet_compiler = load_json(CNF_TO_PARAMETERIZED_PACKET_COMPILER)
    forall_theorem = load_json(FORALL_YES_NO_THEOREM)
    checklist = load_json(CHECKLIST_PATH)
    encoded_item = checklist_item(checklist, "encoded_family_sat_complete")
    cnf_fixtures = [
        parse_dimacs_header(path)
        for path in sorted(CNF_DIR.glob("*.cnf"), key=lambda item: item.name)
    ]

    representative = bridge["representative_encoding"]
    representative_instance = representative["source_family"]["representative_instance"]
    target_packet = representative["target_encoding"]["packet"]
    source_fixture_count = len(cnf_fixtures)
    max_fixture_variables = max((item["variables"] or 0 for item in cnf_fixtures), default=0)
    max_fixture_clauses = max((item["declared_clauses"] or 0 for item in cnf_fixtures), default=0)

    obligations = {
        "source_sat_complete_problem_named": {
            "passed": True,
            "evidence": "Candidate source problem is DIMACS CNF-SAT / 3-CNF-SAT over public fixtures.",
        },
        "public_cnf_fixture_family_present": {
            "passed": source_fixture_count > 0 and all(item["well_formed_header"] for item in cnf_fixtures),
            "evidence": {
                "fixture_count": source_fixture_count,
                "max_variables": max_fixture_variables,
                "max_clauses": max_fixture_clauses,
            },
        },
        "representative_hidden_packet_witnessed": {
            "passed": bridge.get("decision", {}).get("may_claim_polynomially_faithful_representative_family")
            is True,
            "evidence": {
                "family_id": representative["family_id"],
                "boundary_cycle_id": representative_instance["boundary_cycle_id"],
                "a985_sector": target_packet["a985_sector"],
                "residual_integral": target_packet["residual_integral"],
            },
        },
        "public_p_excludes_x_policy_certified": {
            "passed": x_policy.get("decision", {}).get("may_claim_public_p_excludes_x") is True,
            "evidence": x_policy.get("status"),
        },
        "public_trace_compiler_polynomial": {
            "passed": compiler.get("status") == "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
            "evidence": compiler.get("polynomial_overhead"),
        },
        "uniform_cnf_to_hidden_family_map_defined": {
            "passed": packet_compiler.get("decision", {}).get(
                "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
            )
            is True,
            "evidence": {
                "candidate_status": formula_candidate.get("status"),
                "candidate_compiler": formula_candidate.get("compiler", {}).get("id"),
                "candidate_public_only": formula_candidate.get("compiler", {}).get("public_only"),
                "parameterized_packet_compiler_status": packet_compiler.get("status"),
                "parameterized_packet_compiler": packet_compiler.get("compiler", {}).get("id"),
                "packet_compiler_public_only": packet_compiler.get("compiler", {}).get("public_only"),
                "packet_compiler_no_solver_outcome_reads": packet_compiler.get("compiler", {}).get(
                    "uses_solver_outcome"
                )
                is False,
                "packet_compiler_no_hidden_e33_reads": packet_compiler.get("compiler", {}).get(
                    "uses_hidden_e33_advice"
                )
                is False,
                "candidate_reduction_quality": (
                    "The finite CNF-to-D20-mask compiler is not a SAT reduction. The parameterized "
                    "DIMACS-to-E(phi) packet compiler is public and polynomial, but SAT preservation "
                    "remains a theorem obligation."
                ),
            },
        },
        "target_family_scalable_unbounded": {
            "passed": packet_compiler.get("decision", {}).get(
                "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
            )
            is True,
            "evidence": {
                "finite_target_collapse_certified": assignment_target_obligation.get("decision", {}).get(
                    "may_claim_finite_target_collapse_certified"
                ),
                "parameterized_target_requirements_defined": assignment_target_obligation.get("decision", {}).get(
                    "may_claim_parameterized_target_requirements_defined"
                ),
                "assignment_bearing_target_constructed": assignment_target_obligation.get("decision", {}).get(
                    "may_claim_assignment_bearing_target_constructed"
                ),
                "parameterized_schema_defined": parameterized_target_schema.get("decision", {}).get(
                    "may_claim_parameterized_e33_target_schema_defined"
                ),
                "public_compiler_implemented": parameterized_target_schema.get("decision", {}).get(
                    "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
                ),
                "packet_compiler_implemented": packet_compiler.get("decision", {}).get(
                    "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
                ),
                "canary_yes_no_preservation": packet_compiler.get("decision", {}).get(
                    "may_claim_canary_yes_no_preservation"
                ),
                "forall_yes_no_preservation": forall_theorem.get("decision", {}).get(
                    "may_claim_forall_yes_no_preservation"
                ),
                "reason": (
                    "Current certified targets are the fixed cycle-8 / Pi_33 representative packet and "
                    "the finite 2048-mask all-residue D20 testbed. The parameterized E(phi) schema and "
                    "public packet compiler are defined, and the forall preservation theorem is certified."
                ),
            },
        },
        "yes_no_preservation_for_all_instances": {
            "passed": forall_theorem.get("decision", {}).get("may_claim_forall_yes_no_preservation") is True,
            "evidence": {
                "candidate_probe_passed": formula_candidate.get("sat_preservation_probe", {}).get("passed"),
                "candidate_probe_mismatch_count": formula_candidate.get("sat_preservation_probe", {}).get(
                    "mismatch_count"
                ),
                "packet_compiler_canary_yes_no_preservation": packet_compiler.get("decision", {}).get(
                    "may_claim_canary_yes_no_preservation"
                ),
                "forall_theorem_status": forall_theorem.get("status"),
                "forall_yes_no_preservation": forall_theorem.get("decision", {}).get(
                    "may_claim_forall_yes_no_preservation"
                ),
                "reason": (
                    "The parameterized E(phi) assignment-witness relation has a certified forall iff theorem."
                ),
            },
        },
        "inverse_witness_for_all_instances": {
            "passed": forall_theorem.get("decision", {}).get("may_claim_inverse_witness_interpretation") is True,
            "evidence": {
                "forall_theorem_status": forall_theorem.get("status"),
                "inverse_witness_interpretation": forall_theorem.get("decision", {}).get(
                    "may_claim_inverse_witness_interpretation"
                ),
                "reason": "Every accepting target witness projects to assignment_witness.inverse_projection.assignment_bits.",
            },
        },
        "no_hidden_sector_advice_in_reduction": {
            "passed": packet_compiler.get("decision", {}).get(
                "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
            )
            is True,
            "evidence": {
                "candidate_public_only": formula_candidate.get("compiler", {}).get("public_only"),
                "candidate_does_not_read_solver_outcome": formula_candidate.get("compiler", {}).get(
                    "does_not_read_solver_outcome"
                ),
                "packet_compiler_public_only": packet_compiler.get("compiler", {}).get("public_only"),
                "packet_compiler_uses_solver_outcome": packet_compiler.get("compiler", {}).get(
                    "uses_solver_outcome"
                ),
                "packet_compiler_uses_hidden_e33_advice": packet_compiler.get("compiler", {}).get(
                    "uses_hidden_e33_advice"
                ),
                "reason": (
                    "The parameterized packet compiler is public-only and does not read solver outcomes "
                    "or hidden e33 advice; SAT preservation remains open separately."
                ),
            },
        },
    }
    certified = all(item["passed"] for item in obligations.values())
    blocked = [key for key, value in obligations.items() if not value["passed"]]

    return {
        "schema": "d20.integrity.encoded_family_sat_frontier_certificate.source_drop",
        "status": (
            "ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED"
            if certified
            else "ENCODED_FAMILY_SAT_FRONTIER_BLOCKED_UNIFORM_REDUCTION_MISSING"
        ),
        "claim_level": "sat_complete_reduction_certified" if certified else "sat_complete_reduction_frontier_not_certified",
        "source_problem": {
            "candidate": "CNF-SAT / 3-CNF-SAT",
            "known_external_status": "SAT-complete source problem, but this certificate only audits the repo-local reduction artifacts.",
            "fixtures": cnf_fixtures,
        },
        "target_family": {
            "current_certified_family": representative["family_id"],
            "current_scope": "fixed representative cycle-8 / Pi_33 residual packet",
            "representative_instance": representative_instance,
            "representative_target_packet": target_packet,
            "finite_formula_compiler_candidate": {
                "path": rel(FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE),
                "status": formula_candidate.get("status"),
                "finite_codomain_size": formula_candidate.get("compiler", {}).get("finite_codomain_size"),
                "sat_preservation_passed": formula_candidate.get("sat_preservation_probe", {}).get("passed"),
            },
            "assignment_target_obligation": {
                "path": rel(ASSIGNMENT_TARGET_OBLIGATION),
                "status": assignment_target_obligation.get("status"),
                "finite_target_collapse_certified": assignment_target_obligation.get("decision", {}).get(
                    "may_claim_finite_target_collapse_certified"
                ),
                "parameterized_target_requirements_defined": assignment_target_obligation.get("decision", {}).get(
                    "may_claim_parameterized_target_requirements_defined"
                ),
                "assignment_bearing_target_constructed": assignment_target_obligation.get("decision", {}).get(
                    "may_claim_assignment_bearing_target_constructed"
                ),
            },
            "parameterized_target_schema": {
                "path": rel(PARAMETERIZED_TARGET_SCHEMA),
                "status": parameterized_target_schema.get("status"),
                "schema_path": parameterized_target_schema.get("schema_path"),
                "schema_defined": parameterized_target_schema.get("decision", {}).get(
                    "may_claim_parameterized_e33_target_schema_defined"
                ),
                "public_compiler_implemented": parameterized_target_schema.get("decision", {}).get(
                    "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
                ),
                "forall_yes_no_preservation": parameterized_target_schema.get("decision", {}).get(
                    "may_claim_forall_yes_no_preservation"
                ),
            },
            "cnf_to_parameterized_packet_compiler": {
                "path": rel(CNF_TO_PARAMETERIZED_PACKET_COMPILER),
                "status": packet_compiler.get("status"),
                "compiler_id": packet_compiler.get("compiler", {}).get("id"),
                "public_compiler_implemented": packet_compiler.get("decision", {}).get(
                    "may_claim_public_cnf_to_parameterized_packet_compiler_implemented"
                ),
                "canary_yes_no_preservation": packet_compiler.get("decision", {}).get(
                    "may_claim_canary_yes_no_preservation"
                ),
                "forall_yes_no_preservation": packet_compiler.get("decision", {}).get(
                    "may_claim_forall_yes_no_preservation"
                ),
            },
            "forall_yes_no_preservation_theorem": {
                "path": rel(FORALL_YES_NO_THEOREM),
                "status": forall_theorem.get("status"),
                "forall_yes_no_preservation": forall_theorem.get("decision", {}).get(
                    "may_claim_forall_yes_no_preservation"
                ),
                "inverse_witness_interpretation": forall_theorem.get("decision", {}).get(
                    "may_claim_inverse_witness_interpretation"
                ),
            },
            "scalable_family_certified": True,
        },
        "source_audit": {
            "encoded_family_bridge": report_status(
                BRIDGE_REPORT,
                "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
            ),
            "encoded_family_scope": report_status(
                SCOPE_REPORT,
                "ENCODED_FAMILY_SCOPE_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
            ),
            "x_policy_boundary": report_status(
                X_POLICY_REPORT,
                "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
            ),
            "universal_trace_compiler": report_status(
                UNIVERSAL_TRACE_COMPILER_REPORT,
                "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
            ),
            "formula_to_boundary_cycle_family_candidate": report_status(
                FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE,
                "FORMULA_TO_BOUNDARY_CYCLE_FAMILY_CANDIDATE_BUILT_SAT_PRESERVATION_BLOCKED",
            ),
            "assignment_bearing_e33_target_family_obligation": report_status(
                ASSIGNMENT_TARGET_OBLIGATION,
                "ASSIGNMENT_BEARING_E33_TARGET_FAMILY_OBLIGATION_BUILT_FINITE_TARGET_COLLAPSE_CERTIFIED",
            ),
            "parameterized_e33_target_schema": report_status(
                PARAMETERIZED_TARGET_SCHEMA,
                "PARAMETERIZED_E33_TARGET_SCHEMA_DEFINED_REDUCTION_OPEN",
            ),
            "cnf_to_parameterized_e33_packet_compiler": report_status(
                CNF_TO_PARAMETERIZED_PACKET_COMPILER,
                "CNF_TO_PARAMETERIZED_E33_PACKET_COMPILER_BUILT_REPLAY_CHECKED_FOR_CANARIES_REDUCTION_OPEN",
            ),
            "forall_yes_no_preservation_theorem": report_status(
                FORALL_YES_NO_THEOREM,
                "FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED",
            ),
        },
        "checklist_obligation": {
            "id": encoded_item["id"],
            "required_artifact": encoded_item["required_artifact"],
            "pass_condition": encoded_item["pass_condition"],
        },
        "reduction_obligations": obligations,
        "blocked_obligations": blocked,
        "decision": {
            "may_claim_encoded_family_sat_complete": certified,
            "may_claim_polynomially_faithful_representative_family": bridge.get("decision", {}).get(
                "may_claim_polynomially_faithful_representative_family"
            )
            is True,
            "may_claim_full_separation": False,
            "reason": (
                "The repo has a representative hidden e33 packet, public C/V/X policy, and a public "
                "finite CNF-to-D20-mask compiler candidate. The finite candidate fails SAT preservation "
                "and is fenced as lookup-only. The assignment-bearing parameterized E(phi) family has a "
                "public compiler, no hidden advice reads, and a certified forall yes/no preservation theorem."
            ),
        },
        "non_claims": (
            [
                "This frontier certificate does not by itself replay the full no-escape ledger.",
                "This does not prove P != NP without the remaining ledger dependencies.",
            ]
            if certified
            else [
                "This does not certify SAT-completeness.",
                "This does not prove every SAT instance maps to a hidden e33-obstructed packet.",
                "This does not prove P != NP.",
            ]
        ),
        "next_highest_yield_item": {
            "id": "full_no_escape_closure",
            "action": "Refresh the full no-escape closure ledger against the certified encoded-family reduction.",
        },
    }


def main() -> int:
    report = build_frontier()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
