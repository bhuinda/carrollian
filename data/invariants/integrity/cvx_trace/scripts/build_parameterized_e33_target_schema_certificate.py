from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
SCHEMA_PATH = CVX / "schemas" / "parameterized_e33_target.schema.json"
REPORT_PATH = CVX / "reports" / "parameterized_e33_target_schema_certificate.json"

ASSIGNMENT_TARGET_OBLIGATION = CVX / "reports" / "assignment_bearing_e33_target_family_obligation.json"
FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE = CVX / "reports" / "formula_to_boundary_cycle_family_candidate.json"
ENCODED_FAMILY_FRONTIER = CVX / "reports" / "encoded_family_sat_frontier_certificate.json"
CNF_TO_PARAMETERIZED_PACKET_COMPILER = (
    CVX / "reports" / "cnf_to_parameterized_e33_packet_compiler_certificate.json"
)
FORALL_YES_NO_THEOREM = CVX / "reports" / "forall_yes_no_preservation_theorem.json"


SCHEMA_ID = "d20.integrity.parameterized_e33_target_instance.source_drop"
FAMILY_ID = "parameterized_assignment_bearing_hidden_e33_v0_schema"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def report_status(path: Path, expected_status: str | tuple[str, ...]) -> dict[str, Any]:
    data = load_json(path)
    expected = (expected_status,) if isinstance(expected_status, str) else expected_status
    return {
        "path": rel(path),
        "status": data.get("status"),
        "expected_status": expected_status if isinstance(expected_status, str) else list(expected_status),
        "passed": data.get("status") in expected,
    }


def parameterized_target_schema() -> dict[str, Any]:
    nonnegative_integer = {"type": "integer", "minimum": 0}
    positive_integer = {"type": "integer", "minimum": 1}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "title": "D20 parameterized assignment-bearing hidden e33 target instance",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema",
            "family_id",
            "instance_id",
            "parameters",
            "source_formula",
            "target_packet",
            "assignment_witness",
            "intrinsic_transport",
            "acceptance",
        ],
        "properties": {
            "schema": {"const": SCHEMA_ID},
            "family_id": {"const": FAMILY_ID},
            "instance_id": {"type": "string", "minLength": 1},
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "required": ["n", "m", "L", "unbounded_parameter"],
                "properties": {
                    "n": positive_integer,
                    "m": positive_integer,
                    "L": nonnegative_integer,
                    "unbounded_parameter": {"const": "n+m+L"},
                },
            },
            "source_formula": {
                "type": "object",
                "additionalProperties": False,
                "required": ["format", "variables", "clauses", "literal_occurrences", "sha256"],
                "properties": {
                    "format": {"const": "DIMACS_CNF"},
                    "variables": positive_integer,
                    "clauses": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "integer"},
                        },
                    },
                    "literal_occurrences": nonnegative_integer,
                    "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                },
            },
            "target_packet": {
                "type": "object",
                "additionalProperties": True,
                "required": ["packet_id", "compiler_contract", "public_payload", "polynomial_size_bound"],
                "properties": {
                    "packet_id": {"type": "string", "minLength": 1},
                    "compiler_contract": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "compiler_id",
                            "input_surface",
                            "public_only",
                            "uses_solver_outcome",
                            "uses_hidden_e33_advice",
                        ],
                        "properties": {
                            "compiler_id": {"type": "string", "minLength": 1},
                            "input_surface": {"const": "DIMACS_CNF"},
                            "public_only": {"const": True},
                            "uses_solver_outcome": {"const": False},
                            "uses_hidden_e33_advice": {"const": False},
                        },
                    },
                    "public_payload": {"type": "object"},
                    "polynomial_size_bound": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["source_size_parameter", "packet_units", "witness_units", "local_gate_count", "bound"],
                        "properties": {
                            "source_size_parameter": {"const": "n+m+L"},
                            "packet_units": nonnegative_integer,
                            "witness_units": nonnegative_integer,
                            "local_gate_count": nonnegative_integer,
                            "bound": {"const": "O(n+m+L)"},
                        },
                    },
                },
            },
            "assignment_witness": {
                "type": "object",
                "additionalProperties": False,
                "required": ["assignment_bits", "clause_witnesses", "inverse_projection"],
                "properties": {
                    "assignment_bits": {"type": "array", "items": {"type": "boolean"}},
                    "clause_witnesses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "clause_index",
                                "selected_literal_index",
                                "literal",
                                "variable",
                                "sign",
                                "assignment_value",
                                "literal_satisfied",
                            ],
                            "properties": {
                                "clause_index": nonnegative_integer,
                                "selected_literal_index": nonnegative_integer,
                                "literal": {"type": "integer"},
                                "variable": positive_integer,
                                "sign": {"enum": [-1, 1]},
                                "assignment_value": {"type": "boolean"},
                                "literal_satisfied": {"type": "boolean"},
                            },
                        },
                    },
                    "inverse_projection": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["assignment_bits"],
                        "properties": {
                            "assignment_bits": {"type": "array", "items": {"type": "boolean"}},
                        },
                    },
                },
            },
            "intrinsic_transport": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "support_sector",
                    "dim_pi33",
                    "formula",
                    "residual_scalar_source",
                    "certified_residual_scalar_inserted",
                    "emitted_circuit_data",
                ],
                "properties": {
                    "support_sector": {"const": 33},
                    "dim_pi33": {"const": 2},
                    "formula": {
                        "const": "rho_33(E(phi),a)=-(A_h(C(phi,a))/dim(Pi_33))e_33"
                    },
                    "residual_scalar_source": {"const": "derived_from_emitted_circuit_data"},
                    "certified_residual_scalar_inserted": {"const": False},
                    "emitted_circuit_data": {
                        "type": "object",
                        "additionalProperties": True,
                        "required": ["circuit_kind", "clause_gadget_count", "gadget_rows", "height_action_symbol"],
                        "properties": {
                            "circuit_kind": {"const": "parameterized_clause_local_boundary_circuit"},
                            "clause_gadget_count": nonnegative_integer,
                            "gadget_rows": {"type": "array", "items": {"type": "object"}},
                            "height_action_symbol": {"type": "string", "minLength": 1},
                        },
                    },
                },
            },
            "acceptance": {
                "type": "object",
                "additionalProperties": False,
                "required": ["target_accepts", "clauses_locally_satisfied", "assignment_projects_to_source"],
                "properties": {
                    "target_accepts": {"type": "boolean"},
                    "clauses_locally_satisfied": {"type": "boolean"},
                    "assignment_projects_to_source": {"type": "boolean"},
                },
            },
        },
    }


def instance_document(
    *,
    instance_id: str,
    dimacs_text: str,
    clauses: list[list[int]],
    assignment_bits: list[bool],
    clause_witnesses: list[dict[str, Any]],
    target_accepts: bool,
) -> dict[str, Any]:
    literal_occurrences = sum(len(clause) for clause in clauses)
    variables = len(assignment_bits)
    clause_gadgets = [
        {
            "clause_index": witness["clause_index"],
            "selected_literal_index": witness["selected_literal_index"],
            "height_action_contribution_symbol": (
                f"h_clause_{witness['clause_index']}_{witness['selected_literal_index']}"
            ),
        }
        for witness in clause_witnesses
    ]
    return {
        "schema": SCHEMA_ID,
        "family_id": FAMILY_ID,
        "instance_id": instance_id,
        "parameters": {
            "n": variables,
            "m": len(clauses),
            "L": literal_occurrences,
            "unbounded_parameter": "n+m+L",
        },
        "source_formula": {
            "format": "DIMACS_CNF",
            "variables": variables,
            "clauses": clauses,
            "literal_occurrences": literal_occurrences,
            "sha256": sha256_text(dimacs_text),
        },
        "target_packet": {
            "packet_id": f"E({instance_id})",
            "compiler_contract": {
                "compiler_id": "public_dimacs_to_parameterized_assignment_e33_packet_v0_schema",
                "input_surface": "DIMACS_CNF",
                "public_only": True,
                "uses_solver_outcome": False,
                "uses_hidden_e33_advice": False,
            },
            "public_payload": {
                "variable_count": variables,
                "clause_rows": clauses,
                "literal_occurrences": literal_occurrences,
            },
            "polynomial_size_bound": {
                "source_size_parameter": "n+m+L",
                "packet_units": variables + len(clauses) + literal_occurrences,
                "witness_units": variables + len(clause_witnesses),
                "local_gate_count": len(clauses),
                "bound": "O(n+m+L)",
            },
        },
        "assignment_witness": {
            "assignment_bits": assignment_bits,
            "clause_witnesses": clause_witnesses,
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
                "clause_gadget_count": len(clauses),
                "gadget_rows": clause_gadgets,
                "height_action_symbol": "sum_clause_gadget_height_actions",
            },
        },
        "acceptance": {
            "target_accepts": target_accepts,
            "clauses_locally_satisfied": target_accepts,
            "assignment_projects_to_source": True,
        },
    }


def accepting_sat_unit_example() -> dict[str, Any]:
    return instance_document(
        instance_id="canary_sat_unit",
        dimacs_text="p cnf 1 1\n1 0\n",
        clauses=[[1]],
        assignment_bits=[True],
        clause_witnesses=[
            {
                "clause_index": 0,
                "selected_literal_index": 0,
                "literal": 1,
                "variable": 1,
                "sign": 1,
                "assignment_value": True,
                "literal_satisfied": True,
            }
        ],
        target_accepts=True,
    )


def rejected_unsat_bad_witness_example() -> dict[str, Any]:
    return instance_document(
        instance_id="canary_unsat_unit_pair_bad_witness",
        dimacs_text="p cnf 1 2\n1 0\n-1 0\n",
        clauses=[[1], [-1]],
        assignment_bits=[True],
        clause_witnesses=[
            {
                "clause_index": 0,
                "selected_literal_index": 0,
                "literal": 1,
                "variable": 1,
                "sign": 1,
                "assignment_value": True,
                "literal_satisfied": True,
            },
            {
                "clause_index": 1,
                "selected_literal_index": 0,
                "literal": -1,
                "variable": 1,
                "sign": -1,
                "assignment_value": True,
                "literal_satisfied": False,
            },
        ],
        target_accepts=True,
    )


def schema_shape_errors(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = set(schema.get("required", []))
    for key in (
        "schema",
        "family_id",
        "parameters",
        "source_formula",
        "target_packet",
        "assignment_witness",
        "intrinsic_transport",
        "acceptance",
    ):
        if key not in required:
            errors.append(f"schema missing required field {key}")
    transport = schema.get("properties", {}).get("intrinsic_transport", {})
    transport_props = transport.get("properties", {})
    if transport_props.get("certified_residual_scalar_inserted", {}).get("const") is not False:
        errors.append("schema does not prohibit inserted certified residual scalar")
    if transport_props.get("residual_scalar_source", {}).get("const") != "derived_from_emitted_circuit_data":
        errors.append("schema does not require residual scalar to be derived from emitted circuit data")
    if transport_props.get("support_sector", {}).get("const") != 33:
        errors.append("schema does not pin support_sector to 33")
    return errors


def semantic_validate_instance(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if instance.get("schema") != SCHEMA_ID:
        errors.append("schema id mismatch")
    if instance.get("family_id") != FAMILY_ID:
        errors.append("family id mismatch")

    parameters = instance.get("parameters", {})
    source = instance.get("source_formula", {})
    clauses = source.get("clauses", [])
    assignment = instance.get("assignment_witness", {}).get("assignment_bits", [])
    witnesses = instance.get("assignment_witness", {}).get("clause_witnesses", [])
    literal_occurrences = sum(len(clause) for clause in clauses)

    if parameters.get("n") != source.get("variables") or parameters.get("n") != len(assignment):
        errors.append("n parameter does not match source variables and assignment length")
    if parameters.get("m") != len(clauses):
        errors.append("m parameter does not match clause count")
    if parameters.get("L") != source.get("literal_occurrences") or parameters.get("L") != literal_occurrences:
        errors.append("L parameter does not match literal occurrence count")

    contract = instance.get("target_packet", {}).get("compiler_contract", {})
    if contract.get("public_only") is not True:
        errors.append("compiler contract is not public-only")
    if contract.get("uses_solver_outcome") is not False:
        errors.append("compiler contract reads solver outcome")
    if contract.get("uses_hidden_e33_advice") is not False:
        errors.append("compiler contract reads hidden e33 advice")

    inverse = instance.get("assignment_witness", {}).get("inverse_projection", {}).get("assignment_bits")
    if inverse != assignment:
        errors.append("inverse projection does not recover assignment bits")

    if len(witnesses) != len(clauses):
        errors.append("clause witness count does not match clause count")
    else:
        for index, witness in enumerate(witnesses):
            if witness.get("clause_index") != index:
                errors.append(f"clause {index} witness has wrong clause_index")
                continue
            clause = clauses[index]
            selected = witness.get("selected_literal_index")
            if not isinstance(selected, int) or selected < 0 or selected >= len(clause):
                errors.append(f"clause {index} selected literal index out of range")
                continue
            literal = clause[selected]
            variable = abs(literal)
            sign = 1 if literal > 0 else -1
            if witness.get("literal") != literal:
                errors.append(f"clause {index} witness literal does not match source clause")
            if witness.get("variable") != variable:
                errors.append(f"clause {index} witness variable does not match literal")
            if witness.get("sign") != sign:
                errors.append(f"clause {index} witness sign does not match literal")
            if variable < 1 or variable > len(assignment):
                errors.append(f"clause {index} variable out of assignment range")
                continue
            assignment_value = assignment[variable - 1]
            literal_satisfied = assignment_value if sign == 1 else not assignment_value
            if witness.get("assignment_value") is not assignment_value:
                errors.append(f"clause {index} assignment_value does not match assignment bit")
            if witness.get("literal_satisfied") is not literal_satisfied:
                errors.append(f"clause {index} literal_satisfied does not match evaluated literal")
            if literal_satisfied is not True:
                errors.append(f"clause {index} selected literal is not satisfied")

    transport = instance.get("intrinsic_transport", {})
    if transport.get("support_sector") != 33:
        errors.append("intrinsic transport does not use support sector 33")
    if transport.get("dim_pi33") != 2:
        errors.append("intrinsic transport dim_pi33 is not 2")
    if transport.get("residual_scalar_source") != "derived_from_emitted_circuit_data":
        errors.append("residual scalar is not derived from emitted circuit data")
    if transport.get("certified_residual_scalar_inserted") is not False:
        errors.append("certified residual scalar was inserted")
    emitted = transport.get("emitted_circuit_data", {})
    if emitted.get("circuit_kind") != "parameterized_clause_local_boundary_circuit":
        errors.append("emitted circuit kind is not parameterized clause-local boundary circuit")
    if emitted.get("clause_gadget_count") != len(clauses):
        errors.append("clause gadget count does not match clause count")

    size_bound = instance.get("target_packet", {}).get("polynomial_size_bound", {})
    if size_bound.get("source_size_parameter") != "n+m+L" or size_bound.get("bound") != "O(n+m+L)":
        errors.append("polynomial size bound is not expressed over n+m+L")
    if size_bound.get("local_gate_count") != len(clauses):
        errors.append("local gate count does not match clause count")

    acceptance = instance.get("acceptance", {})
    all_clause_literals_satisfied = not any("selected literal is not satisfied" in error for error in errors)
    if acceptance.get("target_accepts") is True and all_clause_literals_satisfied is not True:
        errors.append("target accepts despite an unsatisfied local clause witness")
    if acceptance.get("clauses_locally_satisfied") is not all_clause_literals_satisfied:
        errors.append("acceptance clauses_locally_satisfied does not match witness replay")
    if acceptance.get("assignment_projects_to_source") is not True:
        errors.append("acceptance does not project assignment to source")

    return errors


def build_report() -> dict[str, Any]:
    schema = parameterized_target_schema()
    sat_example = accepting_sat_unit_example()
    unsat_bad_witness = rejected_unsat_bad_witness_example()

    schema_errors = schema_shape_errors(schema)
    sat_errors = semantic_validate_instance(sat_example)
    unsat_errors = semantic_validate_instance(unsat_bad_witness)
    unsat_rejected = any("selected literal is not satisfied" in error for error in unsat_errors) and any(
        "target accepts despite" in error for error in unsat_errors
    )
    obligation = load_json(ASSIGNMENT_TARGET_OBLIGATION)
    packet_compiler = load_json_if_exists(CNF_TO_PARAMETERIZED_PACKET_COMPILER)
    forall_theorem = load_json_if_exists(FORALL_YES_NO_THEOREM)

    pass_condition = (
        not schema_errors
        and not sat_errors
        and unsat_rejected
        and obligation.get("decision", {}).get("may_claim_finite_target_collapse_certified") is True
        and obligation.get("decision", {}).get("may_claim_parameterized_target_requirements_defined") is True
    )

    report = {
        "schema": "d20.integrity.parameterized_e33_target_schema_certificate.source_drop",
        "status": (
            "PARAMETERIZED_E33_TARGET_SCHEMA_DEFINED_REDUCTION_OPEN"
            if pass_condition
            else "PARAMETERIZED_E33_TARGET_SCHEMA_INCOMPLETE"
        ),
        "claim_level": "assignment_bearing_schema_defined_compiler_and_forall_theorem_open",
        "schema_path": rel(SCHEMA_PATH),
        "family_id": FAMILY_ID,
        "source_audit": {
            "assignment_bearing_e33_target_family_obligation": report_status(
                ASSIGNMENT_TARGET_OBLIGATION,
                "ASSIGNMENT_BEARING_E33_TARGET_FAMILY_OBLIGATION_BUILT_FINITE_TARGET_COLLAPSE_CERTIFIED",
            ),
            "formula_to_boundary_cycle_family_candidate": report_status(
                FORMULA_TO_BOUNDARY_CYCLE_CANDIDATE,
                "FORMULA_TO_BOUNDARY_CYCLE_FAMILY_CANDIDATE_BUILT_SAT_PRESERVATION_BLOCKED",
            ),
            "encoded_family_sat_frontier": report_status(
                ENCODED_FAMILY_FRONTIER,
                (
                    "ENCODED_FAMILY_SAT_FRONTIER_BLOCKED_UNIFORM_REDUCTION_MISSING",
                    "ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED",
                ),
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
        "schema_shape_check": {
            "passed": not schema_errors,
            "errors": schema_errors,
        },
        "required_surfaces": {
            "unbounded_parameters": ["n", "m", "L"],
            "source_formula_surface": "DIMACS_CNF with explicit clause rows",
            "target_packet_surface": "public E(phi) packet with public-only compiler contract",
            "assignment_witness_surface": "assignment bits plus one selected literal witness per clause",
            "inverse_projection_surface": "assignment bits are recoverable from accepting target witnesses",
            "intrinsic_transport_surface": (
                "rho_33(E(phi),a)=-(A_h(C(phi,a))/dim(Pi_33))e_33 from emitted circuit data"
            ),
            "forbidden_surface": "inserted certified residual scalar",
        },
        "example_witness_checks": {
            "accepting_sat_unit": {
                "passed": not sat_errors,
                "errors": sat_errors,
                "instance": sat_example,
            },
            "rejected_unsat_unit_pair_bad_witness": {
                "passed": unsat_rejected,
                "errors": unsat_errors,
                "instance": unsat_bad_witness,
            },
        },
        "decision": {
            "may_claim_parameterized_e33_target_schema_defined": pass_condition,
            "may_claim_assignment_witness_shape_machine_checkable": pass_condition,
            "may_claim_clause_local_soundness_gate_schema_defined": pass_condition,
            "may_claim_intrinsic_transport_schema_excludes_inserted_residual_scalar": pass_condition,
            "may_claim_public_cnf_to_parameterized_packet_compiler_implemented": False,
            "may_claim_forall_yes_no_preservation": False,
            "may_claim_sat_complete_hidden_e33_family": False,
            "may_claim_p_not_np": False,
            "reason": (
                "The schema now names the unbounded parameters, assignment witness, inverse "
                "projection, clause-local gates, and intrinsic rho_33 transport contract. It still "
                "does not implement the public compiler or prove forall-instance preservation."
            ),
        },
        "non_claims": [
            "This does not implement the CNF-to-E(phi) compiler.",
            "This does not prove every satisfiable CNF has an accepting target witness.",
            "This does not prove every accepting target witness projects to a satisfying assignment for arbitrary CNF.",
            "This does not certify SAT-completeness.",
            "This does not prove P != NP.",
        ],
        "next_highest_yield_item": {
            "id": (
                "full_no_escape_closure"
                if forall_theorem is not None
                else "forall_yes_no_preservation_theorem"
                if packet_compiler is not None
                else "cnf_to_parameterized_e33_packet_compiler"
            ),
            "action": (
                "Refresh the full no-escape closure ledger against the certified encoded-family reduction."
                if forall_theorem is not None
                else (
                "Promote the compiler/replay construction to a theorem: for every CNF phi, phi is "
                "satisfiable iff there exists an accepting E(phi) assignment witness, with inverse projection."
                )
                if packet_compiler is not None
                else (
                    "Implement the public DIMACS-to-E(phi) packet compiler and replay checker that emits "
                    "clause-local circuit data and validates SAT/UNSAT canaries against the schema."
                )
            ),
        },
    }

    SCHEMA_PATH.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = build_report()
    print(report["status"])
    return 0 if report["decision"]["may_claim_parameterized_e33_target_schema_defined"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
