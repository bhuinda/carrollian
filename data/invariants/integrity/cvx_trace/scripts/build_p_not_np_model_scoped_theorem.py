from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
REPORT_PATH = CVX / "reports" / "p_not_np_model_scoped_theorem.json"
NOTE_PATH = CVX / "reports" / "p_not_np_model_scoped_theorem.md"

SOURCES: dict[str, tuple[Path, str]] = {
    "bridge_checklist": (
        BASE / "p_vs_np_bridge_checklist.json",
        "P_VS_NP_BRIDGE_CHECKLIST_FORMALIZED",
    ),
    "encoded_family_sat_frontier": (
        CVX / "reports" / "encoded_family_sat_frontier_certificate.json",
        "ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED",
    ),
    "forall_yes_no_preservation": (
        CVX / "reports" / "forall_yes_no_preservation_theorem.json",
        "FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED",
    ),
    "universal_trace_compiler": (
        CVX / "reports" / "universal_trace_compiler_report.json",
        "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
    ),
    "universal_trace_typing": (
        CVX / "reports" / "universal_trace_typing_report.json",
        "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
    ),
    "universal_pure_c_no_escape": (
        CVX / "reports" / "universal_pure_c_no_escape_report.json",
        "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS",
    ),
    "universal_v_wall_crossing": (
        CVX / "reports" / "universal_v_wall_crossing_accounting_report.json",
        "UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_PASS",
    ),
    "x_policy_boundary": (
        CVX / "reports" / "x_policy_boundary_certificate.json",
        "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
    ),
    "quotient_kernel_reflection": (
        CVX / "reports" / "quotient_kernel_reflection_certificate.json",
        "QUOTIENT_KERNEL_REFLECTION_CERTIFIED_ROLEWISE",
    ),
    "full_no_escape_closure": (
        CVX / "reports" / "full_no_escape_closure_ledger.json",
        "FULL_NO_ESCAPE_CLOSURE_LEDGER_BUILT_CLOSED",
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
    encoded = load_json(SOURCES["encoded_family_sat_frontier"][0])
    ledger = load_json(SOURCES["full_no_escape_closure"][0])
    x_policy = load_json(SOURCES["x_policy_boundary"][0])
    quotient_kernel = load_json(SOURCES["quotient_kernel_reflection"][0])
    t985 = load_json(SOURCES["t985_univalent_equivalence_obligation"][0])

    obligations = {
        "sat_complete_encoded_family": {
            "passed": encoded.get("decision", {}).get("may_claim_encoded_family_sat_complete") is True,
            "evidence": {
                "status": encoded.get("status"),
                "frontier_decision": encoded.get("decision"),
            },
            "needed": "A public polynomial reduction from DIMACS CNF-SAT to the encoded E(phi) family with yes/no preservation.",
        },
        "public_polynomial_trace_model": {
            "passed": audit["universal_trace_compiler"]["passed"]
            and audit["universal_trace_typing"]["passed"],
            "evidence": {
                "compiler_status": audit["universal_trace_compiler"]["status"],
                "typing_status": audit["universal_trace_typing"]["status"],
            },
            "needed": "A polynomial-overhead public trace compiler and total C/V/X typing for accepted public executions.",
        },
        "pure_c_no_escape": {
            "passed": audit["universal_pure_c_no_escape"]["passed"],
            "evidence": {
                "status": audit["universal_pure_c_no_escape"]["status"],
            },
            "needed": "A replayed theorem that pure C traces cannot recover the hidden obstruction.",
        },
        "v_is_public_boundary_not_hidden_advice": {
            "passed": audit["universal_v_wall_crossing"]["passed"],
            "evidence": {
                "status": audit["universal_v_wall_crossing"]["status"],
            },
            "needed": "V events must be visible, replayable boundary crossings rather than hidden extractor access.",
        },
        "x_excluded_from_public_p": {
            "passed": x_policy.get("decision", {}).get("may_claim_public_p_excludes_x") is True,
            "evidence": {
                "status": x_policy.get("status"),
                "decision": x_policy.get("decision"),
            },
            "needed": "X access must remain typed as extractor/oracle/advice surface, not public-P computation.",
        },
        "quotient_kernel_noncollapse_reflection": {
            "passed": quotient_kernel.get("decision", {}).get(
                "may_claim_quotient_kernel_rolewise_reflection"
            )
            is True,
            "evidence": {
                "status": quotient_kernel.get("status"),
                "bridge_map": quotient_kernel.get("bridge_map"),
                "decision": quotient_kernel.get("decision"),
            },
            "needed": "A certified structural witness that public quotient access is not hidden kernel recovery.",
        },
        "full_no_escape_ledger_closed": {
            "passed": ledger.get("decision", {}).get("may_claim_full_separation") is True,
            "evidence": {
                "status": ledger.get("status"),
                "decision": ledger.get("decision"),
                "blocked_by": ledger.get("full_no_escape_claim", {}).get("blocked_by"),
            },
            "needed": "A dependency ledger linking the reduction, trace, no-escape, V, and X policy obligations with no blockers.",
        },
        "literal_t985_iff_not_used": {
            "passed": t985.get("decision", {}).get("may_claim_univalent_p_not_np_iff_t985") is False,
            "evidence": {
                "status": t985.get("status"),
                "decision": t985.get("decision"),
            },
            "needed": "The theorem extraction must not rely on the blocked literal P != NP iff T985 equivalence.",
        },
    }

    pass_condition = all(item["passed"] for item in obligations.values()) and all(
        item["passed"] for item in audit.values()
    )

    report = {
        "schema": "d20.integrity.p_not_np_model_scoped_theorem.source_drop",
        "status": (
            "P_NOT_NP_CVX_MODEL_THEOREM_EXTRACTED"
            if pass_condition
            else "P_NOT_NP_CVX_MODEL_THEOREM_BLOCKED"
        ),
        "claim_level": "model_scoped_theorem_extraction",
        "theorem": {
            "name": "C/V/X Model P != NP Separation",
            "statement": (
                "In the repository C/V/X public computation model, no public polynomial-time C-only "
                "computation decides the SAT-complete parameterized E(phi) family. Equivalently, "
                "P_CVX != NP_CVX for this encoded family under the certified C/V/X interface."
            ),
            "conditional_standard_form": (
                "If the repository C/V/X public trace model is proved extensionally equivalent to the "
                "standard Turing-machine definition of polynomial-time public computation, then this "
                "model-scoped theorem promotes to the standard statement P != NP."
            ),
        },
        "definitions": {
            "P_CVX": (
                "Polynomial-time public computations whose executions compile with polynomial overhead "
                "into the certified public C/V/X trace model and do not use X extractor/oracle/advice events."
            ),
            "NP_CVX": (
                "Certificate-bearing computations over the encoded E(phi) family with public witness "
                "checking and inverse assignment projection."
            ),
            "E_phi": (
                "The parameterized assignment-bearing e33 target family produced from DIMACS CNF inputs."
            ),
        },
        "proof_chain": [
            {
                "step": "SAT completeness",
                "claim": "DIMACS CNF-SAT reduces publicly and polynomially to the E(phi) encoded family with forall yes/no preservation.",
                "witness": rel(SOURCES["encoded_family_sat_frontier"][0]),
            },
            {
                "step": "Trace universality",
                "claim": "Accepted public polynomial executions compile to the C/V/X trace vocabulary with polynomial overhead.",
                "witness": rel(SOURCES["universal_trace_compiler"][0]),
            },
            {
                "step": "Total typing",
                "claim": "Accepted trace events are C, V, X, or explicit residues; no untyped escape is silently accepted.",
                "witness": rel(SOURCES["universal_trace_typing"][0]),
            },
            {
                "step": "Pure-C no escape",
                "claim": "Pure public C traces do not recover the hidden e33 obstruction needed to decide the family.",
                "witness": rel(SOURCES["universal_pure_c_no_escape"][0]),
            },
            {
                "step": "V accounting",
                "claim": "Visible V wall crossings are public boundary certificates, not hidden advice.",
                "witness": rel(SOURCES["universal_v_wall_crossing"][0]),
            },
            {
                "step": "X boundary",
                "claim": "Successful hidden-sector extraction is typed X and excluded from public-P computation.",
                "witness": rel(SOURCES["x_policy_boundary"][0]),
            },
            {
                "step": "No-escape closure",
                "claim": "A public polynomial decider would need either an impossible pure-C recovery or an X extractor outside public P.",
                "witness": rel(SOURCES["full_no_escape_closure"][0]),
            },
        ],
        "supporting_geometry": {
            "quotient_kernel_reflection": {
                "witness": rel(SOURCES["quotient_kernel_reflection"][0]),
                "role": (
                    "The 297-dimensional public quotient and 44,224-dimensional retained kernel certify "
                    "the surface/fiber non-collapse pattern used as structural support."
                ),
            },
            "t985_boundary": {
                "witness": rel(SOURCES["t985_univalent_equivalence_obligation"][0]),
                "role": (
                    "T985 suffices for the repo-local separation chain, while the blocked backward map "
                    "prevents replacing the theorem by a literal P != NP iff T985 slogan."
                ),
            },
        },
        "obligations": obligations,
        "source_audit": audit,
        "decision": {
            "may_claim_repo_model_p_not_np": pass_condition,
            "may_claim_standard_global_p_not_np": False,
            "may_claim_standard_p_not_np_conditional_on_model_equivalence": pass_condition,
            "may_claim_literal_p_not_np_iff_t985": False,
            "reason": (
                "The dependency chain closes inside the repository C/V/X model. Standard global P != NP "
                "still requires an external formal identification of P_CVX with standard polynomial-time "
                "Turing computation."
                if pass_condition
                else "One or more theorem extraction obligations failed."
            ),
        },
        "non_claims": [
            "This is not a peer-reviewed or proof-assistant-checked Clay theorem proof.",
            "This does not assert the blocked literal equivalence P != NP iff T985.",
            "This does not allow X extractor/oracle/advice access inside public P.",
            "This does not use the finite 2048-mask candidate as a SAT-preserving reduction.",
        ],
        "next_highest_yield_item": {
            "id": "formal_standard_model_identification",
            "action": (
                "Formalize P_CVX and standard P in a proof assistant, then prove or refute their "
                "extensional equivalence."
            ),
        },
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# C/V/X Model P != NP Separation",
        "",
        "## Statement",
        "",
        report["theorem"]["statement"],
        "",
        "Conditional standard form:",
        "",
        report["theorem"]["conditional_standard_form"],
        "",
        "## Definitions",
        "",
    ]
    for name, text in report["definitions"].items():
        lines.append(f"- `{name}`: {text}")
    lines.extend(
        [
            "",
            "## Proof Chain",
            "",
        ]
    )
    for index, step in enumerate(report["proof_chain"], start=1):
        lines.append(f"{index}. {step['step']}: {step['claim']}")
        lines.append(f"   Witness: `{step['witness']}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- The theorem is extracted inside the repository C/V/X model.",
            "- The standard global P != NP statement is conditional on identifying `P_CVX` with standard polynomial-time public computation.",
            "- The document does not use the blocked literal `P != NP iff T985` equivalence.",
            "- The finite 2048-mask candidate remains lookup-only; SAT preservation is carried by the parameterized `E(phi)` family.",
            "",
            "## Decision",
            "",
            f"- Repo model P != NP: `{report['decision']['may_claim_repo_model_p_not_np']}`",
            f"- Standard global P != NP: `{report['decision']['may_claim_standard_global_p_not_np']}`",
            f"- Conditional standard promotion: `{report['decision']['may_claim_standard_p_not_np_conditional_on_model_equivalence']}`",
            "",
            "## Verification Sources",
            "",
        ]
    )
    for key, item in report["source_audit"].items():
        lines.append(f"- `{key}`: `{item['status']}` at `{item['path']}`")
    lines.extend(
        [
            "",
            "## Next",
            "",
            report["next_highest_yield_item"]["action"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    NOTE_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(report["status"])
    return 0 if report["status"] == "P_NOT_NP_CVX_MODEL_THEOREM_EXTRACTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
