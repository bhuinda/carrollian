from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
CHECKLIST_PATH = BASE / "p_vs_np_bridge_checklist.json"
FIXTURE_OVERHEAD_REPORT = CVX / "reports" / "public_dpll_contradiction_4_overhead.json"
FIXTURE_TRACE = CVX / "traces" / "public_dpll_contradiction_4.trace.json"
REPORT_PATH = CVX / "reports" / "polynomial_trace_compiler_scope_certificate.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def checklist_item(checklist: dict[str, Any], item_id: str) -> dict[str, Any]:
    for item in checklist["checklist"]:
        if item["id"] == item_id:
            return item
    raise KeyError(item_id)


def fixture_status() -> dict[str, Any]:
    overhead_report = load_json(FIXTURE_OVERHEAD_REPORT)
    trace = load_json(FIXTURE_TRACE)
    polynomial_bound = overhead_report.get("overhead", {}).get("polynomial_bound", {})
    trace_summary = trace.get("summary", {})
    fixture_passed = (
        overhead_report.get("status") == "CVX_SOLVER_EXECUTION_TRACE_OVERHEAD_PASS"
        and polynomial_bound.get("within_bound") is True
        and trace_summary.get("all_events_classified") is True
        and trace_summary.get("pure_c_trace") is True
    )
    return {
        "trace_path": rel(FIXTURE_TRACE),
        "overhead_report": rel(FIXTURE_OVERHEAD_REPORT),
        "overhead_status": overhead_report.get("status"),
        "result": overhead_report.get("result"),
        "input_measures": overhead_report.get("overhead", {}).get("input_measures"),
        "actual_trace_cost": overhead_report.get("overhead", {}).get("actual_trace_cost"),
        "polynomial_bound": polynomial_bound,
        "trace_summary": trace_summary,
        "fixture_passed": fixture_passed,
    }


def main() -> int:
    checklist = load_json(CHECKLIST_PATH)
    compiler_item = checklist_item(checklist, "polynomial_trace_compiler")
    fixture = fixture_status()

    universal_machine_defined = False
    arbitrary_solver_compiler_certified = False
    polynomial_overhead_for_arbitrary_solvers_certified = False
    fixture_scope_declared = fixture["fixture_passed"]

    certificate = {
        "schema": "d20.integrity.polynomial_trace_compiler_scope_certificate.v1",
        "status": "POLYNOMIAL_TRACE_COMPILER_SCOPE_DECLARED_FIXTURE_ONLY",
        "claim_level": "public_dpll_fixture_trace_compiler_only",
        "checklist_path": rel(CHECKLIST_PATH),
        "checklist_item": {
            "id": compiler_item["id"],
            "obligation": compiler_item["obligation"],
            "required_artifact": compiler_item["required_artifact"],
            "pass_condition": compiler_item["pass_condition"],
            "checklist_status": compiler_item.get("status"),
        },
        "fixture_witness": fixture,
        "universal_compiler_bridge": {
            "universal_machine_defined": universal_machine_defined,
            "arbitrary_solver_compiler_certified": arbitrary_solver_compiler_certified,
            "polynomial_overhead_for_arbitrary_solvers_certified": polynomial_overhead_for_arbitrary_solvers_certified,
            "certified_bridge_present": (
                universal_machine_defined
                and arbitrary_solver_compiler_certified
                and polynomial_overhead_for_arbitrary_solvers_certified
            ),
            "reason": "The current executable evidence instruments one deterministic public unit-propagation DPLL fixture. It does not define a universal trace vocabulary or prove a polynomial-overhead compiler for arbitrary polynomial-time solvers.",
        },
        "declared_scope": {
            "fixture_scope_declared": fixture_scope_declared,
            "meaning": "The current compiler evidence witnesses the trace shape and polynomial overhead accounting for the accepted public DPLL fixture only.",
            "non_claim": "This certificate does not prove arbitrary solver universality, total typing for a universal machine, a no-escape theorem for all polynomial-time solvers, or P != NP.",
        },
        "decision": {
            "may_claim_public_dpll_fixture_trace_compiler": fixture_scope_declared,
            "may_claim_arbitrary_polynomial_solver_trace_compiler": False,
            "may_claim_full_separation": False,
            "reason": "Arbitrary solver universality remains open until a universal machine trace compiler and polynomial overhead proof are present.",
        },
        "promotion_requirements": [
            "choose the universal execution model to trace, such as RAM, Turing machine, or circuit evaluator",
            "define the public trace vocabulary for every instruction or gate family",
            "implement instrumentation from executions into C/V/X trace events",
            "prove the trace length is polynomial in the original solver runtime and input size",
            "prove each event is locally checkable with polynomial verification cost",
            "prove the trace preserves the solver decision result",
            "connect the universal trace vocabulary to total C/V/X typing with residue fallback",
        ],
        "next_highest_yield_item": {
            "id": "pure_c_no_escape",
            "action": "Lift pure-C no-escape from current accepted traces to the universal trace vocabulary.",
        },
    }

    REPORT_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(certificate["status"])
    return 0 if fixture_scope_declared else 1


if __name__ == "__main__":
    raise SystemExit(main())
