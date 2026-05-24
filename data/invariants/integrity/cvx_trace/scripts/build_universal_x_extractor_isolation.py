from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
CLASSIFIER_PATH = BASE / "reports" / "universal_trace_typing_classifier.json"
TYPING_REPORT_PATH = BASE / "reports" / "universal_trace_typing_report.json"
PURE_C_REPORT_PATH = BASE / "reports" / "universal_pure_c_no_escape_report.json"
BOUNDED_SEARCH_REPORT_PATH = BASE / "reports" / "x_extractor_bounded_search_report.json"
REPORT_PATH = BASE / "reports" / "universal_x_extractor_isolation_report.json"

EXTRACTOR_TOKENS = {
    "ADVICE",
    "E33",
    "EXTRACTOR",
    "GAUSSIAN",
    "GF(2)",
    "HIDDEN",
    "NON-PUBLIC",
    "NONPUBLIC",
    "PARITY",
    "SECTOR",
    "XOR",
}

NON_X_FORBIDDEN_TOKENS = {
    "ADVICE",
    "E33",
    "EXTRACTOR",
    "HIDDEN",
    "NON-PUBLIC",
    "NONPUBLIC",
    "SECTOR",
}

REQUIRED_X_CODES = {
    "X_EXTRACTOR_GF2_GAUSSIAN_ELIMINATION",
    "X_EXTRACTOR_HIDDEN_ADVICE_READ",
    "X_EXTRACTOR_HIDDEN_SECTOR_MAP",
    "X_EXTRACTOR_NATIVE_XOR_ELIMINATION",
    "X_EXTRACTOR_NONPUBLIC_PARITY_BASIS",
    "X_EXTRACTOR_PARITY_BASIS_RECOVERY",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def token_hits(value: str, tokens: set[str] = EXTRACTOR_TOKENS) -> list[str]:
    haystack = value.upper()
    return sorted(token for token in tokens if token in haystack)


def audit_surfaces(classifier: dict[str, Any]) -> dict[str, Any]:
    c_codes = classifier.get("public_c_class_codes", {})
    v_codes = classifier.get("visible_v_class_codes", {})
    x_codes = classifier.get("extractor_x_class_codes", {})
    failures: list[dict[str, Any]] = []

    for surface_name, expected_prefix, codes in (
        ("C", "C_PUBLIC_", c_codes),
        ("V", "V_VISIBLE_", v_codes),
        ("X", "X_EXTRACTOR_", x_codes),
    ):
        for class_code, description in sorted(codes.items()):
            errors: list[str] = []
            if not class_code.startswith(expected_prefix):
                errors.append(f"{surface_name} code lacks {expected_prefix} prefix")
            if surface_name != "X":
                hits = token_hits(f"{class_code} {description}", NON_X_FORBIDDEN_TOKENS)
                if hits:
                    errors.append("non-X surface contains extractor token: " + ",".join(hits))
            if surface_name == "X":
                hits = token_hits(f"{class_code} {description}")
                if not hits:
                    errors.append("X surface lacks extractor token")
            if errors:
                failures.append(
                    {
                        "surface": surface_name,
                        "class_code": class_code,
                        "description": description,
                        "errors": errors,
                    }
                )

    overlap_failures: list[dict[str, Any]] = []
    surfaces = {"C": set(c_codes), "V": set(v_codes), "X": set(x_codes)}
    for left_name, left_codes in surfaces.items():
        for right_name, right_codes in surfaces.items():
            if left_name >= right_name:
                continue
            overlap = sorted(left_codes & right_codes)
            if overlap:
                overlap_failures.append(
                    {
                        "left": left_name,
                        "right": right_name,
                        "overlap": overlap,
                    }
                )

    missing_required_x = sorted(REQUIRED_X_CODES - set(x_codes))
    return {
        "surface_counts": {
            "C": len(c_codes),
            "V": len(v_codes),
            "X": len(x_codes),
        },
        "required_x_codes": sorted(REQUIRED_X_CODES),
        "missing_required_x_codes": missing_required_x,
        "surface_failures": failures,
        "overlap_failures": overlap_failures,
        "passed": not failures and not overlap_failures and not missing_required_x,
    }


def audit_upstream_reports(
    typing_report: dict[str, Any],
    pure_c_report: dict[str, Any],
    bounded_report: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    if typing_report.get("status") != "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS":
        errors.append("universal typing witness did not pass")
    if pure_c_report.get("status") != "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS":
        errors.append("universal pure-C no-escape witness did not pass")
    if bounded_report.get("status") != "X_EXTRACTOR_BOUNDED_SEARCH_NO_EXTRACTOR_FOUND":
        errors.append("bounded current-trace X search did not pass")
    if bounded_report.get("result", {}).get("x_extractor_present") is not False:
        errors.append("current trace bounded search detected an X extractor")
    if bounded_report.get("result", {}).get("e33_extraction_present") is not False:
        errors.append("current trace bounded search detected e33 extraction")
    return {
        "typing_report": {
            "path": rel(TYPING_REPORT_PATH),
            "status": typing_report.get("status"),
        },
        "universal_pure_c_no_escape": {
            "path": rel(PURE_C_REPORT_PATH),
            "status": pure_c_report.get("status"),
        },
        "bounded_current_trace_search": {
            "path": rel(BOUNDED_SEARCH_REPORT_PATH),
            "status": bounded_report.get("status"),
            "result": bounded_report.get("result"),
        },
        "errors": errors,
        "passed": not errors,
    }


def main() -> int:
    classifier = load_json(CLASSIFIER_PATH)
    typing_report = load_json(TYPING_REPORT_PATH)
    pure_c_report = load_json(PURE_C_REPORT_PATH)
    bounded_report = load_json(BOUNDED_SEARCH_REPORT_PATH)

    surface_audit = audit_surfaces(classifier)
    upstream_audit = audit_upstream_reports(typing_report, pure_c_report, bounded_report)
    pass_condition = surface_audit["passed"] and upstream_audit["passed"]

    report = {
        "schema": "d20.integrity.universal_x_extractor_isolation.source_drop",
        "status": (
            "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS"
            if pass_condition
            else "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_FAIL"
        ),
        "claim_level": "finite_universal_vocabulary_x_surface_isolation",
        "classifier_path": rel(CLASSIFIER_PATH),
        "surface_audit": surface_audit,
        "upstream_audit": upstream_audit,
        "isolation_witness": {
            "minimum_x_event_count_for_extractor_opcode": 1,
            "zero_x_trace_can_contain_extractor_opcode": False,
            "current_accepted_trace_x_event_count": 0,
            "current_accepted_trace_extractor_found": False,
            "meaning": "Within the finite universal trace vocabulary, every extractor-capable operation is on the X surface. Pure C/V traces and residue-free zero-X traces do not contain extractor opcodes.",
        },
        "decision": {
            "may_claim_universal_vocabulary_x_surface_isolated": pass_condition,
            "may_claim_no_polynomial_size_x_extractor": False,
            "may_claim_full_separation": False,
            "reason": "The X surface is isolated and current accepted traces contain no X extractor. This is not a lower bound against polynomial-size X traces for the hidden e33 family.",
        },
        "non_claim": "This report does not rule out polynomial-size X extractors. It only isolates the extractor surface and preserves the lower-bound obligation.",
        "next_highest_yield_item": {
            "id": "x_extractor_target_certificate",
            "action": "Certify the concrete hidden-sector target that any X extractor must recover.",
        },
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if pass_condition else 1


if __name__ == "__main__":
    raise SystemExit(main())
