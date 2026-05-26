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


THEOREM_ID = "d20_talagrand_closure_chain_audit"
STATUS = "D20_TALAGRAND_CLOSURE_CHAIN_AUDITED_FINAL_PROOF_NOT_CLAIMED"
ARTIFACT_STATUS = "D20_TALAGRAND_CLOSURE_CHAIN_EXTRACTED_FROM_HANDOFF"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

HANDOFF_ROOT = ROOT / "data" / "evidence" / "talagrand_python_handoff"
WORK_ROOT = HANDOFF_ROOT / "work"
HANDOFF_MANIFEST = HANDOFF_ROOT / "manifest.json"
STATUS_LEDGER = HANDOFF_ROOT / "STATUS_LEDGER.json"
RUN_ORDER = HANDOFF_ROOT / "RUN_ORDER.md"
KKT_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_talagrand_multilevel_kkt_obstruction_system"
    / "report.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_talagrand_closure_chain_audit.py"
VALIDATOR = ROOT / "src" / "certify_d20_talagrand_closure_chain_audit.py"

EXPECTED_STEPS = [
    {
        "order": 1,
        "directory": "hamming_gaussian_talagrand_bridge",
        "certificate": "hamming_gaussian_talagrand_bridge_certificate.json",
        "expected_status": "HAMMING_GAUSSIAN_TALAGRAND_BRIDGE_CONSTRUCTED",
        "classification": "supporting_bridge",
    },
    {
        "order": 2,
        "directory": "exact_all_two_level_shell_certificate",
        "certificate": "exact_all_two_level_shell_certificate.json",
        "expected_status": "EXACT_ALL_TWO_LEVEL_SHELL_GAP_FACTOR_CERTIFIED",
        "classification": "exact_slice_closed",
    },
    {
        "order": 3,
        "directory": "exact_pair_stabilized_shell_certificate",
        "certificate": "exact_pair_stabilized_shell_certificate.json",
        "expected_status": "EXACT_PAIR_STABILIZED_SHELL_GAP_CERTIFIED",
        "classification": "exact_slice_closed",
    },
    {
        "order": 4,
        "directory": "talagrand_global_pairwise_schur_polynomial",
        "certificate": "global_pairwise_schur_polynomial_certificate.json",
        "expected_status": "GLOBAL_PAIRWISE_SCHUR_POLYNOMIAL_TARGET_MATERIALIZED",
        "classification": "reduction_target_materialized",
    },
    {
        "order": 5,
        "directory": "talagrand_exterior_trace_first_difference",
        "certificate": "exterior_trace_first_difference_certificate.json",
        "expected_status": "EXTERIOR_TRACE_FIRST_DIFFERENCE_NORMAL_FORM_CERTIFIED",
        "classification": "normal_form_certified",
    },
    {
        "order": 6,
        "directory": "talagrand_ordered_branch_Q_cone_decomposition",
        "certificate": "ordered_branch_Q_cone_certificate.json",
        "expected_status": "ORDERED_BRANCH_Q_CONE_DECOMPOSITION_BUILT",
        "classification": "reduction_built",
    },
    {
        "order": 7,
        "directory": "talagrand_Q_residual_oriented_block_factorization",
        "certificate": "Q_residual_oriented_block_factorization_certificate.json",
        "expected_status": "Q_RESIDUAL_ORIENTED_BLOCK_FACTORIZATION_CERTIFIED",
        "classification": "factorization_certified",
    },
    {
        "order": 8,
        "directory": "talagrand_barrier_contact_derivative_identity",
        "certificate": "barrier_contact_derivative_identity_certificate.json",
        "expected_status": "BARRIER_CONTACT_DERIVATIVE_IDENTITY_CERTIFIED",
        "classification": "identity_certified",
    },
    {
        "order": 9,
        "directory": "talagrand_pair_stabilized_contact_closure",
        "certificate": "pair_stabilized_contact_closure_certificate.json",
        "expected_status": "PAIR_STABILIZED_CONTACT_DERIVATIVE_CLOSED_EXACT",
        "classification": "exact_slice_closed",
    },
    {
        "order": 10,
        "directory": "talagrand_multilevel_contact_normal_form",
        "certificate": "multilevel_contact_normal_form_certificate.json",
        "expected_status": "MULTILEVEL_CONTACT_NORMAL_FORM_CERTIFIED",
        "classification": "normal_form_certified",
    },
    {
        "order": 11,
        "directory": "talagrand_weighted_asymmetry_contact_audit",
        "certificate": "weighted_asymmetry_contact_audit_certificate.json",
        "expected_status": "WEIGHTED_ASYMMETRY_CONTACT_AUDIT_NO_VALID_OUTWARD_DERIVATIVE",
        "classification": "numerical_audit_only",
    },
    {
        "order": 12,
        "directory": "talagrand_multilevel_KKT_obstruction_system",
        "certificate": "multilevel_KKT_obstruction_certificate.json",
        "expected_status": "MULTILEVEL_KKT_OBSTRUCTION_SYSTEM_FORMALIZED_NOT_CLOSED",
        "classification": "open_exact_obstruction",
    },
]


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


def run_order_directories() -> list[str]:
    out: list[str] = []
    for line in RUN_ORDER.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or not stripped[0].isdigit() or "`" not in stripped:
            continue
        out.append(stripped.split("`", 2)[1].rstrip("/"))
    return out


def step_record(spec: dict[str, Any]) -> dict[str, Any]:
    cert_path = WORK_ROOT / spec["directory"] / spec["certificate"]
    cert = load_json(cert_path)
    claim_boundary = cert.get("claim_boundary")
    final_proof_language = "final proof" in str(claim_boundary).lower()
    return {
        "order": spec["order"],
        "directory": spec["directory"],
        "certificate": input_entry(cert_path),
        "expected_status": spec["expected_status"],
        "status": cert.get("status"),
        "classification": spec["classification"],
        "claim": cert.get("claim"),
        "claim_boundary": claim_boundary,
        "status_matches_expected": cert.get("status") == spec["expected_status"],
        "boundary_mentions_not_final_proof": final_proof_language
        or spec["classification"]
        in {"supporting_bridge", "exact_slice_closed", "open_exact_obstruction"},
    }


def build_artifact() -> dict[str, Any]:
    handoff_manifest = load_json(HANDOFF_MANIFEST)
    status_ledger = load_json(STATUS_LEDGER)
    kkt_report = load_json(KKT_REPORT)
    run_order = run_order_directories()
    steps = [step_record(spec) for spec in EXPECTED_STEPS]

    classifications: dict[str, int] = {}
    for step in steps:
        key = str(step["classification"])
        classifications[key] = classifications.get(key, 0) + 1

    exact_closed_names = status_ledger.get("exactly_closed", [])
    if not isinstance(exact_closed_names, list):
        exact_closed_names = []

    checks = {
        "handoff_manifest_passed": handoff_manifest.get("schema")
        == "d20.evidence.talagrand_python_handoff.manifest@1"
        and all(handoff_manifest.get("checks", {}).values()),
        "final_global_proof_not_claimed": handoff_manifest.get("claim_boundary", {}).get(
            "final_global_talagrand_proof_claimed"
        )
        is False
        and "FINAL_GLOBAL_TALAGRAND_PROOF_NOT_CLAIMED"
        in str(status_ledger.get("global_status", "")),
        "run_order_has_expected_steps": run_order
        == [str(step["directory"]) for step in EXPECTED_STEPS],
        "all_step_statuses_match_expected": all(step["status_matches_expected"] for step in steps),
        "source_certificates_present": len(steps) == 12
        and all((WORK_ROOT / step["directory"] / EXPECTED_STEPS[step["order"] - 1]["certificate"]).exists() for step in steps),
        "exactly_closed_ledger_nonempty": len(exact_closed_names) >= 5,
        "numerical_audit_not_promoted_to_proof": classifications.get("numerical_audit_only") == 1,
        "open_obstruction_is_last_step": steps[-1]["classification"] == "open_exact_obstruction"
        and "NOT_CLOSED" in str(steps[-1]["status"]),
        "kkt_obligation_report_present": KKT_REPORT.exists()
        and kkt_report.get("status")
        == "D20_TALAGRAND_MULTILEVEL_KKT_OBSTRUCTION_SYSTEM_FORMALIZED_NOT_CLOSED",
        "kkt_obligation_preserves_open_target": "dF>0"
        in str(kkt_report.get("source_handoff", {}).get("remaining_open_target", "")),
    }

    artifact: dict[str, Any] = {
        "schema": "d20.proof_obligation.talagrand_closure_chain_audit.artifact@1",
        "status": ARTIFACT_STATUS,
        "name": THEOREM_ID,
        "source_handoff": {
            "root": relpath(HANDOFF_ROOT),
            "manifest_sha256": handoff_manifest.get("manifest_sha256"),
            "global_status": status_ledger.get("global_status"),
            "remaining_open_target": status_ledger.get("remaining_open_target"),
        },
        "claim": (
            "The Talagrand handoff main chain is indexed and classified in canonical "
            "proof-obligation form without claiming the final global proof."
        ),
        "claim_boundary": (
            "This is a chain audit and integration map. It verifies the handoff status, "
            "ordered source certificates, and open KKT boundary; it does not exclude the "
            "multilevel KKT obstruction system."
        ),
        "checks": checks,
        "step_count": len(steps),
        "classification_counts": dict(sorted(classifications.items())),
        "run_order": run_order,
        "steps": steps,
        "status_ledger_exactly_closed": exact_closed_names,
        "open_boundary": {
            "certified_here": [
                "all 12 RUN_ORDER entries are present in canonical evidence storage",
                "each primary certificate has the expected handoff status",
                "the weighted-asymmetry audit is classified as numerical only",
                "the KKT obstruction is linked to the first-class open proof obligation",
            ],
            "not_certified": [
                "the weighted-asymmetry contact lemma exactly",
                "absence of KKT solutions with dF>0",
                "the final global Talagrand inequality",
            ],
        },
    }
    artifact["artifact_sha256_excluding_this_field"] = hash_without(
        artifact,
        "artifact_sha256_excluding_this_field",
    )
    return artifact


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    step_inputs = {
        str(step["order"]).zfill(2) + "_" + step["directory"]: step["certificate"]
        for step in artifact["steps"]
    }
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.talagrand_closure_chain_audit@1",
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
            "run_order": input_entry(RUN_ORDER),
            "kkt_obligation_report": input_entry(KKT_REPORT),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR),
            "step_certificates": step_inputs,
        },
        "witness": {
            "classification_counts": artifact["classification_counts"],
            "steps": artifact["steps"],
            "status_ledger_exactly_closed": artifact["status_ledger_exactly_closed"],
            "open_boundary": artifact["open_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Use the chain audit to drive the exact KKT exclusion certificate: start from "
            "the multilevel contact normal form and construct a Terwilliger block-SOS or "
            "exact interval/Krawtchouk certificate for w=12,16."
        ),
    }
    report["certificate_sha256"] = hash_without(report, "certificate_sha256")
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.talagrand_closure_chain_audit_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify the Talagrand handoff manifest and status ledger keep final proof not claimed",
            "verify RUN_ORDER contains the expected 12-step main chain",
            "verify each primary step certificate has the expected handoff status",
            "verify the weighted-asymmetry step is numerical-only",
            "verify the final KKT step is linked to the open KKT proof obligation",
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
                "step_count": artifact["step_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
