from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
REPORT_PATH = CVX / "reports" / "x_extractor_target_certificate.json"

X_ISOLATION_REPORT = CVX / "reports" / "universal_x_extractor_isolation_report.json"
ENCODED_BRIDGE_REPORT = CVX / "reports" / "encoded_family_bridge_certificate.json"
BOUNDARY_ANNIHILATION_REPORT = (
    ROOT / "data" / "invariants" / "d20" / "theorems" / "sector33_boundary_annihilation" / "report.json"
)
RESIDUAL_LIFT_REPORT = (
    ROOT / "data" / "invariants" / "d20" / "theorems" / "sector33_residual_lift" / "report.json"
)
PROJECTION_OBLIGATION_REPORT = (
    ROOT / "data" / "invariants" / "d20" / "proof_obligations" / "cycle8_pi33_projection_coefficient" / "report.json"
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def report_status(path: Path, expected_status: str, all_checks: bool = False) -> dict[str, Any]:
    data = load_json(path)
    passed = data.get("status") == expected_status
    if all_checks:
        passed = passed and data.get("all_checks_pass") is True
    return {
        "path": rel(path),
        "status": data.get("status"),
        "expected_status": expected_status,
        "all_checks_pass": data.get("all_checks_pass"),
        "passed": passed,
    }


def build_target(
    residual_lift: dict[str, Any],
    boundary_annihilation: dict[str, Any],
    x_isolation: dict[str, Any],
) -> dict[str, Any]:
    derived = residual_lift["derived"]
    residual = derived["residual"]
    vectors = derived["vectors"]
    chi = derived["pi33_tube_character"]
    public_shadows = derived["public_shadows"]
    annihilation_checks = boundary_annihilation["checks"]
    isolation = x_isolation["isolation_witness"]

    return {
        "object_id": "rho33_cycle8_hidden_residual_lift",
        "cycle_id": derived["cycle_id"],
        "sector": derived["sector"],
        "field_prime": derived["field_prime"],
        "residual": {
            "integral": residual["integral"],
            "mod_prime": residual["mod_prime"],
            "dimension": residual["dimension"],
            "residual_lift_scalar": residual["residual_lift_scalar"],
            "residual_lift_scalar_signed": residual["residual_lift_scalar_signed"],
        },
        "public_transport_floor": {
            "bare_lambda_pi33_coefficient_signed": chi["lambda_boundary_gamma8"]["coefficient_signed"],
            "bare_lambda_pi33_coefficient_mod_prime": chi["lambda_boundary_gamma8"]["coefficient_mod_prime"],
            "all_30_directed_pair_lifts_annihilated": annihilation_checks[
                "pi33_annihilates_all_directed_pair_lifts_left_and_right"
            ],
            "cycle8_unweighted_annihilated": annihilation_checks["cycle8_unweighted_pi33_coefficient_is_zero"],
            "cycle8_optical_weighted_annihilated": annihilation_checks[
                "cycle8_optical_weighted_pi33_coefficient_is_zero"
            ],
            "cycle8_signed_orientation_annihilated": annihilation_checks[
                "cycle8_signed_orientation_pi33_coefficient_is_zero"
            ],
            "meaning": "The certified bare D20 boundary-to-Loop_297 transport has zero Pi_33 coefficient, including every directed object-pair lift and the cycle-8 variants.",
        },
        "hidden_residual_lift": {
            "e33_vector": {
                "support": vectors["e33"]["support"],
                "sha256": vectors["e33"]["sha256"],
                "pi33_coefficient_signed": chi["e33"]["coefficient_signed"],
                "pi33_coefficient_mod_prime": chi["e33"]["coefficient_mod_prime"],
            },
            "residual_lift_vector": {
                "support": vectors["residual_lift"]["support"],
                "sha256": vectors["residual_lift"]["sha256"],
                "pi33_coefficient_signed": chi["residual_lift"]["coefficient_signed"],
                "pi33_coefficient_mod_prime": chi["residual_lift"]["coefficient_mod_prime"],
            },
            "corrected_lift_vector": {
                "support": vectors["corrected_lift"]["support"],
                "sha256": vectors["corrected_lift"]["sha256"],
                "pi33_coefficient_signed": chi["corrected_lift"]["coefficient_signed"],
                "pi33_coefficient_mod_prime": chi["corrected_lift"]["coefficient_mod_prime"],
            },
            "public_shadows": {
                "q42_nonzero_count": public_shadows["residual_lift_q42"]["nonzero_count"],
                "q42_sha256": public_shadows["residual_lift_q42"]["sha256"],
                "q12_nonzero_count": public_shadows["residual_lift_q12"]["nonzero_count"],
                "q12_sha256": public_shadows["residual_lift_q12"]["sha256"],
            },
            "meaning": "The explicit hidden-sector object is the dimension-normalized residual multiple of e33. It recovers the certified residual and remains invisible to A42/A12 public shadows.",
        },
        "x_surface_floor": {
            "minimum_x_event_count_for_extractor_opcode": isolation["minimum_x_event_count_for_extractor_opcode"],
            "zero_x_trace_can_contain_extractor_opcode": isolation["zero_x_trace_can_contain_extractor_opcode"],
            "current_accepted_trace_x_event_count": isolation["current_accepted_trace_x_event_count"],
        },
    }


def audit_target(target: dict[str, Any], residual_lift: dict[str, Any]) -> dict[str, Any]:
    checks = residual_lift["checks"]
    audits = {
        "bare_public_transport_pi33_zero": target["public_transport_floor"][
            "bare_lambda_pi33_coefficient_mod_prime"
        ]
        == 0
        and checks["bare_lambda_pi33_coefficient_is_zero"],
        "directed_pair_public_span_annihilated": target["public_transport_floor"][
            "all_30_directed_pair_lifts_annihilated"
        ],
        "residual_lift_recovers_target_residual": target["hidden_residual_lift"]["residual_lift_vector"][
            "pi33_coefficient_signed"
        ]
        == target["residual"]["integral"]
        and checks["residual_lift_pi33_coefficient_is_residual"],
        "corrected_lift_recovers_target_residual": target["hidden_residual_lift"]["corrected_lift_vector"][
            "pi33_coefficient_signed"
        ]
        == target["residual"]["integral"]
        and checks["corrected_lift_pi33_coefficient_is_residual"],
        "hidden_lift_public_shadows_zero": target["hidden_residual_lift"]["public_shadows"]["q42_nonzero_count"] == 0
        and target["hidden_residual_lift"]["public_shadows"]["q12_nonzero_count"] == 0
        and checks["residual_lift_has_zero_q42_shadow"]
        and checks["residual_lift_has_zero_q12_shadow"],
        "zero_x_trace_cannot_contain_extractor_opcode": target["x_surface_floor"][
            "zero_x_trace_can_contain_extractor_opcode"
        ]
        is False,
    }
    return {
        "checks": audits,
        "passed": all(audits.values()),
    }


def main() -> int:
    x_isolation = load_json(X_ISOLATION_REPORT)
    encoded_bridge = load_json(ENCODED_BRIDGE_REPORT)
    boundary_annihilation = load_json(BOUNDARY_ANNIHILATION_REPORT)
    residual_lift = load_json(RESIDUAL_LIFT_REPORT)
    projection_obligation = load_json(PROJECTION_OBLIGATION_REPORT)

    source_audit = {
        "universal_x_extractor_isolation": report_status(
            X_ISOLATION_REPORT, "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS"
        ),
        "encoded_family_bridge": report_status(
            ENCODED_BRIDGE_REPORT,
            "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN",
        ),
        "sector33_boundary_annihilation": report_status(
            BOUNDARY_ANNIHILATION_REPORT,
            "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED",
            all_checks=True,
        ),
        "sector33_residual_lift": report_status(
            RESIDUAL_LIFT_REPORT,
            "D20_SECTOR33_RESIDUAL_LIFT_CERTIFIED",
            all_checks=True,
        ),
        "cycle8_pi33_projection_obligation": report_status(
            PROJECTION_OBLIGATION_REPORT,
            "D20_CYCLE8_PI33_BARE_LAMBDA_COEFFICIENT_ZERO_CERTIFIED",
            all_checks=True,
        ),
    }
    target = build_target(residual_lift, boundary_annihilation, x_isolation)
    target_audit = audit_target(target, residual_lift)
    sources_passed = all(item["passed"] for item in source_audit.values())
    target_certified = sources_passed and target_audit["passed"]

    certificate = {
        "schema": "d20.integrity.x_extractor_target_certificate.v1",
        "status": (
            "X_EXTRACTOR_TARGET_CERTIFIED_POLYNOMIAL_LOWER_BOUND_OPEN"
            if target_certified
            else "X_EXTRACTOR_TARGET_CERTIFICATE_BLOCKED"
        ),
        "claim_level": "explicit_hidden_sector_target_not_polynomial_lower_bound",
        "source_audit": source_audit,
        "target": target,
        "target_audit": target_audit,
        "bridge_context": {
            "encoded_family_bridge_decision": encoded_bridge.get("decision", {}),
            "projection_obligation_closure_state": projection_obligation.get("closure_state"),
            "projection_obligation_remaining_recovery_obligation": projection_obligation.get(
                "formal_obligation", {}
            ).get("remaining_recovery_obligation"),
        },
        "lower_bound_state": {
            "bare_public_transport_lower_bound_certified": target_certified,
            "no_polynomial_size_x_extractor_proved": False,
            "explicit_hidden_sector_map_certified": target_certified,
            "must_leave_bare_public_transport_span_to_recover_residual": target_certified,
            "must_use_x_or_a_refined_non_bare_transport_for_hidden_residual_recovery": target_certified,
        },
        "decision": {
            "may_claim_x_extractor_target_certified": target_certified,
            "may_claim_explicit_hidden_sector_map_certified": target_certified,
            "may_claim_no_polynomial_size_x_extractor": False,
            "may_claim_full_separation": False,
            "reason": "The concrete hidden-sector target is certified, and the bare public transport span is ruled out for recovering it. This is not a polynomial-size X-extractor lower bound.",
        },
        "non_claims": [
            "This does not prove that polynomial-size X extractors are impossible.",
            "This does not derive rho_33(gamma_8) from an intrinsic height-coherent transport rule.",
            "This does not certify SAT-completeness of the encoded family.",
            "This does not prove P != NP.",
        ],
        "next_highest_yield_item": {
            "id": "intrinsic_height_coherent_transport",
            "action": "Define and certify a height-coherent/action-return transport that derives rho_33(gamma_8) from edge or circuit data instead of inserting the certified residual scalar.",
        },
    }
    REPORT_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(certificate["status"])
    return 0 if target_certified else 1


if __name__ == "__main__":
    raise SystemExit(main())
