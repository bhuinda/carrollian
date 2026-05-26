from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_talagrand_multilevel_kkt_obstruction_system"
STATUS = "D20_TALAGRAND_MULTILEVEL_KKT_OBSTRUCTION_SYSTEM_FORMALIZED_NOT_CLOSED"
ARTIFACT_STATUS = "D20_TALAGRAND_MULTILEVEL_KKT_OBSTRUCTION_SYSTEM_EXTRACTED_FROM_HANDOFF"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

HANDOFF_ROOT = ROOT / "data" / "evidence" / "talagrand_python_handoff"
HANDOFF_MANIFEST = HANDOFF_ROOT / "manifest.json"
STATUS_LEDGER = HANDOFF_ROOT / "STATUS_LEDGER.json"
KKT_DIR = HANDOFF_ROOT / "work" / "talagrand_multilevel_KKT_obstruction_system"
KKT_CERTIFICATE = KKT_DIR / "multilevel_KKT_obstruction_certificate.json"
KKT_THEOREM = KKT_DIR / "multilevel_KKT_obstruction_theorem.json"
CONTACT_NORMAL_FORM = (
    HANDOFF_ROOT
    / "work"
    / "talagrand_multilevel_contact_normal_form"
    / "multilevel_contact_normal_form_certificate.json"
)
WEIGHTED_ASYMMETRY_AUDIT = (
    HANDOFF_ROOT
    / "work"
    / "talagrand_weighted_asymmetry_contact_audit"
    / "weighted_asymmetry_contact_audit_certificate.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_talagrand_multilevel_kkt_obstruction_system.py"
VALIDATOR = ROOT / "src" / "certify_d20_talagrand_multilevel_kkt_obstruction_system.py"


def canonical(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {
        "path": relpath(path),
        "sha256": sha_file(path),
        "size": path.stat().st_size,
    }
    if extra:
        entry.update(extra)
    return entry


def hash_without(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return sha_json(tmp)


def audit_summary(audit: dict[str, Any]) -> dict[str, Any]:
    rows = audit.get("summary", [])
    if not isinstance(rows, list):
        rows = []
    positive_rows = 0
    valid_rows = 0
    starts = 0
    shells: list[int] = []
    max_valid = None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if isinstance(row.get("shell"), int):
            shells.append(row["shell"])
        positive_rows += int(row.get("positive_outward_derivative_rows", 0) or 0)
        valid_rows += int(row.get("valid_contact_rows", 0) or 0)
        starts += int(row.get("starts", 0) or 0)
        value = row.get("max_valid_dF_pair")
        if isinstance(value, (int, float)):
            max_valid = float(value) if max_valid is None else max(max_valid, float(value))
    return {
        "shells": sorted(shells),
        "starts": starts,
        "valid_contact_rows": valid_rows,
        "positive_outward_derivative_rows": positive_rows,
        "max_valid_dF_pair": max_valid,
        "claim_boundary": audit.get("claim_boundary"),
        "status": audit.get("status"),
    }


def build_artifact() -> dict[str, Any]:
    handoff_manifest = load_json(HANDOFF_MANIFEST)
    status_ledger = load_json(STATUS_LEDGER)
    kkt_certificate = load_json(KKT_CERTIFICATE)
    kkt_theorem = load_json(KKT_THEOREM)
    contact_normal_form = load_json(CONTACT_NORMAL_FORM)
    weighted_audit = load_json(WEIGHTED_ASYMMETRY_AUDIT)

    audit = audit_summary(weighted_audit)
    theorem = kkt_certificate.get("theorem", {})
    checks = {
        "handoff_final_global_proof_not_claimed": handoff_manifest.get("claim_boundary", {}).get(
            "final_global_talagrand_proof_claimed"
        )
        is False
        and "FINAL_GLOBAL_TALAGRAND_PROOF_NOT_CLAIMED"
        in str(status_ledger.get("global_status", "")),
        "kkt_certificate_status_not_closed": kkt_certificate.get("status")
        == "MULTILEVEL_KKT_OBSTRUCTION_SYSTEM_FORMALIZED_NOT_CLOSED",
        "kkt_certificate_claim_boundary_not_proof": "not a proof"
        in str(kkt_certificate.get("claim_boundary", "")).lower(),
        "kkt_theorem_status_not_closed": kkt_theorem.get("status")
        == "KKT_OBSTRUCTION_SYSTEM_FORMALIZED_NOT_CLOSED",
        "remaining_certificate_mentions_df_positive": "dF>0"
        in str(kkt_theorem.get("remaining_exact_certificate", "")),
        "remaining_certificate_mentions_shells_12_16": "w=12,16"
        in str(kkt_theorem.get("remaining_exact_certificate", "")),
        "contact_normal_form_certified": contact_normal_form.get("status")
        == "MULTILEVEL_CONTACT_NORMAL_FORM_CERTIFIED",
        "contact_normal_form_keeps_weighted_asymmetry_open": "Weighted Asymmetry"
        in str(contact_normal_form.get("theorem", {}).get("remaining_exact_lemma", "")),
        "weighted_asymmetry_audit_numerical_only": "Numerical audit only"
        in str(weighted_audit.get("claim_boundary", "")),
        "weighted_asymmetry_audit_found_no_positive_rows": audit[
            "positive_outward_derivative_rows"
        ]
        == 0,
        "kkt_source_files_present": all(
            path.exists()
            for path in (
                HANDOFF_MANIFEST,
                STATUS_LEDGER,
                KKT_CERTIFICATE,
                KKT_THEOREM,
                CONTACT_NORMAL_FORM,
                WEIGHTED_ASYMMETRY_AUDIT,
            )
        ),
    }

    artifact: dict[str, Any] = {
        "schema": "d20.proof_obligation.talagrand_multilevel_kkt_obstruction_system.artifact@1",
        "status": ARTIFACT_STATUS,
        "name": THEOREM_ID,
        "source_handoff": {
            "root": relpath(HANDOFF_ROOT),
            "manifest_sha256": handoff_manifest.get("manifest_sha256"),
            "global_status": status_ledger.get("global_status"),
            "remaining_open_target": status_ledger.get("remaining_open_target"),
        },
        "claim": kkt_certificate.get("claim"),
        "claim_boundary": kkt_certificate.get("claim_boundary"),
        "checks": checks,
        "theorem": theorem,
        "proof_spine": kkt_certificate.get("proof_spine", []),
        "cases": kkt_certificate.get("cases", []),
        "supporting_evidence": {
            "contact_normal_form": {
                "status": contact_normal_form.get("status"),
                "claim_boundary": contact_normal_form.get("claim_boundary"),
                "remaining_exact_lemma": contact_normal_form.get("theorem", {}).get(
                    "remaining_exact_lemma"
                ),
            },
            "weighted_asymmetry_numerical_audit": audit,
        },
        "open_boundary": {
            "certified_here": [
                "the exact KKT obstruction system is promoted from the handoff into the proof-obligation registry",
                "the multilevel contact normal form input is present and certified by the handoff",
                "the weighted-asymmetry audit is recorded only as numerical supporting evidence",
            ],
            "not_certified": [
                "no exclusion proof for KKT solutions with dF>0",
                "no Terwilliger block-SOS certificate",
                "no exact interval/Krawtchouk certificate",
                "no final global Talagrand proof",
            ],
        },
    }
    artifact["artifact_sha256_excluding_this_field"] = hash_without(
        artifact,
        "artifact_sha256_excluding_this_field",
    )
    return artifact


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.talagrand_multilevel_kkt_obstruction_system@1",
        "status": STATUS,
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": artifact["claim"],
        "claim_boundary": artifact["claim_boundary"],
        "source_handoff": artifact["source_handoff"],
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "schema": artifact["schema"],
                    "status": artifact["status"],
                    "artifact_sha256_excluding_this_field": artifact[
                        "artifact_sha256_excluding_this_field"
                    ],
                },
            ),
            "handoff_manifest": input_entry(HANDOFF_MANIFEST),
            "status_ledger": input_entry(STATUS_LEDGER),
            "kkt_certificate": input_entry(
                KKT_CERTIFICATE,
                {"embedded_certificate_sha256": load_json(KKT_CERTIFICATE).get("certificate_sha256")},
            ),
            "kkt_theorem": input_entry(KKT_THEOREM),
            "contact_normal_form_certificate": input_entry(CONTACT_NORMAL_FORM),
            "weighted_asymmetry_audit_certificate": input_entry(WEIGHTED_ASYMMETRY_AUDIT),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR),
        },
        "witness": {
            "theorem": artifact["theorem"],
            "proof_spine": artifact["proof_spine"],
            "cases": artifact["cases"],
            "supporting_evidence": artifact["supporting_evidence"],
            "open_boundary": artifact["open_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Build an exact exclusion certificate for the KKT obstruction system with dF>0, "
            "starting with a Terwilliger block-SOS or exact interval/Krawtchouk certificate for w=12,16."
        ),
    }
    report["certificate_sha256"] = hash_without(report, "certificate_sha256")
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.talagrand_multilevel_kkt_obstruction_system_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify the canonical Talagrand handoff still declares final global proof not claimed",
            "verify the KKT obstruction certificate is formalized-not-closed",
            "verify the KKT theorem names dF>0 and shells w=12,16 as the exact remaining target",
            "verify the multilevel contact normal form is certified by the handoff",
            "verify the weighted-asymmetry audit is treated as numerical evidence only",
            "verify the proof obligation registry records this open boundary without claiming closure",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(ARTIFACT_PATH),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "artifact_sha256_excluding_hash_field": artifact["artifact_sha256_excluding_this_field"],
    }
    manifest["manifest_sha256"] = hash_without(manifest, "manifest_sha256")
    return manifest


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    index["registry_sha256"] = hash_without(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def main() -> None:
    artifact = build_artifact()
    write_json(ARTIFACT_PATH, artifact)
    report = build_report(artifact)
    manifest = build_manifest(report, artifact)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    update_index(report)
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
