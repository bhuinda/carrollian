from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
CHECKLIST_PATH = BASE / "p_vs_np_bridge_checklist.json"
REPORT_PATH = CVX / "reports" / "full_no_escape_closure_ledger.json"

REPORTS = {
    "cvx_trace_index": CVX / "index.json",
    "assignment_bearing_e33_target_family_obligation": CVX
    / "reports"
    / "assignment_bearing_e33_target_family_obligation.json",
    "encoded_family_bridge": CVX / "reports" / "encoded_family_bridge_certificate.json",
    "encoded_family_sat_frontier": CVX / "reports" / "encoded_family_sat_frontier_certificate.json",
    "uniform_cnf_to_e33_family_encoding_investigation": CVX
    / "reports"
    / "uniform_cnf_to_e33_family_encoding_investigation.json",
    "formula_to_boundary_cycle_family_candidate": CVX
    / "reports"
    / "formula_to_boundary_cycle_family_candidate.json",
    "parameterized_e33_target_schema": CVX / "reports" / "parameterized_e33_target_schema_certificate.json",
    "cnf_to_parameterized_e33_packet_compiler": CVX
    / "reports"
    / "cnf_to_parameterized_e33_packet_compiler_certificate.json",
    "forall_yes_no_preservation_theorem": CVX / "reports" / "forall_yes_no_preservation_theorem.json",
    "encoded_family_scope": CVX / "reports" / "encoded_family_scope_certificate.json",
    "polynomial_trace_compiler_scope": CVX / "reports" / "polynomial_trace_compiler_scope_certificate.json",
    "universal_trace_compiler": CVX / "reports" / "universal_trace_compiler_report.json",
    "solver_execution_overhead": CVX / "reports" / "public_dpll_contradiction_4_overhead.json",
    "solver_opcode_totality": CVX / "reports" / "solver_opcode_totality_report.json",
    "universal_trace_typing": CVX / "reports" / "universal_trace_typing_report.json",
    "pure_c_no_escape": CVX / "reports" / "pure_c_no_escape_report.json",
    "universal_pure_c_no_escape": CVX / "reports" / "universal_pure_c_no_escape_report.json",
    "x_extractor_bounded_search": CVX / "reports" / "x_extractor_bounded_search_report.json",
    "universal_x_extractor_isolation": CVX / "reports" / "universal_x_extractor_isolation_report.json",
    "x_extractor_target": CVX / "reports" / "x_extractor_target_certificate.json",
    "x_extractor_frontier": CVX / "reports" / "x_extractor_frontier_certificate.json",
    "x_policy_boundary": CVX / "reports" / "x_policy_boundary_certificate.json",
    "v_wall_crossing_accounting": CVX / "reports" / "v_wall_crossing_accounting_report.json",
    "universal_v_wall_crossing_accounting": CVX / "reports" / "universal_v_wall_crossing_accounting_report.json",
}

FULLY_WITNESSED_STATUSES = {
    "witnessed_for_public_lrat_replay",
    "universal_trace_vocabulary_totality_witnessed_residue_guarded",
    "universal_trace_pure_c_no_escape_witnessed",
    "universal_v_surface_accounted_certificate_guarded",
    "universal_public_bit_machine_trace_compiler_witnessed",
    "formal_x_policy_boundary_certified_x_not_public_p",
    "encoded_family_sat_complete_reduction_certified",
    "dependency_ledger_built_full_closure_closed",
}

SCOPED_WITNESSED_STATUSES = {
    "explicit_hidden_sector_map_certified_polynomial_lower_bound_open",
    "intrinsic_height_transport_certified_polynomial_lower_bound_open",
    "explicit_polynomial_x_extractor_promoted_family_scope",
    "polynomially_faithful_representative_family_witnessed_sat_complete_open",
    "prototype_witnessed_for_public_dpll_fixture",
    "witnessed_for_public_dpll_opcode_surface",
    "witnessed_for_current_accepted_pure_c_traces",
    "bounded_search_no_extractor_found_current_traces",
    "universal_x_surface_isolated_polynomial_lower_bound_open",
    "no_v_events_current_traces_certificate_schema_defined",
}

SCOPED_DECLARATION_STATUSES = {
    "representative_family_scope_declared_sat_complete_open",
    "fixture_scope_declared_universal_compiler_open",
}

LEDGER_STATUSES = {
    "dependency_ledger_built_full_closure_blocked",
}

OPEN_STATUSES = {
    "open",
    "blocked_by_open_obligations",
    "assignment_bearing_target_obligation_built_reduction_open",
    "parameterized_e33_target_schema_defined_reduction_open",
    "cnf_to_parameterized_e33_packet_compiler_built_forall_theorem_open",
    "sat_complete_frontier_blocked_uniform_reduction_missing",
    "formula_to_boundary_cycle_candidate_built_sat_preservation_blocked",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def checklist_items(checklist: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in checklist["checklist"]}


def classify_item(item: dict[str, Any]) -> dict[str, Any]:
    status = item.get("status", "")
    if status in FULLY_WITNESSED_STATUSES:
        closure_level = "witnessed"
        blocks_full_closure = False
    elif status in SCOPED_WITNESSED_STATUSES:
        closure_level = "scoped_witness"
        blocks_full_closure = True
    elif status in SCOPED_DECLARATION_STATUSES:
        closure_level = "scope_declaration"
        blocks_full_closure = True
    elif status in LEDGER_STATUSES:
        closure_level = "dependency_ledger"
        blocks_full_closure = True
    elif status in OPEN_STATUSES:
        closure_level = "open"
        blocks_full_closure = True
    else:
        closure_level = "unknown"
        blocks_full_closure = True
    return {
        "id": item["id"],
        "status": status,
        "closure_level": closure_level,
        "blocks_full_closure": blocks_full_closure,
        "witness": item.get("witness"),
        "scope_warning": item.get("scope_warning"),
    }


def report_statuses() -> dict[str, Any]:
    statuses: dict[str, Any] = {}
    for key, path in REPORTS.items():
        data = load_json(path)
        statuses[key] = {
            "path": rel(path),
            "status": data.get("status"),
        }
    return statuses


def current_trace_surface_closed(statuses: dict[str, Any]) -> bool:
    expected = {
        "solver_execution_overhead": "CVX_SOLVER_EXECUTION_TRACE_OVERHEAD_PASS",
        "universal_trace_compiler": "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
        "solver_opcode_totality": "SOLVER_OPCODE_TOTALITY_WITNESS_PASS",
        "universal_trace_typing": "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
        "pure_c_no_escape": "PURE_C_NO_ESCAPE_WITNESS_PASS",
        "universal_pure_c_no_escape": "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS",
        "x_extractor_bounded_search": "X_EXTRACTOR_BOUNDED_SEARCH_NO_EXTRACTOR_FOUND",
        "universal_x_extractor_isolation": "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS",
        "x_policy_boundary": "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
        "v_wall_crossing_accounting": "V_WALL_CROSSING_ACCOUNTING_NO_V_EVENTS",
        "universal_v_wall_crossing_accounting": "UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_PASS",
    }
    return all(statuses[key]["status"] == value for key, value in expected.items())


def main() -> int:
    checklist = load_json(CHECKLIST_PATH)
    items = checklist_items(checklist)
    classified = [classify_item(item) for item in checklist["checklist"]]
    statuses = report_statuses()
    current_surface_closed = current_trace_surface_closed(statuses)

    hard_blockers = []
    scope_declaration_blockers = []
    scoped_blockers = []
    for item in classified:
        if item["id"] == "full_no_escape_closure":
            continue
        if item["closure_level"] == "open":
            hard_blockers.append(item)
        elif item["closure_level"] == "scope_declaration":
            scope_declaration_blockers.append(item)
        elif item["blocks_full_closure"]:
            scoped_blockers.append(item)

    blocker_ids = [item["id"] for item in hard_blockers + scope_declaration_blockers + scoped_blockers]
    full_claim_allowed = not blocker_ids and current_surface_closed
    conditional_claim_allowed = current_surface_closed
    classified_by_id = {item["id"]: item for item in classified}
    remaining_gaps = []
    if classified_by_id["encoded_family_sat_complete"]["blocks_full_closure"]:
        remaining_gaps.append(
            {
                "id": "encoded_family_sat_complete",
                "gap": "A public formula-to-boundary-cycle compiler candidate emits D20 masks and recomputes rho_33 from circuit data, but it is a finite nonzero-residual fingerprint and fails SAT preservation. The finite target is fenced as a lookup testbed. The parameterized E(phi) schema names assignment witnesses, clause-local gates, inverse projection, and intrinsic rho_33 transport. The public DIMACS-to-E(phi) compiler now builds packets and the supplied-witness replay checker passes bounded SAT/UNSAT canaries. Full closure still needs a forall-instance yes/no preservation theorem, inverse witness theorem, and no-hidden-advice proof for the reduction algorithm.",
                "needed": items["encoded_family_sat_complete"]["required_artifact"],
                "assignment_target_obligation_witness": items["encoded_family_sat_complete"].get(
                    "assignment_target_obligation_witness"
                ),
                "parameterized_target_schema_witness": items["encoded_family_sat_complete"].get(
                    "parameterized_target_schema_witness"
                ),
                "compiler_witness": items["encoded_family_sat_complete"].get("compiler_witness"),
                "candidate_witness": items["encoded_family_sat_complete"].get("candidate_witness"),
                "investigation_witness": items["encoded_family_sat_complete"].get("investigation_witness"),
            }
        )
    if classified_by_id["x_extractor_lower_bound"]["blocks_full_closure"]:
        remaining_gaps.append(
            {
                "id": "x_extractor_lower_bound",
                "gap": "The family-scope polynomial X extractor is promoted from the certified height-coherent transport, so full closure requires the X policy boundary to exclude X from public-P computation or explicitly change models.",
                "needed": items["x_extractor_lower_bound"]["required_artifact"],
            }
        )

    if classified_by_id["encoded_family_sat_complete"]["blocks_full_closure"]:
        next_item = {
            "id": "forall_yes_no_preservation_theorem",
            "action": "Promote the compiler/replay construction to a theorem: for every CNF phi, phi is satisfiable iff there exists an accepting E(phi) assignment witness, with inverse projection.",
        }
    elif full_claim_allowed:
        next_item = {
            "id": "external_formal_audit_pack",
            "action": "Package the closed dependency ledger, theorem certificates, and minimal replay commands for external formal audit.",
        }
    else:
        next_item = {
            "id": "full_no_escape_closure",
            "action": "Promote the dependency ledger to a closed no-escape theorem after all bridge obligations are witnessed.",
        }

    ledger = {
        "schema": "d20.integrity.full_no_escape_closure_ledger.source_drop",
        "status": (
            "FULL_NO_ESCAPE_CLOSURE_LEDGER_BUILT_CLOSED"
            if full_claim_allowed
            else "FULL_NO_ESCAPE_CLOSURE_LEDGER_BUILT_BLOCKED"
        ),
        "claim_level": "dependency_ledger_not_full_separation" if not full_claim_allowed else "full_no_escape_candidate",
        "checklist_path": rel(CHECKLIST_PATH),
        "report_statuses": statuses,
        "checklist_items": classified,
        "current_accepted_trace_surface": {
            "status": "closed_for_current_accepted_traces" if current_surface_closed else "requires_review",
            "closed": current_surface_closed,
            "meaning": "The current accepted trace artifacts pass schema, totality, pure-C no-escape, bounded X search, and V accounting checks.",
        },
        "full_no_escape_claim": {
            "allowed": full_claim_allowed,
            "conditional_claim_allowed": conditional_claim_allowed,
            "blocked_by": blocker_ids,
            "hard_open_blockers": [item["id"] for item in hard_blockers],
            "scope_declaration_blockers": [item["id"] for item in scope_declaration_blockers],
            "scoped_witness_blockers": [item["id"] for item in scoped_blockers],
        },
        "remaining_gaps": remaining_gaps,
        "decision": {
            "may_claim_current_trace_no_escape": current_surface_closed,
            "may_claim_conditional_no_escape": conditional_claim_allowed,
            "may_claim_full_separation": full_claim_allowed,
            "reason": "Full separation remains blocked by unresolved bridge obligations." if not full_claim_allowed else "All bridge obligations are closed.",
        },
        "next_highest_yield_item": next_item,
    }
    REPORT_PATH.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(ledger["status"])
    return 0 if current_surface_closed else 1


if __name__ == "__main__":
    raise SystemExit(main())
