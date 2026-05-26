from __future__ import annotations

import csv
import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_golay_shell_three_level_structured_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        PROFILE_CSV,
        THEOREM_ID,
        TOL,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_golay_shell_three_level_structured_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        PROFILE_CSV,
        THEOREM_ID,
        TOL,
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
    "exhaustive_two_level_input_certified",
    "generated_code_has_4096_words",
    "generated_code_weight_histogram_matches_w24",
    "selected_partitions_nonempty",
    "unique_profiles_nonempty",
    "no_positive_structured_three_level_profile_found",
    "all_profile_hessians_nonpositive_at_equality",
    "profile_csv_written",
    "full_three_level_exhaustion_not_certified",
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


def validate_d20_golay_shell_three_level_structured_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.golay_shell_three_level_structured_probe.artifact@1":
        raise AssertionError("Golay three-level structured artifact schema mismatch")
    if artifact.get("status") != "D20_GOLAY_SHELL_THREE_LEVEL_STRUCTURED_PROBE_NO_COUNTEREXAMPLE":
        raise AssertionError("Golay three-level structured artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay three-level structured artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay three-level structured artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("Golay three-level structured checks mismatch")

    selection = artifact.get("selection", {})
    if selection.get("selected_partition_count", 0) < 100000:
        raise AssertionError("Golay three-level structured partition family unexpectedly small")
    if selection.get("unique_profile_count", 0) < 100:
        raise AssertionError("Golay three-level structured profile family unexpectedly small")
    if selection.get("positive_profile_count") != 0:
        raise AssertionError("Golay three-level structured positive profile found")
    if selection.get("local_hessian_positive_count") != 0:
        raise AssertionError("Golay three-level structured Hessian positivity found")
    if float(selection.get("max_best_F")) > TOL:
        raise AssertionError("Golay three-level structured max F exceeds tolerance")

    witness = artifact.get("witness", {})
    _check_input_file(witness.get("profile_csv", {}), PROFILE_CSV_REL, "profile CSV")
    csv_rows = _read_profile_csv()
    if len(csv_rows) != witness.get("profile_csv_row_count"):
        raise AssertionError("Golay three-level structured CSV row count mismatch")
    if any(float(row["best_F"]) > TOL for row in csv_rows):
        raise AssertionError("Golay three-level structured CSV positive best F")
    if any(row["local_hessian_nonpositive"] != "True" for row in csv_rows):
        raise AssertionError("Golay three-level structured CSV Hessian flag mismatch")

    if report.get("schema") != "d20.proof_obligation.golay_shell_three_level_structured_probe@1":
        raise AssertionError("Golay three-level structured report schema mismatch")
    if report.get("status") != "D20_GOLAY_SHELL_THREE_LEVEL_STRUCTURED_PROBE_CERTIFIED_NO_COUNTEREXAMPLE":
        raise AssertionError("Golay three-level structured report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Golay three-level structured report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("Golay three-level structured report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay three-level structured report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay three-level structured report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_golay_shell_three_level_structured_probe.py",
        "derive input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_golay_shell_three_level_structured_probe.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.golay_shell_three_level_structured_probe_manifest@1":
        raise AssertionError("Golay three-level structured manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay three-level structured manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay three-level structured manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay three-level structured manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay three-level structured manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("Golay three-level structured registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay three-level structured registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Golay three-level structured registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_golay_shell_three_level_structured_probe()
    print("D20 Golay shell three-level structured probe validated")
