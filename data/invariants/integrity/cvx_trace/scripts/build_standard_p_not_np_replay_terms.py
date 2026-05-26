from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
FORMAL_PATH = CVX / "formal" / "StandardPNotNPReplayTerms.agda"
REPORT_PATH = CVX / "reports" / "standard_p_not_np_replay_terms.json"
NOTE_PATH = CVX / "reports" / "standard_p_not_np_replay_terms.md"

AGDA_COMMAND = [
    "agda",
    "-v0",
    "-i",
    "data/invariants/integrity/cvx_trace/formal",
    "data/invariants/integrity/cvx_trace/formal/StandardPNotNPReplayTerms.agda",
]

SOURCES: dict[str, tuple[Path, str]] = {
    "formal_machine_interface": (
        CVX / "reports" / "p_cvx_formal_machine_interface.json",
        "P_CVX_STANDARD_P_FORMAL_MACHINE_INTERFACE_DEFINED",
    ),
    "public_bit_ram_standard_simulation": (
        CVX / "reports" / "public_bit_ram_standard_simulation.json",
        "PUBLIC_BIT_RAM_STANDARD_SIMULATION_CERTIFIED",
    ),
    "standard_tm_public_bit_ram_frontend": (
        CVX / "reports" / "standard_tm_public_bit_ram_frontend.json",
        "STANDARD_TM_TO_PUBLIC_BIT_RAM_FRONTEND_CERTIFIED",
    ),
    "semantic_x_reclassification": (
        CVX / "reports" / "semantic_x_reclassification_theorem.json",
        "SEMANTIC_X_RECLASSIFICATION_THEOREM_CERTIFIED",
    ),
    "p_cvx_standard_model_identification": (
        CVX / "reports" / "p_cvx_standard_model_identification.json",
        "P_CVX_STANDARD_P_IDENTIFICATION_CERTIFIED",
    ),
    "p_cvx_standard_equivalence_witness": (
        CVX / "reports" / "p_cvx_standard_equivalence_witness.json",
        "P_CVX_STANDARD_P_EQUIVALENCE_WITNESS_BOUND",
    ),
    "p_not_np_model_scoped_theorem": (
        CVX / "reports" / "p_not_np_model_scoped_theorem.json",
        "P_NOT_NP_CVX_MODEL_THEOREM_EXTRACTED",
    ),
    "encoded_family_sat_frontier": (
        CVX / "reports" / "encoded_family_sat_frontier_certificate.json",
        "ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED",
    ),
    "forall_yes_no_preservation": (
        CVX / "reports" / "forall_yes_no_preservation_theorem.json",
        "FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED",
    ),
    "t985_univalent_equivalence_obligation": (
        CVX / "reports" / "t985_univalent_equivalence_obligation.json",
        "T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING",
    ),
}

REQUIRED_DECLARATIONS = {
    "ReplayCertificate": "record ReplayCertificate (status : CertificateStatus) : Set where",
    "PcvxStandardEquivalenceReplayTerms": "record PcvxStandardEquivalenceReplayTerms : Set where",
    "EphiStandardNPReplayTerms": "record EphiStandardNPReplayTerms : Set where",
    "StandardPNoDeciderReplayTerms": "record StandardPNoDeciderReplayTerms : Set where",
    "RepoCertifiedStandardPNotNPReplayTerm": "record RepoCertifiedStandardPNotNPReplayTerm : Set where",
    "repoCertifiedStandardPNotNPReplayTermValue": (
        "repoCertifiedStandardPNotNPReplayTermValue :\n"
        "  RepoCertifiedStandardPNotNPReplayTerm"
    ),
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_audit() -> dict[str, Any]:
    audit = {}
    for key, (path, expected) in SOURCES.items():
        data = load_json(path)
        status = data.get("status")
        audit[key] = {
            "path": rel(path),
            "status": status,
            "expected_status": expected,
            "passed": status == expected,
            "sha256": sha256(path),
        }
    return audit


def declaration_audit(source: str) -> dict[str, Any]:
    return {
        key: {"needle": needle, "passed": needle in source}
        for key, needle in REQUIRED_DECLARATIONS.items()
    }


def typecheck_audit() -> dict[str, Any]:
    try:
        completed = subprocess.run(
            AGDA_COMMAND,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
        return {
            "command": " ".join(AGDA_COMMAND),
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "passed": completed.returncode == 0,
        }
    except FileNotFoundError as exc:
        return {
            "command": " ".join(AGDA_COMMAND),
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "passed": False,
        }


def build_report() -> dict[str, Any]:
    audit = source_audit()
    exists = FORMAL_PATH.exists()
    source = FORMAL_PATH.read_text(encoding="utf-8") if exists else ""
    declarations = declaration_audit(source)
    typecheck = typecheck_audit() if exists else {
        "command": " ".join(AGDA_COMMAND),
        "returncode": None,
        "stdout": "",
        "stderr": "formal replay-term file is missing",
        "passed": False,
    }
    pass_condition = (
        exists
        and all(item["passed"] for item in audit.values())
        and all(item["passed"] for item in declarations.values())
        and typecheck["passed"]
    )

    return {
        "schema": "d20.integrity.standard_p_not_np_replay_terms.source_drop",
        "status": (
            "STANDARD_P_NOT_NP_REPLAY_TERMS_TYPECHECKED"
            if pass_condition
            else "STANDARD_P_NOT_NP_REPLAY_TERMS_BLOCKED"
        ),
        "claim_level": "proof_assistant_replay_obligation_term_embedding",
        "formal_file": {
            "path": rel(FORMAL_PATH),
            "exists": exists,
            "language": "Agda",
            "sha256": sha256(FORMAL_PATH) if exists else None,
            "validation_command": " ".join(AGDA_COMMAND),
        },
        "typecheck_audit": typecheck,
        "declaration_audit": declarations,
        "source_audit": audit,
        "embedded_terms": {
            "equivalence_terms": "PcvxStandardEquivalenceReplayTerms",
            "np_side_terms": "EphiStandardNPReplayTerms",
            "no_standard_p_decider_terms": "StandardPNoDeciderReplayTerms",
            "standard_statement_term": "RepoCertifiedStandardPNotNPReplayTerm",
            "canonical_value": "repoCertifiedStandardPNotNPReplayTermValue",
        },
        "decision": {
            "may_claim_replay_terms_typechecked": pass_condition,
            "may_claim_replay_obligations_embedded_as_terms": pass_condition,
            "may_claim_standard_p_not_np_from_replay_terms": pass_condition,
            "may_claim_json_parser_or_hash_verification_inside_agda": False,
            "may_claim_peer_reviewed_or_clay_resolution": False,
            "reason": (
                "The replayed standard-promotion obligations are embedded as typechecked Agda terms, "
                "with source statuses audited by the builder."
                if pass_condition
                else "The replay terms are missing, failed typecheck, or lack a required source certificate."
            ),
        },
        "non_claims": [
            "This does not parse JSON or recompute SHA-256 inside Agda.",
            "This does not replace independent external review.",
            "This does not use the blocked literal P != NP iff T985 equivalence.",
        ],
        "next_highest_yield_item": {
            "id": "proof_assistant_hash_or_external_reviewer",
            "action": (
                "Either mechanize the artifact parser/hash checks in the proof assistant, or hand the "
                "audit pack to an independent reviewer for clean-room validation."
            ),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Standard P != NP Replay Terms",
        "",
        "## Status",
        "",
        f"- `{report['status']}`",
        "",
        "## Formal File",
        "",
        f"- `{report['formal_file']['path']}`",
        f"- Validation command: `{report['formal_file']['validation_command']}`",
        "",
        "## Embedded Terms",
        "",
    ]
    for key, value in report["embedded_terms"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Source Audit", ""])
    for key, item in report["source_audit"].items():
        lines.append(f"- `{key}`: passed=`{item['passed']}` status=`{item['status']}`")
    lines.extend(["", "## Next", "", report["next_highest_yield_item"]["action"], ""])
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    NOTE_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(report["status"])
    return 0 if report["decision"]["may_claim_replay_terms_typechecked"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
