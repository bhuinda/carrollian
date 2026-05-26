from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_alphabetized_golay_finiteness import build_artifact
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_alphabetized_golay_finiteness import build_artifact


THEOREM_ID = "d20_alphabetized_golay_finiteness"
ARTIFACT_REL = "generated/d20_alphabetized_golay_finiteness.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "coorient_word_presentation": "data/coorient/absolute_d20_word_presentation.json",
    "canonical_24_syzygy_frame": "data/geometry/canonical_24_syzygy_frame.json",
    "mog_resolvent_invariant": "data/selectors/mog_resolvent_invariant.json",
    "mog_canonicity_boundary": "data/selectors/mog_canonicity_boundary.json",
    "full_row_refined_obstruction": "data/selectors/full_row_refined_obstruction.json",
    "wu_spinh_6j_marking": "data/selectors/wu_spinh_6j_marking.json",
    "hexacode_row_selector": "data/selectors/hexacode_row_selector.json",
    "minor_puncture_search": (
        "data/invariants/d20/proof_obligations/d20_golay_hamming_minor_puncture_search/report.json"
    ),
}


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


def _artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} input path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} input file hash mismatch")


def validate_d20_alphabetized_golay_finiteness() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.alphabetized_golay_finiteness.artifact@1":
        raise AssertionError("alphabetized finiteness artifact schema mismatch")
    if artifact.get("status") != "D20_ALPHABETIZED_GOLAY_FINITENESS_DERIVED":
        raise AssertionError("alphabetized finiteness artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("alphabetized finiteness artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("alphabetized finiteness artifact does not replay")

    checks = artifact.get("checks", {})
    required_checks = {
        "d20_alphabet_has_six_labels",
        "d20_residual_symmetry_is_dih6",
        "w24_frame_is_constructed_with_24_coordinates",
        "w24_labels_are_euler_plus_23_syzygies",
        "mog_atom_partition_is_six_by_four",
        "d20_and_mog_alphabets_match_as_sets",
        "mog_columns_cover_w24_disjointly",
        "pair_octad_addresses_are_lambda2_h6",
        "spin12_big_cell_is_scalar_plus_lambda2_h6",
        "internal_s4_count_matches_certificate",
        "full_coordinate_aut_count_matches_6_factorial_times_internal_s4",
        "row_alignment_count_matches_preserve_all_h6_label_stabilizer",
        "row_alignment_mod_global_is_quotient_by_s4",
        "quadratic_selector_search_space_is_finite",
        "full_row_refined_selector_remains_obstructed",
        "hexacode_selector_is_external_endpoint",
        "minor_search_was_negative_bounded_search",
        "alphabetization_finiteness_boundary_recorded",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("alphabetized finiteness artifact check mismatch")

    finite = artifact.get("finite_reduction", {})
    if finite.get("label_sets_match") is not True:
        raise AssertionError("alphabetized finiteness label set mismatch")
    if sorted(finite.get("d20_signed_alphabet", [])) != sorted(
        ["B-", "B+", "S-", "S+", "V-", "V+"]
    ):
        raise AssertionError("alphabetized finiteness D20 alphabet mismatch")
    if sorted(finite.get("mog_atom_labels", [])) != sorted(
        ["B-", "B+", "S-", "S+", "V-", "V+"]
    ):
        raise AssertionError("alphabetized finiteness MOG alphabet mismatch")
    if finite.get("w24_coordinate_count") != 24:
        raise AssertionError("alphabetized finiteness W24 coordinate count mismatch")
    atom = finite.get("atom_partition", {})
    if atom.get("atom_count") != 6 or atom.get("atom_sizes") != [4, 4, 4, 4, 4, 4]:
        raise AssertionError("alphabetized finiteness atom partition mismatch")
    addresses = finite.get("finite_address_spaces", {})
    if addresses.get("d20_projective_root_count") != 30:
        raise AssertionError("alphabetized finiteness D20 root count mismatch")
    if addresses.get("pair_octad_address_count") != 15:
        raise AssertionError("alphabetized finiteness pair-octad count mismatch")
    if addresses.get("scalar_plus_lambda2_h6_dimension") != 16:
        raise AssertionError("alphabetized finiteness scalar-plus-Lambda2 dimension mismatch")

    bounds = artifact.get("finite_bounds", {})
    internal_s4 = math.factorial(4) ** 6
    full_aut = math.factorial(6) * internal_s4
    if bounds.get("internal_s4_per_atom_order") != internal_s4:
        raise AssertionError("alphabetized finiteness internal S4 bound mismatch")
    if bounds.get("column_permutation_order_6_factorial") != math.factorial(6):
        raise AssertionError("alphabetized finiteness column permutation mismatch")
    if bounds.get("full_pair_octad_hypergraph_coordinate_aut_order") != full_aut:
        raise AssertionError("alphabetized finiteness full coordinate automorphism mismatch")
    if bounds.get("labeled_row_alignments") != internal_s4:
        raise AssertionError("alphabetized finiteness labelled row alignment mismatch")
    if bounds.get("row_alignments_mod_global_row_relabel") * math.factorial(4) != internal_s4:
        raise AssertionError("alphabetized finiteness quotient alignment mismatch")
    singular = bounds.get("candidate_maximal_singular_7_planes_before_min_distance_filter")
    if singular != 9_845_550:
        raise AssertionError("alphabetized finiteness singular-plane count mismatch")
    if bounds.get("coarse_alphabetized_selector_upper_bound") != internal_s4 * singular:
        raise AssertionError("alphabetized finiteness coarse bound mismatch")
    if bounds.get("preserve_all_h6_labels_coordinate_stabilizer") != internal_s4:
        raise AssertionError("alphabetized finiteness preserve-H6 stabilizer mismatch")

    selector = artifact.get("selector_boundary", {})
    if selector.get("column_sextet_certified") is not True:
        raise AssertionError("alphabetized finiteness column sextet mismatch")
    if selector.get("row_alignment_from_pair_octad_wu_6j_data") is not False:
        raise AssertionError("alphabetized finiteness row-alignment boundary mismatch")
    if selector.get("full_row_refined_golay_selector_certified") is not False:
        raise AssertionError("alphabetized finiteness full selector boundary mismatch")
    if selector.get("hexacode_endpoint_constructs_g24") is not True:
        raise AssertionError("alphabetized finiteness hexacode endpoint mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(artifact.get("source_reports", {}).get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != "d20.proof_obligation.alphabetized_golay_finiteness@1":
        raise AssertionError("alphabetized finiteness report schema mismatch")
    if report.get("status") != "D20_ALPHABETIZED_GOLAY_FINITENESS_CERTIFIED":
        raise AssertionError("alphabetized finiteness report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("alphabetized finiteness report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("alphabetized finiteness report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("alphabetized finiteness report artifact hash mismatch")
    if report.get("witness", {}).get("finite_reduction") != artifact.get("finite_reduction"):
        raise AssertionError("alphabetized finiteness report finite reduction mismatch")
    if report.get("witness", {}).get("finite_bounds") != artifact.get("finite_bounds"):
        raise AssertionError("alphabetized finiteness report finite bounds mismatch")
    if report.get("witness", {}).get("selector_boundary") != artifact.get("selector_boundary"):
        raise AssertionError("alphabetized finiteness report selector boundary mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("alphabetized finiteness report checks mismatch")
    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != "d20.proof_obligation.alphabetized_golay_finiteness_manifest@1":
        raise AssertionError("alphabetized finiteness manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("alphabetized finiteness manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("alphabetized finiteness manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("alphabetized finiteness manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("alphabetized finiteness registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("alphabetized finiteness registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("alphabetized finiteness registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_alphabetized_golay_finiteness()
    print("D20 alphabetized Golay finiteness proof obligation validated")
