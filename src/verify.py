#!/usr/bin/env python3
"""Readable verifier entrypoint for d20.

The `src.commands.certify` entrypoint remains authoritative. This module exposes
the practical verification modes without hiding file writes behind a default:

* core: validate the mathematical core and layer statuses only;
* audit: validate core plus constructor witness and the file manifest;
* rebuild: regenerate d20.json, refresh hashes, then audit;
  pass --cached-source to reuse checked source artifacts and skip heavy source refresh;
* refresh-certificate: rescan certified invariant reports into certificate.json;
* strict-replay: validate core plus a fresh zero-axiom coorient replay;
* evidence-index: validate the lightweight data/evidence registry;
* compiler-scene-selftest: validate the source-to-scene compiler smoke test;
* compiler-a42-d20-replay: validate compiler A42/D20 coordinate replay evidence;
* compiler-nonstrict: run the cheap compiler integration gates;
* integration-nonstrict: run the cheap compiler and cubic integration gates;
* jacobian-cubic-contract: validate the normalized cubic cache input contract;
* jacobian-cubic-intake: validate the normalized cubic certificate intake protocol;
* jacobian-cubic-closure: validate the normalized cubic closure checklist;
* jacobian-cubic-status: report the normalized cubic closure level and certificate counts;
* jacobian-cubic-nonstrict: run the cheap cubic integration gates, excluding strict cache;
* jacobian-cubic-cache: validate the cached normalized cubic elimination certificates;
* talagrand-chain-audit: validate the extracted Talagrand closure chain audit;
* talagrand-kkt-obligation: validate the extracted Talagrand KKT open proof obligation;
* c985-registry: validate the C985 typed simple-object registry proof obligation;
* c985-fusion: validate the C985 fusion multiplicity typing proof obligation;
* c985-associator: validate the C985 associator rebracketing oracle proof obligation;
* c985-unit: validate the C985 unit tensor laws proof obligation;
* c985-triangle: validate the C985 unit triangle coherence proof obligation;
* c985-duality: validate the C985 transpose duality support proof obligation;
* c985-pentagon: validate the C985 pentagon chain normal form proof obligation;
* c985-zigzag: validate the C985 dual zig-zag identities proof obligation;
* c985-final: validate the final C985 finite semisimple multi-fusion certificate;
* c985-geometry: validate the C985 tensor geometry invariant-discovery readout;
* c985-d20-atlas: validate the C985-to-d20 boundary invariant atlas;
* c985-hyperbolic-graph: validate the C985-derived d20 hyperbolic boundary graph;
* c985-poincare: validate the C985-derived d20 Poincare disk embedding;
* c985-filtration: validate the C985-derived d20 Poincare landmark filtration;
* c985-nerve: validate the C985-derived d20 signature-class nerve;
* c985-chart-atlas: validate the C985-derived d20 hyperbolic chart atlas;
* c985-transition-groupoid: validate the C985-derived d20 transition groupoid;
* c985-normal-words: validate the C985-derived d20 normal-form words;
* c985-symbolic-rewrites: validate the C985-derived d20 symbolic rewrite rules;
* c985-symbolic-associativity: validate the C985-derived d20 symbolic associativity diamond;
* c985-rewrite-complex: validate the C985-derived d20 rewrite-complex hyperbolicity;
* c985-interval-sheaf: validate the C985-derived d20 geodesic interval sheaf;
* c985-preserved-core: validate the C985-derived d20 preserved-core subcomplex;
* c985-chamber-spine: validate the C985-derived d20 chamber-spine orientation;
* c985-morse-reeb: validate the C985-derived d20 Morse/Reeb quotient;
* c985-boundary-transfer: validate the C985-derived d20 boundary transfer operator;
* c985-atom-flow: validate the C985-derived d20 stationary atom-flow lift;
* c985-signature-subboundary: validate the C985-derived d20 recurrent signature subboundary;
* c985-signature-transfer: validate the C985-derived d20 signature subboundary transfer operator;
* c985-signature-spectral-cut: validate the C985-derived d20 signature transfer spectral cut;
* c985-signature-quotient: validate the C985-derived d20 signature spectral quotient dynamics;
* c985-signature-geometry: validate the C985-derived d20 signature quotient Poincare geometry;
* c985-signature-geodesic: validate the C985-derived d20 signature geodesic order;
* c985-signature-residual-chart: validate the C985-derived d20 signature geodesic residual chart;
* c985-signature-cell-complex: validate the C985-derived d20 signature residual cell complex;
* token-burn: validate bounded-output guard coverage for repo-defined runners;
* tamper: mutate certified evidence in memory and require verification failure.
"""
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime import ensure_numpy_runtime  # noqa: E402

ensure_numpy_runtime(ROOT, __file__)

from src.commands import certify  # noqa: E402
from src.evidence_registry import EVIDENCE_INDEX_PATH, sha_file  # noqa: E402
from src.token_burn_guard import emit_json  # noqa: E402

EVIDENCE_INDEX = EVIDENCE_INDEX_PATH
DATA_INDEX = ROOT / "data" / "index.json"
CUBIC_EVIDENCE_ID = "jacobian_cubic_symbolic_elimination"
CUBIC_EVIDENCE_ROOT = "data/evidence/jacobian_cubic_symbolic_elimination"
CUBIC_DATA_DOMAIN = "jacobian_cubic_symbolic_elimination_evidence"
COMPILER_A42_D20_EVIDENCE_ID = "compiler_a42_d20_replay_test"
COMPILER_A42_D20_EVIDENCE_ROOT = "data/evidence/compiler_a42_d20_replay_test"
COMPILER_A42_D20_MANIFEST = "data/evidence/compiler_a42_d20_replay_test/manifest.json"
COMPILER_A42_D20_STATUS = "COMPILER_A42_D20_REPLAY_CERTIFIED"
COMPILER_A42_D20_DATA_DOMAIN = "compiler_a42_d20_replay_evidence"
TOKEN_BURN_EVIDENCE_ID = "token_burn_guard"
TOKEN_BURN_CERTIFICATE = "data/evidence/token_burn_guard/certificate.json"
TOKEN_BURN_STATUS = "TOKEN_BURN_GUARD_CERTIFIED"
TALAGRAND_EVIDENCE_ID = "talagrand_python_handoff"
TALAGRAND_EVIDENCE_ROOT = "data/evidence/talagrand_python_handoff"
TALAGRAND_MANIFEST = "data/evidence/talagrand_python_handoff/manifest.json"
TALAGRAND_DATA_DOMAIN = "talagrand_python_handoff_evidence"
TALAGRAND_STATUS = "TALAGRAND_PYTHON_HANDOFF_IMPORTED_WITH_OPEN_GLOBAL_TARGET"


MODES = {
    "core": "fast",
    "audit": "audit",
    "rebuild": "rebuild",
    "strict-replay": "strict-replay",
    "token-burn": "token-burn",
    "tamper": "tamper",
}


def emit(obj: dict[str, Any], pretty: bool) -> None:
    emit_json(obj, pretty=pretty)


def run(command: str, *, pretty: bool) -> int:
    mode = MODES[command]
    result = certify.run(mode)
    return finish(result, pretty)


def rebuild(*, pretty: bool, cached_source: bool = False) -> int:
    regen_info = certify.maybe_regenerate(
        "rebuild",
        pretty,
        True,
        refresh_sources=not cached_source,
    )
    result = certify.run("rebuild")
    result["regeneration"] = regen_info
    return finish(result, pretty)


def refresh_certificate(*, pretty: bool) -> int:
    from src.commands import regen

    certificate = regen.refresh_certificate()
    manifest_entry = regen.refresh_manifest_entry(ROOT / "certificate.json")
    cert_payload, cert_error = read_json_or_error(ROOT / "certificate.json")
    inventory = (
        cert_payload.get("invariant_report_inventory", {})
        if isinstance(cert_payload.get("invariant_report_inventory"), dict)
        else {}
    )
    checks = {
        "certificate_json_valid": cert_error is None,
        "certificate_refresh_scanned_all_reports": certificate.get("invariant_report_count")
        == inventory.get("report_count"),
        "certified_report_count_matches_inventory": certificate.get("certified_invariant_report_count")
        == inventory.get("certified_report_count"),
        "provisional_report_count_matches_inventory": certificate.get("provisional_invariant_report_count")
        == inventory.get("provisional_report_count"),
        "demoted_report_count_matches_inventory": certificate.get("demoted_invariant_report_count")
        == inventory.get("demoted_report_count"),
        "manifest_certificate_entry_updated": manifest_entry.get("manifest_entry_updated") is True,
    }
    result = {
        "schema": "d20.verification.refresh_certificate",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "certificate": certificate,
        "manifest_entry": manifest_entry,
        "errors": [] if all(checks.values()) else [key for key, passed in checks.items() if not passed],
    }
    return finish(result, pretty)


def read_json_or_error(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return {}, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, f"invalid_json: {exc}"
    if not isinstance(payload, dict):
        return {}, "not_object"
    return payload, None


def verify_evidence_index(*, pretty: bool) -> int:
    index, index_error = read_json_or_error(EVIDENCE_INDEX)
    data_index, data_index_error = read_json_or_error(DATA_INDEX)
    entries = index.get("evidence_roots", []) if isinstance(index.get("evidence_roots"), list) else []
    errors: list[str] = []
    if index_error is not None:
        errors.append(f"evidence index unreadable: {index_error}")
    if data_index_error is not None:
        errors.append(f"data registry unreadable: {data_index_error}")
    if index.get("schema") != "d20.evidence.index":
        errors.append("evidence index schema mismatch")

    seen_ids: set[str] = set()
    checked_entries: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("evidence index entry is not an object")
            continue
        entry_id = str(entry.get("id", ""))
        if not entry_id:
            errors.append("evidence index entry missing id")
        elif entry_id in seen_ids:
            errors.append(f"duplicate evidence index id: {entry_id}")
        seen_ids.add(entry_id)

        root_ref = str(entry.get("root", ""))
        entrypoint = entry.get("entrypoint", {})
        entrypoint_ref = str(entrypoint.get("path", "")) if isinstance(entrypoint, dict) else ""
        expected_sha = entrypoint.get("sha256") if isinstance(entrypoint, dict) else None
        root_path = ROOT / root_ref
        entrypoint_path = ROOT / entrypoint_ref
        actual_sha = sha_file(entrypoint_path) if entrypoint_path.exists() else None
        if not root_path.exists():
            errors.append(f"evidence root missing: {root_ref}")
        if not entrypoint_path.exists():
            errors.append(f"evidence entrypoint missing: {entrypoint_ref}")
        if expected_sha and actual_sha and expected_sha != actual_sha:
            errors.append(f"evidence entrypoint hash mismatch: {entrypoint_ref}")
        checked_entries.append(
            {
                "id": entry_id,
                "root": root_ref,
                "entrypoint": entrypoint_ref,
                "entrypoint_sha256": actual_sha,
                "status": entry.get("status"),
            }
        )

    data_domains = data_index.get("domains", {}) if isinstance(data_index.get("domains"), dict) else {}
    planned_layout = data_index.get("planned_layout", {}) if isinstance(data_index.get("planned_layout"), dict) else {}
    cubic_domain = data_domains.get(CUBIC_DATA_DOMAIN)
    cubic_registry_checks = {
        "evidence_index_has_cubic_root": any(
            entry.get("id") == CUBIC_EVIDENCE_ID and entry.get("root") == CUBIC_EVIDENCE_ROOT
            for entry in entries
            if isinstance(entry, dict)
        ),
        "data_registry_has_cubic_domain": isinstance(cubic_domain, dict),
        "data_registry_cubic_path_matches": isinstance(cubic_domain, dict)
        and cubic_domain.get("path") == CUBIC_EVIDENCE_ROOT,
        "data_registry_cubic_target_matches": isinstance(cubic_domain, dict)
        and cubic_domain.get("target_path") == CUBIC_EVIDENCE_ROOT,
        "data_registry_cubic_required_files": isinstance(cubic_domain, dict)
        and {
            "README.md",
            "manifest.json",
            "saturation_certificate_closure_checklist.json",
            "saturation_certificate_jobs.json",
            "saturation_certificate_queue.json",
            "saturation_certificate_queue_audit.json",
            "saturation_certificate_source_audit.json",
            "saturation_certificate_intake_protocol.json",
            "saturation_certificate_status_summary.json",
        }.issubset(
            set(cubic_domain.get("required_files", []))
        ),
        "planned_layout_describes_cubic_root": CUBIC_EVIDENCE_ROOT in planned_layout,
    }
    for check, passed in cubic_registry_checks.items():
        if not passed:
            errors.append(f"cubic registry coherence failed: {check}")

    compiler_entry = next(
        (
            entry
            for entry in entries
            if isinstance(entry, dict) and entry.get("id") == COMPILER_A42_D20_EVIDENCE_ID
        ),
        {},
    )
    compiler_entrypoint = compiler_entry.get("entrypoint", {}) if isinstance(compiler_entry, dict) else {}
    compiler_domain = data_domains.get(COMPILER_A42_D20_DATA_DOMAIN)
    compiler_registry_checks = {
        "evidence_index_has_compiler_a42_d20_root": bool(compiler_entry),
        "compiler_a42_d20_status_matches": isinstance(compiler_entry, dict)
        and compiler_entry.get("status") == COMPILER_A42_D20_STATUS,
        "compiler_a42_d20_root_matches": isinstance(compiler_entry, dict)
        and compiler_entry.get("root") == COMPILER_A42_D20_EVIDENCE_ROOT,
        "compiler_a42_d20_entrypoint_matches": isinstance(compiler_entrypoint, dict)
        and compiler_entrypoint.get("path") == COMPILER_A42_D20_MANIFEST,
        "compiler_a42_d20_manifest_exists": (ROOT / COMPILER_A42_D20_MANIFEST).exists(),
        "data_registry_has_compiler_a42_d20_domain": isinstance(compiler_domain, dict),
        "data_registry_compiler_a42_d20_path_matches": isinstance(compiler_domain, dict)
        and compiler_domain.get("path") == COMPILER_A42_D20_EVIDENCE_ROOT,
        "data_registry_compiler_a42_d20_target_matches": isinstance(compiler_domain, dict)
        and compiler_domain.get("target_path") == COMPILER_A42_D20_EVIDENCE_ROOT,
        "data_registry_compiler_a42_d20_required_files": isinstance(compiler_domain, dict)
        and {
            "CORE.lock.json",
            "manifest.json",
            "report.json",
            "support_coordinates.json",
            "positive/TURN.lock.json",
            "positive/08_residue_ledger.json",
            "missing_coordinate/08_residue_ledger.json",
            "tampered_coordinate/04_support_ledger.json",
        }.issubset(set(compiler_domain.get("required_files", []))),
        "planned_layout_describes_compiler_a42_d20_root": COMPILER_A42_D20_EVIDENCE_ROOT
        in planned_layout,
    }
    for check, passed in compiler_registry_checks.items():
        if not passed:
            errors.append(f"compiler A42/D20 registry coherence failed: {check}")

    token_entry = next(
        (
            entry
            for entry in entries
            if isinstance(entry, dict) and entry.get("id") == TOKEN_BURN_EVIDENCE_ID
        ),
        {},
    )
    token_entrypoint = token_entry.get("entrypoint", {}) if isinstance(token_entry, dict) else {}
    token_registry_checks = {
        "evidence_index_has_token_burn_root": bool(token_entry),
        "token_burn_status_matches": isinstance(token_entry, dict)
        and token_entry.get("status") == TOKEN_BURN_STATUS,
        "token_burn_entrypoint_matches": isinstance(token_entrypoint, dict)
        and token_entrypoint.get("path") == TOKEN_BURN_CERTIFICATE,
        "token_burn_certificate_exists": (ROOT / TOKEN_BURN_CERTIFICATE).exists(),
    }
    for check, passed in token_registry_checks.items():
        if not passed:
            errors.append(f"token-burn registry coherence failed: {check}")

    talagrand_domain = data_domains.get(TALAGRAND_DATA_DOMAIN)
    talagrand_entry = next(
        (
            entry
            for entry in entries
            if isinstance(entry, dict) and entry.get("id") == TALAGRAND_EVIDENCE_ID
        ),
        {},
    )
    talagrand_entrypoint = talagrand_entry.get("entrypoint", {}) if isinstance(talagrand_entry, dict) else {}
    talagrand_registry_checks = {
        "evidence_index_has_talagrand_root": bool(talagrand_entry),
        "talagrand_status_matches": isinstance(talagrand_entry, dict)
        and talagrand_entry.get("status") == TALAGRAND_STATUS,
        "talagrand_root_matches": isinstance(talagrand_entry, dict)
        and talagrand_entry.get("root") == TALAGRAND_EVIDENCE_ROOT,
        "talagrand_entrypoint_matches": isinstance(talagrand_entrypoint, dict)
        and talagrand_entrypoint.get("path") == TALAGRAND_MANIFEST,
        "talagrand_manifest_exists": (ROOT / TALAGRAND_MANIFEST).exists(),
        "data_registry_has_talagrand_domain": isinstance(talagrand_domain, dict),
        "data_registry_talagrand_path_matches": isinstance(talagrand_domain, dict)
        and talagrand_domain.get("path") == TALAGRAND_EVIDENCE_ROOT,
        "data_registry_talagrand_target_matches": isinstance(talagrand_domain, dict)
        and talagrand_domain.get("target_path") == TALAGRAND_EVIDENCE_ROOT,
        "data_registry_talagrand_required_files": isinstance(talagrand_domain, dict)
        and {"README_HANDOFF.md", "RUN_ORDER.md", "STATUS_LEDGER.json", "MANIFEST.csv", "manifest.json"}.issubset(
            set(talagrand_domain.get("required_files", []))
        ),
        "planned_layout_describes_talagrand_root": TALAGRAND_EVIDENCE_ROOT in planned_layout,
    }
    for check, passed in talagrand_registry_checks.items():
        if not passed:
            errors.append(f"talagrand handoff registry coherence failed: {check}")

    result = {
        "schema": "d20.verification.evidence_index",
        "status": "PASS" if not errors else "FAIL",
        "data_registry": str(DATA_INDEX.relative_to(ROOT).as_posix()),
        "cubic_registry_checks": cubic_registry_checks,
        "compiler_a42_d20_registry_checks": compiler_registry_checks,
        "token_burn_registry_checks": token_registry_checks,
        "talagrand_registry_checks": talagrand_registry_checks,
        "index": str(EVIDENCE_INDEX.relative_to(ROOT).as_posix()),
        "entry_count": len(entries),
        "checked_entries": checked_entries,
        "errors": errors,
    }
    return finish(result, pretty)


def compiler_a42_d20_replay(*, pretty: bool) -> int:
    from src.compiler.common import sha256_json
    from src.compiler_a42_d20_replay_test import (
        LOCK_FILE,
        MANIFEST,
        REPORT,
        STAGING_ROOT,
        STATUS,
        build_manifest,
        run_test,
    )

    generated_error = None
    try:
        generated_report = run_test()
    except Exception as exc:
        generated_report = {"status": "FAIL"}
        generated_error = f"{type(exc).__name__}: {exc}"
    report_payload, report_error = read_json_or_error(REPORT)
    manifest_payload, manifest_error = read_json_or_error(MANIFEST)
    report_body = {key: value for key, value in report_payload.items() if key != "certificate_sha256"}
    manifest_body = {key: value for key, value in manifest_payload.items() if key != "manifest_sha256"}
    expected_manifest = build_manifest(report_payload) if report_error is None else {}
    checks_payload = (
        manifest_payload.get("checks", {}) if isinstance(manifest_payload.get("checks"), dict) else {}
    )
    promotion = (
        manifest_payload.get("promotion", {}) if isinstance(manifest_payload.get("promotion"), dict) else {}
    )
    checks = {
        "test_report_generated": generated_report.get("status") == "PASS",
        "report_written": REPORT.exists(),
        "report_json_valid": report_error is None,
        "report_matches_generated_payload": report_payload == generated_report,
        "report_hash_matches_payload": report_payload.get("certificate_sha256") == sha256_json(report_body),
        "manifest_written": MANIFEST.exists(),
        "manifest_json_valid": manifest_error is None,
        "manifest_matches_report": manifest_payload == expected_manifest,
        "manifest_hash_matches_payload": manifest_payload.get("manifest_sha256") == sha256_json(manifest_body),
        "manifest_status_certified": manifest_payload.get("status") == STATUS,
        "manifest_declares_locked_staging_promotion": promotion.get("method")
        == "locked_staging_then_file_replace"
        and promotion.get("lock_file") == str(LOCK_FILE.relative_to(ROOT).as_posix())
        and promotion.get("manifest_promoted_last") is True,
        "write_lock_released": not LOCK_FILE.exists(),
        "staging_directory_clear": not STAGING_ROOT.exists() or not any(STAGING_ROOT.iterdir()),
        "positive_a42_d20_coordinate_replay_passed": checks_payload.get(
            "positive_a42_d20_coordinate_replay"
        )
        is True,
        "missing_coordinate_blocks_passed": checks_payload.get("missing_coordinate_blocks") is True,
        "tampered_coordinate_fails_replay_passed": checks_payload.get(
            "tampered_coordinate_fails_replay"
        )
        is True,
    }
    result = {
        "schema": "d20.verification.compiler_a42_d20_replay",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "generated_error": generated_error,
        "report": str(REPORT.relative_to(ROOT).as_posix()),
        "report_error": report_error,
        "manifest": str(MANIFEST.relative_to(ROOT).as_posix()),
        "manifest_error": manifest_error,
        "positive": generated_report.get("checks", {}).get("positive_a42_d20_coordinate_replay"),
        "missing_coordinate": generated_report.get("checks", {}).get("missing_coordinate_blocks"),
        "tampered_coordinate": generated_report.get("checks", {}).get("tampered_coordinate_fails_replay"),
    }
    return finish(result, pretty)


def compiler_scene_selftest(*, pretty: bool) -> int:
    from src.compiler.scene_compiler import run_scene_selftest

    selftest = run_scene_selftest()
    checks_payload = selftest.get("checks", {}) if isinstance(selftest.get("checks"), dict) else {}
    verification = selftest.get("verification", {}) if isinstance(selftest.get("verification"), dict) else {}
    checks = {
        "selftest_passes": selftest.get("status") == "PASS",
        "d20_boundary_present": checks_payload.get("d20_boundary") is True,
        "scene_ir_schema_present": checks_payload.get("scene_ir_schema") is True,
        "source_hash_present": checks_payload.get("has_source_hash") is True,
        "observation_ledger_present": checks_payload.get("has_observation_ledger") is True,
        "admission_ledger_present": checks_payload.get("has_admission_ledger") is True,
        "receipt_ledger_present": checks_payload.get("has_receipt_ledger") is True,
        "verify_scene_passes": verification.get("status") == "PASS",
        "verify_scene_promotes_claims": int(verification.get("promoted_claim_count", 0)) > 0,
        "no_pending_claims": int(verification.get("pending_claim_count", 0)) == 0,
    }
    result = {
        "schema": "d20.verification.compiler_scene_selftest",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "program_hash": selftest.get("program_hash"),
        "summary": selftest.get("summary"),
        "verification_status": verification.get("status"),
        "promoted_claim_count": verification.get("promoted_claim_count"),
        "pending_claim_count": verification.get("pending_claim_count"),
    }
    return finish(result, pretty)


def talagrand_handoff(*, pretty: bool) -> int:
    from src.verify_talagrand_handoff import validate_manifest

    return finish(validate_manifest(), pretty)


def talagrand_kkt_obligation(*, pretty: bool) -> int:
    from src.certify_d20_talagrand_multilevel_kkt_obstruction_system import (
        validate_d20_talagrand_multilevel_kkt_obstruction_system,
    )

    return finish(validate_d20_talagrand_multilevel_kkt_obstruction_system(), pretty)


def talagrand_chain_audit(*, pretty: bool) -> int:
    from src.certify_d20_talagrand_closure_chain_audit import (
        validate_d20_talagrand_closure_chain_audit,
    )

    return finish(validate_d20_talagrand_closure_chain_audit(), pretty)


def jacobian_cubic_cache(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import verify_saturation_cache

    verification = verify_saturation_cache()
    indexed_contract = verification.get("indexed_contract")
    indexed_manifest = verification.get("indexed_manifest")
    cache_manifest = verification.get("manifest_file")
    errors = verification.get("errors", [])
    missing_certificate_count = sum(
        1 for error in errors if isinstance(error, dict) and error.get("check") == "cache_present"
    )
    checks = {
        "cache_verifier_passed": verification.get("status") == "PASS",
        "expected_certificate_count_is_48": verification.get("expected_certificate_count") == 48,
        "verified_certificate_count_is_48": verification.get("verified_certificate_count") == 48,
        "no_extra_cache_files": not verification.get("extra_cache_files"),
        "no_cache_errors": not errors,
        "cache_manifest_written": bool(cache_manifest) and (ROOT / str(cache_manifest)).exists(),
        "indexed_contract_written": bool(indexed_contract) and (ROOT / str(indexed_contract)).exists(),
        "indexed_manifest_status_matches_cache_status": verification.get("indexed_manifest_written") is True
        and verification.get("indexed_manifest_sha256") is not None,
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_saturation_cache",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "cache_directory": verification.get("cache_directory"),
        "cache_manifest": cache_manifest,
        "cache_manifest_sha256": verification.get("manifest_sha256"),
        "error_count": len(errors),
        "first_errors": errors[:5],
        "indexed_contract": indexed_contract,
        "indexed_contract_sha256": verification.get("indexed_contract_sha256"),
        "indexed_manifest": indexed_manifest,
        "indexed_manifest_sha256": verification.get("indexed_manifest_sha256"),
        "missing_certificate_count": missing_certificate_count,
        "promoted_certificate_count": verification.get("promoted_certificate_count"),
        "promotion_requested": verification.get("promotion_requested"),
        "staging_cache_directory": verification.get("staging_cache_directory"),
        "verified_certificate_count": verification.get("verified_certificate_count"),
    }
    return finish(result, pretty)


def jacobian_cubic_contract(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import (
        CERTIFICATE_JOB_PLAN,
        CERTIFICATE_QUEUE,
        CERTIFICATE_QUEUE_AUDIT,
        CERTIFICATE_SOURCE_AUDIT,
        CERTIFICATE_INTAKE_PROTOCOL,
        CERTIFICATE_CLOSURE_CHECKLIST,
        CERTIFICATE_STATUS_SUMMARY,
        EVIDENCE_MANIFEST,
        EVIDENCE_README,
        INDEXED_CACHE_CONTRACT,
        expected_saturation_cache_specs,
        saturation_certificate_job_plan,
        saturation_certificate_intake_protocol,
        saturation_certificate_queue,
        saturation_certificate_source_audit,
        saturation_cache_contract,
        saturation_closure_checklist,
        saturation_evidence_manifest,
        saturation_queue_audit,
        saturation_status_summary,
        sha_json,
    )

    specs = expected_saturation_cache_specs()
    expected_contract = saturation_cache_contract(specs)
    input_hashes = [spec["input_sha256"] for spec in specs]
    contract_payload, contract_error = read_json_or_error(INDEXED_CACHE_CONTRACT)
    contract_body = {key: value for key, value in contract_payload.items() if key != "contract_sha256"}
    expected_evidence_manifest = saturation_evidence_manifest(expected_contract)
    evidence_manifest_payload, evidence_manifest_error = read_json_or_error(EVIDENCE_MANIFEST)
    evidence_manifest_body = {
        key: value for key, value in evidence_manifest_payload.items() if key != "manifest_sha256"
    }
    expected_job_plan = saturation_certificate_job_plan(expected_contract)
    job_plan_payload, job_plan_error = read_json_or_error(CERTIFICATE_JOB_PLAN)
    job_plan_body = {key: value for key, value in job_plan_payload.items() if key != "job_plan_sha256"}
    job_plan_jobs = job_plan_payload.get("jobs", []) if isinstance(job_plan_payload.get("jobs"), list) else []
    expected_queue = saturation_certificate_queue(expected_contract)
    queue_payload, queue_error = read_json_or_error(CERTIFICATE_QUEUE)
    queue_body = {key: value for key, value in queue_payload.items() if key != "queue_sha256"}
    queue_jobs = queue_payload.get("jobs", []) if isinstance(queue_payload.get("jobs"), list) else []
    queue_policy = (
        queue_payload.get("queue_policy", {}) if isinstance(queue_payload.get("queue_policy"), dict) else {}
    )
    expected_queue_audit = saturation_queue_audit(
        expected_contract,
        queue_payload=queue_payload,
        queue_error=queue_error,
    )
    queue_audit_payload, queue_audit_error = read_json_or_error(CERTIFICATE_QUEUE_AUDIT)
    queue_audit_body = {
        key: value for key, value in queue_audit_payload.items() if key != "audit_sha256"
    }
    queue_audit_checks = (
        queue_audit_payload.get("checks", {})
        if isinstance(queue_audit_payload.get("checks"), dict)
        else {}
    )
    expected_source_audit = saturation_certificate_source_audit(expected_contract)
    source_audit_payload, source_audit_error = read_json_or_error(CERTIFICATE_SOURCE_AUDIT)
    source_audit_body = {
        key: value for key, value in source_audit_payload.items() if key != "audit_sha256"
    }
    source_audit_checks = (
        source_audit_payload.get("checks", {})
        if isinstance(source_audit_payload.get("checks"), dict)
        else {}
    )
    source_audit_counts = (
        source_audit_payload.get("counts", {})
        if isinstance(source_audit_payload.get("counts"), dict)
        else {}
    )
    expected_intake_protocol = saturation_certificate_intake_protocol(expected_contract)
    intake_protocol_payload, intake_protocol_error = read_json_or_error(CERTIFICATE_INTAKE_PROTOCOL)
    intake_protocol_body = {
        key: value for key, value in intake_protocol_payload.items() if key != "protocol_sha256"
    }
    intake_protocol_checks = (
        intake_protocol_payload.get("checks", {})
        if isinstance(intake_protocol_payload.get("checks"), dict)
        else {}
    )
    intake_transitions = (
        intake_protocol_payload.get("transitions", [])
        if isinstance(intake_protocol_payload.get("transitions"), list)
        else []
    )
    expected_closure_checklist = saturation_closure_checklist(expected_contract)
    closure_checklist_payload, closure_checklist_error = read_json_or_error(CERTIFICATE_CLOSURE_CHECKLIST)
    closure_checklist_body = {
        key: value for key, value in closure_checklist_payload.items() if key != "checklist_sha256"
    }
    closure_checklist_checks = (
        closure_checklist_payload.get("checks", {})
        if isinstance(closure_checklist_payload.get("checks"), dict)
        else {}
    )
    closure_levels = (
        closure_checklist_payload.get("levels", {})
        if isinstance(closure_checklist_payload.get("levels"), dict)
        else {}
    )
    expected_status_summary = saturation_status_summary(expected_contract)
    status_summary_payload, status_summary_error = read_json_or_error(CERTIFICATE_STATUS_SUMMARY)
    status_summary_body = {
        key: value for key, value in status_summary_payload.items() if key != "status_summary_sha256"
    }
    status_summary_checks = (
        status_summary_payload.get("checks", {})
        if isinstance(status_summary_payload.get("checks"), dict)
        else {}
    )
    status_summary_counts = (
        status_summary_payload.get("counts", {})
        if isinstance(status_summary_payload.get("counts"), dict)
        else {}
    )
    single_job_lookup = (
        job_plan_payload.get("single_job_lookup", {})
        if isinstance(job_plan_payload.get("single_job_lookup"), dict)
        else {}
    )
    single_job_producer = (
        job_plan_payload.get("single_job_producer", {})
        if isinstance(job_plan_payload.get("single_job_producer"), dict)
        else {}
    )
    single_job_verification = (
        job_plan_payload.get("single_job_verification", {})
        if isinstance(job_plan_payload.get("single_job_verification"), dict)
        else {}
    )
    batch_job_status = (
        job_plan_payload.get("batch_job_status", {})
        if isinstance(job_plan_payload.get("batch_job_status"), dict)
        else {}
    )
    checks = {
        "expected_certificate_count_is_48": len(specs) == 48,
        "input_hashes_are_unique": len(set(input_hashes)) == len(input_hashes),
        "contract_manifest_written": INDEXED_CACHE_CONTRACT.exists(),
        "contract_manifest_json_valid": contract_error is None,
        "contract_payload_matches_current_specs": contract_payload == expected_contract,
        "contract_hash_matches_payload": contract_payload.get("contract_sha256") == sha_json(contract_body),
        "certificate_job_plan_written": CERTIFICATE_JOB_PLAN.exists(),
        "certificate_job_plan_json_valid": job_plan_error is None,
        "certificate_job_plan_matches_current_contract": job_plan_payload == expected_job_plan,
        "certificate_job_plan_hash_matches_payload": job_plan_payload.get("job_plan_sha256")
        == sha_json(job_plan_body),
        "certificate_job_plan_declares_single_job_lookup": bool(single_job_lookup.get("command")),
        "certificate_job_plan_lookup_is_non_running": single_job_lookup.get("runs_expensive_computation") is False,
        "certificate_jobs_have_lookup_commands": len(job_plan_jobs) == 48
        and all(isinstance(job, dict) and bool(job.get("lookup_command")) for job in job_plan_jobs),
        "certificate_job_plan_declares_single_job_producer": bool(single_job_producer.get("command")),
        "certificate_job_plan_producer_is_plan_only_by_default": single_job_producer.get(
            "runs_expensive_computation_by_default"
        )
        is False,
        "certificate_job_plan_producer_has_explicit_run_flag": single_job_producer.get("explicit_run_flag")
        == "--run-saturation-job",
        "certificate_jobs_have_produce_plan_commands": len(job_plan_jobs) == 48
        and all(isinstance(job, dict) and bool(job.get("produce_plan_command")) for job in job_plan_jobs),
        "certificate_job_plan_declares_single_job_verification": bool(single_job_verification.get("command")),
        "certificate_job_plan_verification_is_non_running": single_job_verification.get(
            "runs_expensive_computation"
        )
        is False,
        "certificate_job_plan_verifies_existing_cache_only": single_job_verification.get(
            "validates_existing_cache_only"
        )
        is True,
        "certificate_jobs_have_verify_commands": len(job_plan_jobs) == 48
        and all(isinstance(job, dict) and bool(job.get("verify_command")) for job in job_plan_jobs),
        "certificate_queue_written": CERTIFICATE_QUEUE.exists(),
        "certificate_queue_json_valid": queue_error is None,
        "certificate_queue_matches_current_status": queue_payload == expected_queue,
        "certificate_queue_hash_matches_payload": queue_payload.get("queue_sha256") == sha_json(queue_body),
        "certificate_queue_is_non_running": queue_payload.get("runs_expensive_computation") is False,
        "certificate_queue_has_48_jobs": len(queue_jobs) == 48,
        "certificate_queue_declares_next_job": isinstance(queue_payload.get("next_job"), dict)
        or queue_payload.get("status") == "READY_FOR_STRICT_CACHE",
        "certificate_queue_requires_explicit_run_flag": queue_policy.get("run_requires_explicit_flag")
        == "--run-saturation-job",
        "certificate_queue_jobs_have_plan_run_verify_commands": len(queue_jobs) == 48
        and all(
            isinstance(job, dict)
            and bool(job.get("plan_command"))
            and bool(job.get("run_command"))
            and bool(job.get("verify_command"))
            for job in queue_jobs
        ),
        "certificate_queue_audit_written": CERTIFICATE_QUEUE_AUDIT.exists(),
        "certificate_queue_audit_json_valid": queue_audit_error is None,
        "certificate_queue_audit_matches_current_queue": queue_audit_payload == expected_queue_audit,
        "certificate_queue_audit_hash_matches_payload": queue_audit_payload.get("audit_sha256")
        == sha_json(queue_audit_body),
        "certificate_queue_audit_passes": queue_audit_payload.get("status") == "PASS",
        "certificate_queue_audit_is_non_running": queue_audit_payload.get("runs_expensive_computation")
        is False,
        "certificate_queue_audit_checks_monotonicity": queue_audit_checks.get("queue_positions_are_contiguous")
        is True
        and queue_audit_checks.get("job_ids_are_contiguous") is True,
        "certificate_queue_audit_checks_command_guards": queue_audit_checks.get("plan_commands_are_plan_only")
        is True
        and queue_audit_checks.get("run_commands_are_explicitly_guarded") is True
        and queue_audit_checks.get("verify_commands_are_non_producing") is True,
        "certificate_source_audit_written": CERTIFICATE_SOURCE_AUDIT.exists(),
        "certificate_source_audit_json_valid": source_audit_error is None,
        "certificate_source_audit_matches_current_sources": source_audit_payload == expected_source_audit,
        "certificate_source_audit_hash_matches_payload": source_audit_payload.get("audit_sha256")
        == sha_json(source_audit_body),
        "certificate_source_audit_passes": source_audit_payload.get("status") == "PASS",
        "certificate_source_audit_is_non_running": source_audit_payload.get("runs_expensive_computation")
        is False,
        "certificate_source_audit_distinguishes_sources": source_audit_checks.get(
            "staging_promotion_distinguished_from_missing"
        )
        is True
        and source_audit_checks.get("source_paths_are_distinct") is True,
        "certificate_source_audit_counts_cover_jobs": source_audit_checks.get("counts_partition_jobs")
        is True
        and source_audit_counts.get("produce_needed", 0)
        + source_audit_counts.get("promotion_ready", 0)
        + source_audit_counts.get("invalid_present", 0)
        + source_audit_counts.get("stable_verified", 0)
        == 48,
        "certificate_source_audit_checks_safe_commands": source_audit_checks.get("plan_commands_are_non_running")
        is True
        and source_audit_checks.get("run_commands_are_guarded") is True
        and source_audit_checks.get("verify_commands_are_non_producing") is True
        and source_audit_checks.get("promotion_command_is_non_recomputing") is True,
        "certificate_intake_protocol_written": CERTIFICATE_INTAKE_PROTOCOL.exists(),
        "certificate_intake_protocol_json_valid": intake_protocol_error is None,
        "certificate_intake_protocol_matches_current_artifacts": intake_protocol_payload
        == expected_intake_protocol,
        "certificate_intake_protocol_hash_matches_payload": intake_protocol_payload.get("protocol_sha256")
        == sha_json(intake_protocol_body),
        "certificate_intake_protocol_passes": intake_protocol_payload.get("status") == "PASS",
        "certificate_intake_protocol_is_non_running": intake_protocol_payload.get("runs_expensive_computation")
        is False,
        "certificate_intake_protocol_declares_run_guard": intake_protocol_checks.get(
            "single_job_run_requires_explicit_flag"
        )
        is True
        and intake_protocol_checks.get("single_job_run_writes_stable_cache") is True,
        "certificate_intake_protocol_declares_staging_promotion": intake_protocol_checks.get(
            "staging_promotion_path_declared"
        )
        is True
        and any(
            isinstance(transition, dict)
            and transition.get("name") == "verified_staging_source_to_stable_candidate"
            for transition in intake_transitions
        ),
        "certificate_intake_protocol_declares_strict_gate": intake_protocol_checks.get(
            "strict_cache_requires_48_verified"
        )
        is True
        and any(
            isinstance(transition, dict)
            and transition.get("name") == "verified_jobs_to_strict_cache"
            for transition in intake_transitions
        ),
        "certificate_intake_protocol_non_running_commands_are_safe": intake_protocol_checks.get(
            "non_running_commands_are_guarded"
        )
        is True,
        "certificate_closure_checklist_written": CERTIFICATE_CLOSURE_CHECKLIST.exists(),
        "certificate_closure_checklist_json_valid": closure_checklist_error is None,
        "certificate_closure_checklist_matches_current_artifacts": closure_checklist_payload
        == expected_closure_checklist,
        "certificate_closure_checklist_hash_matches_payload": closure_checklist_payload.get("checklist_sha256")
        == sha_json(closure_checklist_body),
        "certificate_closure_checklist_passes": closure_checklist_payload.get("status") == "PASS",
        "certificate_closure_checklist_is_non_running": closure_checklist_payload.get("runs_expensive_computation")
        is False,
        "certificate_closure_checklist_declares_three_levels": {
            "provisional_integrated",
            "intake_ready",
            "strict_certified",
        }.issubset(set(closure_levels)),
        "certificate_closure_checklist_lists_required_verifiers": closure_checklist_checks.get(
            "provisional_lists_contract_and_index"
        )
        is True
        and closure_checklist_checks.get("intake_ready_lists_focused_intake_verifier") is True
        and closure_checklist_checks.get("strict_certified_lists_strict_cache_verifier") is True,
        "certificate_status_summary_written": CERTIFICATE_STATUS_SUMMARY.exists(),
        "certificate_status_summary_json_valid": status_summary_error is None,
        "certificate_status_summary_matches_current_status": status_summary_payload
        == expected_status_summary,
        "certificate_status_summary_hash_matches_payload": status_summary_payload.get(
            "status_summary_sha256"
        )
        == sha_json(status_summary_body),
        "certificate_status_summary_passes": status_summary_payload.get("status") == "PASS",
        "certificate_status_summary_is_non_running": status_summary_payload.get(
            "runs_expensive_computation"
        )
        is False,
        "certificate_status_summary_declares_gates": status_summary_payload.get("recommended_verifier")
        == "python src/verify.py jacobian-cubic-nonstrict --pretty"
        and status_summary_payload.get("strict_verifier")
        == "python src/verify.py jacobian-cubic-cache --pretty",
        "certificate_status_summary_counts_cover_jobs": status_summary_checks.get(
            "counts_cover_48_jobs"
        )
        is True
        and status_summary_counts.get("stable_verified", 0)
        + status_summary_counts.get("promotion_ready", 0)
        + status_summary_counts.get("invalid_present", 0)
        + status_summary_counts.get("produce_needed", 0)
        == 48,
        "certificate_job_plan_declares_batch_status": bool(batch_job_status.get("command")),
        "certificate_job_plan_declares_batch_status_summary": bool(batch_job_status.get("summary_command")),
        "certificate_job_plan_batch_status_is_non_running": batch_job_status.get("runs_expensive_computation")
        is False,
        "certificate_job_plan_batch_status_uses_existing_cache_only": batch_job_status.get(
            "validates_existing_cache_only"
        )
        is True,
        "evidence_manifest_written": EVIDENCE_MANIFEST.exists(),
        "evidence_manifest_json_valid": evidence_manifest_error is None,
        "evidence_manifest_matches_current_contract": evidence_manifest_payload == expected_evidence_manifest,
        "evidence_manifest_hash_matches_payload": evidence_manifest_payload.get("manifest_sha256")
        == sha_json(evidence_manifest_body),
        "evidence_readme_written": EVIDENCE_README.exists(),
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_saturation_cache_contract",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "contract_manifest": str(INDEXED_CACHE_CONTRACT.relative_to(ROOT).as_posix()),
        "contract_manifest_error": contract_error,
        "contract_sha256": expected_contract.get("contract_sha256"),
        "certificate_job_plan": str(CERTIFICATE_JOB_PLAN.relative_to(ROOT).as_posix()),
        "certificate_job_plan_error": job_plan_error,
        "certificate_job_plan_sha256": expected_job_plan.get("job_plan_sha256"),
        "certificate_queue": str(CERTIFICATE_QUEUE.relative_to(ROOT).as_posix()),
        "certificate_queue_error": queue_error,
        "certificate_queue_sha256": expected_queue.get("queue_sha256"),
        "certificate_queue_audit": str(CERTIFICATE_QUEUE_AUDIT.relative_to(ROOT).as_posix()),
        "certificate_queue_audit_error": queue_audit_error,
        "certificate_queue_audit_sha256": expected_queue_audit.get("audit_sha256"),
        "certificate_source_audit": str(CERTIFICATE_SOURCE_AUDIT.relative_to(ROOT).as_posix()),
        "certificate_source_audit_error": source_audit_error,
        "certificate_source_audit_sha256": expected_source_audit.get("audit_sha256"),
        "certificate_intake_protocol": str(CERTIFICATE_INTAKE_PROTOCOL.relative_to(ROOT).as_posix()),
        "certificate_intake_protocol_error": intake_protocol_error,
        "certificate_intake_protocol_sha256": expected_intake_protocol.get("protocol_sha256"),
        "certificate_closure_checklist": str(CERTIFICATE_CLOSURE_CHECKLIST.relative_to(ROOT).as_posix()),
        "certificate_closure_checklist_error": closure_checklist_error,
        "certificate_closure_checklist_sha256": expected_closure_checklist.get("checklist_sha256"),
        "certificate_status_summary": str(CERTIFICATE_STATUS_SUMMARY.relative_to(ROOT).as_posix()),
        "certificate_status_summary_error": status_summary_error,
        "certificate_status_summary_sha256": expected_status_summary.get("status_summary_sha256"),
        "evidence_manifest": str(EVIDENCE_MANIFEST.relative_to(ROOT).as_posix()),
        "evidence_manifest_error": evidence_manifest_error,
        "evidence_manifest_sha256": expected_evidence_manifest.get("manifest_sha256"),
        "evidence_readme": str(EVIDENCE_README.relative_to(ROOT).as_posix()),
        "expected_certificate_count": len(specs),
    }
    return finish(result, pretty)


def jacobian_cubic_intake(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import (
        CERTIFICATE_INTAKE_PROTOCOL,
        CERTIFICATE_QUEUE,
        CERTIFICATE_SOURCE_AUDIT,
        expected_saturation_cache_specs,
        saturation_cache_contract,
        saturation_certificate_intake_protocol,
        sha_json,
    )

    specs = expected_saturation_cache_specs()
    expected_contract = saturation_cache_contract(specs)
    expected_protocol = saturation_certificate_intake_protocol(expected_contract)
    protocol_payload, protocol_error = read_json_or_error(CERTIFICATE_INTAKE_PROTOCOL)
    protocol_body = {
        key: value for key, value in protocol_payload.items() if key != "protocol_sha256"
    }
    commands = protocol_payload.get("commands", {}) if isinstance(protocol_payload.get("commands"), dict) else {}
    checks_payload = (
        protocol_payload.get("checks", {}) if isinstance(protocol_payload.get("checks"), dict) else {}
    )
    transitions = (
        protocol_payload.get("transitions", []) if isinstance(protocol_payload.get("transitions"), list) else []
    )
    transition_names = {
        transition.get("name")
        for transition in transitions
        if isinstance(transition, dict)
    }
    required_transition_names = {
        "declared_to_planned",
        "planned_to_stable_candidate",
        "staging_candidate_to_verified_source",
        "verified_staging_source_to_stable_candidate",
        "stable_candidate_to_verified_job",
        "verified_jobs_to_strict_cache",
    }
    required_command_names = {
        "inspect_job",
        "plan_job",
        "run_one_job",
        "verify_job",
        "audit_sources",
        "promote_staging",
        "strict_cache",
    }
    non_running_command_names = required_command_names - {"run_one_job"}
    non_running_commands = [str(commands.get(name, "")) for name in non_running_command_names]
    run_command = str(commands.get("run_one_job", ""))
    strict_transition = next(
        (
            transition
            for transition in transitions
            if isinstance(transition, dict) and transition.get("name") == "verified_jobs_to_strict_cache"
        ),
        {},
    )
    staging_transition = next(
        (
            transition
            for transition in transitions
            if isinstance(transition, dict)
            and transition.get("name") == "verified_staging_source_to_stable_candidate"
        ),
        {},
    )
    artifacts = protocol_payload.get("artifacts", {}) if isinstance(protocol_payload.get("artifacts"), dict) else {}
    current_state = (
        protocol_payload.get("current_state", {})
        if isinstance(protocol_payload.get("current_state"), dict)
        else {}
    )
    source_counts = (
        current_state.get("source_counts", {}) if isinstance(current_state.get("source_counts"), dict) else {}
    )
    checks = {
        "expected_certificate_count_is_48": len(specs) == 48,
        "protocol_written": CERTIFICATE_INTAKE_PROTOCOL.exists(),
        "protocol_json_valid": protocol_error is None,
        "protocol_matches_current_artifacts": protocol_payload == expected_protocol,
        "protocol_hash_matches_payload": protocol_payload.get("protocol_sha256") == sha_json(protocol_body),
        "protocol_status_passes": protocol_payload.get("status") == "PASS",
        "protocol_is_non_running": protocol_payload.get("runs_expensive_computation") is False,
        "declares_required_commands": required_command_names.issubset(set(commands)),
        "non_running_commands_are_guarded": all(
            "--run-saturation-job" not in command and "--recompute-saturations" not in command
            for command in non_running_commands
        ),
        "run_command_requires_explicit_flag": "--run-saturation-job" in run_command
        and "--recompute-saturations" not in run_command,
        "declares_required_transitions": required_transition_names.issubset(transition_names),
        "staging_promotion_transition_points_to_expected_paths": staging_transition.get("from_directory")
        == "data/evidence/jacobian_cubic_symbolic_elimination/saturation_staging_cache"
        and staging_transition.get("to_directory")
        == "data/evidence/jacobian_cubic_symbolic_elimination/saturation_cache",
        "strict_transition_requires_48_verified": strict_transition.get("requires", {}).get(
            "verified_certificate_count"
        )
        == 48,
        "artifact_dependencies_exist": CERTIFICATE_QUEUE.exists()
        and CERTIFICATE_SOURCE_AUDIT.exists()
        and artifacts.get("stable_cache_directory")
        == "data/evidence/jacobian_cubic_symbolic_elimination/saturation_cache"
        and artifacts.get("staging_source_directory")
        == "data/evidence/jacobian_cubic_symbolic_elimination/saturation_staging_cache",
        "current_state_counts_cover_jobs": source_counts.get("stable_verified", 0)
        + source_counts.get("promotion_ready", 0)
        + source_counts.get("invalid_present", 0)
        + source_counts.get("produce_needed", 0)
        == 48,
        "embedded_checks_pass": all(checks_payload.values()) if checks_payload else False,
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_intake_protocol",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "certificate_intake_protocol": str(CERTIFICATE_INTAKE_PROTOCOL.relative_to(ROOT).as_posix()),
        "certificate_intake_protocol_error": protocol_error,
        "certificate_intake_protocol_sha256": expected_protocol.get("protocol_sha256"),
        "certificate_queue": str(CERTIFICATE_QUEUE.relative_to(ROOT).as_posix()),
        "certificate_source_audit": str(CERTIFICATE_SOURCE_AUDIT.relative_to(ROOT).as_posix()),
        "current_state": current_state,
        "transition_names": sorted(name for name in transition_names if isinstance(name, str)),
    }
    return finish(result, pretty)


def jacobian_cubic_closure(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import (
        CERTIFICATE_CLOSURE_CHECKLIST,
        CERTIFICATE_INTAKE_PROTOCOL,
        CERTIFICATE_SOURCE_AUDIT,
        expected_saturation_cache_specs,
        saturation_cache_contract,
        saturation_closure_checklist,
        sha_json,
    )

    specs = expected_saturation_cache_specs()
    expected_contract = saturation_cache_contract(specs)
    expected_checklist = saturation_closure_checklist(expected_contract)
    checklist_payload, checklist_error = read_json_or_error(CERTIFICATE_CLOSURE_CHECKLIST)
    checklist_body = {
        key: value for key, value in checklist_payload.items() if key != "checklist_sha256"
    }
    checks_payload = (
        checklist_payload.get("checks", {}) if isinstance(checklist_payload.get("checks"), dict) else {}
    )
    levels = checklist_payload.get("levels", {}) if isinstance(checklist_payload.get("levels"), dict) else {}
    current_state = (
        checklist_payload.get("current_state", {})
        if isinstance(checklist_payload.get("current_state"), dict)
        else {}
    )
    source_counts = (
        current_state.get("source_counts", {}) if isinstance(current_state.get("source_counts"), dict) else {}
    )
    provisional = levels.get("provisional_integrated", {}) if isinstance(levels.get("provisional_integrated"), dict) else {}
    intake_ready = levels.get("intake_ready", {}) if isinstance(levels.get("intake_ready"), dict) else {}
    strict_certified = levels.get("strict_certified", {}) if isinstance(levels.get("strict_certified"), dict) else {}
    provisional_verifiers = (
        provisional.get("required_verifiers", []) if isinstance(provisional.get("required_verifiers"), list) else []
    )
    intake_verifiers = (
        intake_ready.get("required_verifiers", []) if isinstance(intake_ready.get("required_verifiers"), list) else []
    )
    strict_verifiers = (
        strict_certified.get("required_verifiers", [])
        if isinstance(strict_certified.get("required_verifiers"), list)
        else []
    )
    checks = {
        "expected_certificate_count_is_48": len(specs) == 48,
        "checklist_written": CERTIFICATE_CLOSURE_CHECKLIST.exists(),
        "checklist_json_valid": checklist_error is None,
        "checklist_matches_current_artifacts": checklist_payload == expected_checklist,
        "checklist_hash_matches_payload": checklist_payload.get("checklist_sha256") == sha_json(checklist_body),
        "checklist_status_passes": checklist_payload.get("status") == "PASS",
        "checklist_is_non_running": checklist_payload.get("runs_expensive_computation") is False,
        "declares_three_closure_levels": {
            "provisional_integrated",
            "intake_ready",
            "strict_certified",
        }.issubset(set(levels)),
        "provisional_level_lists_contract_and_index": {
            "python src/verify.py jacobian-cubic-contract --pretty",
            "python src/verify.py evidence-index --pretty",
        }.issubset(set(provisional_verifiers)),
        "intake_ready_level_lists_intake_and_status": {
            "python src/verify.py jacobian-cubic-intake --pretty",
            "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --saturation-job-status-summary",
        }.issubset(set(intake_verifiers)),
        "strict_level_lists_strict_cache": "python src/verify.py jacobian-cubic-cache --pretty"
        in strict_verifiers,
        "current_counts_cover_48_jobs": source_counts.get("stable_verified", 0)
        + source_counts.get("promotion_ready", 0)
        + source_counts.get("invalid_present", 0)
        + source_counts.get("produce_needed", 0)
        == 48,
        "current_missing_is_explicit": source_counts.get("missing_both", 0)
        == source_counts.get("produce_needed", 0),
        "strict_level_requires_48_stable_verified": strict_certified.get("required_state", {}).get(
            "stable_verified"
        )
        == 48,
        "artifact_dependencies_exist": CERTIFICATE_INTAKE_PROTOCOL.exists() and CERTIFICATE_SOURCE_AUDIT.exists(),
        "embedded_checks_pass": all(checks_payload.values()) if checks_payload else False,
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_closure_checklist",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "certificate_closure_checklist": str(CERTIFICATE_CLOSURE_CHECKLIST.relative_to(ROOT).as_posix()),
        "certificate_closure_checklist_error": checklist_error,
        "certificate_closure_checklist_sha256": expected_checklist.get("checklist_sha256"),
        "current_level": checklist_payload.get("current_level"),
        "current_state": current_state,
        "levels": sorted(level for level in levels if isinstance(level, str)),
    }
    return finish(result, pretty)


def jacobian_cubic_status(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import (
        CERTIFICATE_CLOSURE_CHECKLIST,
        CERTIFICATE_STATUS_SUMMARY,
        expected_saturation_cache_specs,
        saturation_cache_contract,
        saturation_closure_checklist,
        saturation_status_summary,
        sha_json,
    )

    specs = expected_saturation_cache_specs()
    expected_contract = saturation_cache_contract(specs)
    expected_checklist = saturation_closure_checklist(expected_contract)
    checklist_payload, checklist_error = read_json_or_error(CERTIFICATE_CLOSURE_CHECKLIST)
    checklist_body = {
        key: value for key, value in checklist_payload.items() if key != "checklist_sha256"
    }
    expected_summary = saturation_status_summary(expected_contract)
    summary_payload, summary_error = read_json_or_error(CERTIFICATE_STATUS_SUMMARY)
    summary_body = {
        key: value for key, value in summary_payload.items() if key != "status_summary_sha256"
    }
    current_state = (
        checklist_payload.get("current_state", {})
        if isinstance(checklist_payload.get("current_state"), dict)
        else {}
    )
    source_counts = (
        current_state.get("source_counts", {}) if isinstance(current_state.get("source_counts"), dict) else {}
    )
    summary_counts = (
        summary_payload.get("counts", {}) if isinstance(summary_payload.get("counts"), dict) else {}
    )
    next_job = summary_payload.get("next_job") if isinstance(summary_payload.get("next_job"), dict) else None
    stable_verified = int(summary_counts.get("stable_verified", 0))
    promotion_ready = int(summary_counts.get("promotion_ready", 0))
    invalid_present = int(summary_counts.get("invalid_present", 0))
    produce_needed = int(summary_counts.get("produce_needed", 0))
    staging_present = int(summary_counts.get("staging_present", 0))
    stable_present = int(summary_counts.get("stable_present", 0))
    current_level = summary_payload.get("current_level")
    is_strict_counts = (
        stable_verified == 48
        and promotion_ready == 0
        and invalid_present == 0
        and produce_needed == 0
    )
    checks = {
        "expected_certificate_count_is_48": len(specs) == 48,
        "checklist_written": CERTIFICATE_CLOSURE_CHECKLIST.exists(),
        "checklist_json_valid": checklist_error is None,
        "checklist_matches_current_artifacts": checklist_payload == expected_checklist,
        "checklist_hash_matches_payload": checklist_payload.get("checklist_sha256") == sha_json(checklist_body),
        "checklist_status_passes": checklist_payload.get("status") == "PASS",
        "status_summary_written": CERTIFICATE_STATUS_SUMMARY.exists(),
        "status_summary_json_valid": summary_error is None,
        "status_summary_matches_current_status": summary_payload == expected_summary,
        "status_summary_hash_matches_payload": summary_payload.get("status_summary_sha256")
        == sha_json(summary_body),
        "status_summary_status_passes": summary_payload.get("status") == "PASS",
        "status_summary_is_non_running": summary_payload.get("runs_expensive_computation") is False,
        "current_level_known": current_level
        in {"provisional_integrated", "intake_ready", "strict_certified"},
        "summary_level_matches_checklist": current_level == checklist_payload.get("current_level"),
        "summary_counts_match_checklist": summary_counts == {
            "stable_present": int(source_counts.get("stable_present", 0)),
            "staging_present": int(source_counts.get("staging_present", 0)),
            "stable_verified": int(source_counts.get("stable_verified", 0)),
            "promotion_ready": int(source_counts.get("promotion_ready", 0)),
            "invalid_present": int(source_counts.get("invalid_present", 0)),
            "produce_needed": int(source_counts.get("produce_needed", 0)),
            "missing_both": int(source_counts.get("missing_both", 0)),
        },
        "status_summary_declares_gates": summary_payload.get("recommended_verifier")
        == "python src/verify.py jacobian-cubic-nonstrict --pretty"
        and summary_payload.get("strict_verifier") == "python src/verify.py jacobian-cubic-cache --pretty",
        "counts_cover_48_jobs": stable_verified + promotion_ready + invalid_present + produce_needed == 48,
        "strict_level_matches_counts": (current_level == "strict_certified") == is_strict_counts,
        "non_strict_level_has_next_job": current_level == "strict_certified" or isinstance(next_job, dict),
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_status",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "current_level": current_level,
        "counts": {
            "stable_present": stable_present,
            "staging_present": staging_present,
            "stable_verified": stable_verified,
            "promotion_ready": promotion_ready,
            "invalid_present": invalid_present,
            "produce_needed": produce_needed,
            "missing_both": int(source_counts.get("missing_both", 0)),
        },
        "next_job": (
            {
                "job_id": next_job.get("job_id"),
                "label": next_job.get("label"),
                "next_action": next_job.get("next_action"),
                "plan_command": next_job.get("plan_command"),
                "run_command": next_job.get("run_command"),
                "verify_command": next_job.get("verify_command"),
            }
            if isinstance(next_job, dict)
            else None
        ),
        "strict_cache_ready": is_strict_counts,
        "certificate_closure_checklist": str(CERTIFICATE_CLOSURE_CHECKLIST.relative_to(ROOT).as_posix()),
        "certificate_closure_checklist_error": checklist_error,
        "certificate_closure_checklist_sha256": expected_checklist.get("checklist_sha256"),
        "certificate_status_summary": str(CERTIFICATE_STATUS_SUMMARY.relative_to(ROOT).as_posix()),
        "certificate_status_summary_error": summary_error,
        "certificate_status_summary_sha256": expected_summary.get("status_summary_sha256"),
    }
    return finish(result, pretty)


def run_verify_subcommand(command: str) -> dict[str, Any]:
    commands = {
        "evidence-index": lambda: verify_evidence_index(pretty=False),
        "compiler-scene-selftest": lambda: compiler_scene_selftest(pretty=False),
        "compiler-a42-d20-replay": lambda: compiler_a42_d20_replay(pretty=False),
        "compiler-nonstrict": lambda: compiler_nonstrict(pretty=False),
        "integration-nonstrict": lambda: integration_nonstrict(pretty=False),
        "jacobian-cubic-status": lambda: jacobian_cubic_status(pretty=False),
        "jacobian-cubic-intake": lambda: jacobian_cubic_intake(pretty=False),
        "jacobian-cubic-closure": lambda: jacobian_cubic_closure(pretty=False),
        "jacobian-cubic-nonstrict": lambda: jacobian_cubic_nonstrict(pretty=False),
    }
    buffer = io.StringIO()
    if command not in commands:
        return {
            "command": f"python src/verify.py {command}",
            "exit_code": 1,
            "status": "FAIL",
            "payload": {
                "schema": "d20.verification.unknown_subcommand",
                "status": "FAIL",
                "error": f"unsupported non-strict subcommand: {command}",
            },
        }
    try:
        with contextlib.redirect_stdout(buffer):
            exit_code = commands[command]()
    except Exception as exc:
        return {
            "command": f"python src/verify.py {command}",
            "exit_code": 1,
            "status": "FAIL",
            "payload": {
                "schema": "d20.verification.subcommand_exception",
                "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}",
            },
        }
    stdout = buffer.getvalue()
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        payload = {
            "schema": "d20.verification.subcommand_unparseable",
            "status": "FAIL",
            "stdout": stdout,
        }
    return {
        "command": f"python src/verify.py {command}",
        "exit_code": exit_code,
        "status": payload.get("status"),
        "payload": payload,
    }


def compiler_nonstrict(*, pretty: bool) -> int:
    included_modes = [
        "compiler-scene-selftest",
        "compiler-a42-d20-replay",
        "evidence-index",
    ]
    excluded_modes = ["jacobian-cubic-cache", "rebuild", "strict-replay"]
    results = [run_verify_subcommand(command) for command in included_modes]
    by_command = {
        result["command"]: {
            "command": result["command"],
            "exit_code": result["exit_code"],
            "status": result["status"],
            "schema": result.get("payload", {}).get("schema"),
        }
        for result in results
    }
    scene_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py compiler-scene-selftest"
        ),
        {},
    )
    replay_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py compiler-a42-d20-replay"
        ),
        {},
    )
    evidence_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py evidence-index"
        ),
        {},
    )
    compiler_registry_checks = (
        evidence_payload.get("compiler_a42_d20_registry_checks", {})
        if isinstance(evidence_payload.get("compiler_a42_d20_registry_checks"), dict)
        else {}
    )
    checks = {
        "runs_only_declared_compiler_modes": [result["command"] for result in results]
        == [f"python src/verify.py {mode}" for mode in included_modes],
        "strict_and_expensive_modes_excluded": all(mode not in included_modes for mode in excluded_modes),
        "all_included_modes_pass": all(result["exit_code"] == 0 and result["status"] == "PASS" for result in results),
        "scene_selftest_promotes_claims": int(scene_payload.get("promoted_claim_count", 0)) > 0,
        "scene_selftest_has_no_pending_claims": int(scene_payload.get("pending_claim_count", 0)) == 0,
        "a42_d20_positive_replay_passes": replay_payload.get("positive", {}).get("verify_status")
        == "PASS_WITH_RESIDUE",
        "a42_d20_missing_coordinate_blocks": replay_payload.get("missing_coordinate", {}).get("verify_status")
        == "BLOCKED_WITH_RESIDUE",
        "a42_d20_tamper_fails": replay_payload.get("tampered_coordinate", {}).get(
            "tampered_verify_status"
        )
        == "FAIL",
        "evidence_index_has_compiler_replay_root": compiler_registry_checks.get(
            "evidence_index_has_compiler_a42_d20_root"
        )
        is True,
    }
    result = {
        "schema": "d20.verification.compiler_nonstrict",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "included_modes": included_modes,
        "excluded_modes": excluded_modes,
        "scene_summary": scene_payload.get("summary"),
        "a42_d20_replay": {
            "positive": replay_payload.get("positive"),
            "missing_coordinate": replay_payload.get("missing_coordinate"),
            "tampered_coordinate": replay_payload.get("tampered_coordinate"),
        },
        "results": by_command,
    }
    return finish(result, pretty)


def jacobian_cubic_nonstrict(*, pretty: bool) -> int:
    included_modes = [
        "evidence-index",
        "jacobian-cubic-status",
        "jacobian-cubic-intake",
        "jacobian-cubic-closure",
    ]
    excluded_modes = ["jacobian-cubic-cache"]
    results = [run_verify_subcommand(command) for command in included_modes]
    by_command = {
        result["command"]: {
            "command": result["command"],
            "exit_code": result["exit_code"],
            "status": result["status"],
            "schema": result.get("payload", {}).get("schema"),
        }
        for result in results
    }
    status_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py jacobian-cubic-status"
        ),
        {},
    )
    checks = {
        "runs_only_declared_non_strict_modes": [result["command"] for result in results]
        == [f"python src/verify.py {mode}" for mode in included_modes],
        "strict_cache_gate_excluded": "jacobian-cubic-cache" not in included_modes
        and excluded_modes == ["jacobian-cubic-cache"],
        "all_included_modes_pass": all(result["exit_code"] == 0 and result["status"] == "PASS" for result in results),
        "status_mode_reports_intake_ready_or_strict": status_payload.get("current_level")
        in {"intake_ready", "strict_certified"},
        "status_mode_reports_48_jobs": (
            status_payload.get("counts", {}).get("stable_verified", 0)
            + status_payload.get("counts", {}).get("promotion_ready", 0)
            + status_payload.get("counts", {}).get("invalid_present", 0)
            + status_payload.get("counts", {}).get("produce_needed", 0)
            == 48
        ),
        "strict_cache_not_ready_is_allowed": status_payload.get("strict_cache_ready") in {True, False},
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_nonstrict",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "included_modes": included_modes,
        "excluded_modes": excluded_modes,
        "current_level": status_payload.get("current_level"),
        "strict_cache_ready": status_payload.get("strict_cache_ready"),
        "counts": status_payload.get("counts"),
        "next_job": status_payload.get("next_job"),
        "results": by_command,
    }
    return finish(result, pretty)


def integration_nonstrict(*, pretty: bool) -> int:
    included_modes = [
        "compiler-nonstrict",
        "jacobian-cubic-nonstrict",
    ]
    excluded_modes = ["jacobian-cubic-cache", "rebuild", "strict-replay"]
    results = [run_verify_subcommand(command) for command in included_modes]
    by_command = {
        result["command"]: {
            "command": result["command"],
            "exit_code": result["exit_code"],
            "status": result["status"],
            "schema": result.get("payload", {}).get("schema"),
        }
        for result in results
    }
    compiler_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py compiler-nonstrict"
        ),
        {},
    )
    cubic_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py jacobian-cubic-nonstrict"
        ),
        {},
    )
    checks = {
        "runs_only_declared_integration_modes": [result["command"] for result in results]
        == [f"python src/verify.py {mode}" for mode in included_modes],
        "strict_and_expensive_modes_excluded": all(mode not in included_modes for mode in excluded_modes),
        "all_included_modes_pass": all(result["exit_code"] == 0 and result["status"] == "PASS" for result in results),
        "compiler_gate_passes": compiler_payload.get("status") == "PASS",
        "cubic_gate_passes": cubic_payload.get("status") == "PASS",
        "cubic_reports_48_jobs": (
            cubic_payload.get("counts", {}).get("stable_verified", 0)
            + cubic_payload.get("counts", {}).get("promotion_ready", 0)
            + cubic_payload.get("counts", {}).get("invalid_present", 0)
            + cubic_payload.get("counts", {}).get("produce_needed", 0)
            == 48
        ),
        "strict_cache_not_claimed": cubic_payload.get("strict_cache_ready") in {True, False}
        and cubic_payload.get("current_level") in {"intake_ready", "strict_certified"},
    }
    result = {
        "schema": "d20.verification.integration_nonstrict",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "included_modes": included_modes,
        "excluded_modes": excluded_modes,
        "compiler": {
            "scene_summary": compiler_payload.get("scene_summary"),
            "a42_d20_replay": compiler_payload.get("a42_d20_replay"),
        },
        "cubic": {
            "current_level": cubic_payload.get("current_level"),
            "strict_cache_ready": cubic_payload.get("strict_cache_ready"),
            "counts": cubic_payload.get("counts"),
            "next_job": cubic_payload.get("next_job"),
        },
        "results": by_command,
    }
    return finish(result, pretty)


def c985_registry(*, pretty: bool) -> int:
    from src.certify_c985_typed_simple_object_registry import (
        validate_c985_typed_simple_object_registry,
    )

    try:
        result = validate_c985_typed_simple_object_registry()
    except Exception as exc:
        result = {
            "schema": "c985.verification.typed_simple_object_registry@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_fusion(*, pretty: bool) -> int:
    from src.certify_c985_fusion_multiplicity_typing import (
        validate_c985_fusion_multiplicity_typing,
    )

    try:
        result = validate_c985_fusion_multiplicity_typing()
    except Exception as exc:
        result = {
            "schema": "c985.verification.fusion_multiplicity_typing@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_associator(*, pretty: bool) -> int:
    from src.certify_c985_associator_rebracketing_oracle import (
        validate_c985_associator_rebracketing_oracle,
    )

    try:
        result = validate_c985_associator_rebracketing_oracle()
    except Exception as exc:
        result = {
            "schema": "c985.verification.associator_rebracketing_oracle@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_unit(*, pretty: bool) -> int:
    from src.certify_c985_unit_tensor_laws import validate_c985_unit_tensor_laws

    try:
        result = validate_c985_unit_tensor_laws()
    except Exception as exc:
        result = {
            "schema": "c985.verification.unit_tensor_laws@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_triangle(*, pretty: bool) -> int:
    from src.certify_c985_unit_triangle_coherence import (
        validate_c985_unit_triangle_coherence,
    )

    try:
        result = validate_c985_unit_triangle_coherence()
    except Exception as exc:
        result = {
            "schema": "c985.verification.unit_triangle_coherence@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_duality(*, pretty: bool) -> int:
    from src.certify_c985_duality_support import validate_c985_duality_support

    try:
        result = validate_c985_duality_support()
    except Exception as exc:
        result = {
            "schema": "c985.verification.duality_support@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_pentagon(*, pretty: bool) -> int:
    from src.certify_c985_pentagon_chain_normal_form import (
        validate_c985_pentagon_chain_normal_form,
    )

    try:
        result = validate_c985_pentagon_chain_normal_form()
    except Exception as exc:
        result = {
            "schema": "c985.verification.pentagon_chain_normal_form@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_zigzag(*, pretty: bool) -> int:
    from src.certify_c985_zigzag_identities import validate_c985_zigzag_identities

    try:
        result = validate_c985_zigzag_identities()
    except Exception as exc:
        result = {
            "schema": "c985.verification.zigzag_identities@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_final(*, pretty: bool) -> int:
    from src.certify_c985_final_multifusion_certificate import (
        validate_c985_final_multifusion_certificate,
    )

    try:
        result = validate_c985_final_multifusion_certificate()
    except Exception as exc:
        result = {
            "schema": "c985.verification.final_multifusion_certificate@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_geometry(*, pretty: bool) -> int:
    from src.certify_c985_tensor_geometry_invariants import (
        validate_c985_tensor_geometry_invariants,
    )

    try:
        result = validate_c985_tensor_geometry_invariants()
    except Exception as exc:
        result = {
            "schema": "c985.verification.tensor_geometry_invariants@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_d20_atlas(*, pretty: bool) -> int:
    from src.certify_c985_d20_boundary_invariant_atlas import (
        validate_c985_d20_boundary_invariant_atlas,
    )

    try:
        result = validate_c985_d20_boundary_invariant_atlas()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_boundary_invariant_atlas@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_hyperbolic_graph(*, pretty: bool) -> int:
    from src.certify_c985_d20_hyperbolic_boundary_graph import (
        validate_c985_d20_hyperbolic_boundary_graph,
    )

    try:
        result = validate_c985_d20_hyperbolic_boundary_graph()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_hyperbolic_boundary_graph@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_poincare(*, pretty: bool) -> int:
    from src.certify_c985_d20_poincare_embedding import (
        validate_c985_d20_poincare_embedding,
    )

    try:
        result = validate_c985_d20_poincare_embedding()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_poincare_embedding@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_filtration(*, pretty: bool) -> int:
    from src.certify_c985_d20_poincare_landmark_filtration import (
        validate_c985_d20_poincare_landmark_filtration,
    )

    try:
        result = validate_c985_d20_poincare_landmark_filtration()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_poincare_landmark_filtration@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_nerve(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_class_nerve import (
        validate_c985_d20_signature_class_nerve,
    )

    try:
        result = validate_c985_d20_signature_class_nerve()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_class_nerve@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_chart_atlas(*, pretty: bool) -> int:
    from src.certify_c985_d20_hyperbolic_chart_atlas import (
        validate_c985_d20_hyperbolic_chart_atlas,
    )

    try:
        result = validate_c985_d20_hyperbolic_chart_atlas()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_hyperbolic_chart_atlas@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_transition_groupoid(*, pretty: bool) -> int:
    from src.certify_c985_d20_transition_groupoid import (
        validate_c985_d20_transition_groupoid,
    )

    try:
        result = validate_c985_d20_transition_groupoid()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_transition_groupoid@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_normal_words(*, pretty: bool) -> int:
    from src.certify_c985_d20_normal_form_words import (
        validate_c985_d20_normal_form_words,
    )

    try:
        result = validate_c985_d20_normal_form_words()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_normal_form_words@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_symbolic_rewrites(*, pretty: bool) -> int:
    from src.certify_c985_d20_symbolic_rewrite_rules import (
        validate_c985_d20_symbolic_rewrite_rules,
    )

    try:
        result = validate_c985_d20_symbolic_rewrite_rules()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_symbolic_rewrite_rules@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_symbolic_associativity(*, pretty: bool) -> int:
    from src.certify_c985_d20_symbolic_associativity import (
        validate_c985_d20_symbolic_associativity,
    )

    try:
        result = validate_c985_d20_symbolic_associativity()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_symbolic_associativity@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_rewrite_complex(*, pretty: bool) -> int:
    from src.certify_c985_d20_rewrite_complex_hyperbolicity import (
        validate_c985_d20_rewrite_complex_hyperbolicity,
    )

    try:
        result = validate_c985_d20_rewrite_complex_hyperbolicity()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_rewrite_complex_hyperbolicity@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_interval_sheaf(*, pretty: bool) -> int:
    from src.certify_c985_d20_geodesic_interval_sheaf import (
        validate_c985_d20_geodesic_interval_sheaf,
    )

    try:
        result = validate_c985_d20_geodesic_interval_sheaf()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_geodesic_interval_sheaf@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_preserved_core(*, pretty: bool) -> int:
    from src.certify_c985_d20_preserved_core_subcomplex import (
        validate_c985_d20_preserved_core_subcomplex,
    )

    try:
        result = validate_c985_d20_preserved_core_subcomplex()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_preserved_core_subcomplex@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_chamber_spine(*, pretty: bool) -> int:
    from src.certify_c985_d20_chamber_spine import (
        validate_c985_d20_chamber_spine,
    )

    try:
        result = validate_c985_d20_chamber_spine()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_chamber_spine@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_morse_reeb(*, pretty: bool) -> int:
    from src.certify_c985_d20_morse_reeb_quotient import (
        validate_c985_d20_morse_reeb_quotient,
    )

    try:
        result = validate_c985_d20_morse_reeb_quotient()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_morse_reeb_quotient@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_boundary_transfer(*, pretty: bool) -> int:
    from src.certify_c985_d20_boundary_transfer_operator import (
        validate_c985_d20_boundary_transfer_operator,
    )

    try:
        result = validate_c985_d20_boundary_transfer_operator()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_boundary_transfer_operator@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_atom_flow(*, pretty: bool) -> int:
    from src.certify_c985_d20_stationary_atom_flow_lift import (
        validate_c985_d20_stationary_atom_flow_lift,
    )

    try:
        result = validate_c985_d20_stationary_atom_flow_lift()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_stationary_atom_flow_lift@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_subboundary(*, pretty: bool) -> int:
    from src.certify_c985_d20_recurrent_signature_subboundary import (
        validate_c985_d20_recurrent_signature_subboundary,
    )

    try:
        result = validate_c985_d20_recurrent_signature_subboundary()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_recurrent_signature_subboundary@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_transfer(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_subboundary_transfer_operator import (
        validate_c985_d20_signature_subboundary_transfer_operator,
    )

    try:
        result = validate_c985_d20_signature_subboundary_transfer_operator()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_subboundary_transfer_operator@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_spectral_cut(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_transfer_spectral_cut import (
        validate_c985_d20_signature_transfer_spectral_cut,
    )

    try:
        result = validate_c985_d20_signature_transfer_spectral_cut()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_transfer_spectral_cut@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_quotient(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_spectral_quotient_dynamics import (
        validate_c985_d20_signature_spectral_quotient_dynamics,
    )

    try:
        result = validate_c985_d20_signature_spectral_quotient_dynamics()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_spectral_quotient_dynamics@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_geometry(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_quotient_poincare_geometry import (
        validate_c985_d20_signature_quotient_poincare_geometry,
    )

    try:
        result = validate_c985_d20_signature_quotient_poincare_geometry()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_quotient_poincare_geometry@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_geodesic(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_geodesic_order import (
        validate_c985_d20_signature_geodesic_order,
    )

    try:
        result = validate_c985_d20_signature_geodesic_order()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_geodesic_order@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_residual_chart(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_geodesic_residual_chart import (
        validate_c985_d20_signature_geodesic_residual_chart,
    )

    try:
        result = validate_c985_d20_signature_geodesic_residual_chart()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_geodesic_residual_chart@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_cell_complex(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_residual_cell_complex import (
        validate_c985_d20_signature_residual_cell_complex,
    )

    try:
        result = validate_c985_d20_signature_residual_cell_complex()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_residual_cell_complex@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def finish(result: dict[str, Any], pretty: bool) -> int:
    emit(result, pretty)
    return 0 if result.get("status") == "PASS" else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the d20 bundle.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in (
        "core",
        "audit",
        "rebuild",
        "refresh-certificate",
        "strict-replay",
        "evidence-index",
        "compiler-scene-selftest",
        "compiler-a42-d20-replay",
        "compiler-nonstrict",
        "integration-nonstrict",
        "jacobian-cubic-contract",
        "jacobian-cubic-intake",
        "jacobian-cubic-closure",
        "jacobian-cubic-status",
        "jacobian-cubic-nonstrict",
        "jacobian-cubic-cache",
        "talagrand-handoff",
        "talagrand-chain-audit",
        "talagrand-kkt-obligation",
        "c985-registry",
        "c985-fusion",
        "c985-associator",
        "c985-unit",
        "c985-triangle",
        "c985-duality",
        "c985-pentagon",
        "c985-zigzag",
        "c985-final",
        "c985-geometry",
        "c985-d20-atlas",
        "c985-hyperbolic-graph",
        "c985-poincare",
        "c985-filtration",
        "c985-nerve",
        "c985-chart-atlas",
        "c985-transition-groupoid",
        "c985-normal-words",
        "c985-symbolic-rewrites",
        "c985-symbolic-associativity",
        "c985-rewrite-complex",
        "c985-interval-sheaf",
        "c985-preserved-core",
        "c985-chamber-spine",
        "c985-morse-reeb",
        "c985-boundary-transfer",
        "c985-atom-flow",
        "c985-signature-subboundary",
        "c985-signature-transfer",
        "c985-signature-spectral-cut",
        "c985-signature-quotient",
        "c985-signature-geometry",
        "c985-signature-geodesic",
        "c985-signature-residual-chart",
        "c985-signature-cell-complex",
        "token-burn",
        "tamper",
    ):
        p = sub.add_parser(name)
        p.add_argument("--pretty", action="store_true")
        if name == "rebuild":
            p.add_argument(
                "--cached-source",
                action="store_true",
                help="Reuse existing checked source artifacts and skip heavy source refresh.",
            )
    args = parser.parse_args()

    if args.command == "rebuild":
        raise SystemExit(rebuild(pretty=args.pretty, cached_source=args.cached_source))
    if args.command == "refresh-certificate":
        raise SystemExit(refresh_certificate(pretty=args.pretty))
    if args.command == "evidence-index":
        raise SystemExit(verify_evidence_index(pretty=args.pretty))
    if args.command == "compiler-scene-selftest":
        raise SystemExit(compiler_scene_selftest(pretty=args.pretty))
    if args.command == "compiler-a42-d20-replay":
        raise SystemExit(compiler_a42_d20_replay(pretty=args.pretty))
    if args.command == "compiler-nonstrict":
        raise SystemExit(compiler_nonstrict(pretty=args.pretty))
    if args.command == "integration-nonstrict":
        raise SystemExit(integration_nonstrict(pretty=args.pretty))
    if args.command == "jacobian-cubic-contract":
        raise SystemExit(jacobian_cubic_contract(pretty=args.pretty))
    if args.command == "jacobian-cubic-intake":
        raise SystemExit(jacobian_cubic_intake(pretty=args.pretty))
    if args.command == "jacobian-cubic-closure":
        raise SystemExit(jacobian_cubic_closure(pretty=args.pretty))
    if args.command == "jacobian-cubic-status":
        raise SystemExit(jacobian_cubic_status(pretty=args.pretty))
    if args.command == "jacobian-cubic-nonstrict":
        raise SystemExit(jacobian_cubic_nonstrict(pretty=args.pretty))
    if args.command == "jacobian-cubic-cache":
        raise SystemExit(jacobian_cubic_cache(pretty=args.pretty))
    if args.command == "talagrand-handoff":
        raise SystemExit(talagrand_handoff(pretty=args.pretty))
    if args.command == "talagrand-chain-audit":
        raise SystemExit(talagrand_chain_audit(pretty=args.pretty))
    if args.command == "talagrand-kkt-obligation":
        raise SystemExit(talagrand_kkt_obligation(pretty=args.pretty))
    if args.command == "c985-registry":
        raise SystemExit(c985_registry(pretty=args.pretty))
    if args.command == "c985-fusion":
        raise SystemExit(c985_fusion(pretty=args.pretty))
    if args.command == "c985-associator":
        raise SystemExit(c985_associator(pretty=args.pretty))
    if args.command == "c985-unit":
        raise SystemExit(c985_unit(pretty=args.pretty))
    if args.command == "c985-triangle":
        raise SystemExit(c985_triangle(pretty=args.pretty))
    if args.command == "c985-duality":
        raise SystemExit(c985_duality(pretty=args.pretty))
    if args.command == "c985-pentagon":
        raise SystemExit(c985_pentagon(pretty=args.pretty))
    if args.command == "c985-zigzag":
        raise SystemExit(c985_zigzag(pretty=args.pretty))
    if args.command == "c985-final":
        raise SystemExit(c985_final(pretty=args.pretty))
    if args.command == "c985-geometry":
        raise SystemExit(c985_geometry(pretty=args.pretty))
    if args.command == "c985-d20-atlas":
        raise SystemExit(c985_d20_atlas(pretty=args.pretty))
    if args.command == "c985-hyperbolic-graph":
        raise SystemExit(c985_hyperbolic_graph(pretty=args.pretty))
    if args.command == "c985-poincare":
        raise SystemExit(c985_poincare(pretty=args.pretty))
    if args.command == "c985-filtration":
        raise SystemExit(c985_filtration(pretty=args.pretty))
    if args.command == "c985-nerve":
        raise SystemExit(c985_nerve(pretty=args.pretty))
    if args.command == "c985-chart-atlas":
        raise SystemExit(c985_chart_atlas(pretty=args.pretty))
    if args.command == "c985-transition-groupoid":
        raise SystemExit(c985_transition_groupoid(pretty=args.pretty))
    if args.command == "c985-normal-words":
        raise SystemExit(c985_normal_words(pretty=args.pretty))
    if args.command == "c985-symbolic-rewrites":
        raise SystemExit(c985_symbolic_rewrites(pretty=args.pretty))
    if args.command == "c985-symbolic-associativity":
        raise SystemExit(c985_symbolic_associativity(pretty=args.pretty))
    if args.command == "c985-rewrite-complex":
        raise SystemExit(c985_rewrite_complex(pretty=args.pretty))
    if args.command == "c985-interval-sheaf":
        raise SystemExit(c985_interval_sheaf(pretty=args.pretty))
    if args.command == "c985-preserved-core":
        raise SystemExit(c985_preserved_core(pretty=args.pretty))
    if args.command == "c985-chamber-spine":
        raise SystemExit(c985_chamber_spine(pretty=args.pretty))
    if args.command == "c985-morse-reeb":
        raise SystemExit(c985_morse_reeb(pretty=args.pretty))
    if args.command == "c985-boundary-transfer":
        raise SystemExit(c985_boundary_transfer(pretty=args.pretty))
    if args.command == "c985-atom-flow":
        raise SystemExit(c985_atom_flow(pretty=args.pretty))
    if args.command == "c985-signature-subboundary":
        raise SystemExit(c985_signature_subboundary(pretty=args.pretty))
    if args.command == "c985-signature-transfer":
        raise SystemExit(c985_signature_transfer(pretty=args.pretty))
    if args.command == "c985-signature-spectral-cut":
        raise SystemExit(c985_signature_spectral_cut(pretty=args.pretty))
    if args.command == "c985-signature-quotient":
        raise SystemExit(c985_signature_quotient(pretty=args.pretty))
    if args.command == "c985-signature-geometry":
        raise SystemExit(c985_signature_geometry(pretty=args.pretty))
    if args.command == "c985-signature-geodesic":
        raise SystemExit(c985_signature_geodesic(pretty=args.pretty))
    if args.command == "c985-signature-residual-chart":
        raise SystemExit(c985_signature_residual_chart(pretty=args.pretty))
    if args.command == "c985-signature-cell-complex":
        raise SystemExit(c985_signature_cell_complex(pretty=args.pretty))
    raise SystemExit(run(args.command, pretty=args.pretty))


if __name__ == "__main__":
    main()
