from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import sys
from pathlib import Path
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_a985_labelled_nonfaithful_packet_hom_obstruction import (
        build_report,
    )
except ImportError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.certify_io import ROOT, h_file, h_json
    from src.derive_d20_a985_labelled_nonfaithful_packet_hom_obstruction import (
        build_report,
    )


THEOREM_ID = "d20_a985_labelled_nonfaithful_packet_hom_obstruction"
REPORT_REL = f"data/invariants/d20/theorems/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/theorems/{THEOREM_ID}/manifest.json"
INPUT_RELS = {
    "halloween_npz": "data/raw/Halloween.npz",
    "quotients_npz": "data/raw/quotients.npz",
    "full_matrix_unit_arrays_npz": (
        "data/invariants/d20/theorems/tiny_pointer_a985_full_matrix_unit_orbital_coo/"
        "source_sector_matrix_units_raw_orbital_arrays.npz"
    ),
    "full_matrix_unit_coo_report": (
        "data/invariants/d20/theorems/tiny_pointer_a985_full_matrix_unit_orbital_coo/report.json"
    ),
    "canonical_sector_matrix_units_report": (
        "data/invariants/d20/theorems/tiny_pointer_a985_canonical_sector_matrix_units/report.json"
    ),
    "canonical_sector_summary_csv": (
        "data/invariants/d20/theorems/tiny_pointer_a985_canonical_sector_matrix_units/"
        "canonical_source_sector_matrix_unit_summary.csv"
    ),
    "full_packet_matrix_lift_report": (
        "data/invariants/d20/theorems/d20_full_packet_matrix_lift/report.json"
    ),
    "packet_quotient_action_probe_report": (
        "data/invariants/d20/theorems/d20_packet_quotient_action_probe/report.json"
    ),
    "fourier_screen0_tube_central_element_report": (
        "data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json"
    ),
    "a985_mat2_hom_boundary_report": (
        "data/invariants/d20/theorems/d20_a985_mat2_hom_boundary/report.json"
    ),
}
EXPECTED_CHECKS = {
    "canonical_sector_matrix_units_certified",
    "full_matrix_unit_coo_certified",
    "full_packet_matrix_lift_certified",
    "packet_quotient_action_probe_certified",
    "tube_screen0_certified",
    "mat2_hom_boundary_certified",
    "small_sector_count_is_15",
    "candidate_count_is_1041",
    "evaluated_candidate_sector_pairs_is_15615",
    "only_2i_has_matches",
    "exact_matches_equal_signature_matches",
    "only_raw_relations_match_2i",
    "matching_2i_relation_ids_are_expected",
    "all_2i_matches_are_sector34_scalar",
    "no_labelled_candidate_realizes_4s",
    "no_labelled_candidate_realizes_2i_plus_4s",
    "no_q42_q12_or_tube_candidate_matches_any_target",
}
EXPECTED_CANDIDATE_FAMILY_ROWS = [
    {"candidate_kind": "q12_class_sum", "candidate_count": 12},
    {"candidate_kind": "q42_class_sum", "candidate_count": 42},
    {"candidate_kind": "raw_relation", "candidate_count": 985},
    {"candidate_kind": "tube_closed_loop_unit", "candidate_count": 1},
    {"candidate_kind": "tube_signed_object_unit", "candidate_count": 1},
]
EXPECTED_SMALL_SECTORS = [5, 6, 7, 10, 13, 19, 20, 21, 22, 24, 25, 26, 32, 33, 34]
EXPECTED_MATCHING_2I_RELATIONS = [358, 362, 369, 370, 383, 385, 388, 389, 427]
EXPECTED_TARGET_SIGNATURE_ROWS = [
    {
        "target": "2I",
        "matrix": [[2, 0], [0, 2]],
        "trace_mod": 4,
        "trace_signed": 4,
        "determinant_mod": 4,
        "determinant_signed": 4,
    },
    {
        "target": "4S",
        "matrix": [[0, 4], [4, 0]],
        "trace_mod": 0,
        "trace_signed": 0,
        "determinant_mod": 999987,
        "determinant_signed": -16,
    },
    {
        "target": "2I+4S",
        "matrix": [[2, 4], [4, 2]],
        "trace_mod": 4,
        "trace_signed": 4,
        "determinant_mod": 999991,
        "determinant_signed": -12,
    },
]


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


def validate_d20_a985_labelled_nonfaithful_packet_hom_obstruction() -> dict[str, Any]:
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)

    if report.get("schema") != (
        "d20.theorem.d20_a985_labelled_nonfaithful_packet_hom_obstruction"
    ):
        raise AssertionError("A985 labelled nonfaithful packet obstruction schema mismatch")
    if report.get("status") != (
        "D20_A985_LABELLED_NONFAITHFUL_PACKET_HOM_OBSTRUCTION_CERTIFIED"
    ):
        raise AssertionError("A985 labelled nonfaithful packet obstruction status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("A985 labelled nonfaithful packet obstruction checks did not pass")
    if report.get("field_prime") != 1_000_003:
        raise AssertionError("A985 labelled nonfaithful packet obstruction field mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction self hash mismatch")

    for key, rel_path in INPUT_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if build_report() != report:
        raise AssertionError("A985 labelled nonfaithful packet obstruction does not replay")

    checks = report.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("A985 labelled nonfaithful packet obstruction check table mismatch")

    derived = report.get("derived", {})
    if derived.get("candidate_family_rows") != EXPECTED_CANDIDATE_FAMILY_ROWS:
        raise AssertionError("A985 labelled nonfaithful packet obstruction candidate rows mismatch")
    if h_json(EXPECTED_CANDIDATE_FAMILY_ROWS) != derived.get("candidate_family_rows_sha256"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction candidate hash mismatch")
    if derived.get("target_signature_rows") != EXPECTED_TARGET_SIGNATURE_ROWS:
        raise AssertionError("A985 labelled nonfaithful packet obstruction target signatures mismatch")
    if h_json(EXPECTED_TARGET_SIGNATURE_ROWS) != derived.get("target_signature_rows_sha256"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction target hash mismatch")

    small_rows = derived.get("small_sector_rows", [])
    if [row.get("source_sector") for row in small_rows] != EXPECTED_SMALL_SECTORS:
        raise AssertionError("A985 labelled nonfaithful packet obstruction small sectors mismatch")
    if h_json(small_rows) != derived.get("small_sector_rows_sha256"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction small-sector hash mismatch")

    summary = derived.get("evaluation_summary", {})
    expected_summary = {
        "candidate_count": 1041,
        "small_sector_count": 15,
        "evaluated_candidate_sector_pairs": 15615,
        "exact_match_count": 9,
        "signature_match_count": 9,
        "exact_match_count_by_target": {"2I": 9, "4S": 0, "2I+4S": 0},
        "signature_match_count_by_target": {"2I": 9, "4S": 0, "2I+4S": 0},
        "non_diagonal_target_signature_match_count": 0,
    }
    if summary != expected_summary:
        raise AssertionError("A985 labelled nonfaithful packet obstruction summary mismatch")

    per_target = derived.get("per_target_summary", [])
    if per_target != [
        {
            "target": "2I",
            "exact_match_count": 9,
            "signature_match_count": 9,
            "candidate_kinds_with_signature_match": ["raw_relation"],
        },
        {
            "target": "4S",
            "exact_match_count": 0,
            "signature_match_count": 0,
            "candidate_kinds_with_signature_match": [],
        },
        {
            "target": "2I+4S",
            "exact_match_count": 0,
            "signature_match_count": 0,
            "candidate_kinds_with_signature_match": [],
        },
    ]:
        raise AssertionError("A985 labelled nonfaithful packet obstruction target summary mismatch")

    matches = derived.get("signature_match_rows", [])
    if [row.get("candidate_id") for row in matches] != EXPECTED_MATCHING_2I_RELATIONS:
        raise AssertionError("A985 labelled nonfaithful packet obstruction 2I matches mismatch")
    if not all(
        row.get("candidate_kind") == "raw_relation"
        and row.get("source_sector") == 34
        and row.get("target") == "2I"
        and row.get("matrix_mod") == [[2, 0], [0, 2]]
        and row.get("trace_mod") == 4
        and row.get("determinant_mod") == 4
        for row in matches
    ):
        raise AssertionError("A985 labelled nonfaithful packet obstruction match row mismatch")
    if h_json(matches) != derived.get("signature_match_rows_sha256"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction match hash mismatch")

    closure = report.get("closure_boundary", {})
    certifies = closure.get("certifies", [])
    if not any("4S" in row for row in certifies):
        raise AssertionError("A985 labelled nonfaithful packet obstruction missing 4S closure")
    if not any("2I+4S" in row for row in certifies):
        raise AssertionError("A985 labelled nonfaithful packet obstruction missing 2I+4S closure")
    exclusions = closure.get("does_not_certify", [])
    if not any("arbitrary unlabelled linear-combination" in row for row in exclusions):
        raise AssertionError("A985 labelled nonfaithful packet obstruction overclaims linear combinations")
    if not any("rational Q lift" in row for row in exclusions):
        raise AssertionError("A985 labelled nonfaithful packet obstruction overclaims rational lift")

    if manifest.get("schema") != (
        "d20.theorem.d20_a985_labelled_nonfaithful_packet_hom_obstruction_manifest"
    ):
        raise AssertionError("A985 labelled nonfaithful packet obstruction manifest schema mismatch")
    if manifest.get("status") != report.get("status"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction manifest status mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction manifest report hash mismatch")
    if manifest.get("artifacts", {}).get("report") != REPORT_REL:
        raise AssertionError("A985 labelled nonfaithful packet obstruction manifest report path mismatch")
    if manifest.get("artifacts", {}).get("manifest") != MANIFEST_REL:
        raise AssertionError("A985 labelled nonfaithful packet obstruction manifest path mismatch")
    if manifest.get("inputs") != report.get("inputs"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction manifest input mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("A985 labelled nonfaithful packet obstruction manifest hash mismatch")

    return report


if __name__ == "__main__":
    rec = validate_d20_a985_labelled_nonfaithful_packet_hom_obstruction()
    print(rec["status"])
    print(rec["certificate_sha256"])
