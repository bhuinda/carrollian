from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
CHECKLIST_PATH = BASE / "p_vs_np_bridge_checklist.json"
REPORT_PATH = CVX / "reports" / "encoded_family_scope_certificate.json"
BRIDGE_REPORT_PATH = CVX / "reports" / "encoded_family_bridge_certificate.json"

CURRENT_TRACE_REPORTS = {
    "solver_execution_overhead": CVX / "reports" / "public_dpll_contradiction_4_overhead.json",
    "solver_opcode_totality": CVX / "reports" / "solver_opcode_totality_report.json",
    "pure_c_no_escape": CVX / "reports" / "pure_c_no_escape_report.json",
    "x_extractor_bounded_search": CVX / "reports" / "x_extractor_bounded_search_report.json",
    "v_wall_crossing_accounting": CVX / "reports" / "v_wall_crossing_accounting_report.json",
}

EXPECTED_CURRENT_TRACE_STATUSES = {
    "solver_execution_overhead": "CVX_SOLVER_EXECUTION_TRACE_OVERHEAD_PASS",
    "solver_opcode_totality": "SOLVER_OPCODE_TOTALITY_WITNESS_PASS",
    "pure_c_no_escape": "PURE_C_NO_ESCAPE_WITNESS_PASS",
    "x_extractor_bounded_search": "X_EXTRACTOR_BOUNDED_SEARCH_NO_EXTRACTOR_FOUND",
    "v_wall_crossing_accounting": "V_WALL_CROSSING_ACCOUNTING_NO_V_EVENTS",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def checklist_item(checklist: dict[str, Any], item_id: str) -> dict[str, Any]:
    for item in checklist["checklist"]:
        if item["id"] == item_id:
            return item
    raise KeyError(item_id)


def current_trace_report_statuses() -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for key, path in CURRENT_TRACE_REPORTS.items():
        data = load_json(path)
        expected = EXPECTED_CURRENT_TRACE_STATUSES[key]
        statuses[key] = {
            "path": rel(path),
            "status": data.get("status"),
            "expected_status": expected,
            "passed": data.get("status") == expected,
        }
    return statuses


def current_trace_surface_closed(statuses: dict[str, dict[str, Any]]) -> bool:
    return all(item["passed"] for item in statuses.values())


def bridge_report_status() -> dict[str, Any]:
    if not BRIDGE_REPORT_PATH.exists():
        return {
            "path": rel(BRIDGE_REPORT_PATH),
            "status": "missing",
            "may_claim_polynomially_faithful_representative_family": False,
            "may_claim_encoded_family_sat_complete": False,
            "passed": False,
        }
    data = load_json(BRIDGE_REPORT_PATH)
    decision = data.get("decision", {})
    return {
        "path": rel(BRIDGE_REPORT_PATH),
        "status": data.get("status"),
        "may_claim_polynomially_faithful_representative_family": decision.get(
            "may_claim_polynomially_faithful_representative_family", False
        ),
        "may_claim_encoded_family_sat_complete": decision.get("may_claim_encoded_family_sat_complete", False),
        "passed": data.get("status") == "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
    }


def main() -> int:
    checklist = load_json(CHECKLIST_PATH)
    encoded_item = checklist_item(checklist, "encoded_family_sat_complete")
    report_statuses = current_trace_report_statuses()
    trace_surface_closed = current_trace_surface_closed(report_statuses)
    bridge_status = bridge_report_status()

    sat_complete_reduction_certified = bool(bridge_status["may_claim_encoded_family_sat_complete"])
    polynomially_faithful_representative_certified = bool(
        bridge_status["may_claim_polynomially_faithful_representative_family"]
    )
    representative_current_trace_scope_declared = True
    may_claim_representative_current_trace_no_escape = (
        representative_current_trace_scope_declared
        and trace_surface_closed
    )
    may_claim_encoded_family_bridge = (
        sat_complete_reduction_certified
        or polynomially_faithful_representative_certified
    )

    certificate = {
        "schema": "d20.integrity.encoded_family_scope_certificate.source_drop",
        "status": (
            "ENCODED_FAMILY_SCOPE_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN"
            if polynomially_faithful_representative_certified
            else "ENCODED_FAMILY_SCOPE_DECLARED_REPRESENTATIVE_ONLY"
        ),
        "claim_level": (
            "polynomially_faithful_representative_family_not_sat_complete"
            if polynomially_faithful_representative_certified
            else "representative_current_trace_family_only"
        ),
        "checklist_path": rel(CHECKLIST_PATH),
        "checklist_item": {
            "id": encoded_item["id"],
            "obligation": encoded_item["obligation"],
            "required_artifact": encoded_item["required_artifact"],
            "pass_condition": encoded_item["pass_condition"],
            "checklist_status": encoded_item.get("status"),
        },
        "encoded_family_bridge": {
            "bridge_report": bridge_status,
            "sat_complete_reduction_certified": sat_complete_reduction_certified,
            "polynomially_faithful_representative_certified": polynomially_faithful_representative_certified,
            "certified_bridge_present": may_claim_encoded_family_bridge,
            "reason": (
                "A polynomially bounded representative-family bridge is present for the cycle-8 / Pi_33 residual packet, but no SAT-complete reduction is certified."
                if polynomially_faithful_representative_certified
                else "No reduction certificate with source problem, target encoding, polynomial size bound, yes/no preservation, and inverse witness interpretation is present in the canonical integrity data."
            ),
        },
        "declared_scope": {
            "representative_current_trace_scope_declared": representative_current_trace_scope_declared,
            "meaning": (
                "The current evidence now includes a representative-family bridge for the certified sector-33 residual packet, not a SAT-complete family bridge."
                if polynomially_faithful_representative_certified
                else "The current evidence may be read as a representative/current-trace no-escape certificate for the accepted public proof-log and public DPLL fixtures, not as a SAT-complete family bridge."
            ),
            "non_claim": "This certificate does not prove SAT-completeness, an X-extractor lower bound, or P != NP.",
        },
        "current_trace_surface": {
            "closed": trace_surface_closed,
            "report_statuses": report_statuses,
        },
        "decision": {
            "may_claim_representative_current_trace_no_escape": may_claim_representative_current_trace_no_escape,
            "may_claim_encoded_family_sat_complete": sat_complete_reduction_certified,
            "may_claim_polynomially_faithful_representative_family": polynomially_faithful_representative_certified,
            "may_claim_full_separation": False,
            "reason": (
                "The encoded-family bridge is witnessed at representative-family scope, but SAT-completeness and the X-extractor lower bound remain open."
                if polynomially_faithful_representative_certified
                else "The encoded-family bridge is explicitly downgraded to representative/current-trace scope until a real reduction or polynomial-faithfulness certificate is added."
            ),
        },
        "promotion_requirements": [
            "name the source SAT-complete problem or source family",
            "define the target hidden e33-obstructed encoding",
            "prove a polynomial size and construction-time bound",
            "prove yes/no instance preservation",
            "provide inverse witness interpretation",
            "prove that the reduction uses no hidden-sector advice",
            "connect the reduction certificate to the C/V/X trace and no-escape ledger",
        ],
        "next_highest_yield_item": {
            "id": "x_extractor_lower_bound" if polynomially_faithful_representative_certified else "encoded_family_sat_complete",
            "action": (
                "Attack the polynomial-size X-extractor lower bound; the encoded-family bridge is now witnessed only at representative-family scope."
                if polynomially_faithful_representative_certified
                else "Build the reduction certificate for the hidden e33-obstructed family, or keep the claim representative/current-trace scoped."
            ),
        },
    }

    REPORT_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(certificate["status"])
    return 0 if may_claim_representative_current_trace_no_escape else 1


if __name__ == "__main__":
    raise SystemExit(main())
