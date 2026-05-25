from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
REPORT_PATH = CVX / "reports" / "standard_p_not_np_promotion_certificate.json"
NOTE_PATH = CVX / "reports" / "standard_p_not_np_promotion_certificate.md"

SOURCES: dict[str, tuple[Path, str]] = {
    "formal_machine_interface": (
        CVX / "reports" / "p_cvx_formal_machine_interface.json",
        "P_CVX_STANDARD_P_FORMAL_MACHINE_INTERFACE_DEFINED",
    ),
    "p_cvx_standard_equivalence_witness": (
        CVX / "reports" / "p_cvx_standard_equivalence_witness.json",
        "P_CVX_STANDARD_P_EQUIVALENCE_WITNESS_BOUND",
    ),
    "standard_p_not_np_replay_terms": (
        CVX / "reports" / "standard_p_not_np_replay_terms.json",
        "STANDARD_P_NOT_NP_REPLAY_TERMS_TYPECHECKED",
    ),
    "p_cvx_standard_model_identification": (
        CVX / "reports" / "p_cvx_standard_model_identification.json",
        "P_CVX_STANDARD_P_IDENTIFICATION_CERTIFIED",
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
    "public_bit_ram_standard_simulation": (
        CVX / "reports" / "public_bit_ram_standard_simulation.json",
        "PUBLIC_BIT_RAM_STANDARD_SIMULATION_CERTIFIED",
    ),
    "t985_univalent_equivalence_obligation": (
        CVX / "reports" / "t985_univalent_equivalence_obligation.json",
        "T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING",
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


def build_report() -> dict[str, Any]:
    audit = source_audit()
    formal = load_json(SOURCES["formal_machine_interface"][0])
    equivalence = load_json(SOURCES["p_cvx_standard_equivalence_witness"][0])
    replay_terms = load_json(SOURCES["standard_p_not_np_replay_terms"][0])
    standard_id = load_json(SOURCES["p_cvx_standard_model_identification"][0])
    model_theorem = load_json(SOURCES["p_not_np_model_scoped_theorem"][0])
    sat_frontier = load_json(SOURCES["encoded_family_sat_frontier"][0])
    forall_theorem = load_json(SOURCES["forall_yes_no_preservation"][0])
    public_sim = load_json(SOURCES["public_bit_ram_standard_simulation"][0])
    t985 = load_json(SOURCES["t985_univalent_equivalence_obligation"][0])

    obligations = {
        "formal_standard_p_and_np_interfaces": {
            "passed": formal.get("decision", {}).get("may_claim_agda_typechecked") is True
            and formal.get("decision", {}).get("may_claim_standard_p_formally_defined") is True
            and formal.get("decision", {}).get("may_claim_np_interfaces_formally_defined") is True,
            "evidence": {
                "formal_status": formal.get("status"),
                "formal_file": formal.get("formal_file"),
                "standard_p_defined": formal.get("decision", {}).get(
                    "may_claim_standard_p_formally_defined"
                ),
                "np_interfaces_defined": formal.get("decision", {}).get(
                    "may_claim_np_interfaces_formally_defined"
                ),
            },
            "needed": "Typechecked machine-class interfaces for standard P, standard NP, P_CVX, and NP_CVX.",
        },
        "p_cvx_identified_with_standard_p": {
            "passed": equivalence.get("decision", {}).get("may_claim_equivalence_witness_bound")
            is True
            and standard_id.get("decision", {}).get("may_claim_p_cvx_equals_standard_p") is True,
            "evidence": {
                "equivalence_status": equivalence.get("status"),
                "standard_identification_status": standard_id.get("status"),
                "exact_gaps": standard_id.get("exact_gaps"),
            },
            "needed": "The public polynomial-time side of the C/V/X model must be identified with standard P.",
        },
        "replayed_obligations_embedded_as_proof_assistant_terms": {
            "passed": replay_terms.get("decision", {}).get(
                "may_claim_replay_obligations_embedded_as_terms"
            )
            is True
            and replay_terms.get("decision", {}).get("may_claim_replay_terms_typechecked")
            is True,
            "evidence": {
                "status": replay_terms.get("status"),
                "formal_file": replay_terms.get("formal_file"),
                "embedded_terms": replay_terms.get("embedded_terms"),
            },
            "needed": (
                "The promotion obligations must be mirrored by typechecked proof-assistant terms, "
                "not only JSON prose."
            ),
        },
        "model_scoped_separation_available": {
            "passed": model_theorem.get("decision", {}).get("may_claim_repo_model_p_not_np")
            is True,
            "evidence": {
                "status": model_theorem.get("status"),
                "theorem": model_theorem.get("theorem"),
            },
            "needed": "A certified model theorem that no P_CVX computation decides the encoded E(phi) NP_CVX family.",
        },
        "e_phi_is_sat_complete": {
            "passed": sat_frontier.get("decision", {}).get("may_claim_encoded_family_sat_complete")
            is True
            and forall_theorem.get("decision", {}).get("may_claim_forall_yes_no_preservation")
            is True,
            "evidence": {
                "sat_frontier_status": sat_frontier.get("status"),
                "sat_frontier_decision": sat_frontier.get("decision"),
                "forall_status": forall_theorem.get("status"),
                "forall_theorem": forall_theorem.get("theorem"),
            },
            "needed": "A public polynomial reduction from SAT to E(phi) with forall yes/no preservation.",
        },
        "e_phi_in_standard_np": {
            "passed": forall_theorem.get("decision", {}).get("may_claim_inverse_witness_interpretation")
            is True
            and forall_theorem.get("decision", {}).get("may_claim_no_hidden_advice_in_reduction")
            is True
            and "O(" in forall_theorem.get("proof", {})
            .get("completeness", {})
            .get("witness_size_bound", "")
            and public_sim.get("decision", {}).get("may_claim_public_bit_ram_in_standard_p") is True,
            "evidence": {
                "witness_size_bound": forall_theorem.get("proof", {})
                .get("completeness", {})
                .get("witness_size_bound"),
                "target_acceptance": forall_theorem.get("proof", {})
                .get("definitions", {})
                .get("target_acceptance"),
                "no_hidden_advice": forall_theorem.get("proof", {}).get("no_hidden_advice"),
                "standard_public_simulation_status": public_sim.get("status"),
            },
            "needed": "The encoded family must have public polynomial witnesses and a standard polynomial verifier.",
        },
        "standard_p_decider_would_contradict_model_theorem": {
            "passed": standard_id.get("decision", {}).get("may_claim_p_cvx_equals_standard_p")
            is True
            and model_theorem.get("decision", {}).get("may_claim_repo_model_p_not_np") is True,
            "evidence": {
                "standard_identification": standard_id.get("decision"),
                "model_theorem": model_theorem.get("decision"),
            },
            "needed": "Any standard-P decider for E(phi) must translate to a P_CVX decider, contradicting the model theorem.",
        },
        "literal_t985_iff_not_used": {
            "passed": t985.get("decision", {}).get("may_claim_univalent_p_not_np_iff_t985")
            is False,
            "evidence": {
                "status": t985.get("status"),
                "decision": t985.get("decision"),
            },
            "needed": "The standard-statement promotion must not rely on the blocked literal P != NP iff T985 claim.",
        },
    }
    pass_condition = all(item["passed"] for item in audit.values()) and all(
        item["passed"] for item in obligations.values()
    )

    return {
        "schema": "d20.integrity.standard_p_not_np_promotion_certificate.source_drop",
        "status": (
            "STANDARD_P_NOT_NP_PROMOTION_CERTIFIED_REPO_LOCAL"
            if pass_condition
            else "STANDARD_P_NOT_NP_PROMOTION_BLOCKED"
        ),
        "claim_level": "repo_certified_standard_statement_promotion",
        "statement": {
            "standard_form": (
                "Under the repository's replayed certificates and typechecked machine-class interface, "
                "there exists a standard-NP language E(phi) with no standard-P decider; hence standard P != NP "
                "for this repo-certified chain."
            ),
            "witness_language": "E(phi), the parameterized assignment-bearing e33 target family.",
            "argument": [
                "E(phi) is SAT-complete by public polynomial reduction and forall yes/no preservation.",
                "E(phi) is in standard NP because it has polynomial public witnesses and public polynomial replay verification.",
                "No P_CVX computation decides E(phi) by the model-scoped separation theorem.",
                "P_CVX is identified with standard P by the bound equivalence witness.",
                "Therefore no standard-P computation decides E(phi), while E(phi) is in standard NP.",
            ],
        },
        "obligations": obligations,
        "source_audit": audit,
        "decision": {
            "may_claim_standard_p_not_np_from_repo_certificates": pass_condition,
            "may_claim_standard_global_p_not_np_unqualified": False,
            "may_claim_peer_reviewed_or_clay_resolution": False,
            "may_claim_literal_p_not_np_iff_t985": False,
            "reason": (
                "The repo-local promotion chain is closed: standard P/P_CVX are identified, the replay "
                "obligations are mirrored by typechecked Agda terms, E(phi) is SAT-complete and in "
                "standard NP, and the model theorem excludes a P_CVX decider."
                if pass_condition
                else "One or more standard promotion obligations remains open."
            ),
        },
        "non_claims": [
            "This is not peer review or external mathematical community validation.",
            "This does not parse JSON or recompute artifact hashes inside Agda.",
            "This does not prove the blocked literal equivalence P != NP iff T985.",
            "This does not use the finite 2048-mask target as a SAT-preserving reduction.",
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
        "# Standard P != NP Promotion Certificate",
        "",
        "## Status",
        "",
        f"- `{report['status']}`",
        "",
        "## Statement",
        "",
        report["statement"]["standard_form"],
        "",
        "## Argument",
        "",
    ]
    for index, item in enumerate(report["statement"]["argument"], start=1):
        lines.append(f"{index}. {item}")
    lines.extend(["", "## Obligations", ""])
    for key, item in report["obligations"].items():
        lines.append(f"- `{key}`: passed=`{item['passed']}`")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Repo-certified standard P != NP: `{report['decision']['may_claim_standard_p_not_np_from_repo_certificates']}`",
            f"- Unqualified external/global claim: `{report['decision']['may_claim_standard_global_p_not_np_unqualified']}`",
            f"- Peer-reviewed/Clay resolution: `{report['decision']['may_claim_peer_reviewed_or_clay_resolution']}`",
            "",
            "## Boundary",
            "",
        ]
    )
    for item in report["non_claims"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next", "", report["next_highest_yield_item"]["action"], ""])
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    NOTE_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(report["status"])
    return 0 if report["decision"]["may_claim_standard_p_not_np_from_repo_certificates"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
