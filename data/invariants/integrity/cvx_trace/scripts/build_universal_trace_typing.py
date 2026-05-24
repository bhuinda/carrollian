from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
TRACE_PATHS = [
    BASE / "traces" / "cadical_lrat_contradiction_4.trace.json",
    BASE / "traces" / "public_dpll_contradiction_4.trace.json",
]
SCHEMA_PATH = BASE / "schemas" / "universal_trace_event.v1.schema.json"
CLASSIFIER_PATH = BASE / "reports" / "universal_trace_typing_classifier.json"
REPORT_PATH = BASE / "reports" / "universal_trace_typing_report.json"
RESIDUE_PATH = BASE / "residues" / "unsupported_universal_trace_event_residue.json"


PUBLIC_MACHINE_CODES = {
    "C_PUBLIC_INPUT_READ": "read a public input bit or symbol",
    "C_PUBLIC_CONST": "introduce a public constant",
    "C_PUBLIC_COPY": "copy public register or tape content",
    "C_PUBLIC_BIT_NOT": "public Boolean NOT gate",
    "C_PUBLIC_BIT_AND": "public Boolean AND gate",
    "C_PUBLIC_BIT_OR": "public Boolean OR gate",
    "C_PUBLIC_BIT_XOR": "public Boolean XOR gate over public bits only",
    "C_PUBLIC_COMPARE_ZERO": "public zero-test or equality check",
    "C_PUBLIC_BRANCH": "branch on a public control bit",
    "C_PUBLIC_RAM_LOAD": "load from public-addressed public memory",
    "C_PUBLIC_RAM_STORE": "store to public-addressed public memory",
    "C_PUBLIC_LOOP_TICK": "public bounded execution-step counter",
    "C_PUBLIC_HALT_ACCEPT": "public accepting halt state",
    "C_PUBLIC_HALT_REJECT": "public rejecting halt state",
    "C_PUBLIC_EMIT_DECISION": "emit a public decision bit",
}

C_PUBLIC_CLASS_CODES = {
    **PUBLIC_MACHINE_CODES,
    "C_PUBLIC_DPLL_SCAN_CLAUSE": "public clause scan over DIMACS literals",
    "C_PUBLIC_DPLL_UNIT_ASSIGN": "public unit propagation assignment",
    "C_PUBLIC_DPLL_EMPTY_CLAUSE_CONFLICT": "public empty-clause conflict",
    "C_PUBLIC_DPLL_UNIT_CONFLICT": "public contradictory unit conflict",
    "C_PUBLIC_LRAT_LEMMA": "public checked LRAT lemma",
    "C_PUBLIC_LRAT_DELETION": "public LRAT proof bookkeeping",
    "C_PUBLIC_LRAT_EMPTY_CLAUSE": "public checked LRAT empty-clause witness",
}

V_VISIBLE_CLASS_CODES = {
    "V_VISIBLE_COMMUTATOR_WALL_CROSSING": "visible commutator wall crossing with replayable public boundary",
    "V_VISIBLE_PUBLIC_BOUNDARY_TRANSPORT": "visible boundary transport with public replay data",
}

X_EXTRACTOR_CLASS_CODES = {
    "X_EXTRACTOR_NATIVE_XOR_ELIMINATION": "native XOR elimination recovers hidden parity structure",
    "X_EXTRACTOR_GF2_GAUSSIAN_ELIMINATION": "GF(2) Gaussian elimination adjoins a hidden parity extractor",
    "X_EXTRACTOR_PARITY_BASIS_RECOVERY": "solver recovers hidden-sector parity basis",
    "X_EXTRACTOR_HIDDEN_ADVICE_READ": "solver reads non-public hidden-sector advice",
    "X_EXTRACTOR_HIDDEN_SECTOR_MAP": "solver constructs a hidden-sector map",
    "X_EXTRACTOR_NONPUBLIC_PARITY_BASIS": "solver uses a non-public parity basis",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def universal_event_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "d20.integrity.universal_trace_event.v1",
        "title": "D20 universal C/V/X trace event",
        "type": "object",
        "required": [
            "schema",
            "event_id",
            "step",
            "op",
            "class_code",
            "integrity_type",
            "public_inputs",
            "public_outputs",
            "checks",
        ],
        "properties": {
            "schema": {"const": "d20.integrity.universal_trace_event.v1"},
            "event_id": {"type": "string", "minLength": 1},
            "step": {"type": "integer", "minimum": 1},
            "op": {
                "enum": [
                    "universal_machine_opcode",
                    "proof_opcode",
                    "solver_opcode",
                    "visible_wall_crossing",
                    "extractor_opcode",
                    "residue",
                ]
            },
            "class_code": {"type": "string", "minLength": 1},
            "integrity_type": {"enum": ["C", "V", "X", "UNCLASSIFIED"]},
            "reason": {"type": "string"},
            "public_inputs": {"type": "object"},
            "public_outputs": {"type": "object"},
            "checks": {
                "type": "object",
                "required": ["locally_checkable", "uses_hidden_advice"],
                "properties": {
                    "locally_checkable": {"type": "boolean"},
                    "uses_hidden_advice": {"type": "boolean"},
                    "uses_extension_variable": {"type": "boolean"},
                },
                "additionalProperties": True,
            },
        },
        "additionalProperties": False,
    }


def classifier_document() -> dict[str, Any]:
    return {
        "schema": "d20.integrity.universal_trace_typing_classifier.v1",
        "status": "UNIVERSAL_TRACE_TYPING_CLASSIFIER_DEFINED",
        "vocabulary_model": "finite_public_bit_ram_plus_solver_and_proof_surface",
        "accepted_types": ["C", "V", "X"],
        "fallback_type": "UNCLASSIFIED",
        "fallback_policy": "emit_explicit_typed_residue",
        "public_machine_class_codes": PUBLIC_MACHINE_CODES,
        "public_c_class_codes": C_PUBLIC_CLASS_CODES,
        "visible_v_class_codes": V_VISIBLE_CLASS_CODES,
        "extractor_x_class_codes": X_EXTRACTOR_CLASS_CODES,
        "coverage_statement": "Every class code in this finite vocabulary has exactly one C/V/X type. Any event outside the vocabulary is not silently accepted; it is emitted as an UNCLASSIFIED residue.",
    }


def classify_class_code(class_code: str) -> dict[str, Any]:
    if class_code in C_PUBLIC_CLASS_CODES:
        return {
            "integrity_type": "C",
            "status": "classified",
            "reason": C_PUBLIC_CLASS_CODES[class_code],
        }
    if class_code in V_VISIBLE_CLASS_CODES:
        return {
            "integrity_type": "V",
            "status": "classified",
            "reason": V_VISIBLE_CLASS_CODES[class_code],
        }
    if class_code in X_EXTRACTOR_CLASS_CODES:
        return {
            "integrity_type": "X",
            "status": "classified",
            "reason": X_EXTRACTOR_CLASS_CODES[class_code],
        }
    return {
        "integrity_type": "UNCLASSIFIED",
        "status": "residue",
        "reason": "event class code is outside the finite universal C/V/X vocabulary",
    }


def classify_event(event: dict[str, Any]) -> dict[str, Any]:
    classification = classify_class_code(str(event.get("class_code", "")))
    checks = event.get("checks", {})
    if classification["integrity_type"] == "C" and checks.get("uses_hidden_advice") is True:
        return {
            "integrity_type": "X",
            "status": "classified",
            "reason": "public opcode attempted to read hidden advice and is retyped as X",
        }
    return classification


def residue_for(event: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "d20.integrity.universal_trace.unsupported_event_residue.v1",
        "status": "UNIVERSAL_TRACE_UNSUPPORTED_EVENT_TYPED_RESIDUE",
        "residue_type": "UNCLASSIFIED_UNIVERSAL_TRACE_EVENT",
        "event_id": event.get("event_id", "unknown"),
        "op": event.get("op", "unknown"),
        "class_code": event.get("class_code", "unknown"),
        "integrity_type": classification["integrity_type"],
        "reason": classification["reason"],
        "policy": "events outside the finite universal trace vocabulary are rejected from accepted traces unless represented as residues",
    }


def schema_shape_check(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("schema", "event_id", "step", "op", "class_code", "integrity_type", "public_inputs", "public_outputs", "checks"):
        if key not in schema["required"]:
            errors.append(f"schema missing required field: {key}")
    if "UNCLASSIFIED" not in schema["properties"]["integrity_type"]["enum"]:
        errors.append("schema does not include UNCLASSIFIED fallback type")
    if "residue" not in schema["properties"]["op"]["enum"]:
        errors.append("schema does not include residue op")
    return errors


def vocabulary_totality_check() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicate_codes: list[str] = []
    type_counts = {"C": 0, "V": 0, "X": 0, "UNCLASSIFIED": 0}
    for expected_type, codes in (
        ("C", C_PUBLIC_CLASS_CODES),
        ("V", V_VISIBLE_CLASS_CODES),
        ("X", X_EXTRACTOR_CLASS_CODES),
    ):
        for class_code in sorted(codes):
            if class_code in seen:
                duplicate_codes.append(class_code)
            seen.add(class_code)
            classification = classify_class_code(class_code)
            type_counts[classification["integrity_type"]] += 1
            rows.append(
                {
                    "class_code": class_code,
                    "expected_integrity_type": expected_type,
                    "classifier_integrity_type": classification["integrity_type"],
                    "status": classification["status"],
                    "passed": (
                        classification["status"] == "classified"
                        and classification["integrity_type"] == expected_type
                    ),
                }
            )
    failures = [row for row in rows if not row["passed"]]
    return {
        "vocabulary_class_code_count": len(rows),
        "type_counts": type_counts,
        "duplicate_codes": duplicate_codes,
        "failures": failures,
        "passed": not duplicate_codes and not failures and type_counts["UNCLASSIFIED"] == 0,
        "rows": rows,
    }


def current_trace_classification() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    residues: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    counts = {"C": 0, "V": 0, "X": 0, "UNCLASSIFIED": 0}

    for path in TRACE_PATHS:
        trace = load_json(path)
        for event in trace.get("events", []):
            classification = classify_event(event)
            counts[classification["integrity_type"]] += 1
            row = {
                "trace_path": rel(path),
                "trace_id": trace.get("trace_id"),
                "event_id": event.get("event_id"),
                "class_code": event.get("class_code"),
                "trace_integrity_type": event.get("integrity_type"),
                "classifier_integrity_type": classification["integrity_type"],
                "status": classification["status"],
            }
            rows.append(row)
            if classification["status"] == "residue":
                residues.append(row)
            elif event.get("integrity_type") != classification["integrity_type"]:
                mismatches.append(row)

    return {
        "trace_paths": [rel(path) for path in TRACE_PATHS],
        "event_count": len(rows),
        "classified_counts": counts,
        "residue_count": len(residues),
        "mismatch_count": len(mismatches),
        "residues": residues,
        "mismatches": mismatches,
        "accepted_events": rows,
        "passed": not residues and not mismatches,
    }


def unsupported_fixture() -> dict[str, Any]:
    return {
        "schema": "d20.integrity.universal_trace_event.v1",
        "event_id": "unsupported-universal-opcode-fixture:0001",
        "step": 1,
        "op": "universal_machine_opcode",
        "class_code": "UNKNOWN_NATIVE_MACHINE_INSTRUCTION",
        "integrity_type": "UNCLASSIFIED",
        "reason": "fixture event used to witness residue fallback",
        "public_inputs": {},
        "public_outputs": {},
        "checks": {
            "locally_checkable": False,
            "uses_hidden_advice": False,
            "uses_extension_variable": False,
        },
    }


def main() -> int:
    schema = universal_event_schema()
    schema_errors = schema_shape_check(schema)
    vocabulary_check = vocabulary_totality_check()
    trace_check = current_trace_classification()
    fallback = classify_event(unsupported_fixture())
    fallback_residue = residue_for(unsupported_fixture(), fallback)

    fallback_passed = (
        fallback["status"] == "residue"
        and fallback["integrity_type"] == "UNCLASSIFIED"
    )
    pass_condition = (
        not schema_errors
        and vocabulary_check["passed"]
        and trace_check["passed"]
        and fallback_passed
    )

    report = {
        "schema": "d20.integrity.universal_trace_typing_report.v1",
        "status": (
            "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS"
            if pass_condition
            else "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_FAIL"
        ),
        "schema_path": rel(SCHEMA_PATH),
        "classifier_path": rel(CLASSIFIER_PATH),
        "residue_fallback_path": rel(RESIDUE_PATH),
        "schema_shape_check": {
            "passed": not schema_errors,
            "errors": schema_errors,
        },
        "vocabulary_totality_check": vocabulary_check,
        "current_trace_classification": trace_check,
        "fallback_fixture": {
            "class_code": unsupported_fixture()["class_code"],
            "status": fallback["status"],
            "integrity_type": fallback["integrity_type"],
            "residue_path": rel(RESIDUE_PATH),
            "passed": fallback_passed,
        },
        "decision": {
            "may_claim_totality_for_universal_trace_vocabulary": pass_condition,
            "may_claim_totality_for_uncompiled_native_machine_instructions": False,
            "may_claim_full_separation": False,
            "reason": "The finite universal trace vocabulary is totally typed with explicit residue fallback. Native instructions are not silently accepted; they must compile into this vocabulary or become residues.",
        },
        "non_claim": "This report does not provide the arbitrary-solver trace compiler, the no-escape theorem over all universal traces, an X-extractor lower bound, or P != NP.",
        "next_highest_yield_item": {
            "id": "pure_c_no_escape",
            "action": "Lift pure-C no-escape from current accepted traces to the universal trace vocabulary.",
        },
    }

    SCHEMA_PATH.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CLASSIFIER_PATH.write_text(json.dumps(classifier_document(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RESIDUE_PATH.write_text(json.dumps(fallback_residue, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if pass_condition else 1


if __name__ == "__main__":
    raise SystemExit(main())
