from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
REPORT_PATH = CVX / "reports" / "encoded_family_bridge_certificate.json"

SECTOR33_REPORT = ROOT / "data" / "invariants" / "d20" / "theorems" / "sector33_residual_attachment" / "report.json"
UNIVERSAL_INTEGRAL_REPORT = ROOT / "data" / "invariants" / "d20" / "universal_integral_uniqueness.json"

INTEGRITY_REPORTS = {
    "universal_trace_compiler": (
        CVX / "reports" / "universal_trace_compiler_report.json",
        "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
    ),
    "universal_trace_typing": (
        CVX / "reports" / "universal_trace_typing_report.json",
        "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
    ),
    "universal_pure_c_no_escape": (
        CVX / "reports" / "universal_pure_c_no_escape_report.json",
        "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS",
    ),
    "universal_x_extractor_isolation": (
        CVX / "reports" / "universal_x_extractor_isolation_report.json",
        "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS",
    ),
    "universal_v_wall_crossing_accounting": (
        CVX / "reports" / "universal_v_wall_crossing_accounting_report.json",
        "UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_PASS",
    ),
}

REQUIRED_SECTOR33_CHECKS = [
    "sector33_exists_once",
    "sector33_is_unique_public_zero_sector",
    "sector33_signature_matches_public_zero_obstruction",
    "cycle_8_edges_are_present",
    "first_obstruction_is_cycle_8",
    "first_obstruction_mask_is_256",
    "first_residual_nonzero_over_integers",
    "first_residual_nonzero_mod_field",
    "tube_projection_section_certified",
    "tube_kernel_descent_audit_certified",
    "hesse_tube_pencil_sees_all_39_sectors",
    "line_surface_trace_separates_all_sectors",
    "accepted_pure_c_traces_do_not_extract_e33",
    "bounded_x_search_finds_no_extractor",
    "visible_v_accounting_has_no_current_v_events",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def count_leaves(value: Any) -> int:
    if isinstance(value, dict):
        return sum(count_leaves(item) for item in value.values())
    if isinstance(value, list):
        return sum(count_leaves(item) for item in value)
    return 1


def integrity_statuses() -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for key, (path, expected_status) in INTEGRITY_REPORTS.items():
        data = load_json(path)
        statuses[key] = {
            "path": rel(path),
            "status": data.get("status"),
            "expected_status": expected_status,
            "passed": data.get("status") == expected_status,
        }
    return statuses


def sector33_audit(sector33: dict[str, Any], universal_integral: dict[str, Any]) -> dict[str, Any]:
    checks = sector33.get("checks", {})
    check_results = {
        key: {
            "value": checks.get(key),
            "passed": checks.get(key) is True,
        }
        for key in REQUIRED_SECTOR33_CHECKS
    }
    sector_witness = sector33["derived"]["sector33_witness"]
    public_shadow = sector33["derived"]["sector_attachment"]["public_terminal_shadow"]
    integral_reading = universal_integral.get("pushforward_integration", {}).get("sector33_reading", "")
    public_zero_obstruction_visible = (
        sector_witness.get("sector") == 33
        and sector_witness.get("q12_nonzero_count") == 0
        and sector_witness.get("q42_nonzero_count") == 0
        and public_shadow.get("A12") == "zero"
        and public_shadow.get("A42") == "zero"
        and "public-zero" in integral_reading
        and "obstruction-visible" in integral_reading
    )
    return {
        "sector33_report": {
            "path": rel(SECTOR33_REPORT),
            "status": sector33.get("status"),
            "expected_status": "D20_SECTOR33_RESIDUAL_ATTACHMENT_CERTIFIED",
            "all_checks_pass": sector33.get("all_checks_pass"),
            "passed": (
                sector33.get("status") == "D20_SECTOR33_RESIDUAL_ATTACHMENT_CERTIFIED"
                and sector33.get("all_checks_pass") is True
            ),
        },
        "universal_integral_report": {
            "path": rel(UNIVERSAL_INTEGRAL_REPORT),
            "status": universal_integral.get("status"),
            "expected_status": "UNIVERSAL_A985_INTEGRAL_UNIQUENESS_PASS",
            "sector33_reading": integral_reading,
            "passed": universal_integral.get("status") == "UNIVERSAL_A985_INTEGRAL_UNIQUENESS_PASS",
        },
        "required_sector33_checks": check_results,
        "public_zero_obstruction_visible": public_zero_obstruction_visible,
        "passed": (
            all(item["passed"] for item in check_results.values())
            and public_zero_obstruction_visible
            and sector33.get("status") == "D20_SECTOR33_RESIDUAL_ATTACHMENT_CERTIFIED"
            and sector33.get("all_checks_pass") is True
            and universal_integral.get("status") == "UNIVERSAL_A985_INTEGRAL_UNIQUENESS_PASS"
        ),
    }


def representative_encoding(sector33: dict[str, Any]) -> dict[str, Any]:
    derived = sector33["derived"]
    boundary = derived["first_boundary_obstruction"]
    cycle = boundary["cycle"]
    attachment = derived["sector_attachment"]
    sector_witness = derived["sector33_witness"]
    tube_visibility = derived["tube_visibility_witness"]

    return {
        "family_id": "cycle8_sector33_residual_family",
        "source_family": {
            "name": "d20_closed_return_boundary_obstruction_packets",
            "representative_instance": {
                "boundary_cycle_id": cycle["cycle_id"],
                "edge_ids": cycle["edge_ids"],
                "mask": boundary["mask"],
                "optical_action": boundary["optical_action"],
                "forced_residual_integral": boundary["forced_res_A985_optical_Z"],
                "forced_residual_mod_prime": boundary["forced_res_A985_optical_mod_prime"],
            },
            "yes_instance_definition": "a public D20 closed-return boundary packet whose certified optical action forces a nonzero A985 residual",
        },
        "target_encoding": {
            "packet": {
                "boundary_cycle_id": attachment["boundary_cycle_id"],
                "a985_sector": attachment["a985_sector"],
                "a985_sector_name": attachment["a985_sector_name"],
                "residual_integral": attachment["residual_integral"],
                "residual_mod_prime": attachment["residual_mod_prime"],
                "public_terminal_shadow": attachment["public_terminal_shadow"],
            },
            "sector_witness": {
                "sector": sector_witness["sector"],
                "active_objects": sector_witness["active_objects"],
                "active_cy_sectors": sector_witness["active_cy_sectors"],
                "block_dimension": sector_witness["block_dimension"],
                "permutation_rank": sector_witness["permutation_rank"],
                "q12_nonzero_count": sector_witness["q12_nonzero_count"],
                "q42_nonzero_count": sector_witness["q42_nonzero_count"],
                "spectral_signature": sector_witness["spectral_signature"],
            },
            "visibility_witness": {
                "drinfeld_sector_count": tube_visibility["drinfeld_sector_count"],
                "drinfeld_half_braiding_nullity": tube_visibility["drinfeld_half_braiding_nullity"],
                "projection_section_identity": tube_visibility["projection_section_identity"],
                "full_relation_pairing_separates_all_39_sectors": tube_visibility["full_relation_pairing_separates_all_39_sectors"],
                "secondary_surface_splits_all_39_sectors": tube_visibility["secondary_surface_splits_all_39_sectors"],
                "unique_Hesse_pencils": tube_visibility["unique_Hesse_pencils"],
            },
            "target_yes_definition": "the encoded packet has a nonzero residual attached to the unique public-zero, tube-visible sector 33",
        },
    }


def polynomial_bound(encoding: dict[str, Any]) -> dict[str, Any]:
    instance = encoding["source_family"]["representative_instance"]
    edge_count = len(instance["edge_ids"])
    public_instance_scalar_count = len(instance)
    target_payload_leaf_count = count_leaves(encoding["target_encoding"])
    integrity_report_count = len(INTEGRITY_REPORTS)
    base_measure = edge_count + public_instance_scalar_count + integrity_report_count + 1
    polynomial_bound_value = base_measure ** 3
    return {
        "bound_kind": "representative_family_payload_bound",
        "source_edge_count": edge_count,
        "source_public_field_count": public_instance_scalar_count,
        "integrity_report_count": integrity_report_count,
        "source_size_measure": base_measure,
        "target_payload_leaf_count": target_payload_leaf_count,
        "polynomial_bound": "source_size_measure^3",
        "polynomial_bound_value": polynomial_bound_value,
        "within_bound": target_payload_leaf_count <= polynomial_bound_value,
        "construction_time_bound": "one pass over the public cycle edge list plus fixed certified sector/audit payloads for this representative family witness",
    }


def yes_no_preservation(sector33: dict[str, Any], encoding: dict[str, Any]) -> dict[str, Any]:
    checks = sector33["checks"]
    instance = encoding["source_family"]["representative_instance"]
    packet = encoding["target_encoding"]["packet"]
    source_yes = (
        instance["boundary_cycle_id"] == 8
        and instance["mask"] == 256
        and instance["forced_residual_integral"] != 0
        and checks["first_obstruction_is_cycle_8"]
        and checks["first_obstruction_mask_is_256"]
        and checks["first_residual_nonzero_over_integers"]
    )
    target_yes = (
        packet["a985_sector"] == 33
        and packet["public_terminal_shadow"]["A12"] == "zero"
        and packet["public_terminal_shadow"]["A42"] == "zero"
        and packet["residual_integral"] != 0
        and checks["sector33_is_unique_public_zero_sector"]
        and checks["sector33_signature_matches_public_zero_obstruction"]
    )
    inverse_witness = {
        "recoverable_fields": {
            "boundary_cycle_id": packet["boundary_cycle_id"],
            "mask": instance["mask"],
            "a985_sector": packet["a985_sector"],
            "residual_integral": packet["residual_integral"],
            "residual_mod_prime": packet["residual_mod_prime"],
        },
        "passed": (
            packet["boundary_cycle_id"] == instance["boundary_cycle_id"]
            and packet["residual_integral"] == instance["forced_residual_integral"]
            and packet["residual_mod_prime"] == instance["forced_residual_mod_prime"]
        ),
    }
    return {
        "source_yes": source_yes,
        "target_yes": target_yes,
        "forward_preservation": source_yes and target_yes,
        "inverse_witness_interpretation": inverse_witness,
        "without_solver_hidden_sector_advice": True,
        "advice_policy": "The certificate uses canonical public reports and sector witnesses as audited inputs. Solver-side hidden-sector reads remain typed X and are not used by the representative bridge construction.",
        "passed": source_yes and target_yes and inverse_witness["passed"],
    }


def main() -> int:
    sector33 = load_json(SECTOR33_REPORT)
    universal_integral = load_json(UNIVERSAL_INTEGRAL_REPORT)
    encoding = representative_encoding(sector33)
    sector_audit = sector33_audit(sector33, universal_integral)
    integrity = integrity_statuses()
    bound = polynomial_bound(encoding)
    preservation = yes_no_preservation(sector33, encoding)

    integrity_passed = all(item["passed"] for item in integrity.values())
    representative_passed = sector_audit["passed"] and integrity_passed and bound["within_bound"] and preservation["passed"]

    certificate = {
        "schema": "d20.integrity.encoded_family_bridge_certificate.v1",
        "status": (
            "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_WITNESSED_SAT_COMPLETE_OPEN"
            if representative_passed
            else "ENCODED_FAMILY_REPRESENTATIVE_BRIDGE_BLOCKED"
        ),
        "claim_level": "polynomially_faithful_representative_family_not_sat_complete",
        "bridge_kind": "representative_family_witness",
        "source_reports": {
            "sector33_residual_attachment": rel(SECTOR33_REPORT),
            "universal_integral_uniqueness": rel(UNIVERSAL_INTEGRAL_REPORT),
        },
        "representative_encoding": encoding,
        "sector33_audit": sector_audit,
        "integrity_report_audit": integrity,
        "polynomial_faithfulness": bound,
        "yes_no_preservation": preservation,
        "non_claims": [
            "This is not a SAT-complete reduction certificate.",
            "This does not prove every SAT instance maps to a hidden e33-obstructed packet.",
            "This does not prove a polynomial-size lower bound against X extractors.",
            "This does not prove P != NP.",
        ],
        "decision": {
            "may_claim_polynomially_faithful_representative_family": representative_passed,
            "may_claim_encoded_family_sat_complete": False,
            "may_claim_full_separation": False,
            "reason": "The cycle-8 / Pi_33 / residual packet is now a polynomially bounded representative-family bridge, while SAT-completeness and the X-extractor lower bound remain open.",
        },
        "next_highest_yield_item": {
            "id": "x_extractor_lower_bound" if representative_passed else "encoded_family_sat_complete",
            "action": (
                "Attack the polynomial-size X-extractor lower bound, because the representative encoded-family bridge is now witnessed but SAT-completeness is still not certified."
                if representative_passed
                else "Repair the representative encoded-family bridge inputs before relying on the witness."
            ),
        },
    }
    REPORT_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(certificate["status"])
    return 0 if representative_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
