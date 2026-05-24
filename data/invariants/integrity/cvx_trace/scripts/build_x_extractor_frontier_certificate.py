from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
REPORT_PATH = CVX / "reports" / "x_extractor_frontier_certificate.json"

CLASSIFIER_REPORT = CVX / "reports" / "universal_trace_typing_classifier.json"
X_BOUNDED_SEARCH_REPORT = CVX / "reports" / "x_extractor_bounded_search_report.json"
X_ISOLATION_REPORT = CVX / "reports" / "universal_x_extractor_isolation_report.json"
X_TARGET_REPORT = CVX / "reports" / "x_extractor_target_certificate.json"
ENCODED_BRIDGE_REPORT = CVX / "reports" / "encoded_family_bridge_certificate.json"
UNIVERSAL_TRACE_COMPILER_REPORT = CVX / "reports" / "universal_trace_compiler_report.json"
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    ROOT / "data" / "invariants" / "d20" / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)


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


def build_frontier() -> dict[str, Any]:
    classifier = load_json(CLASSIFIER_REPORT)
    bounded = load_json(X_BOUNDED_SEARCH_REPORT)
    isolation = load_json(X_ISOLATION_REPORT)
    target = load_json(X_TARGET_REPORT)
    encoded = load_json(ENCODED_BRIDGE_REPORT)
    compiler = load_json(UNIVERSAL_TRACE_COMPILER_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)

    transport = target["target"]["intrinsic_height_coherent_transport"]
    active = transport["active_circuit"]
    edge_residual = transport["edge_derived_residual"]
    e33_support = int(transport["vectors"]["e33"]["support"])
    gamma8_edge_count = len(active["edge_ids"])
    representative_payload_width = gamma8_edge_count + e33_support + 6
    polynomial_bound_value = int(encoded["polynomial_faithfulness"]["polynomial_bound_value"])
    basis_width = len(all_residue["derived"]["basis_cycle_height_vector"])
    max_family_payload_width = basis_width + e33_support + 6

    x_codes = classifier.get("extractor_x_class_codes", {})
    required_opcode = "X_EXTRACTOR_HIDDEN_SECTOR_MAP"
    checks = {
        "x_surface_isolated": isolation.get("status") == "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS",
        "bounded_current_traces_have_no_x": bounded.get("result", {}).get("x_extractor_present") is False,
        "target_transport_certified": target.get("decision", {}).get(
            "may_claim_intrinsic_height_transport_derives_rho33_gamma8"
        )
        is True,
        "required_hidden_sector_opcode_available": required_opcode in x_codes,
        "gamma8_extractor_matches_target_residual": transport.get("matches_residual_lift_target") is True
        and edge_residual["residual_integral"] == target["target"]["residual"]["integral"],
        "gamma8_public_shadow_zero": transport["public_shadows"]["q42_nonzero_count"] == 0
        and transport["public_shadows"]["q12_nonzero_count"] == 0,
        "all_residue_transport_certified": all_residue.get("all_checks_pass") is True
        and all_residue["checks"]["all_transport_coefficients_match_height_residuals"],
        "representative_payload_within_prior_polynomial_bound": representative_payload_width
        <= polynomial_bound_value,
        "universal_public_compiler_polynomial": compiler.get("status")
        == "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
    }
    passed = all(checks.values())

    return {
        "schema": "d20.integrity.x_extractor_frontier_certificate.source_drop",
        "status": (
            "X_EXTRACTOR_FRONTIER_EXPLICIT_POLYNOMIAL_FAMILY_EXTRACTOR_PROMOTED"
            if passed
            else "X_EXTRACTOR_FRONTIER_REQUIRES_REVIEW"
        ),
        "claim_level": "explicit_polynomial_x_extractor_family_scope_not_lower_bound",
        "source_audit": {
            "universal_trace_typing_classifier": {
                "path": rel(CLASSIFIER_REPORT),
                "required_hidden_sector_opcode": required_opcode,
                "required_opcode_present": required_opcode in x_codes,
                "x_opcode_count": len(x_codes),
            },
            "x_extractor_bounded_search": report_status(
                X_BOUNDED_SEARCH_REPORT,
                "X_EXTRACTOR_BOUNDED_SEARCH_NO_EXTRACTOR_FOUND",
            ),
            "universal_x_extractor_isolation": report_status(
                X_ISOLATION_REPORT,
                "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS",
            ),
            "x_extractor_target": report_status(
                X_TARGET_REPORT,
                "X_EXTRACTOR_TARGET_AND_INTRINSIC_TRANSPORT_CERTIFIED_POLYNOMIAL_LOWER_BOUND_OPEN",
            ),
            "encoded_family_bridge": report_status(
                ENCODED_BRIDGE_REPORT,
                "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
            ),
            "universal_trace_compiler": report_status(
                UNIVERSAL_TRACE_COMPILER_REPORT,
                "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
            ),
            "sector33_all_residue_height_transport": report_status(
                ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT,
                "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED",
            ),
        },
        "extractor": {
            "id": "E_hc_sector33",
            "x_opcode": required_opcode,
            "scope": "certified d20 closed-return residue family and the cycle-8 / Pi_33 representative packet",
            "input": [
                "closed-return circuit row C_gamma",
                "certified height cochain h",
                "certified public-zero sector support e_33",
                "dim(Pi_33)",
            ],
            "algorithm": [
                "compute A_h(gamma)=<C_gamma,h>",
                "compute scalar -A_h(gamma)/dim(Pi_33) in F_1000003",
                "return rho_33(gamma)=(-A_h(gamma)/dim(Pi_33)) e_33",
                "optionally return Lambda_hc(gamma)=lambda_boundary(gamma)+rho_33(gamma)",
            ],
            "gamma8_witness": {
                "edge_ids": active["edge_ids"],
                "edge_count": gamma8_edge_count,
                "height_action": active["height_action"],
                "residual_integral": edge_residual["residual_integral"],
                "residual_mod_prime": edge_residual["residual_mod_prime"],
                "transport_scalar": edge_residual["transport_scalar"],
                "height_transport_sha256": transport["vectors"]["height_transport"]["sha256"],
                "corrected_transport_sha256": transport["vectors"]["corrected_transport"]["sha256"],
                "q42_nonzero_count": transport["public_shadows"]["q42_nonzero_count"],
                "q12_nonzero_count": transport["public_shadows"]["q12_nonzero_count"],
            },
            "all_residue_family_witness": {
                "basis_cycle_width": basis_width,
                "residue_class_count": all_residue["derived"]["residue_class_count"],
                "nonzero_residue_class_count": all_residue["derived"]["nonzero_residue_class_count"],
                "transport_rows_sha256": all_residue["derived"]["transport_rows_sha256"],
                "support_sector": all_residue["derived"]["sector33_support"]["sector"],
            },
        },
        "complexity": {
            "representative_payload_width": representative_payload_width,
            "representative_prior_polynomial_bound": polynomial_bound_value,
            "representative_within_prior_polynomial_bound": representative_payload_width
            <= polynomial_bound_value,
            "family_basis_width": basis_width,
            "e33_support": e33_support,
            "max_family_payload_width": max_family_payload_width,
            "runtime_bound": "O(active_circuit_support + support(e_33)) for materialized vector output; O(active_circuit_support) for scalar residual output with e_33 as certified support handle.",
            "verification_bound": "one X opcode classification plus height-dot-product replay and q42/q12 zero-shadow checks",
        },
        "checks": checks,
        "decision": {
            "may_claim_explicit_polynomial_family_x_extractor": passed,
            "may_claim_no_polynomial_size_x_extractor": False,
            "may_claim_x_extractor_lower_bound": False,
            "may_claim_full_separation": False,
            "reason": (
                "The certified height-coherent transport gives an explicit polynomial family-scope X extractor "
                "for the sector-33 residual. Therefore the no-polynomial-X lower-bound branch is not proved; "
                "the extractor branch is promoted as the central object."
            ),
        },
        "non_claims": [
            "This does not prove that polynomial-size X extractors are impossible.",
            "This does not make the X extractor a public-C operation; it remains on the X surface.",
            "This does not certify SAT-completeness of the encoded family.",
            "This does not prove P != NP.",
        ],
        "next_highest_yield_item": {
            "id": "formal_x_policy_boundary",
            "action": "Define whether X events are excluded public computation, oracle/advice events, or admitted hidden-sector extractor steps in the final no-escape theorem.",
        },
    }


def main() -> int:
    report = build_frontier()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["status"] == "X_EXTRACTOR_FRONTIER_EXPLICIT_POLYNOMIAL_FAMILY_EXTRACTOR_PROMOTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
