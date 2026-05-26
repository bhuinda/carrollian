from __future__ import annotations

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_hamming_gaussian_python_work_archive_import import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_hamming_gaussian_python_work_archive_import import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
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
    "archive_root_exists",
    "source_manifest_hashes_all_match",
    "source_manifest_sizes_all_match",
    "source_manifest_count_matches_actual_python_count",
    "all_python_sources_compile",
    "syntax_warnings_are_warning_only",
    "expected_replay_certificates_present",
    "expected_replay_statuses_match",
    "root_killing_sequence_42_18_6_0_replayed",
    "endpoint_dual_distance_8_replayed",
    "indicator_shell_domination_passes_boolean_case",
    "indicator_shell_total_subsets_is_full_boolean_cube",
    "sparse_signed_probe_pass_checks",
    "talagrand_sparse_mgf_sanity_passes",
    "logsobolev_local_sdpi_csv_passes",
    "spinh_veronese_csv_passes",
    "scipy_dependency_scripts_recorded",
    "mnt_data_bound_scripts_recorded",
    "w24_endpoint_is_certified",
    "final_entropy_inequality_not_certified",
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


def validate_d20_hamming_gaussian_python_work_archive_import() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.hamming_gaussian_python_work_archive_import.artifact@1":
        raise AssertionError("Hamming/Gaussian archive artifact schema mismatch")
    if artifact.get("status") != "D20_HAMMING_GAUSSIAN_PYTHON_WORK_ARCHIVE_IMPORTED_PARTIAL_REPLAY":
        raise AssertionError("Hamming/Gaussian archive artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Hamming/Gaussian archive artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Hamming/Gaussian archive artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("Hamming/Gaussian archive checks mismatch")

    source = artifact.get("source_archive", {}).get("source_manifest", {})
    if source.get("manifest_count") != 16 or source.get("actual_python_file_count") != 16:
        raise AssertionError("Hamming/Gaussian archive source count mismatch")
    if not source.get("all_hashes_match") or not source.get("all_sizes_match"):
        raise AssertionError("Hamming/Gaussian archive source manifest mismatch")

    syntax = artifact.get("syntax", {})
    if any(row.get("ok") is not True for row in syntax.get("compile_results", [])):
        raise AssertionError("Hamming/Gaussian archive compile failure")
    if not syntax.get("warning_files"):
        raise AssertionError("Hamming/Gaussian archive expected warning boundary missing")

    certs = artifact.get("replayed_certificates", {})
    dual = certs.get(
        "hamming_gaussian_dual_distance/hamming_gaussian_dual_distance_certificate.json", {}
    )
    if dual.get("root_sequence") != [42, 18, 6, 0]:
        raise AssertionError("Hamming/Gaussian root sequence mismatch")
    if dual.get("endpoint", {}).get("dual_distance_is_8") is not True:
        raise AssertionError("Hamming/Gaussian endpoint dual distance mismatch")

    indicator = certs.get(
        "hamming_gaussian_indicator_shell_domination/hamming_gaussian_indicator_shell_domination_certificate.json",
        {},
    )
    if indicator.get("global_max_ratio") != 1.0 or indicator.get("total_subsets_checked") != 2**24:
        raise AssertionError("Hamming/Gaussian indicator shell witness mismatch")

    talagrand = certs.get(
        "hamming_gaussian_talagrand_bridge/hamming_gaussian_talagrand_bridge_certificate.json",
        {},
    )
    if talagrand.get("sanity_checks", {}).get("mgf_bound_all_pass") is not True:
        raise AssertionError("Hamming/Gaussian Talagrand MGF sanity mismatch")

    full = certs.get(
        "hamming_gaussian_full_subgaussian_probe/hamming_gaussian_full_subgaussian_probe_certificate.json",
        {},
    )
    if abs(float(full.get("codeword_K", 0.0)) - 1.2020187417182888) > 1e-12:
        raise AssertionError("Hamming/Gaussian sharp constant witness mismatch")

    env = artifact.get("environment_boundary", {})
    if len(env.get("scipy_dependency_scripts_not_replayed_by_certificate", [])) != 4:
        raise AssertionError("Hamming/Gaussian SciPy blocker set mismatch")
    if len(env.get("mnt_data_bound_scripts_not_workspace_replayed", [])) != 3:
        raise AssertionError("Hamming/Gaussian /mnt/data blocker set mismatch")

    if report.get("schema") != "d20.proof_obligation.hamming_gaussian_python_work_archive_import@1":
        raise AssertionError("Hamming/Gaussian archive report schema mismatch")
    if report.get("status") != "D20_HAMMING_GAUSSIAN_PYTHON_WORK_ARCHIVE_IMPORT_CERTIFIED_PARTIAL_REPLAY":
        raise AssertionError("Hamming/Gaussian archive report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Hamming/Gaussian archive report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("Hamming/Gaussian archive report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Hamming/Gaussian archive report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Hamming/Gaussian archive report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_hamming_gaussian_python_work_archive_import.py",
        "derive input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_hamming_gaussian_python_work_archive_import.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.hamming_gaussian_python_work_archive_import_manifest@1":
        raise AssertionError("Hamming/Gaussian archive manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Hamming/Gaussian archive manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Hamming/Gaussian archive manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Hamming/Gaussian archive manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Hamming/Gaussian archive manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("Hamming/Gaussian archive registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Hamming/Gaussian archive registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Hamming/Gaussian archive registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_hamming_gaussian_python_work_archive_import()
    print("D20 Hamming/Gaussian Python work archive import validated")
