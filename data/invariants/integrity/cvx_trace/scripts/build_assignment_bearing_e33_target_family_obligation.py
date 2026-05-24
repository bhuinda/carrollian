from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
D20 = ROOT / "data" / "invariants" / "d20"
REPORT_PATH = CVX / "reports" / "assignment_bearing_e33_target_family_obligation.json"

ALL_RESIDUE_TRANSPORT = D20 / "theorems" / "sector33_all_residue_height_transport" / "report.json"
FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE = CVX / "reports" / "formula_to_boundary_cycle_family_candidate.json"
ENCODED_FAMILY_FRONTIER = CVX / "reports" / "encoded_family_sat_frontier_certificate.json"
UNIFORM_INVESTIGATION = CVX / "reports" / "uniform_cnf_to_e33_family_encoding_investigation.json"
X_POLICY = CVX / "reports" / "x_policy_boundary_certificate.json"
X_TARGET = CVX / "reports" / "x_extractor_target_certificate.json"


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


def finite_target_summary(all_residue: dict[str, Any]) -> dict[str, Any]:
    derived = all_residue.get("derived", {})
    checks = all_residue.get("checks", {})
    basis_columns = len(derived.get("basis_cycle_height_vector", []))
    residue_count = derived.get("residue_class_count")
    nonzero_count = derived.get("nonzero_residue_class_count")
    return {
        "source": rel(ALL_RESIDUE_TRANSPORT),
        "status": all_residue.get("status"),
        "basis_cycle_coordinate_count": basis_columns,
        "finite_codomain_size": residue_count,
        "nonzero_residual_class_count": nonzero_count,
        "zero_residual_class_count": None
        if residue_count is None or nonzero_count is None
        else residue_count - nonzero_count,
        "support_sector": derived.get("sector33_support", {}).get("sector"),
        "height_transport_formula": all_residue.get("definition", {}).get("global_transport"),
        "checks": {
            "residue_masks_are_complete": checks.get("residue_masks_are_complete"),
            "nonzero_residue_class_count_is_2047": checks.get("nonzero_residue_class_count_is_2047"),
            "zero_class_has_zero_transport_scalar": checks.get("zero_class_has_zero_transport_scalar"),
            "all_transports_carried_by_sector33": checks.get("all_transports_carried_by_sector33"),
            "all_transport_coefficients_match_height_residuals": checks.get(
                "all_transport_coefficients_match_height_residuals"
            ),
        },
    }


def candidate_summary(candidate: dict[str, Any]) -> dict[str, Any]:
    compiler = candidate.get("compiler", {})
    probe = candidate.get("sat_preservation_probe", {})
    summary = candidate.get("compiled_instance_summary", {})
    checks = candidate.get("construction_checks", {})
    return {
        "source": rel(FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE),
        "status": candidate.get("status"),
        "compiler_id": compiler.get("id"),
        "public_only": compiler.get("public_only"),
        "does_not_read_solver_outcome": compiler.get("does_not_read_solver_outcome"),
        "does_not_read_hidden_e33_to_choose_mask": compiler.get("does_not_read_hidden_e33_to_choose_mask"),
        "finite_codomain_size": compiler.get("finite_codomain_size"),
        "output_size_bound": compiler.get("output_size_bound"),
        "rho33_recomputed_from_emitted_circuit_data": checks.get(
            "rho33_transport_recomputed_from_emitted_circuit_data"
        ),
        "truth_diverse_probe_surface_present": checks.get("truth_diverse_probe_surface_present"),
        "sat_preservation_passed": probe.get("passed"),
        "known_truth_instances": probe.get("known_truth_instances"),
        "sat_instances": probe.get("sat_instances"),
        "unsat_instances": probe.get("unsat_instances"),
        "mismatch_count": probe.get("mismatch_count"),
        "false_positive_unsat_as_target_yes_count": probe.get("false_positive_unsat_as_target_yes_count"),
        "false_negative_sat_as_target_no_count": probe.get("false_negative_sat_as_target_no_count"),
        "unique_mask_count_on_probe": summary.get("unique_mask_count"),
        "nonzero_e33_residual_count_on_probe": summary.get("nonzero_e33_residual_count"),
    }


def build_report() -> dict[str, Any]:
    all_residue = load_json(ALL_RESIDUE_TRANSPORT)
    candidate = load_json(FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE)
    frontier = load_json(ENCODED_FAMILY_FRONTIER)
    x_target = load_json(X_TARGET)

    finite_target = finite_target_summary(all_residue)
    compiler_candidate = candidate_summary(candidate)
    transport = x_target.get("target", {}).get("intrinsic_height_coherent_transport", {})

    finite_codomain_size = finite_target["finite_codomain_size"]
    candidate_codomain_size = compiler_candidate["finite_codomain_size"]
    candidate_false_positives = compiler_candidate["false_positive_unsat_as_target_yes_count"] or 0

    collapse_checks = {
        "fixed_finite_codomain_certified": {
            "passed": finite_codomain_size == 2048
            and finite_target["basis_cycle_coordinate_count"] == 11
            and finite_target["checks"]["residue_masks_are_complete"] is True,
            "evidence": {
                "basis_cycle_coordinate_count": finite_target["basis_cycle_coordinate_count"],
                "finite_codomain_size": finite_codomain_size,
                "complete_mask_table": finite_target["checks"]["residue_masks_are_complete"],
            },
        },
        "nonzero_residual_predicate_is_finite_lookup": {
            "passed": finite_target["nonzero_residual_class_count"] == 2047
            and finite_target["zero_residual_class_count"] == 1,
            "evidence": {
                "yes_table_size": finite_target["nonzero_residual_class_count"],
                "no_table_size": finite_target["zero_residual_class_count"],
                "decider": "mask in certified finite table and residual_integral != 0",
                "lookup_bound": "O(1) after the 2048-row certificate is loaded",
            },
        },
        "public_compiler_lands_inside_finite_table": {
            "passed": candidate_codomain_size == finite_codomain_size
            and candidate.get("compiled_instance_summary", {}).get("all_masks_in_2048_residue_table") is True,
            "evidence": {
                "candidate_codomain_size": candidate_codomain_size,
                "target_codomain_size": finite_codomain_size,
                "all_probe_masks_in_table": candidate.get("compiled_instance_summary", {}).get(
                    "all_masks_in_2048_residue_table"
                ),
            },
        },
        "finite_nonzero_residual_fails_sat_preservation": {
            "passed": compiler_candidate["sat_preservation_passed"] is False and candidate_false_positives > 0,
            "evidence": {
                "truth_diverse_probe_surface_present": compiler_candidate["truth_diverse_probe_surface_present"],
                "mismatch_count": compiler_candidate["mismatch_count"],
                "false_positive_unsat_as_target_yes_count": candidate_false_positives,
                "false_negative_sat_as_target_no_count": compiler_candidate[
                    "false_negative_sat_as_target_no_count"
                ],
            },
        },
        "assignment_payload_absent_from_current_target": {
            "passed": frontier.get("target_family", {}).get("scalable_family_certified") is False,
            "evidence": {
                "frontier_scope": frontier.get("target_family", {}).get("current_scope"),
                "frontier_scalable_family_certified": frontier.get("target_family", {}).get(
                    "scalable_family_certified"
                ),
                "current_target_predicate": candidate.get("sat_preservation_probe", {}).get("target_predicate"),
            },
        },
        "intrinsic_rho33_transport_available_but_not_semantic_sat_relation": {
            "passed": transport.get("derived_from_edge_or_circuit_data") is True,
            "evidence": {
                "formula": transport.get("formula"),
                "derived_from_edge_or_circuit_data": transport.get("derived_from_edge_or_circuit_data"),
                "meaning": (
                    "The height/action-return transport is present; what is missing is the "
                    "assignment-bearing target relation that makes the transport semantic for SAT."
                ),
            },
        },
    }

    target_family_requirements = {
        "parameterized_unbounded_instance_family": {
            "requirement_defined": True,
            "currently_witnessed": False,
            "shape": (
                "Target instances must be indexed by formula size parameters such as variables n, "
                "clauses m, and literal occurrences L; the support cannot be the fixed 2048-mask table."
            ),
        },
        "public_cnf_to_target_packet_compiler": {
            "requirement_defined": True,
            "currently_witnessed": False,
            "shape": (
                "A deterministic public compiler maps DIMACS CNF phi to a target packet E(phi) "
                "without solver outcome, hidden e33 data, or X-extractor advice."
            ),
        },
        "assignment_bearing_witness_relation": {
            "requirement_defined": True,
            "currently_witnessed": False,
            "shape": (
                "Witnesses must contain assignment bits a in {0,1}^n plus local clause/literal "
                "selectors, so accepting target witnesses project back to satisfying assignments."
            ),
        },
        "clause_local_soundness_gates": {
            "requirement_defined": True,
            "currently_witnessed": False,
            "shape": (
                "Each clause gadget must expose a public local check that at least one selected "
                "literal is true under the carried assignment."
            ),
        },
        "intrinsic_height_action_return_transport": {
            "requirement_defined": True,
            "currently_witnessed": False,
            "shape": (
                "rho_33(E(phi), a) must be derived as -A_h(C(phi, a))/dim(Pi_33) e_33 from "
                "emitted edge or basis-cycle circuit data; no certified residual scalar may be inserted."
            ),
        },
        "forall_yes_no_preservation": {
            "requirement_defined": True,
            "currently_witnessed": False,
            "shape": (
                "Completeness: a satisfying assignment for phi builds an accepting target witness. "
                "Soundness: any accepting target witness projects to a satisfying assignment for phi."
            ),
        },
        "inverse_witness_projection": {
            "requirement_defined": True,
            "currently_witnessed": False,
            "shape": (
                "The target witness must include enough public support data to recover the CNF "
                "assignment, rather than only a hidden-sector residual bit."
            ),
        },
        "polynomial_size_and_replay_bounds": {
            "requirement_defined": True,
            "currently_witnessed": False,
            "shape": (
                "The target packet, witness, local replay checks, and height transport must have "
                "size and verification cost polynomial in n + m + L."
            ),
        },
    }

    collapse_certified = all(item["passed"] for item in collapse_checks.values())
    requirements_defined = all(item["requirement_defined"] for item in target_family_requirements.values())

    return {
        "schema": "d20.integrity.assignment_bearing_e33_target_family_obligation.source_drop",
        "status": (
            "ASSIGNMENT_BEARING_E33_TARGET_FAMILY_OBLIGATION_BUILT_FINITE_TARGET_COLLAPSE_CERTIFIED"
            if collapse_certified and requirements_defined
            else "ASSIGNMENT_BEARING_E33_TARGET_FAMILY_OBLIGATION_INCOMPLETE"
        ),
        "claim_level": "finite_target_collapse_certified_parameterized_assignment_family_open",
        "source_audit": {
            "encoded_family_sat_frontier": report_status(
                ENCODED_FAMILY_FRONTIER,
                "ENCODED_FAMILY_SAT_FRONTIER_BLOCKED_UNIFORM_REDUCTION_MISSING",
            ),
            "uniform_cnf_to_e33_family_encoding_investigation": report_status(
                UNIFORM_INVESTIGATION,
                "UNIFORM_CNF_TO_E33_ENCODING_INVESTIGATION_BLOCKED",
            ),
            "formula_to_boundary_cycle_family_candidate": report_status(
                FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE,
                "FORMULA_TO_BOUNDARY_CYCLE_FAMILY_CANDIDATE_BUILT_SAT_PRESERVATION_BLOCKED",
            ),
            "sector33_all_residue_height_transport": report_status(
                ALL_RESIDUE_TRANSPORT,
                "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED",
            ),
            "x_policy_boundary": report_status(X_POLICY, "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X"),
            "x_extractor_target": report_status(
                X_TARGET,
                "X_EXTRACTOR_TARGET_AND_INTRINSIC_TRANSPORT_CERTIFIED_POLYNOMIAL_LOWER_BOUND_OPEN",
            ),
        },
        "finite_d20_target": finite_target,
        "formula_compiler_candidate": compiler_candidate,
        "finite_target_collapse": {
            "summary": (
                "A target predicate depending only on the fixed 11-bit D20 mask is a finite "
                "lookup problem. As a separation route, that is the wrong target: a many-one "
                "reduction from SAT to this finite language would put SAT in P by running the "
                "compiler and table lookup, while the tested nonzero-residual predicate already "
                "fails on UNSAT canaries."
            ),
            "checks": collapse_checks,
            "certified": collapse_certified,
        },
        "required_parameterized_target_family": target_family_requirements,
        "minimum_acceptance_tests_for_next_artifact": [
            "schema names an unbounded parameter n/m/L rather than a fixed D20 mask table",
            "compiler emits target packet from DIMACS only and records no solver outcome",
            "witness relation carries assignment bits and local clause selectors",
            "rho_33 transport is recomputed from emitted edge or circuit data",
            "SAT canaries and UNSAT canaries exercise both completeness and soundness",
            "inverse witness projection recovers a satisfying assignment from every accepting target witness",
            "all size and replay bounds are polynomial in the source formula size",
        ],
        "decision": {
            "may_claim_finite_d20_mask_target_suffices": False,
            "may_claim_finite_target_collapse_certified": collapse_certified,
            "may_claim_parameterized_target_requirements_defined": requirements_defined,
            "may_claim_assignment_bearing_target_constructed": False,
            "may_claim_sat_complete_hidden_e33_family": False,
            "may_claim_p_not_np": False,
            "reason": (
                "The finite D20 mask table is now fenced as a testbed and local gadget source, "
                "not an asymptotic SAT-complete target. Full bridge closure requires an "
                "assignment-bearing parameterized e33 target family with forward and inverse witnesses."
            ),
        },
        "non_claims": [
            "This does not construct the parameterized target family.",
            "This does not certify SAT-completeness.",
            "This does not prove that every possible finite fingerprint fails unless P != NP is assumed.",
            "This does not prove P != NP.",
        ],
        "next_highest_yield_item": {
            "id": "parameterized_e33_target_schema",
            "action": (
                "Implement the machine-checkable schema for E(phi), assignment witnesses, "
                "clause-local gates, and intrinsic rho_33 transport over an unbounded target family."
            ),
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
