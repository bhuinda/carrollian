from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
REPORT_PATH = CVX / "reports" / "x_policy_boundary_certificate.json"

CLASSIFIER_REPORT = CVX / "reports" / "universal_trace_typing_classifier.json"
UNIVERSAL_TRACE_TYPING_REPORT = CVX / "reports" / "universal_trace_typing_report.json"
UNIVERSAL_TRACE_COMPILER_REPORT = CVX / "reports" / "universal_trace_compiler_report.json"
UNIVERSAL_PURE_C_REPORT = CVX / "reports" / "universal_pure_c_no_escape_report.json"
UNIVERSAL_V_REPORT = CVX / "reports" / "universal_v_wall_crossing_accounting_report.json"
UNIVERSAL_X_ISOLATION_REPORT = CVX / "reports" / "universal_x_extractor_isolation_report.json"
X_FRONTIER_REPORT = CVX / "reports" / "x_extractor_frontier_certificate.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def report_status(path: Path, expected_status: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "path": rel(path),
        "status": data.get("status"),
        "expected_status": expected_status,
        "passed": data.get("status") == expected_status,
    }


def build_policy() -> dict[str, Any]:
    classifier = load_json(CLASSIFIER_REPORT)
    typing = load_json(UNIVERSAL_TRACE_TYPING_REPORT)
    compiler = load_json(UNIVERSAL_TRACE_COMPILER_REPORT)
    pure_c = load_json(UNIVERSAL_PURE_C_REPORT)
    v_report = load_json(UNIVERSAL_V_REPORT)
    x_isolation = load_json(UNIVERSAL_X_ISOLATION_REPORT)
    frontier = load_json(X_FRONTIER_REPORT)

    c_codes = set(classifier.get("public_c_class_codes", {}))
    v_codes = set(classifier.get("visible_v_class_codes", {}))
    x_codes = set(classifier.get("extractor_x_class_codes", {}))
    public_machine_codes = set(compiler["compiler_rules"]["opcode_to_class_code"].values())
    surfaces_are_disjoint = not (c_codes & v_codes) and not (c_codes & x_codes) and not (v_codes & x_codes)
    public_machine_compiles_to_c_only = public_machine_codes <= c_codes and all(
        code.startswith("C_PUBLIC_") for code in public_machine_codes
    )
    current_counts = typing["current_trace_classification"]["classified_counts"]

    checks = {
        "typing_totality_passed": typing.get("status") == "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
        "classifier_surfaces_disjoint": surfaces_are_disjoint,
        "public_machine_compiles_to_c_only": public_machine_compiles_to_c_only,
        "pure_c_no_escape_passed": pure_c.get("status") == "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS",
        "v_surface_publicly_accounted": v_report.get("status") == "UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_PASS",
        "x_surface_isolated": x_isolation.get("status") == "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS",
        "explicit_x_extractor_promoted": frontier.get("status")
        == "X_EXTRACTOR_FRONTIER_EXPLICIT_POLYNOMIAL_FAMILY_EXTRACTOR_PROMOTED",
        "current_accepted_traces_have_zero_x": current_counts.get("X") == 0,
        "current_accepted_traces_have_zero_unclassified": current_counts.get("UNCLASSIFIED") == 0,
    }
    passed = all(checks.values())

    return {
        "schema": "d20.integrity.x_policy_boundary_certificate.source_drop",
        "status": "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X" if passed else "X_POLICY_BOUNDARY_REQUIRES_REVIEW",
        "claim_level": "formal_x_policy_boundary_not_x_lower_bound",
        "policy": {
            "ordinary_public_p_execution": {
                "allowed_integrity_types": ["C"],
                "meaning": "A compiled public finite-bit-machine execution uses only C_PUBLIC_* operations.",
            },
            "public_certificate_surface": {
                "allowed_integrity_types": ["V"],
                "admission_rule": "V events require replayable public-boundary certificates; uncertified V events become residues.",
                "meaning": "V can extend an auditable public transcript but does not provide hidden-sector advice.",
            },
            "hidden_extractor_surface": {
                "allowed_integrity_types": ["X"],
                "admission_rule": "X events are explicit hidden-sector extractor/oracle/advice steps, not public-P operations.",
                "meaning": "A trace containing X is an extractor trace or oracle/advice trace. It cannot be used as a public-P solver witness unless the theorem deliberately changes models.",
            },
            "residue_surface": {
                "allowed_integrity_types": ["UNCLASSIFIED"],
                "admission_rule": "unsupported or untyped events are explicit residues and do not silently enter closure.",
            },
        },
        "source_audit": {
            "universal_trace_typing": report_status(
                UNIVERSAL_TRACE_TYPING_REPORT,
                "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
            ),
            "universal_trace_compiler": report_status(
                UNIVERSAL_TRACE_COMPILER_REPORT,
                "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
            ),
            "universal_pure_c_no_escape": report_status(
                UNIVERSAL_PURE_C_REPORT,
                "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS",
            ),
            "universal_v_wall_crossing_accounting": report_status(
                UNIVERSAL_V_REPORT,
                "UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_PASS",
            ),
            "universal_x_extractor_isolation": report_status(
                UNIVERSAL_X_ISOLATION_REPORT,
                "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS",
            ),
            "x_extractor_frontier": report_status(
                X_FRONTIER_REPORT,
                "X_EXTRACTOR_FRONTIER_EXPLICIT_POLYNOMIAL_FAMILY_EXTRACTOR_PROMOTED",
            ),
        },
        "surface_summary": {
            "c_class_code_count": len(c_codes),
            "v_class_code_count": len(v_codes),
            "x_class_code_count": len(x_codes),
            "surfaces_are_disjoint": surfaces_are_disjoint,
            "public_machine_opcode_count": len(public_machine_codes),
            "public_machine_compiles_to_c_only": public_machine_compiles_to_c_only,
            "current_trace_classified_counts": current_counts,
        },
        "x_frontier_resolution": {
            "explicit_extractor_id": frontier["extractor"]["id"],
            "explicit_extractor_opcode": frontier["extractor"]["x_opcode"],
            "may_claim_explicit_polynomial_family_x_extractor": frontier["decision"][
                "may_claim_explicit_polynomial_family_x_extractor"
            ],
            "may_claim_no_polynomial_size_x_extractor": frontier["decision"][
                "may_claim_no_polynomial_size_x_extractor"
            ],
            "policy_resolution": "The explicit extractor is admitted only as X; it is not reclassified as C or V.",
        },
        "checks": checks,
        "decision": {
            "may_claim_x_policy_boundary_certified": passed,
            "may_claim_x_obligation_closed_by_explicit_extractor_policy": passed,
            "may_claim_public_p_excludes_x": passed,
            "may_claim_no_polynomial_size_x_extractor": False,
            "may_claim_full_separation": False,
            "reason": (
                "The explicit sector-33 extractor exists at family scope, but the formal policy keeps it on "
                "the X surface. Public-P executions compile to C-only traces; V is public-certificate "
                "surface; X is oracle/advice/extractor surface."
            ),
        },
        "non_claims": [
            "This does not prove that polynomial-size X extractors are impossible.",
            "This does not prove SAT-completeness of the encoded family.",
            "This does not prove P != NP.",
        ],
        "next_highest_yield_item": {
            "id": "full_no_escape_closure",
            "action": "Refresh the full no-escape closure ledger against the certified encoded-family reduction.",
        },
    }


def main() -> int:
    report = build_policy()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["status"] == "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X" else 1


if __name__ == "__main__":
    raise SystemExit(main())
