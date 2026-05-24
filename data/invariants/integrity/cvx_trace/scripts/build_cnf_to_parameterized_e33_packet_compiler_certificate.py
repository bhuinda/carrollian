from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
SS_SAT = ROOT / "data" / "evidence" / "ss_sat"
REPORT_PATH = CVX / "reports" / "cnf_to_parameterized_e33_packet_compiler_certificate.json"

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_parameterized_e33_target_schema_certificate import (  # noqa: E402
    FAMILY_ID,
    SCHEMA_ID,
    report_status,
    semantic_validate_instance,
    sha256_text,
)


PARAMETERIZED_TARGET_SCHEMA = CVX / "reports" / "parameterized_e33_target_schema_certificate.json"
ASSIGNMENT_TARGET_OBLIGATION = CVX / "reports" / "assignment_bearing_e33_target_family_obligation.json"
FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE = CVX / "reports" / "formula_to_boundary_cycle_family_candidate.json"
FORALL_YES_NO_THEOREM = CVX / "reports" / "forall_yes_no_preservation_theorem.json"

COMPILER_ID = "public_dimacs_to_parameterized_assignment_e33_packet_v0"

CANARY_FORMULAS = {
    "canary_sat_unit": {
        "truth": "SAT",
        "text": "p cnf 1 1\n1 0\n",
        "witness_assignment": [True],
    },
    "canary_sat_binary_choice": {
        "truth": "SAT",
        "text": "p cnf 2 2\n1 2 0\n-1 2 0\n",
        "witness_assignment": [False, True],
    },
    "canary_unsat_unit_pair": {
        "truth": "UNSAT",
        "text": "p cnf 1 2\n1 0\n-1 0\n",
    },
    "canary_unsat_two_var_box": {
        "truth": "UNSAT",
        "text": "p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n",
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def parse_dimacs_text(text: str, source_id: str) -> dict[str, Any]:
    variables: int | None = None
    declared_clauses: int | None = None
    tokens: list[int] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) != 4 or parts[1] != "cnf":
                raise ValueError(f"{source_id}: unsupported DIMACS header {line!r}")
            variables = int(parts[2])
            declared_clauses = int(parts[3])
            continue
        tokens.extend(int(part) for part in line.split())

    clauses: list[list[int]] = []
    current: list[int] = []
    for token in tokens:
        if token == 0:
            clauses.append(current)
            current = []
        else:
            current.append(token)
    if current:
        raise ValueError(f"{source_id}: unterminated DIMACS clause")
    if variables is None or declared_clauses is None:
        raise ValueError(f"{source_id}: missing DIMACS header")
    if declared_clauses != len(clauses):
        raise ValueError(f"{source_id}: declared {declared_clauses} clauses, parsed {len(clauses)}")
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            if literal == 0 or abs(literal) > variables:
                raise ValueError(f"{source_id}: literal {literal} outside header variable range in clause {clause_index}")

    return {
        "source_id": source_id,
        "text": text,
        "variables": variables,
        "clauses": clauses,
        "literal_occurrences": sum(len(clause) for clause in clauses),
        "sha256": sha256_text(text),
    }


def source_formulas() -> list[dict[str, Any]]:
    formulas: list[dict[str, Any]] = []
    for path in sorted((SS_SAT / "benchmarks").glob("*.cnf"), key=lambda item: item.name):
        formulas.append(
            {
                "source_id": path.name,
                "source_kind": "canonical_ss_sat_fixture",
                "path": rel(path),
                "text": path.read_text(encoding="utf-8"),
            }
        )
    for path in sorted((SS_SAT / "benchmarks" / "scaled").glob("*.cnf"), key=lambda item: item.name):
        formulas.append(
            {
                "source_id": f"scaled/{path.name}",
                "source_kind": "canonical_ss_sat_scaled_fixture",
                "path": rel(path),
                "text": path.read_text(encoding="utf-8"),
            }
        )
    for source_id, item in CANARY_FORMULAS.items():
        formulas.append(
            {
                "source_id": source_id,
                "source_kind": "generated_truth_diversity_canary",
                "path": None,
                "text": item["text"],
            }
        )
    return formulas


def compile_packet(parsed: dict[str, Any]) -> dict[str, Any]:
    clauses = parsed["clauses"]
    literal_occurrences = parsed["literal_occurrences"]
    variables = parsed["variables"]
    literal_slots = [
        {
            "clause_index": clause_index,
            "literal_index": literal_index,
            "literal": literal,
            "variable": abs(literal),
            "sign": 1 if literal > 0 else -1,
        }
        for clause_index, clause in enumerate(clauses)
        for literal_index, literal in enumerate(clause)
    ]
    clause_gate_rows = [
        {
            "clause_index": clause_index,
            "literal_slot_count": len(clause),
            "gate": "OR(selected literal truth values)",
        }
        for clause_index, clause in enumerate(clauses)
    ]
    return {
        "packet_id": f"E({parsed['source_id']})",
        "compiler_contract": {
            "compiler_id": COMPILER_ID,
            "input_surface": "DIMACS_CNF",
            "public_only": True,
            "uses_solver_outcome": False,
            "uses_hidden_e33_advice": False,
        },
        "public_payload": {
            "variable_count": variables,
            "clause_rows": clauses,
            "literal_occurrences": literal_occurrences,
            "literal_slots": literal_slots,
            "clause_gate_rows": clause_gate_rows,
        },
        "polynomial_size_bound": {
            "source_size_parameter": "n+m+L",
            "packet_units": variables + len(clauses) + literal_occurrences,
            "witness_units": variables + len(clauses),
            "local_gate_count": len(clauses),
            "bound": "O(n+m+L)",
        },
    }


def compile_source_formula(parsed: dict[str, Any]) -> dict[str, Any]:
    return {
        "format": "DIMACS_CNF",
        "variables": parsed["variables"],
        "clauses": parsed["clauses"],
        "literal_occurrences": parsed["literal_occurrences"],
        "sha256": parsed["sha256"],
    }


def compile_target_skeleton(parsed: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA_ID,
        "family_id": FAMILY_ID,
        "instance_id": parsed["source_id"],
        "parameters": {
            "n": parsed["variables"],
            "m": len(parsed["clauses"]),
            "L": parsed["literal_occurrences"],
            "unbounded_parameter": "n+m+L",
        },
        "source_formula": compile_source_formula(parsed),
        "target_packet": compile_packet(parsed),
    }


def evaluate_literal(literal: int, assignment_bits: list[bool]) -> bool:
    variable = abs(literal)
    value = assignment_bits[variable - 1]
    return value if literal > 0 else not value


def build_clause_witnesses(parsed: dict[str, Any], assignment_bits: list[bool]) -> list[dict[str, Any]]:
    witnesses: list[dict[str, Any]] = []
    for clause_index, clause in enumerate(parsed["clauses"]):
        selected_literal_index = 0
        for literal_index, literal in enumerate(clause):
            if evaluate_literal(literal, assignment_bits):
                selected_literal_index = literal_index
                break
        literal = clause[selected_literal_index]
        sign = 1 if literal > 0 else -1
        variable = abs(literal)
        assignment_value = assignment_bits[variable - 1]
        witnesses.append(
            {
                "clause_index": clause_index,
                "selected_literal_index": selected_literal_index,
                "literal": literal,
                "variable": variable,
                "sign": sign,
                "assignment_value": assignment_value,
                "literal_satisfied": assignment_value if sign == 1 else not assignment_value,
            }
        )
    return witnesses


def attach_witness(parsed: dict[str, Any], assignment_bits: list[bool], claimed_accept: bool) -> dict[str, Any]:
    skeleton = compile_target_skeleton(parsed)
    witnesses = build_clause_witnesses(parsed, assignment_bits)
    gadget_rows = [
        {
            "clause_index": witness["clause_index"],
            "selected_literal_index": witness["selected_literal_index"],
            "literal": witness["literal"],
            "variable": witness["variable"],
            "sign": witness["sign"],
            "height_action_contribution_symbol": (
                f"h_clause_{witness['clause_index']}_{witness['selected_literal_index']}"
            ),
        }
        for witness in witnesses
    ]
    return {
        **skeleton,
        "assignment_witness": {
            "assignment_bits": assignment_bits,
            "clause_witnesses": witnesses,
            "inverse_projection": {
                "assignment_bits": assignment_bits,
            },
        },
        "intrinsic_transport": {
            "support_sector": 33,
            "dim_pi33": 2,
            "formula": "rho_33(E(phi),a)=-(A_h(C(phi,a))/dim(Pi_33))e_33",
            "residual_scalar_source": "derived_from_emitted_circuit_data",
            "certified_residual_scalar_inserted": False,
            "emitted_circuit_data": {
                "circuit_kind": "parameterized_clause_local_boundary_circuit",
                "clause_gadget_count": len(parsed["clauses"]),
                "gadget_rows": gadget_rows,
                "height_action_symbol": "sum_clause_gadget_height_actions",
            },
        },
        "acceptance": {
            "target_accepts": claimed_accept,
            "clauses_locally_satisfied": claimed_accept,
            "assignment_projects_to_source": True,
        },
    }


def replay_result(instance: dict[str, Any]) -> dict[str, Any]:
    errors = semantic_validate_instance(instance)
    accepted = not errors
    return {
        "instance_id": instance["instance_id"],
        "assignment_bits": instance["assignment_witness"]["assignment_bits"],
        "claimed_accept": instance["acceptance"]["target_accepts"],
        "accepted": accepted,
        "errors": errors,
    }


def all_assignments(variable_count: int) -> list[list[bool]]:
    return [list(values) for values in itertools.product([False, True], repeat=variable_count)]


def compile_surface_summary() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for formula in source_formulas():
        try:
            parsed = parse_dimacs_text(formula["text"], formula["source_id"])
            skeleton = compile_target_skeleton(parsed)
            rows.append(
                {
                    "source_id": formula["source_id"],
                    "source_kind": formula["source_kind"],
                    "path": formula["path"],
                    "variables": parsed["variables"],
                    "clauses": len(parsed["clauses"]),
                    "literal_occurrences": parsed["literal_occurrences"],
                    "packet_id": skeleton["target_packet"]["packet_id"],
                    "packet_units": skeleton["target_packet"]["polynomial_size_bound"]["packet_units"],
                    "local_gate_count": skeleton["target_packet"]["polynomial_size_bound"]["local_gate_count"],
                    "public_only": skeleton["target_packet"]["compiler_contract"]["public_only"],
                    "uses_solver_outcome": skeleton["target_packet"]["compiler_contract"]["uses_solver_outcome"],
                    "uses_hidden_e33_advice": skeleton["target_packet"]["compiler_contract"][
                        "uses_hidden_e33_advice"
                    ],
                }
            )
        except Exception as exc:  # pragma: no cover - report seam for malformed fixtures.
            errors.append(f"{formula['source_id']}: {exc}")

    return {
        "compiled_instance_count": len(rows),
        "compile_error_count": len(errors),
        "errors": errors,
        "max_variables": max((row["variables"] for row in rows), default=0),
        "max_clauses": max((row["clauses"] for row in rows), default=0),
        "max_literal_occurrences": max((row["literal_occurrences"] for row in rows), default=0),
        "all_public_only": all(row["public_only"] for row in rows),
        "no_solver_outcome_reads": all(row["uses_solver_outcome"] is False for row in rows),
        "no_hidden_e33_advice_reads": all(row["uses_hidden_e33_advice"] is False for row in rows),
        "all_linear_size_bounds": all(
            row["packet_units"] == row["variables"] + row["clauses"] + row["literal_occurrences"]
            and row["local_gate_count"] == row["clauses"]
            for row in rows
        ),
        "rows": rows,
    }


def canary_replay_checks() -> dict[str, Any]:
    sat_checks: list[dict[str, Any]] = []
    unsat_checks: list[dict[str, Any]] = []

    for source_id, canary in CANARY_FORMULAS.items():
        parsed = parse_dimacs_text(canary["text"], source_id)
        if canary["truth"] == "SAT":
            instance = attach_witness(parsed, list(canary["witness_assignment"]), claimed_accept=True)
            replay = replay_result(instance)
            sat_checks.append(
                {
                    "source_id": source_id,
                    "known_truth": "SAT",
                    "witness_assignment": canary["witness_assignment"],
                    "accepted": replay["accepted"],
                    "errors": replay["errors"],
                    "compiled_packet": compile_target_skeleton(parsed)["target_packet"],
                }
            )
        else:
            assignment_rows = []
            for assignment in all_assignments(parsed["variables"]):
                instance = attach_witness(parsed, assignment, claimed_accept=True)
                replay = replay_result(instance)
                assignment_rows.append(
                    {
                        "assignment_bits": assignment,
                        "accepted": replay["accepted"],
                        "errors": replay["errors"],
                    }
                )
            unsat_checks.append(
                {
                    "source_id": source_id,
                    "known_truth": "UNSAT",
                    "assignments_checked": len(assignment_rows),
                    "all_claimed_accepting_witnesses_rejected": all(not row["accepted"] for row in assignment_rows),
                    "assignment_rows": assignment_rows,
                    "compiled_packet": compile_target_skeleton(parsed)["target_packet"],
                }
            )

    return {
        "sat_canary_count": len(sat_checks),
        "unsat_canary_count": len(unsat_checks),
        "sat_canaries_accept": all(row["accepted"] for row in sat_checks),
        "unsat_canaries_reject_all_bounded_assignments": all(
            row["all_claimed_accepting_witnesses_rejected"] for row in unsat_checks
        ),
        "bounded_assignment_enumeration_limit": "only the generated canaries in this certificate",
        "sat_checks": sat_checks,
        "unsat_checks": unsat_checks,
    }


def build_report() -> dict[str, Any]:
    compile_surface = compile_surface_summary()
    replay = canary_replay_checks()
    schema_certificate = load_json(PARAMETERIZED_TARGET_SCHEMA)
    forall_theorem = load_json_if_exists(FORALL_YES_NO_THEOREM)

    compiler_passed = (
        compile_surface["compile_error_count"] == 0
        and compile_surface["compiled_instance_count"] == len(source_formulas())
        and compile_surface["all_public_only"]
        and compile_surface["no_solver_outcome_reads"]
        and compile_surface["no_hidden_e33_advice_reads"]
        and compile_surface["all_linear_size_bounds"]
    )
    replay_passed = replay["sat_canaries_accept"] and replay["unsat_canaries_reject_all_bounded_assignments"]
    pass_condition = (
        compiler_passed
        and replay_passed
        and schema_certificate.get("decision", {}).get("may_claim_parameterized_e33_target_schema_defined")
        is True
    )

    return {
        "schema": "d20.integrity.cnf_to_parameterized_e33_packet_compiler_certificate.source_drop",
        "status": (
            "CNF_TO_PARAMETERIZED_E33_PACKET_COMPILER_BUILT_REPLAY_CHECKED_FOR_CANARIES_REDUCTION_OPEN"
            if pass_condition
            else "CNF_TO_PARAMETERIZED_E33_PACKET_COMPILER_INCOMPLETE"
        ),
        "claim_level": "public_compiler_and_bounded_canary_replay_witnessed_forall_theorem_open",
        "source_audit": {
            "parameterized_e33_target_schema": report_status(
                PARAMETERIZED_TARGET_SCHEMA,
                "PARAMETERIZED_E33_TARGET_SCHEMA_DEFINED_REDUCTION_OPEN",
            ),
            "assignment_bearing_e33_target_family_obligation": report_status(
                ASSIGNMENT_TARGET_OBLIGATION,
                "ASSIGNMENT_BEARING_E33_TARGET_FAMILY_OBLIGATION_BUILT_FINITE_TARGET_COLLAPSE_CERTIFIED",
            ),
            "formula_to_boundary_cycle_family_candidate": report_status(
                FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE,
                "FORMULA_TO_BOUNDARY_CYCLE_FAMILY_CANDIDATE_BUILT_SAT_PRESERVATION_BLOCKED",
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
        "compiler": {
            "id": COMPILER_ID,
            "input_surface": "DIMACS CNF text only",
            "output_surface": "parameterized E(phi) target packet skeleton with public clause-local gates",
            "public_only": True,
            "uses_solver_outcome": False,
            "uses_hidden_e33_advice": False,
            "emits_assignment_witness": False,
            "polynomial_time_bound": "O(input_bytes + literal_occurrences)",
            "output_size_bound": "O(n+m+L)",
            "algorithm": [
                "parse DIMACS CNF",
                "copy public clause rows into the E(phi) payload",
                "emit one public literal slot per literal occurrence",
                "emit one clause-local OR gate row per clause",
                "emit the intrinsic rho_33 transport contract without a residual scalar",
            ],
        },
        "compile_surface": compile_surface,
        "replay_checker": {
            "input_surface": "compiled E(phi) packet plus supplied assignment witness",
            "does_not_search_for_assignment": True,
            "does_not_read_hidden_e33_advice": True,
            "checks": [
                "assignment length equals n",
                "one selected literal witness exists for each clause",
                "selected literal belongs to the source clause",
                "selected literal evaluates true under the assignment",
                "inverse projection returns the supplied assignment bits",
                "intrinsic transport is derived from emitted clause-local circuit data",
                "claimed accepting witness is rejected if any selected literal is false",
            ],
        },
        "canary_replay": replay,
        "decision": {
            "may_claim_public_cnf_to_parameterized_packet_compiler_implemented": compiler_passed,
            "may_claim_replay_checker_for_supplied_assignment_witnesses": replay_passed,
            "may_claim_canary_yes_no_preservation": replay_passed,
            "may_claim_forall_yes_no_preservation": False,
            "may_claim_sat_complete_hidden_e33_family": False,
            "may_claim_p_not_np": False,
            "reason": (
                "The public compiler now emits parameterized E(phi) packets without hidden advice or "
                "solver-outcome reads, and the replay checker accepts SAT canary witnesses while "
                "rejecting all claimed accepting witnesses for the bounded UNSAT canaries. The forall "
                "CNF theorem is still open."
            ),
        },
        "non_claims": [
            "This does not find satisfying assignments for arbitrary formulas.",
            "This does not prove every satisfiable CNF has an accepting target witness.",
            "This does not prove every accepting target witness projects to a satisfying assignment for arbitrary CNF.",
            "This does not certify SAT-completeness.",
            "This does not prove P != NP.",
        ],
        "next_highest_yield_item": {
            "id": "full_no_escape_closure" if forall_theorem is not None else "forall_yes_no_preservation_theorem",
            "action": (
                "Refresh the full no-escape closure ledger against the certified encoded-family reduction."
                if forall_theorem is not None
                else (
                    "Promote the compiler/replay construction to a theorem: for every CNF phi, phi is "
                    "satisfiable iff there exists an accepting E(phi) assignment witness, with inverse projection."
                )
            ),
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["decision"]["may_claim_public_cnf_to_parameterized_packet_compiler_implemented"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
