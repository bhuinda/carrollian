from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
TRACE_PATH = BASE / "traces" / "public_dpll_contradiction_4.trace.json"
CLASSIFIER_PATH = BASE / "reports" / "solver_opcode_totality_classifier.json"
REPORT_PATH = BASE / "reports" / "solver_opcode_totality_report.json"
RESIDUE_PATH = BASE / "residues" / "unsupported_solver_opcode_residue.json"


C_PUBLIC_CLASS_CODES = {
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
}

X_EXTRACTOR_CLASS_CODES = {
    "X_EXTRACTOR_NATIVE_XOR_ELIMINATION": "native XOR elimination recovers hidden parity structure",
    "X_EXTRACTOR_GF2_GAUSSIAN_ELIMINATION": "GF(2) Gaussian elimination adjoins a hidden parity extractor",
    "X_EXTRACTOR_PARITY_BASIS_RECOVERY": "solver recovers hidden-sector parity basis",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def classify_event(event: dict[str, Any]) -> dict[str, Any]:
    class_code = event.get("class_code", "")
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
        "reason": "unsupported solver opcode or class code; emitted as explicit typed residue",
    }


def residue_for(event: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "d20.integrity.cvx_trace.unsupported_opcode_residue.source_drop",
        "status": "CVX_TRACE_UNSUPPORTED_OPCODE_TYPED_RESIDUE",
        "residue_type": "UNCLASSIFIED_SOLVER_OPCODE",
        "source_trace": rel(TRACE_PATH),
        "event_id": event.get("event_id", "unknown"),
        "op": event.get("op", "unknown"),
        "class_code": event.get("class_code", "unknown"),
        "integrity_type": classification["integrity_type"],
        "reason": classification["reason"],
        "policy": "unknown opcodes are rejected from accepted traces unless represented as residues",
    }


def classifier_document() -> dict[str, Any]:
    return {
        "schema": "d20.integrity.solver_opcode_totality_classifier.source_drop",
        "status": "SOLVER_OPCODE_TOTALITY_CLASSIFIER_DEFINED",
        "accepted_types": ["C", "V", "X"],
        "fallback_type": "UNCLASSIFIED",
        "fallback_policy": "emit_explicit_typed_residue",
        "public_c_class_codes": C_PUBLIC_CLASS_CODES,
        "visible_v_class_codes": V_VISIBLE_CLASS_CODES,
        "extractor_x_class_codes": X_EXTRACTOR_CLASS_CODES,
    }


def unsupported_fixture() -> dict[str, Any]:
    return {
        "event_id": "unsupported-opcode-fixture:0001",
        "line": 1,
        "proof_id": 1,
        "op": "solver_opcode",
        "integrity_type": "UNCLASSIFIED",
        "class_code": "UNKNOWN_NATIVE_SOLVER_HEURISTIC",
        "reason": "fixture event used to witness residue fallback",
        "public_inputs": {"clause_hints": [], "literals": []},
        "public_outputs": {"clause_id": 1, "literal_count": 0, "empty_clause": False},
        "checks": {
            "uses_extension_variable": False,
            "has_duplicate_literal": False,
            "contains_complement_pair": False,
            "locally_checkable": False,
        },
    }


def main() -> int:
    trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
    accepted: list[dict[str, Any]] = []
    residues: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []

    for event in trace["events"]:
        classification = classify_event(event)
        accepted.append(
            {
                "event_id": event["event_id"],
                "class_code": event["class_code"],
                "trace_integrity_type": event["integrity_type"],
                "classifier_integrity_type": classification["integrity_type"],
                "status": classification["status"],
            }
        )
        if classification["status"] == "residue":
            residues.append(residue_for(event, classification))
        elif event["integrity_type"] != classification["integrity_type"]:
            mismatches.append(accepted[-1])

    fallback = classify_event(unsupported_fixture())
    fallback_residue = residue_for(unsupported_fixture(), fallback)
    RESIDUE_PATH.write_text(json.dumps(fallback_residue, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    counts = {"C": 0, "V": 0, "X": 0, "UNCLASSIFIED": 0}
    for row in accepted:
        counts[row["classifier_integrity_type"]] += 1

    report = {
        "schema": "d20.integrity.solver_opcode_totality_report.source_drop",
        "status": (
            "SOLVER_OPCODE_TOTALITY_WITNESS_PASS"
            if not residues and not mismatches and fallback["status"] == "residue"
            else "SOLVER_OPCODE_TOTALITY_WITNESS_FAIL"
        ),
        "trace_path": rel(TRACE_PATH),
        "classifier_path": rel(CLASSIFIER_PATH),
        "residue_fallback_path": rel(RESIDUE_PATH),
        "accepted_event_count": len(accepted),
        "accepted_integrity_counts": counts,
        "accepted_events": accepted,
        "accepted_trace_residue_count": len(residues),
        "mismatches": mismatches,
        "fallback_fixture": {
            "class_code": unsupported_fixture()["class_code"],
            "status": fallback["status"],
            "integrity_type": fallback["integrity_type"],
            "residue_path": rel(RESIDUE_PATH),
        },
        "scope": "Totality witness for the current public DPLL solver-opcode surface plus explicit residue fallback for unsupported opcodes; this is not a total classifier for arbitrary machine instructions.",
    }

    CLASSIFIER_PATH.write_text(
        json.dumps(classifier_document(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["status"].endswith("_PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
