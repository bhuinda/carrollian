from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
CLASSIFIER_PATH = BASE / "reports" / "universal_trace_typing_classifier.json"
TYPING_REPORT_PATH = BASE / "reports" / "universal_trace_typing_report.json"
CURRENT_PURE_C_REPORT_PATH = BASE / "reports" / "pure_c_no_escape_report.json"
REPORT_PATH = BASE / "reports" / "universal_pure_c_no_escape_report.json"

FORBIDDEN_C_TEXT_TOKENS = {
    "ADVICE",
    "E33",
    "EXTRACTOR",
    "HIDDEN",
    "NON-PUBLIC",
    "NONPUBLIC",
    "SECTOR",
}

REQUIRED_X_SURFACE_CODES = {
    "X_EXTRACTOR_HIDDEN_ADVICE_READ",
    "X_EXTRACTOR_HIDDEN_SECTOR_MAP",
    "X_EXTRACTOR_PARITY_BASIS_RECOVERY",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def text_hits(value: str, tokens: set[str]) -> list[str]:
    haystack = value.upper()
    return sorted(token for token in tokens if token in haystack)


def audit_c_vocabulary(classifier: dict[str, Any]) -> dict[str, Any]:
    c_codes = classifier.get("public_c_class_codes", {})
    v_codes = classifier.get("visible_v_class_codes", {})
    x_codes = classifier.get("extractor_x_class_codes", {})
    failures: list[dict[str, Any]] = []

    for class_code, description in sorted(c_codes.items()):
        errors: list[str] = []
        if not class_code.startswith("C_PUBLIC_"):
            errors.append("C class code does not use C_PUBLIC_ prefix")
        if class_code in v_codes:
            errors.append("C class code overlaps V surface")
        if class_code in x_codes:
            errors.append("C class code overlaps X surface")
        code_hits = text_hits(class_code, {"E33", "EXTRACTOR", "HIDDEN", "NONPUBLIC", "SECTOR"})
        description_hits = text_hits(str(description), FORBIDDEN_C_TEXT_TOKENS)
        if code_hits:
            errors.append("C class code contains extractor/hidden token: " + ",".join(code_hits))
        if description_hits:
            errors.append("C description contains extractor/hidden token: " + ",".join(description_hits))
        if errors:
            failures.append(
                {
                    "class_code": class_code,
                    "description": description,
                    "errors": errors,
                }
            )

    return {
        "c_class_code_count": len(c_codes),
        "forbidden_text_tokens": sorted(FORBIDDEN_C_TEXT_TOKENS),
        "failures": failures,
        "passed": not failures and len(c_codes) > 0,
    }


def audit_x_surface(classifier: dict[str, Any]) -> dict[str, Any]:
    x_codes = classifier.get("extractor_x_class_codes", {})
    missing = sorted(REQUIRED_X_SURFACE_CODES - set(x_codes))
    return {
        "x_class_code_count": len(x_codes),
        "required_x_surface_codes": sorted(REQUIRED_X_SURFACE_CODES),
        "missing_required_x_surface_codes": missing,
        "passed": not missing,
    }


def audit_typing_report(typing_report: dict[str, Any]) -> dict[str, Any]:
    current = typing_report.get("current_trace_classification", {})
    fallback = typing_report.get("fallback_fixture", {})
    errors: list[str] = []
    if typing_report.get("status") != "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS":
        errors.append("universal trace typing did not pass")
    if typing_report.get("decision", {}).get("may_claim_totality_for_universal_trace_vocabulary") is not True:
        errors.append("universal trace vocabulary totality is not claimable")
    if current.get("residue_count") != 0:
        errors.append("current traces contain universal typing residues")
    if current.get("mismatch_count") != 0:
        errors.append("current traces contain universal typing mismatches")
    counts = current.get("classified_counts", {})
    if counts.get("V", 0) != 0 or counts.get("X", 0) != 0 or counts.get("UNCLASSIFIED", 0) != 0:
        errors.append("current traces are not purely C under universal typing")
    if fallback.get("status") != "residue" or fallback.get("integrity_type") != "UNCLASSIFIED":
        errors.append("unsupported universal event did not produce UNCLASSIFIED residue")
    return {
        "path": rel(TYPING_REPORT_PATH),
        "status": typing_report.get("status"),
        "current_trace_classified_counts": counts,
        "fallback_fixture": fallback,
        "errors": errors,
        "passed": not errors,
    }


def audit_current_pure_c_report(report: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if report.get("status") != "PURE_C_NO_ESCAPE_WITNESS_PASS":
        errors.append("current pure-C no-escape report did not pass")
    if report.get("accepted_antecedent_holds") is not True:
        errors.append("current accepted pure-C antecedent does not hold")
    return {
        "path": rel(CURRENT_PURE_C_REPORT_PATH),
        "status": report.get("status"),
        "trace_count": report.get("trace_count"),
        "event_count": report.get("event_count"),
        "errors": errors,
        "passed": not errors,
    }


def main() -> int:
    classifier = load_json(CLASSIFIER_PATH)
    typing_report = load_json(TYPING_REPORT_PATH)
    current_pure_c_report = load_json(CURRENT_PURE_C_REPORT_PATH)

    c_audit = audit_c_vocabulary(classifier)
    x_audit = audit_x_surface(classifier)
    typing_audit = audit_typing_report(typing_report)
    current_audit = audit_current_pure_c_report(current_pure_c_report)
    pass_condition = all(
        item["passed"]
        for item in (c_audit, x_audit, typing_audit, current_audit)
    )

    report = {
        "schema": "d20.integrity.universal_pure_c_no_escape_report.source_drop",
        "status": (
            "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS"
            if pass_condition
            else "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_FAIL"
        ),
        "theorem_replayed": "No Public Extractor Theorem over the finite universal trace vocabulary",
        "antecedent": "A trace contains only C_PUBLIC_* events from the finite universal vocabulary, uses no hidden advice, contains no V/X/UNCLASSIFIED events, and emits no residues.",
        "conditional_conclusion": "Under this antecedent, a pure-C universal trace has no operation capable of reading hidden advice, reconstructing the hidden e33 map, or recovering a non-public parity basis. Those operations are typed X or rejected as residues.",
        "classifier_path": rel(CLASSIFIER_PATH),
        "typing_report_path": rel(TYPING_REPORT_PATH),
        "current_pure_c_report_path": rel(CURRENT_PURE_C_REPORT_PATH),
        "c_vocabulary_audit": c_audit,
        "x_surface_audit": x_audit,
        "typing_report_audit": typing_audit,
        "current_trace_audit": current_audit,
        "decision": {
            "may_claim_universal_vocabulary_pure_c_no_escape": pass_condition,
            "may_claim_arbitrary_solver_no_escape": False,
            "may_claim_full_separation": False,
            "reason": "Pure-C no-escape is lifted to traces already expressed in the finite universal vocabulary. Arbitrary solvers still require the compiler bridge, X lower bound, V accounting, and encoded-family bridge.",
        },
        "non_claim": "This report does not prove arbitrary solver compilation, no polynomial X extractor, arbitrary V wall-crossing accounting, encoded-family SAT-completeness, or P != NP.",
        "next_highest_yield_item": {
            "id": "encoded_family_sat_complete",
            "action": "Build the reduction certificate for the hidden e33-obstructed family, or keep the claim representative/current-trace scoped.",
        },
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if pass_condition else 1


if __name__ == "__main__":
    raise SystemExit(main())
