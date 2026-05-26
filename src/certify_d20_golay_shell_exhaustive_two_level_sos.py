from __future__ import annotations

import csv
import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_golay_shell_exhaustive_two_level_sos import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        PROFILE_CSV,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_golay_shell_exhaustive_two_level_sos import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        PROFILE_CSV,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()
PROFILE_CSV_REL = PROFILE_CSV.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "w24_endpoint_certified",
    "archive_two_level_precursor_certified",
    "selected_two_level_precursor_certified",
    "generated_code_has_4096_words",
    "generated_code_weight_histogram_matches_w24",
    "both_shells_have_49_profiles",
    "both_shells_cover_all_subsets",
    "all_profile_entries_well_formed",
    "all_profile_sums_match_shell_sizes",
    "all_gap_polynomials_have_positive_coefficient_quotients",
    "all_gap_polynomials_have_double_equality_root",
    "profile_csv_written",
    "full_arbitrary_vector_theorem_not_certified",
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


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} file hash mismatch")


def _read_profile_csv() -> list[dict[str, str]]:
    with PROFILE_CSV.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_d20_golay_shell_exhaustive_two_level_sos() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.golay_shell_exhaustive_two_level_sos.artifact@1":
        raise AssertionError("Golay exhaustive two-level artifact schema mismatch")
    if artifact.get("status") != "D20_GOLAY_SHELL_EXHAUSTIVE_TWO_LEVEL_POSITIVE_QUOTIENT_CERTIFIED":
        raise AssertionError("Golay exhaustive two-level artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay exhaustive two-level artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay exhaustive two-level artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("Golay exhaustive two-level checks mismatch")

    witness = artifact.get("witness", {})
    shells = witness.get("shells", {})
    for shell in ("12", "16"):
        summary = shells.get(shell, {})
        if summary.get("unique_profile_count") != 49:
            raise AssertionError(f"Golay exhaustive two-level profile count mismatch for {shell}")
        if summary.get("subset_count_total") != 2**24:
            raise AssertionError(f"Golay exhaustive two-level subset count mismatch for {shell}")
        if summary.get("all_positive_quotients_nonnegative") is not True:
            raise AssertionError(f"Golay exhaustive two-level quotient mismatch for {shell}")
        if summary.get("all_gap_polynomials_have_double_root_at_one") is not True:
            raise AssertionError(f"Golay exhaustive two-level double-root mismatch for {shell}")
    if witness.get("profile_csv_row_count") != 98:
        raise AssertionError("Golay exhaustive two-level profile CSV row count mismatch")
    _check_input_file(witness.get("profile_csv", {}), PROFILE_CSV_REL, "profile CSV")

    csv_rows = _read_profile_csv()
    if len(csv_rows) != 98:
        raise AssertionError("Golay exhaustive two-level CSV length mismatch")
    if any(row.get("positive_quotient_nonnegative") != "True" for row in csv_rows):
        raise AssertionError("Golay exhaustive two-level CSV quotient flag mismatch")
    if any(row.get("first_division_remainder") != "0" for row in csv_rows):
        raise AssertionError("Golay exhaustive two-level first remainder mismatch")
    if any(row.get("second_division_remainder") != "0" for row in csv_rows):
        raise AssertionError("Golay exhaustive two-level second remainder mismatch")
    subset_totals = {}
    for row in csv_rows:
        subset_totals[row["shell"]] = subset_totals.get(row["shell"], 0) + int(row["subset_count"])
    if subset_totals != {"12": 2**24, "16": 2**24}:
        raise AssertionError("Golay exhaustive two-level CSV subset totals mismatch")

    if report.get("schema") != "d20.proof_obligation.golay_shell_exhaustive_two_level_sos@1":
        raise AssertionError("Golay exhaustive two-level report schema mismatch")
    if report.get("status") != "D20_GOLAY_SHELL_EXHAUSTIVE_TWO_LEVEL_SOS_CERTIFIED":
        raise AssertionError("Golay exhaustive two-level report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Golay exhaustive two-level report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("Golay exhaustive two-level report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay exhaustive two-level report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay exhaustive two-level report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_golay_shell_exhaustive_two_level_sos.py",
        "derive input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_golay_shell_exhaustive_two_level_sos.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.golay_shell_exhaustive_two_level_sos_manifest@1":
        raise AssertionError("Golay exhaustive two-level manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay exhaustive two-level manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay exhaustive two-level manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay exhaustive two-level manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay exhaustive two-level manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("Golay exhaustive two-level registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay exhaustive two-level registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Golay exhaustive two-level registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_golay_shell_exhaustive_two_level_sos()
    print("D20 Golay shell exhaustive two-level SOS certificate validated")
