from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import sys
from pathlib import Path
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_a985_mat2_hom_boundary import build_report
except ImportError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.certify_io import ROOT, h_file, h_json
    from src.derive_d20_a985_mat2_hom_boundary import build_report


THEOREM_ID = "d20_a985_mat2_hom_boundary"
REPORT_REL = f"data/invariants/d20/theorems/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/theorems/{THEOREM_ID}/manifest.json"
INPUT_RELS = {
    "canonical_sector_matrix_units_report": (
        "data/invariants/d20/theorems/tiny_pointer_a985_canonical_sector_matrix_units/report.json"
    ),
    "canonical_sector_summary_csv": (
        "data/invariants/d20/theorems/tiny_pointer_a985_canonical_sector_matrix_units/"
        "canonical_source_sector_matrix_unit_summary.csv"
    ),
    "full_matrix_unit_coo_report": (
        "data/invariants/d20/theorems/tiny_pointer_a985_full_matrix_unit_orbital_coo/report.json"
    ),
    "full_packet_matrix_lift_report": (
        "data/invariants/d20/theorems/d20_full_packet_matrix_lift/report.json"
    ),
    "a985_direct_packet_bridge_obstruction_report": (
        "data/invariants/d20/theorems/d20_a985_direct_packet_bridge_obstruction/report.json"
    ),
}
EXPECTED_CHECKS = {
    "canonical_sector_matrix_units_certified",
    "full_matrix_unit_coo_certified",
    "full_packet_matrix_lift_certified",
    "direct_packet_bridge_obstruction_certified",
    "sector_rows_count_is_39",
    "matrix_units_sum_to_985",
    "diagonal_units_sum_to_159",
    "block_dimension_histogram_matches",
    "target_mat2_power_10_dimension_is_40",
    "faithful_full_a985_embedding_refuted_by_dimension",
    "small_block_sector_count_is_15",
    "small_block_sectors_can_fill_ten_target_components_as_abstract_shape",
    "literal_current_label_bridge_refuted",
    "unconstrained_no_homomorphism_claim_demoted",
}
EXPECTED_DIMENSION_SUMMARY = {
    "source_sector_count": 39,
    "source_algebra_dimension": 985,
    "source_diagonal_dimension": 159,
    "target_block_count": 10,
    "target_block_dimension": 2,
    "target_algebra": "Mat_2(Q)^10",
    "target_algebra_dimension": 40,
    "faithful_full_a985_embedding_possible_by_dimension": False,
    "small_block_sector_count": 15,
    "small_block_sector_capacity_at_least_target_blocks": True,
    "larger_than_mat2_sector_count": 24,
    "block_dimension_histogram": {
        "1": 7,
        "2": 8,
        "3": 4,
        "4": 8,
        "5": 4,
        "6": 2,
        "8": 1,
        "9": 1,
        "10": 2,
        "11": 1,
        "12": 1,
    },
}
EXPECTED_SMALL_SECTORS = [5, 6, 7, 10, 13, 19, 20, 21, 22, 24, 25, 26, 32, 33, 34]


def _load_json(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} input path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} input hash mismatch")


def validate_d20_a985_mat2_hom_boundary() -> dict[str, Any]:
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)

    if report.get("schema") != "d20.theorem.d20_a985_mat2_hom_boundary":
        raise AssertionError("A985 Mat2 hom boundary schema mismatch")
    if report.get("status") != "D20_A985_MAT2_HOM_BOUNDARY_CERTIFIED":
        raise AssertionError("A985 Mat2 hom boundary status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("A985 Mat2 hom boundary checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("A985 Mat2 hom boundary self hash mismatch")

    for key, rel_path in INPUT_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if build_report() != report:
        raise AssertionError("A985 Mat2 hom boundary does not replay")

    checks = report.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("A985 Mat2 hom boundary check table mismatch")

    derived = report.get("derived", {})
    if derived.get("dimension_summary") != EXPECTED_DIMENSION_SUMMARY:
        raise AssertionError("A985 Mat2 hom boundary dimension summary mismatch")

    small_rows = derived.get("small_block_sector_rows", [])
    if [row.get("source_sector") for row in small_rows] != EXPECTED_SMALL_SECTORS:
        raise AssertionError("A985 Mat2 hom boundary small-sector ids mismatch")
    if h_json(small_rows) != derived.get("small_block_sector_rows_sha256"):
        raise AssertionError("A985 Mat2 hom boundary small-sector hash mismatch")

    boundary = derived.get("homomorphism_boundary", {})
    if boundary.get("faithful_full_a985_to_mat2_power_10") != "refuted_by_dimension":
        raise AssertionError("A985 Mat2 hom boundary faithful no-go mismatch")
    if boundary.get("literal_current_packet_label_map") != (
        "refuted_by_direct_restriction_certificate"
    ):
        raise AssertionError("A985 Mat2 hom boundary direct-label status mismatch")
    if boundary.get("unconstrained_nonfaithful_full_domain_homomorphism") != (
        "not_refuted_by_current_evidence"
    ):
        raise AssertionError("A985 Mat2 hom boundary overclaims nonfaithful no-go")
    if "finite-field block data" not in boundary.get("reason_unconstrained_no_go_is_too_strong", ""):
        raise AssertionError("A985 Mat2 hom boundary finite-field scope missing")

    direct = derived.get("direct_label_bridge_summary", {})
    if direct.get("direct_compressed_map_is_multiplicative") is not False:
        raise AssertionError("A985 Mat2 hom boundary direct multiplicativity mismatch")
    if direct.get("leaking_relation_count") != 979:
        raise AssertionError("A985 Mat2 hom boundary leak count mismatch")
    if direct.get("relation_target_action_matches") != {"2I": [], "4S": [], "2I+4S": []}:
        raise AssertionError("A985 Mat2 hom boundary relation target mismatch")

    closure = report.get("closure_boundary", {})
    if "nonexistence of every abstract nonfaithful A985 -> Mat_2(Q)^10 homomorphism" not in closure.get(
        "does_not_certify", []
    ):
        raise AssertionError("A985 Mat2 hom boundary missing nonfaithful exclusion")
    if "exhaustion of all future label-compatible A985/tube/q42/q12 packet-column assignments" not in closure.get(
        "does_not_certify", []
    ):
        raise AssertionError("A985 Mat2 hom boundary missing column-exhaustion exclusion")

    if manifest.get("schema") != "d20.theorem.d20_a985_mat2_hom_boundary_manifest":
        raise AssertionError("A985 Mat2 hom boundary manifest schema mismatch")
    if manifest.get("status") != report.get("status"):
        raise AssertionError("A985 Mat2 hom boundary manifest status mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("A985 Mat2 hom boundary manifest report hash mismatch")
    if manifest.get("artifacts", {}).get("report") != REPORT_REL:
        raise AssertionError("A985 Mat2 hom boundary manifest report path mismatch")
    if manifest.get("artifacts", {}).get("manifest") != MANIFEST_REL:
        raise AssertionError("A985 Mat2 hom boundary manifest path mismatch")
    if manifest.get("inputs") != report.get("inputs"):
        raise AssertionError("A985 Mat2 hom boundary manifest input mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("A985 Mat2 hom boundary manifest hash mismatch")

    return report


if __name__ == "__main__":
    rec = validate_d20_a985_mat2_hom_boundary()
    print(rec["status"])
    print(rec["certificate_sha256"])
