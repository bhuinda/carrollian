from __future__ import annotations

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json


THEOREM_ID = "d20_golay_hamming_correspondence_probe"
ARTIFACT_REL = "generated/d20_golay_hamming_correspondence_probe.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "intrinsic_hex_metric": "data/invariants/d20/proof_obligations/d20_voltage_lift_intrinsic_hex_metric/report.json",
    "sector33_tutte_os": "data/invariants/d20/theorems/d20_oriented_matroid_tutte_os/report.json",
    "sector33_dual": "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json",
    "wu_golay_resolvent": "data/geometry/wu_golay_quintic_resolvent.json",
    "quadratic_golay_obstruction": "data/selectors/quadratic_golay_obstruction.json",
    "hexacode_row_selector": "data/selectors/hexacode_row_selector.json",
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


def validate_d20_golay_hamming_correspondence_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.golay_hamming_correspondence_probe.artifact@1":
        raise AssertionError("Golay-Hamming probe artifact schema mismatch")
    if artifact.get("status") != "D20_GOLAY_HAMMING_CORRESPONDENCE_PROBE_DERIVED":
        raise AssertionError("Golay-Hamming probe artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("Golay-Hamming probe artifact self hash mismatch")

    checks = artifact.get("checks", {})
    required_checks = {
        "intrinsic_metric_ratio_is_31_over_23",
        "metric_eigenvalues_have_common_denominator_20",
        "major_numerator_matches_sector33_ground_set",
        "sector33_ground_is_30_edges_plus_e33",
        "sector33_os_hilbert_begins_1_31",
        "sector33_all_subsets_is_2_to_31",
        "sector33_dual_positive_cocircuit_has_six_elements",
        "sector33_dual_cocircuit_includes_e33",
        "minor_numerator_matches_wu_syzygy_rank",
        "minor_numerator_matches_punctured_golay_length",
        "wu_report_declares_golay_extension_unresolved",
        "hexacode_selector_constructs_extended_golay",
        "hexacode_has_six_columns",
        "hexacode_canonicity_is_external",
        "quadratic_obstruction_blocks_intrinsic_rank12_typeII_selector",
        "explicit_31_to_24_to_23_morphism_not_constructed",
        "open_boundary_is_recorded",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("Golay-Hamming probe artifact check mismatch")

    alignments = artifact.get("certified_alignments", {})
    metric = alignments.get("metric", {})
    if metric.get("eigenvalues_exact") != {"major": "31/20", "minor": "23/20"}:
        raise AssertionError("Golay-Hamming probe metric eigenvalue mismatch")
    if metric.get("anisotropy_ratio_exact") != "31/23":
        raise AssertionError("Golay-Hamming probe ratio mismatch")
    if metric.get("major_numerator") != 31 or metric.get("minor_numerator") != 23:
        raise AssertionError("Golay-Hamming probe numerator mismatch")

    sector = alignments.get("sector33_hamming_31", {})
    if sector.get("sector33_ground_set_size") != 31:
        raise AssertionError("Golay-Hamming probe sector33 ground mismatch")
    if sector.get("d20_old_edge_elements") != 30 or sector.get("new_element") != "e33":
        raise AssertionError("Golay-Hamming probe sector33 decomposition mismatch")
    if sector.get("hamming_length_m") != 5:
        raise AssertionError("Golay-Hamming probe Hamming-length audit mismatch")
    if sector.get("centered_pentagonal_order") != 4:
        raise AssertionError("Golay-Hamming probe centered pentagonal audit mismatch")

    wu_golay = alignments.get("wu_golay_23", {})
    if wu_golay.get("wu_linear_syzygy_basis_rank") != 23:
        raise AssertionError("Golay-Hamming probe Wu rank mismatch")
    if wu_golay.get("wu_golay_extension_test_passes") is not False:
        raise AssertionError("Golay-Hamming probe Wu unresolved boundary mismatch")
    if wu_golay.get("extended_golay_length") != 24 or wu_golay.get("punctured_golay_length") != 23:
        raise AssertionError("Golay-Hamming probe Golay length mismatch")
    if wu_golay.get("extended_golay_rank") != 12:
        raise AssertionError("Golay-Hamming probe Golay rank mismatch")
    if wu_golay.get("extended_golay_weight_histogram") != {
        "0": 1,
        "8": 759,
        "12": 2576,
        "16": 759,
        "24": 1,
    }:
        raise AssertionError("Golay-Hamming probe Golay weight histogram mismatch")

    sixfold = alignments.get("sixfold_spine", {})
    if sixfold.get("sector33_dual_positive_cocircuit_support_size") != 6:
        raise AssertionError("Golay-Hamming probe sixfold cocircuit mismatch")
    if sixfold.get("hexacode_columns") != 6 or sixfold.get("hexacode_f4_dimension") != 3:
        raise AssertionError("Golay-Hamming probe hexacode shape mismatch")

    candidate = artifact.get("candidate_morphism", {})
    if candidate.get("morphism_status") != "OPEN_NOT_CONSTRUCTED":
        raise AssertionError("Golay-Hamming probe morphism boundary mismatch")
    if "31-element sector33 matroid" not in candidate.get("missing_map", ""):
        raise AssertionError("Golay-Hamming probe missing-map description mismatch")

    source_reports = artifact.get("source_reports", {})
    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(source_reports.get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != "d20.proof_obligation.golay_hamming_correspondence_probe@1":
        raise AssertionError("Golay-Hamming probe report schema mismatch")
    if report.get("status") != "D20_GOLAY_HAMMING_CORRESPONDENCE_PROBE_CERTIFIED":
        raise AssertionError("Golay-Hamming probe report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Golay-Hamming probe report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay-Hamming probe report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("Golay-Hamming probe report artifact hash mismatch")
    if report.get("witness") != artifact.get("certified_alignments"):
        raise AssertionError("Golay-Hamming probe report witness mismatch")
    if report.get("candidate_morphism") != artifact.get("candidate_morphism"):
        raise AssertionError("Golay-Hamming probe report candidate morphism mismatch")
    if report.get("obstruction_boundary") != artifact.get("obstruction_boundary"):
        raise AssertionError("Golay-Hamming probe report obstruction boundary mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("Golay-Hamming probe report checks mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != "d20.proof_obligation.golay_hamming_correspondence_probe_manifest@1":
        raise AssertionError("Golay-Hamming probe manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay-Hamming probe manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("Golay-Hamming probe manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay-Hamming probe manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("Golay-Hamming probe registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay-Hamming probe registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Golay-Hamming probe registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_golay_hamming_correspondence_probe()
    print("D20 Golay-Hamming correspondence probe validated")
