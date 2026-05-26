from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_packet239_e8_root_relation_probe import (
        ARTIFACT_PATH,
        EXPECTED_STATUSES,
        INDEX_PATH,
        OUT_DIR,
        SOURCE_REPORTS,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_packet239_e8_root_relation_probe import (
        ARTIFACT_PATH,
        EXPECTED_STATUSES,
        INDEX_PATH,
        OUT_DIR,
        SOURCE_REPORTS,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "d20_input_is_certified",
    *{f"{name}_input_is_certified" for name in SOURCE_REPORTS},
    "packet_table_has_512_packets_not_240",
    "packet239_zero_based_ordinal_is_240",
    "packet239_is_not_packet240",
    "packet239_selected_id_free",
    "packet239_is_unique_full_exposure_clock_zero",
    "full_exposure_frame_has_20_packets",
    "full_exposure_times_a12_classes_is_240",
    "packet239_seed_closure_is_exactly_packets_238_and_239",
    "packet239_stabilizer_orders_are_uniform_not_exceptional",
    "packet239_linear_image_is_d8_not_e8",
    "selected_packet_reports_have_no_explicit_e8_relation_claim",
    "selected_packet_reports_have_no_rank8_cartan_dynkin_witness",
    "golay_shell_has_240_profile_entries",
    "golay_240_entries_are_shell_profile_counts_not_packet_roots",
    "no_certified_240_root_set_present_in_current_witnesses",
    "explicit_e8_morphism_remains_open",
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


def validate_d20_packet239_e8_root_relation_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.packet239_e8_root_relation_probe.artifact@1":
        raise AssertionError("packet239 E8 probe artifact schema mismatch")
    if artifact.get("status") != "D20_PACKET239_E8_ROOT_RELATION_PROBE_DERIVED":
        raise AssertionError("packet239 E8 probe artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("packet239 E8 probe artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("packet239 E8 probe artifact does not replay")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("packet239 E8 probe checks mismatch")

    witness = artifact.get("witness", {})
    packet_boundary = witness.get("packet_count_boundary", {})
    if packet_boundary.get("packet_count") != 512:
        raise AssertionError("packet239 E8 probe packet count mismatch")
    if packet_boundary.get("full_exposure_packet_count") != 20:
        raise AssertionError("packet239 E8 probe full exposure count mismatch")
    if packet_boundary.get("packet239_zero_based_ordinal") != 240:
        raise AssertionError("packet239 E8 probe ordinal mismatch")

    packet_rows = witness.get("packet_rows", {})
    if packet_rows.get("packet239_selected_seed", {}).get("packet_id") != 239:
        raise AssertionError("packet239 E8 probe selected seed mismatch")
    if packet_rows.get("packet240_successor", {}).get("packet_id") != 240:
        raise AssertionError("packet239 E8 probe successor mismatch")

    candidate_sources = witness.get("candidate_240_sources", {})
    product = candidate_sources.get("full_exposure_times_a12_classes", {})
    if product.get("left_factor", {}).get("value") != 20:
        raise AssertionError("packet239 E8 probe full-exposure factor mismatch")
    if product.get("right_factor", {}).get("value") != 12:
        raise AssertionError("packet239 E8 probe A12 factor mismatch")
    if product.get("product") != 240:
        raise AssertionError("packet239 E8 probe 20x12 product mismatch")
    ordinal = candidate_sources.get("zero_based_ordinal", {})
    if ordinal.get("packet_id") != 239 or ordinal.get("ordinal") != 240:
        raise AssertionError("packet239 E8 probe ordinal source mismatch")
    golay_profile = candidate_sources.get("golay_shell_profile_entries", {})
    if golay_profile.get("profile_entries_equal_240_count", 0) <= 0:
        raise AssertionError("packet239 E8 probe Golay 240 entry count mismatch")

    selection = witness.get("packet239_id_free_selection", {})
    if selection.get("uses_external_packet_id") is not False:
        raise AssertionError("packet239 E8 probe id-free flag mismatch")
    if selection.get("selected_packet_ids") != [239]:
        raise AssertionError("packet239 E8 probe selected packet mismatch")

    propagation = witness.get("seed_propagation_boundary", {})
    if sorted(int(key) for key in propagation.get("two_step_target_packet_histogram", {})) != [
        238,
        239,
    ]:
        raise AssertionError("packet239 E8 probe seed closure mismatch")

    stabilizer = witness.get("stabilizer_boundary", {}).get("packet239_stabilizer", {})
    if stabilizer.get("linear_image_type") != "D8_real_signed_2x2":
        raise AssertionError("packet239 E8 probe linear image type mismatch")
    if stabilizer.get("linear_image_order") != 8:
        raise AssertionError("packet239 E8 probe linear image order mismatch")

    scan = witness.get("semantic_relation_scan", {})
    if scan.get("explicit_e8_relation_hit_count") != 0:
        raise AssertionError("packet239 E8 probe explicit E8 hit mismatch")
    if scan.get("rank8_cartan_dynkin_hit_count") != 0:
        raise AssertionError("packet239 E8 probe Cartan/Dynkin hit mismatch")
    missing = witness.get("missing_e8_witnesses", [])
    for phrase in ("240-element", "rank-8 Gram", "morphism"):
        if not any(phrase in row for row in missing):
            raise AssertionError(f"packet239 E8 probe missing boundary phrase absent: {phrase}")

    for name, rel_path in SOURCE_REPORTS.items():
        entry = artifact.get("inputs", {}).get("source_reports", {}).get(name, {})
        _check_input_file(entry, rel_path.relative_to(ROOT).as_posix(), f"artifact {name}")
        if entry.get("status") != EXPECTED_STATUSES[name]:
            raise AssertionError(f"packet239 E8 probe source status mismatch: {name}")

    if report.get("schema") != "d20.proof_obligation.packet239_e8_root_relation_probe@1":
        raise AssertionError("packet239 E8 probe report schema mismatch")
    if report.get("status") != "D20_PACKET239_E8_ROOT_RELATION_PROBE_CERTIFIED":
        raise AssertionError("packet239 E8 probe report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("packet239 E8 probe report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("packet239 E8 probe report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("packet239 E8 probe report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("packet239 E8 probe report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "report artifact")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_packet239_e8_root_relation_probe.py",
        "derive script",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_packet239_e8_root_relation_probe.py",
        "validator",
    )
    _check_input_file(report.get("inputs", {}).get("d20", {}), "d20.json", "d20")
    if report.get("witness") != witness:
        raise AssertionError("packet239 E8 probe report witness mismatch")

    if manifest.get("schema") != "d20.proof_obligation.packet239_e8_root_relation_probe_manifest@1":
        raise AssertionError("packet239 E8 probe manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("packet239 E8 probe manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("packet239 E8 probe manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("packet239 E8 probe manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("packet239 E8 probe manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("packet239 E8 probe registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("packet239 E8 probe registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("packet239 E8 probe registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_packet239_e8_root_relation_probe()
    print("D20 packet239 E8 root relation probe certificate validated")
