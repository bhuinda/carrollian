from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file
    from .derive_d20_talagrand_multilevel_kkt_obstruction_system import (
        ARTIFACT_PATH,
        ARTIFACT_STATUS,
        INDEX_PATH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        hash_without,
    )
    from .verify_talagrand_handoff import validate_manifest as validate_handoff_manifest
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_d20_talagrand_multilevel_kkt_obstruction_system import (
        ARTIFACT_PATH,
        ARTIFACT_STATUS,
        INDEX_PATH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        hash_without,
    )
    from verify_talagrand_handoff import validate_manifest as validate_handoff_manifest


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "handoff_final_global_proof_not_claimed",
    "kkt_certificate_status_not_closed",
    "kkt_certificate_claim_boundary_not_proof",
    "kkt_theorem_status_not_closed",
    "remaining_certificate_mentions_df_positive",
    "remaining_certificate_mentions_shells_12_16",
    "contact_normal_form_certified",
    "contact_normal_form_keeps_weighted_asymmetry_open",
    "weighted_asymmetry_audit_numerical_only",
    "weighted_asymmetry_audit_found_no_positive_rows",
    "kkt_source_files_present",
}


def load_json(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_d20_talagrand_multilevel_kkt_obstruction_system() -> dict[str, Any]:
    handoff = validate_handoff_manifest()
    if handoff.get("status") != "PASS":
        raise AssertionError("Talagrand handoff manifest is not valid")

    artifact = load_json(ARTIFACT_REL)
    report = load_json(REPORT_REL)
    manifest = load_json(MANIFEST_REL)
    index = load_json(INDEX_REL)

    if artifact.get("schema") != (
        "d20.proof_obligation.talagrand_multilevel_kkt_obstruction_system.artifact@1"
    ):
        raise AssertionError("Talagrand KKT artifact schema mismatch")
    if artifact.get("status") != ARTIFACT_STATUS:
        raise AssertionError("Talagrand KKT artifact status mismatch")
    if hash_without(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Talagrand KKT artifact self hash mismatch")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS:
        raise AssertionError("Talagrand KKT artifact check set mismatch")
    if any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("Talagrand KKT artifact checks are not all true")

    if report.get("schema") != "d20.proof_obligation.talagrand_multilevel_kkt_obstruction_system@1":
        raise AssertionError("Talagrand KKT report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("Talagrand KKT report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Talagrand KKT report does not pass checks")
    if hash_without(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Talagrand KKT report certificate hash mismatch")
    if report.get("claim_boundary") != artifact.get("claim_boundary"):
        raise AssertionError("Talagrand KKT report claim boundary mismatch")
    if report.get("checks") != checks:
        raise AssertionError("Talagrand KKT report checks mismatch")

    witness = report.get("witness", {})
    open_boundary = witness.get("open_boundary", {}) if isinstance(witness, dict) else {}
    not_certified = open_boundary.get("not_certified", []) if isinstance(open_boundary, dict) else []
    if not any("no final global Talagrand proof" in str(item) for item in not_certified):
        raise AssertionError("Talagrand KKT report does not preserve final-proof boundary")
    supporting = witness.get("supporting_evidence", {}) if isinstance(witness, dict) else {}
    audit = supporting.get("weighted_asymmetry_numerical_audit", {}) if isinstance(supporting, dict) else {}
    if audit.get("positive_outward_derivative_rows") != 0:
        raise AssertionError("Talagrand weighted-asymmetry audit did not preserve zero positive rows")
    if "Numerical audit only" not in str(audit.get("claim_boundary", "")):
        raise AssertionError("Talagrand weighted-asymmetry audit boundary lost")

    inputs = report.get("inputs", {})
    if not isinstance(inputs, dict):
        raise AssertionError("Talagrand KKT report inputs missing")
    check_input_file(inputs.get("artifact", {}), ARTIFACT_REL, "artifact")
    check_input_file(inputs.get("handoff_manifest", {}), "data/evidence/talagrand_python_handoff/manifest.json", "handoff manifest")
    check_input_file(inputs.get("status_ledger", {}), "data/evidence/talagrand_python_handoff/STATUS_LEDGER.json", "status ledger")
    check_input_file(
        inputs.get("kkt_certificate", {}),
        "data/evidence/talagrand_python_handoff/work/talagrand_multilevel_KKT_obstruction_system/multilevel_KKT_obstruction_certificate.json",
        "KKT certificate",
    )
    check_input_file(
        inputs.get("kkt_theorem", {}),
        "data/evidence/talagrand_python_handoff/work/talagrand_multilevel_KKT_obstruction_system/multilevel_KKT_obstruction_theorem.json",
        "KKT theorem",
    )
    check_input_file(
        inputs.get("contact_normal_form_certificate", {}),
        "data/evidence/talagrand_python_handoff/work/talagrand_multilevel_contact_normal_form/multilevel_contact_normal_form_certificate.json",
        "contact normal form certificate",
    )
    check_input_file(
        inputs.get("weighted_asymmetry_audit_certificate", {}),
        "data/evidence/talagrand_python_handoff/work/talagrand_weighted_asymmetry_contact_audit/weighted_asymmetry_contact_audit_certificate.json",
        "weighted-asymmetry audit certificate",
    )
    check_input_file(
        inputs.get("derive_script", {}),
        "src/derive_d20_talagrand_multilevel_kkt_obstruction_system.py",
        "derive script",
    )
    check_input_file(
        inputs.get("validator", {}),
        "src/certify_d20_talagrand_multilevel_kkt_obstruction_system.py",
        "validator",
    )

    if manifest.get("schema") != (
        "d20.proof_obligation.talagrand_multilevel_kkt_obstruction_system_manifest@1"
    ):
        raise AssertionError("Talagrand KKT manifest schema mismatch")
    if manifest.get("name") != THEOREM_ID:
        raise AssertionError("Talagrand KKT manifest name mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Talagrand KKT manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Talagrand KKT manifest artifact hash mismatch")
    if hash_without(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Talagrand KKT manifest self hash mismatch")

    obligations = index.get("obligations", [])
    entry = next(
        (
            row
            for row in obligations
            if isinstance(row, dict) and row.get("id") == THEOREM_ID
        ),
        None,
    )
    if entry is None:
        raise AssertionError("Talagrand KKT proof-obligation index entry missing")
    if entry.get("report") != REPORT_REL or entry.get("manifest") != MANIFEST_REL:
        raise AssertionError("Talagrand KKT proof-obligation index paths mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("Talagrand KKT proof-obligation index status mismatch")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Talagrand KKT proof-obligation index report hash mismatch")
    if index.get("obligation_count") != len(obligations):
        raise AssertionError("Talagrand proof-obligation index count mismatch")
    if hash_without(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("Talagrand proof-obligation index self hash mismatch")

    return {
        "schema": "d20.proof_obligation.talagrand_multilevel_kkt_obstruction_system.validation@1",
        "status": "PASS",
        "proof_obligation": THEOREM_ID,
        "report": REPORT_REL,
        "manifest": MANIFEST_REL,
        "certificate_sha256": report.get("certificate_sha256"),
        "handoff_manifest_sha256": handoff.get("manifest_sha256"),
        "remaining_open_target": report.get("source_handoff", {}).get("remaining_open_target"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(
        json.dumps(
            validate_d20_talagrand_multilevel_kkt_obstruction_system(),
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
