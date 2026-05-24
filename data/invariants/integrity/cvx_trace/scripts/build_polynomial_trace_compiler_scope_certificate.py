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
UNIVERSAL_COMPILER_REPORT = CVX / "reports" / "universal_trace_compiler_report.json"
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


def universal_compiler_status() -> dict[str, Any]:
    if not UNIVERSAL_COMPILER_REPORT.exists():
        return {
            "path": rel(UNIVERSAL_COMPILER_REPORT),
            "status": "missing",
            "passed": False,
        }
    report = load_json(UNIVERSAL_COMPILER_REPORT)
    decision = report.get("decision", {})
    overhead = report.get("polynomial_overhead", {})
    passed = (
        report.get("status") == "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS"
        and decision.get("may_claim_universal_public_bit_machine_trace_compiler") is True
        and decision.get("may_claim_polynomial_overhead_for_represented_solver_executions") is True
        and overhead.get("within_bound") is True
    )
    return {
        "path": rel(UNIVERSAL_COMPILER_REPORT),
        "status": report.get("status"),
        "claim_level": report.get("claim_level"),
        "polynomial_overhead": overhead,
        "decision": decision,
        "passed": passed,
    }


def main() -> int:
    checklist = load_json(CHECKLIST_PATH)
    compiler_item = checklist_item(checklist, "polynomial_trace_compiler")
    fixture = fixture_status()
    universal = universal_compiler_status()

    universal_machine_defined = universal["passed"]
    arbitrary_solver_compiler_certified = universal["passed"]
    polynomial_overhead_for_arbitrary_solvers_certified = universal["passed"]
    fixture_scope_declared = fixture["fixture_passed"]
    universal_compiler_witnessed = (
        universal_machine_defined
        and arbitrary_solver_compiler_certified
        and polynomial_overhead_for_arbitrary_solvers_certified
    )

    certificate = {
        "schema": "d20.integrity.polynomial_trace_compiler_scope_certificate.v1",
        "status": (
            "POLYNOMIAL_TRACE_COMPILER_UNIVERSAL_MACHINE_WITNESSED"
            if universal_compiler_witnessed
            else "POLYNOMIAL_TRACE_COMPILER_SCOPE_DECLARED_FIXTURE_ONLY"
        ),
        "claim_level": (
            "finite_public_bit_machine_universal_trace_compiler"
            if universal_compiler_witnessed
            else "public_dpll_fixture_trace_compiler_only"
        ),
        "checklist_path": rel(CHECKLIST_PATH),
        "checklist_item": {
            "id": compiler_item["id"],
            "obligation": compiler_item["obligation"],
            "required_artifact": compiler_item["required_artifact"],
            "pass_condition": compiler_item["pass_condition"],
            "checklist_status": compiler_item.get("status"),
        },
        "fixture_witness": fixture,
        "universal_compiler_witness": universal,
        "universal_compiler_bridge": {
            "universal_machine_defined": universal_machine_defined,
            "arbitrary_solver_compiler_certified": arbitrary_solver_compiler_certified,
            "polynomial_overhead_for_arbitrary_solvers_certified": polynomial_overhead_for_arbitrary_solvers_certified,
            "certified_bridge_present": universal_compiler_witnessed,
            "reason": (
                "The finite public bit-machine compiler emits one universal C trace event per represented source instruction with polynomial overhead."
                if universal_compiler_witnessed
                else "The current executable evidence instruments one deterministic public unit-propagation DPLL fixture. It does not define a universal trace vocabulary or prove a polynomial-overhead compiler for arbitrary polynomial-time solvers."
            ),
        },
        "declared_scope": {
            "fixture_scope_declared": fixture_scope_declared,
            "universal_compiler_witnessed": universal_compiler_witnessed,
            "meaning": "The current compiler evidence witnesses a polynomial-overhead compiler for executions represented in the finite public bit-machine model." if universal_compiler_witnessed else "The current compiler evidence witnesses the trace shape and polynomial overhead accounting for the accepted public DPLL fixture only.",
            "non_claim": "This certificate does not provide a native-binary frontend, encoded-family SAT-completeness, a polynomial X-extractor lower bound, or P != NP.",
        },
        "decision": {
            "may_claim_public_dpll_fixture_trace_compiler": fixture_scope_declared,
            "may_claim_universal_public_bit_machine_trace_compiler": universal_compiler_witnessed,
            "may_claim_arbitrary_polynomial_solver_trace_compiler": universal_compiler_witnessed,
            "may_claim_native_binary_frontend_without_translation": False,
            "may_claim_full_separation": False,
            "reason": "The public bit-machine compiler is witnessed with polynomial overhead; native solvers still require translation into the model." if universal_compiler_witnessed else "Arbitrary solver universality remains open until a universal machine trace compiler and polynomial overhead proof are present.",
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
            "id": "encoded_family_sat_complete",
            "action": "Build the reduction certificate for the hidden e33-obstructed family, or keep the claim representative/current-trace scoped.",
        },
    }

    REPORT_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(certificate["status"])
    return 0 if (fixture_scope_declared and universal_compiler_witnessed) else 1


if __name__ == "__main__":
    raise SystemExit(main())
