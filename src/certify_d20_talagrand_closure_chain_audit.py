from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file
    from .derive_d20_talagrand_closure_chain_audit import (
        ARTIFACT_PATH,
        ARTIFACT_STATUS,
        EXPECTED_STEPS,
        INDEX_PATH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        hash_without,
    )
    from .verify_talagrand_handoff import validate_manifest as validate_handoff_manifest
    from .certify_d20_talagrand_multilevel_kkt_obstruction_system import (
        validate_d20_talagrand_multilevel_kkt_obstruction_system,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_d20_talagrand_closure_chain_audit import (
        ARTIFACT_PATH,
        ARTIFACT_STATUS,
        EXPECTED_STEPS,
        INDEX_PATH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        hash_without,
    )
    from verify_talagrand_handoff import validate_manifest as validate_handoff_manifest
    from certify_d20_talagrand_multilevel_kkt_obstruction_system import (
        validate_d20_talagrand_multilevel_kkt_obstruction_system,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "handoff_manifest_passed",
    "final_global_proof_not_claimed",
    "run_order_has_expected_steps",
    "all_step_statuses_match_expected",
    "source_certificates_present",
    "exactly_closed_ledger_nonempty",
    "numerical_audit_not_promoted_to_proof",
    "open_obstruction_is_last_step",
    "kkt_obligation_report_present",
    "kkt_obligation_preserves_open_target",
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


def validate_d20_talagrand_closure_chain_audit() -> dict[str, Any]:
    handoff = validate_handoff_manifest()
    if handoff.get("status") != "PASS":
        raise AssertionError("Talagrand handoff manifest is not valid")
    kkt = validate_d20_talagrand_multilevel_kkt_obstruction_system()
    if kkt.get("status") != "PASS":
        raise AssertionError("Talagrand KKT proof obligation is not valid")

    artifact = load_json(ARTIFACT_REL)
    report = load_json(REPORT_REL)
    manifest = load_json(MANIFEST_REL)
    index = load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.talagrand_closure_chain_audit.artifact@1":
        raise AssertionError("Talagrand closure chain artifact schema mismatch")
    if artifact.get("status") != ARTIFACT_STATUS:
        raise AssertionError("Talagrand closure chain artifact status mismatch")
    if hash_without(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Talagrand closure chain artifact self hash mismatch")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS:
        raise AssertionError("Talagrand closure chain check set mismatch")
    if any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("Talagrand closure chain checks are not all true")

    steps = artifact.get("steps", [])
    if len(steps) != len(EXPECTED_STEPS):
        raise AssertionError("Talagrand closure chain step count mismatch")
    expected_dirs = [step["directory"] for step in EXPECTED_STEPS]
    if [step.get("directory") for step in steps] != expected_dirs:
        raise AssertionError("Talagrand closure chain step order mismatch")
    expected_statuses = [step["expected_status"] for step in EXPECTED_STEPS]
    if [step.get("status") for step in steps] != expected_statuses:
        raise AssertionError("Talagrand closure chain statuses mismatch")
    if steps[-1].get("classification") != "open_exact_obstruction":
        raise AssertionError("Talagrand closure chain final step is not open obstruction")
    if steps[-2].get("classification") != "numerical_audit_only":
        raise AssertionError("Talagrand closure chain weighted-asymmetry step is not numerical")

    counts = artifact.get("classification_counts", {})
    if counts.get("open_exact_obstruction") != 1:
        raise AssertionError("Talagrand closure chain open obstruction count mismatch")
    if counts.get("numerical_audit_only") != 1:
        raise AssertionError("Talagrand closure chain numerical audit count mismatch")
    if artifact.get("source_handoff", {}).get("global_status") != (
        "HANDOFF_BUNDLE_BUILT; FINAL_GLOBAL_TALAGRAND_PROOF_NOT_CLAIMED"
    ):
        raise AssertionError("Talagrand closure chain final proof boundary mismatch")

    if report.get("schema") != "d20.proof_obligation.talagrand_closure_chain_audit@1":
        raise AssertionError("Talagrand closure chain report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("Talagrand closure chain report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Talagrand closure chain report checks failed")
    if hash_without(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Talagrand closure chain report certificate hash mismatch")
    if report.get("checks") != checks:
        raise AssertionError("Talagrand closure chain report checks mismatch")
    if "does not exclude" not in str(report.get("claim_boundary", "")):
        raise AssertionError("Talagrand closure chain report lost non-closure boundary")

    inputs = report.get("inputs", {})
    if not isinstance(inputs, dict):
        raise AssertionError("Talagrand closure chain inputs missing")
    check_input_file(inputs.get("artifact", {}), ARTIFACT_REL, "artifact")
    check_input_file(inputs.get("handoff_manifest", {}), "data/evidence/talagrand_python_handoff/manifest.json", "handoff manifest")
    check_input_file(inputs.get("status_ledger", {}), "data/evidence/talagrand_python_handoff/STATUS_LEDGER.json", "status ledger")
    check_input_file(inputs.get("run_order", {}), "data/evidence/talagrand_python_handoff/RUN_ORDER.md", "run order")
    check_input_file(
        inputs.get("kkt_obligation_report", {}),
        "data/invariants/d20/proof_obligations/d20_talagrand_multilevel_kkt_obstruction_system/report.json",
        "KKT obligation report",
    )
    check_input_file(
        inputs.get("derive_script", {}),
        "src/derive_d20_talagrand_closure_chain_audit.py",
        "derive script",
    )
    check_input_file(
        inputs.get("validator", {}),
        "src/certify_d20_talagrand_closure_chain_audit.py",
        "validator",
    )

    step_inputs = inputs.get("step_certificates", {})
    if not isinstance(step_inputs, dict) or len(step_inputs) != len(EXPECTED_STEPS):
        raise AssertionError("Talagrand closure chain step certificate inputs missing")
    for spec in EXPECTED_STEPS:
        key = str(spec["order"]).zfill(2) + "_" + spec["directory"]
        rel = (
            "data/evidence/talagrand_python_handoff/work/"
            + spec["directory"]
            + "/"
            + spec["certificate"]
        )
        check_input_file(step_inputs.get(key, {}), rel, key)

    if manifest.get("schema") != "d20.proof_obligation.talagrand_closure_chain_audit_manifest@1":
        raise AssertionError("Talagrand closure chain manifest schema mismatch")
    if manifest.get("name") != THEOREM_ID:
        raise AssertionError("Talagrand closure chain manifest name mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Talagrand closure chain manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Talagrand closure chain manifest artifact hash mismatch")
    if hash_without(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Talagrand closure chain manifest self hash mismatch")

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
        raise AssertionError("Talagrand closure chain index entry missing")
    if entry.get("report") != REPORT_REL or entry.get("manifest") != MANIFEST_REL:
        raise AssertionError("Talagrand closure chain index paths mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("Talagrand closure chain index status mismatch")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Talagrand closure chain index report hash mismatch")
    if index.get("obligation_count") != len(obligations):
        raise AssertionError("Talagrand closure chain index count mismatch")
    if hash_without(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("Talagrand closure chain index self hash mismatch")

    return {
        "schema": "d20.proof_obligation.talagrand_closure_chain_audit.validation@1",
        "status": "PASS",
        "proof_obligation": THEOREM_ID,
        "report": REPORT_REL,
        "manifest": MANIFEST_REL,
        "certificate_sha256": report.get("certificate_sha256"),
        "step_count": len(steps),
        "classification_counts": counts,
        "remaining_open_target": report.get("source_handoff", {}).get("remaining_open_target"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(
        json.dumps(
            validate_d20_talagrand_closure_chain_audit(),
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
