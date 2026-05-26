from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
CNF_PATH = ROOT / "data" / "evidence" / "ss_sat" / "benchmarks" / "contradiction_4.cnf"
TRACE_PATH = BASE / "traces" / "public_dpll_contradiction_4.trace.json"
REPORT_PATH = BASE / "reports" / "public_dpll_contradiction_4_overhead.json"
SCHEMA_PATH = BASE / "schemas" / "cvx_trace.schema.json"
VALIDATOR = BASE / "scripts" / "validate_cvx_trace.py"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_dimacs(path: Path) -> tuple[int, list[list[int]]]:
    variables = 0
    clauses: list[list[int]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            variables = int(parts[2])
            continue
        lits = [int(x) for x in line.split() if int(x) != 0]
        clauses.append(lits)
    if variables <= 0 or not clauses:
        raise ValueError("invalid DIMACS fixture")
    return variables, clauses


def event(
    *,
    n: int,
    kind: str,
    clause_id: int,
    literals: list[int],
    assignment: dict[int, bool],
    reason: str,
    empty_clause: bool = False,
) -> dict[str, Any]:
    return {
        "event_id": f"public-dpll-contradiction-4:{n:04d}",
        "line": n,
        "proof_id": n,
        "op": "solver_opcode",
        "integrity_type": "C",
        "class_code": kind,
        "reason": reason,
        "public_inputs": {
            "clause_hints": [clause_id],
            "literals": literals,
        },
        "public_outputs": {
            "clause_id": n,
            "literal_count": len(literals),
            "empty_clause": empty_clause,
        },
        "checks": {
            "uses_extension_variable": False,
            "has_duplicate_literal": len(set(literals)) != len(literals),
            "contains_complement_pair": any(-lit in literals for lit in literals),
            "locally_checkable": True,
        },
        "_assignment": dict(sorted((str(k), v) for k, v in assignment.items())),
    }


def visible_event(e: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(e)
    cleaned.pop("_assignment", None)
    return cleaned


def unit_propagation_trace(variables: int, clauses: list[list[int]]) -> tuple[list[dict[str, Any]], str]:
    assignment: dict[int, bool] = {}
    events: list[dict[str, Any]] = []
    event_no = 1
    changed = True
    while changed:
        changed = False
        for clause_index, clause in enumerate(clauses, start=1):
            events.append(
                event(
                    n=event_no,
                    kind="C_PUBLIC_DPLL_SCAN_CLAUSE",
                    clause_id=clause_index,
                    literals=clause,
                    assignment=assignment,
                    reason="public DPLL scans a public DIMACS clause under the current partial assignment",
                )
            )
            event_no += 1

            satisfied = False
            undecided: list[int] = []
            for lit in clause:
                var = abs(lit)
                value = assignment.get(var)
                if value is None:
                    undecided.append(lit)
                elif value == (lit > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not undecided:
                events.append(
                    event(
                        n=event_no,
                        kind="C_PUBLIC_DPLL_EMPTY_CLAUSE_CONFLICT",
                        clause_id=clause_index,
                        literals=[],
                        assignment=assignment,
                        reason="public unit propagation derives an empty clause conflict",
                        empty_clause=True,
                    )
                )
                return events, "UNSAT"
            if len(undecided) == 1:
                lit = undecided[0]
                var = abs(lit)
                value = lit > 0
                current = assignment.get(var)
                if current is None:
                    assignment[var] = value
                    changed = True
                    events.append(
                        event(
                            n=event_no,
                            kind="C_PUBLIC_DPLL_UNIT_ASSIGN",
                            clause_id=clause_index,
                            literals=[lit],
                            assignment=assignment,
                            reason="public unit clause assigns a public DIMACS variable",
                        )
                    )
                    event_no += 1
                elif current != value:
                    events.append(
                        event(
                            n=event_no,
                            kind="C_PUBLIC_DPLL_UNIT_CONFLICT",
                            clause_id=clause_index,
                            literals=[lit],
                            assignment=assignment,
                            reason="public unit propagation detects contradictory public assignments",
                            empty_clause=True,
                        )
                    )
                    return events, "UNSAT"
    return events, "UNKNOWN"


def overhead(variables: int, clauses: list[list[int]], events: list[dict[str, Any]]) -> dict[str, Any]:
    literal_occurrences = sum(len(c) for c in clauses)
    event_count = len(events)
    scan_events = sum(1 for e in events if e["class_code"] == "C_PUBLIC_DPLL_SCAN_CLAUSE")
    assignment_events = sum(1 for e in events if e["class_code"] == "C_PUBLIC_DPLL_UNIT_ASSIGN")
    return {
        "input_measures": {
            "variables": variables,
            "clauses": len(clauses),
            "literal_occurrences": literal_occurrences,
        },
        "actual_trace_cost": {
            "event_count": event_count,
            "scan_events": scan_events,
            "assignment_events": assignment_events,
            "max_event_payload_literals": max(len(e["public_inputs"]["literals"]) for e in events),
        },
        "polynomial_bound": {
            "bound_name": "unit_propagation_public_dpll_fixture_bound",
            "event_count_bound": "(variables + 1) * clauses + variables",
            "event_count_bound_value": (variables + 1) * len(clauses) + variables,
            "event_verification_cost_bound": "O(event_count * max_clause_width)",
            "max_clause_width": max(len(c) for c in clauses),
            "within_bound": event_count <= ((variables + 1) * len(clauses) + variables),
        },
        "scope": "Prototype bound for deterministic public unit-propagation DPLL on this fixture; this is not the arbitrary polynomial-time universality theorem.",
    }


def main() -> int:
    variables, clauses = parse_dimacs(CNF_PATH)
    raw_events, result = unit_propagation_trace(variables, clauses)
    events = [visible_event(e) for e in raw_events]
    counts = {"C": len(events), "V": 0, "X": 0, "UNCLASSIFIED": 0}
    trace = {
        "schema": "d20.integrity.cvx_trace.source_drop",
        "status": "CVX_SOLVER_EXECUTION_TRACE_WITNESS",
        "trace_id": "public_dpll_contradiction_4",
        "source": {
            "proof_format": "solver_opcode",
            "cnf_path": rel(CNF_PATH),
            "cnf_sha256": sha256(CNF_PATH),
            "classifier_source": rel(Path(__file__).resolve()),
        },
        "integrity_model": {
            "allowed_types": ["C", "V", "X", "UNCLASSIFIED"],
            "accepted_public_types": ["C"],
            "unsupported_event_policy": "reject_or_emit_typed_residue",
        },
        "events": events,
        "summary": {
            "event_count": len(events),
            "integrity_counts": counts,
            "verdict": f"C_PUBLIC_DPLL_{result}",
            "all_events_classified": True,
            "pure_c_trace": True,
        },
    }
    overhead_report = {
        "schema": "d20.integrity.solver_trace_overhead.source_drop",
        "status": "CVX_SOLVER_EXECUTION_TRACE_OVERHEAD_PASS",
        "trace_path": rel(TRACE_PATH),
        "schema_path": rel(SCHEMA_PATH),
        "source_cnf": rel(CNF_PATH),
        "result": result,
        "integrity_counts": counts,
        "overhead": overhead(variables, clauses, events),
    }
    if not overhead_report["overhead"]["polynomial_bound"]["within_bound"]:
        overhead_report["status"] = "CVX_SOLVER_EXECUTION_TRACE_OVERHEAD_FAIL"

    TRACE_PATH.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(overhead_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(overhead_report["status"])
    return 0 if overhead_report["status"].endswith("_PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
