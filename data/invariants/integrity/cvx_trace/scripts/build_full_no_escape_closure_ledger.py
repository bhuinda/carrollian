from __future__ import annotations

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
    "encoded_family_scope": CVX / "reports" / "encoded_family_scope_certificate.json",
    "polynomial_trace_compiler_scope": CVX / "reports" / "polynomial_trace_compiler_scope_certificate.json",
    "solver_execution_overhead": CVX / "reports" / "public_dpll_contradiction_4_overhead.json",
    "solver_opcode_totality": CVX / "reports" / "solver_opcode_totality_report.json",
    "universal_trace_typing": CVX / "reports" / "universal_trace_typing_report.json",
    "pure_c_no_escape": CVX / "reports" / "pure_c_no_escape_report.json",
    "x_extractor_bounded_search": CVX / "reports" / "x_extractor_bounded_search_report.json",
    "v_wall_crossing_accounting": CVX / "reports" / "v_wall_crossing_accounting_report.json",
}

FULLY_WITNESSED_STATUSES = {
    "witnessed_for_public_lrat_replay",
    "universal_trace_vocabulary_totality_witnessed_residue_guarded",
}

SCOPED_WITNESSED_STATUSES = {
    "prototype_witnessed_for_public_dpll_fixture",
    "witnessed_for_public_dpll_opcode_surface",
    "witnessed_for_current_accepted_pure_c_traces",
    "bounded_search_no_extractor_found_current_traces",
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
        "solver_opcode_totality": "SOLVER_OPCODE_TOTALITY_WITNESS_PASS",
        "universal_trace_typing": "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
        "pure_c_no_escape": "PURE_C_NO_ESCAPE_WITNESS_PASS",
        "x_extractor_bounded_search": "X_EXTRACTOR_BOUNDED_SEARCH_NO_EXTRACTOR_FOUND",
        "v_wall_crossing_accounting": "V_WALL_CROSSING_ACCOUNTING_NO_V_EVENTS",
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

    ledger = {
        "schema": "d20.integrity.full_no_escape_closure_ledger.v1",
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
        "remaining_gaps": [
            {
                "id": "encoded_family_sat_complete",
                "gap": "The encoded family is now explicitly scoped to representative/current-trace evidence. No SAT-complete or polynomially faithful reduction certificate is present.",
                "needed": items["encoded_family_sat_complete"]["required_artifact"],
            },
            {
                "id": "polynomial_trace_compiler",
                "gap": "The trace compiler is explicitly scoped to a public DPLL fixture. No universal-machine compiler or arbitrary-solver polynomial overhead proof is present.",
                "needed": "Compiler theorem or instrumented universal machine with explicit polynomial overhead for arbitrary polynomial-time solvers.",
            },
            {
                "id": "pure_c_no_escape",
                "gap": "Pure-C no-escape is witnessed for current accepted traces, not for every trace over the universal vocabulary.",
                "needed": items["pure_c_no_escape"]["required_artifact"],
            },
            {
                "id": "x_extractor_lower_bound",
                "gap": "The X search is bounded over current accepted trace artifacts; it is not a polynomial-size lower bound for hidden e33 extractors.",
                "needed": items["x_extractor_lower_bound"]["required_artifact"],
            },
            {
                "id": "v_wall_crossing_accounting",
                "gap": "V accounting is certified for current no-V traces; arbitrary traces with V events still need replayed wall-crossing certificates.",
                "needed": items["v_wall_crossing_accounting"]["required_artifact"],
            },
        ],
        "decision": {
            "may_claim_current_trace_no_escape": current_surface_closed,
            "may_claim_conditional_no_escape": conditional_claim_allowed,
            "may_claim_full_separation": full_claim_allowed,
            "reason": "Full separation remains blocked by unresolved bridge obligations." if not full_claim_allowed else "All bridge obligations are closed.",
        },
        "next_highest_yield_item": {
            "id": "pure_c_no_escape",
            "action": "Lift pure-C no-escape from current accepted traces to the universal trace vocabulary."
        },
    }
    REPORT_PATH.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(ledger["status"])
    return 0 if current_surface_closed else 1


if __name__ == "__main__":
    raise SystemExit(main())
