from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_golay_hamming_minor_puncture_search import build_artifact
except ImportError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.certify_io import ROOT, h_file, h_json
    from src.derive_d20_golay_hamming_minor_puncture_search import build_artifact


THEOREM_ID = "d20_golay_hamming_minor_puncture_search"
ARTIFACT_REL = "generated/d20_golay_hamming_minor_puncture_search.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "prior_correspondence_probe": (
        "data/invariants/d20/proof_obligations/d20_golay_hamming_correspondence_probe/report.json"
    ),
    "sector33_dual": "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json",
    "hexacode_row_selector": "data/selectors/hexacode_row_selector.json",
    "quadratic_golay_obstruction": "data/selectors/quadratic_golay_obstruction.json",
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


def validate_d20_golay_hamming_minor_puncture_search() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.golay_hamming_minor_puncture_search.artifact@1":
        raise AssertionError("minor/puncture search artifact schema mismatch")
    if artifact.get("status") != "D20_GOLAY_HAMMING_MINOR_PUNCTURE_SEARCH_DERIVED":
        raise AssertionError("minor/puncture search artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("minor/puncture search artifact self hash mismatch")
    recomputed = build_artifact()
    if recomputed != artifact:
        raise AssertionError("minor/puncture search artifact does not replay")

    checks = artifact.get("checks", {})
    required_checks = {
        "prior_correspondence_probe_is_certified",
        "sector33_dual_input_is_certified",
        "hexacode_golay_endpoint_is_certified",
        "target_extended_golay_histogram_matches_hexacode_report",
        "quadratic_obstruction_remains_active",
        "fixed_cocircuit_has_six_elements",
        "extra_pool_has_twenty_five_elements",
        "candidate_count_is_6400",
        "all_candidates_reduce_to_length_24",
        "no_extended_golay_shape_match_in_bounded_family",
        "no_punctured_golay_shape_match_in_bounded_family",
        "explicit_morphism_remains_open",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("minor/puncture search artifact check mismatch")

    search = artifact.get("search", {})
    family = search.get("natural_removal_family", {})
    if family.get("fixed_six_element_cocircuit") != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("minor/puncture search cocircuit mismatch")
    if family.get("extra_element_count") != 25:
        raise AssertionError("minor/puncture search extra pool mismatch")
    if family.get("operation_masks_per_removal_set") != 128:
        raise AssertionError("minor/puncture search operation mask count mismatch")
    if family.get("source_matrix_count") != 2 or family.get("candidate_count") != 6400:
        raise AssertionError("minor/puncture search candidate count mismatch")

    summary = search.get("search_summary", {})
    if summary.get("all_reduced_lengths_are_24") is not True:
        raise AssertionError("minor/puncture search length check mismatch")
    if summary.get("extended_golay_shape_match_count") != 0:
        raise AssertionError("minor/puncture search unexpectedly found extended Golay match")
    if summary.get("punctured_golay_shape_match_count") != 0:
        raise AssertionError("minor/puncture search unexpectedly found punctured Golay match")
    if summary.get("exact_morphism_found") is not False:
        raise AssertionError("minor/puncture search morphism status mismatch")
    if search.get("matches", {}).get("extended_golay_shape") != []:
        raise AssertionError("minor/puncture search extended match list mismatch")
    if search.get("matches", {}).get("punctured_golay_shape") != []:
        raise AssertionError("minor/puncture search punctured match list mismatch")

    source_summaries = search.get("source_matrix_summaries", {})
    if source_summaries.get("sector33_primal_mod2", {}).get("shape") != {"rows": 21, "cols": 31}:
        raise AssertionError("minor/puncture search primal shape mismatch")
    if source_summaries.get("sector33_dual_mod2", {}).get("shape") != {"rows": 11, "cols": 31}:
        raise AssertionError("minor/puncture search dual shape mismatch")

    target = artifact.get("target_code_profiles", {})
    if target.get("extended_golay_24_12_8", {}).get("weight_histogram") != {
        "0": 1,
        "8": 759,
        "12": 2576,
        "16": 759,
        "24": 1,
    }:
        raise AssertionError("minor/puncture search extended Golay target mismatch")
    if target.get("punctured_golay_23_12_7", {}).get("weight_histogram") != {
        "0": 1,
        "7": 253,
        "8": 506,
        "11": 1288,
        "12": 1288,
        "15": 506,
        "16": 253,
        "23": 1,
    }:
        raise AssertionError("minor/puncture search punctured Golay target mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(artifact.get("source_reports", {}).get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != "d20.proof_obligation.golay_hamming_minor_puncture_search@1":
        raise AssertionError("minor/puncture search report schema mismatch")
    if report.get("status") != "D20_GOLAY_HAMMING_MINOR_PUNCTURE_SEARCH_CERTIFIED":
        raise AssertionError("minor/puncture search report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("minor/puncture search report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("minor/puncture search report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("minor/puncture search report artifact hash mismatch")
    if report.get("target_code_profiles") != artifact.get("target_code_profiles"):
        raise AssertionError("minor/puncture search report target mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("minor/puncture search report checks mismatch")
    witness = report.get("witness", {})
    if witness.get("natural_removal_family") != family:
        raise AssertionError("minor/puncture search report family mismatch")
    if witness.get("search_summary") != summary:
        raise AssertionError("minor/puncture search report summary mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != "d20.proof_obligation.golay_hamming_minor_puncture_search_manifest@1":
        raise AssertionError("minor/puncture search manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("minor/puncture search manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("minor/puncture search manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("minor/puncture search manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("minor/puncture search registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("minor/puncture search registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("minor/puncture search registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_golay_hamming_minor_puncture_search()
    print("D20 Golay-Hamming minor/puncture search validated")
