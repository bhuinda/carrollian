from __future__ import annotations

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_w24_hexacode_row_alphabetization import build_artifact
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_w24_hexacode_row_alphabetization import build_artifact


THEOREM_ID = "d20_w24_hexacode_row_alphabetization"
ARTIFACT_REL = "generated/d20_w24_hexacode_row_alphabetization.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "alphabetized_golay_finiteness": (
        "data/invariants/d20/proof_obligations/d20_alphabetized_golay_finiteness/report.json"
    ),
    "mog_resolvent_invariant": "data/selectors/mog_resolvent_invariant.json",
    "mog_canonicity_boundary": "data/selectors/mog_canonicity_boundary.json",
    "full_row_refined_obstruction": "data/selectors/full_row_refined_obstruction.json",
    "hexacode_row_selector": "data/selectors/hexacode_row_selector.json",
    "wu_spinh_6j_marking": "data/selectors/wu_spinh_6j_marking.json",
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


def validate_d20_w24_hexacode_row_alphabetization() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.w24_hexacode_row_alphabetization.artifact@1":
        raise AssertionError("W24 hexacode row alphabetization artifact schema mismatch")
    if artifact.get("status") != "D20_W24_HEXACODE_ROW_ALPHABETIZATION_DERIVED":
        raise AssertionError("W24 hexacode row alphabetization artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("W24 hexacode row alphabetization artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("W24 hexacode row alphabetization artifact does not replay")

    checks = artifact.get("checks", {})
    required_checks = {
        "alphabetized_finiteness_input_certified",
        "row_selector_endpoint_input_certified",
        "mog_grid_is_4_by_6",
        "row_f4_alphabet_has_four_symbols",
        "hexacode_has_64_words",
        "hexacode_f4_weight_histogram_matches",
        "local_lift_table_has_two_choices_per_parity_symbol",
        "global_choice_rule_yields_4096_unique_words",
        "uniform_column_parity_counts_are_2048_each",
        "each_hexacode_symbol_word_has_32_lifts_per_uniform_parity",
        "golay_weight_histogram_matches",
        "rank_is_12",
        "minimum_nonzero_weight_is_8",
        "self_orthogonal",
        "doubly_even",
        "self_dual_by_rank_and_self_orthogonal",
        "dodecad_count_is_2576",
        "contains_column_pair_code",
        "column_pair_code_profile_matches",
        "contains_row_pair_dodecads",
        "does_not_contain_single_rows",
        "contains_active_6j_edge_code",
        "active_6j_edge_code_profile_matches",
        "contains_wu_octad",
        "external_canonicity_boundary_preserved",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("W24 hexacode row alphabetization check mismatch")

    row_alphabetization = artifact.get("row_alphabetization", {})
    if row_alphabetization.get("grid_row_major") != [
        [0, 1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10, 11],
        [12, 13, 14, 15, 16, 17],
        [18, 19, 20, 21, 22, 23],
    ]:
        raise AssertionError("W24 hexacode row alphabetization grid mismatch")
    if row_alphabetization.get("row_f4_labels") != [
        {"row": 0, "f4_value": 0, "f4_label": "0"},
        {"row": 1, "f4_value": 1, "f4_label": "1"},
        {"row": 2, "f4_value": 2, "f4_label": "omega"},
        {"row": 3, "f4_value": 3, "f4_label": "omega+1"},
    ]:
        raise AssertionError("W24 hexacode row labels mismatch")
    if len(row_alphabetization.get("coordinate_labels", [])) != 24:
        raise AssertionError("W24 hexacode coordinate label count mismatch")

    hexacode = artifact.get("hexacode", {})
    if hexacode.get("word_count") != 64:
        raise AssertionError("W24 hexacode word count mismatch")
    if hexacode.get("symbol_weight_histogram") != {"0": 1, "4": 45, "6": 18}:
        raise AssertionError("W24 hexacode symbol weight histogram mismatch")
    lift_rule = artifact.get("binary_lift_rule", {})
    if len(lift_rule.get("local_lift_table", [])) != 8:
        raise AssertionError("W24 hexacode local lift table count mismatch")
    if lift_rule.get("global_choice_rule") != (
        "For each of the two local lifts per column, let choice_bit be 0 or 1. "
        "Keep exactly the lifts with xor(choice_bits)=p."
    ):
        raise AssertionError("W24 hexacode global choice rule mismatch")

    golay = artifact.get("golay_code", {})
    if golay.get("length") != 24 or golay.get("rank") != 12 or golay.get("size") != 4096:
        raise AssertionError("W24 hexacode Golay shape mismatch")
    if golay.get("generator_shape") != [12, 24]:
        raise AssertionError("W24 hexacode generator shape mismatch")
    if len(golay.get("generator_basis_rows", [])) != 12:
        raise AssertionError("W24 hexacode generator row count mismatch")
    if golay.get("minimum_nonzero_weight") != 8:
        raise AssertionError("W24 hexacode minimum weight mismatch")
    if golay.get("weight_histogram") != {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1}:
        raise AssertionError("W24 hexacode weight histogram mismatch")
    if golay.get("dodecad_count") != 2576:
        raise AssertionError("W24 hexacode dodecad count mismatch")
    if golay.get("self_orthogonal") is not True or golay.get("doubly_even") is not True:
        raise AssertionError("W24 hexacode orthogonality/evenness mismatch")
    if golay.get("self_dual_by_rank_and_self_orthogonal") is not True:
        raise AssertionError("W24 hexacode self-duality witness mismatch")

    contain = artifact.get("containment_witnesses", {})
    if contain.get("contains_column_pair_code") is not True:
        raise AssertionError("W24 hexacode column-pair containment mismatch")
    if contain.get("column_pair_code_rank") != 5:
        raise AssertionError("W24 hexacode column-pair rank mismatch")
    if contain.get("column_pair_code_weight_histogram") != {"0": 1, "8": 15, "16": 15, "24": 1}:
        raise AssertionError("W24 hexacode column-pair histogram mismatch")
    if contain.get("contains_current_row_pair_dodecads") is not True:
        raise AssertionError("W24 hexacode row-pair containment mismatch")
    if contain.get("contains_current_rows") is not False:
        raise AssertionError("W24 hexacode row containment mismatch")
    if contain.get("contains_active_6j_edge_code") is not True:
        raise AssertionError("W24 hexacode active 6j containment mismatch")
    if contain.get("active_6j_edge_code_rank") != 3:
        raise AssertionError("W24 hexacode active 6j rank mismatch")
    if contain.get("active_6j_edge_code_weight_histogram") != {"0": 1, "8": 6, "16": 1}:
        raise AssertionError("W24 hexacode active 6j histogram mismatch")
    if contain.get("contains_wu_octad") is not True:
        raise AssertionError("W24 hexacode Wu octad containment mismatch")

    boundary = artifact.get("canonicity_boundary", {})
    if boundary.get("row_alphabetization_source") != "external hexacode/F4 row selector":
        raise AssertionError("W24 hexacode canonicity source mismatch")
    if boundary.get("canonical_from_pair_octad_wu_6j_data") is not False:
        raise AssertionError("W24 hexacode canonicity boundary mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(artifact.get("source_reports", {}).get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != "d20.proof_obligation.w24_hexacode_row_alphabetization@1":
        raise AssertionError("W24 hexacode row alphabetization report schema mismatch")
    if report.get("status") != "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED":
        raise AssertionError("W24 hexacode row alphabetization report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("W24 hexacode row alphabetization report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("W24 hexacode row alphabetization report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("W24 hexacode row alphabetization report artifact hash mismatch")
    witness = report.get("witness", {})
    if witness.get("row_alphabetization") != artifact.get("row_alphabetization"):
        raise AssertionError("W24 hexacode report row alphabetization mismatch")
    if witness.get("hexacode") != artifact.get("hexacode"):
        raise AssertionError("W24 hexacode report hexacode mismatch")
    if witness.get("golay_code") != artifact.get("golay_code"):
        raise AssertionError("W24 hexacode report Golay mismatch")
    if witness.get("containment_witnesses") != artifact.get("containment_witnesses"):
        raise AssertionError("W24 hexacode report containment mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("W24 hexacode report checks mismatch")
    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != "d20.proof_obligation.w24_hexacode_row_alphabetization_manifest@1":
        raise AssertionError("W24 hexacode row alphabetization manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("W24 hexacode row alphabetization manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("W24 hexacode row alphabetization manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("W24 hexacode row alphabetization manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("W24 hexacode row alphabetization registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("W24 hexacode row alphabetization registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("W24 hexacode row alphabetization registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_w24_hexacode_row_alphabetization()
    print("D20 W24 hexacode row alphabetization proof obligation validated")
