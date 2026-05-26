from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
REPORT_PATH = CVX / "reports" / "semantic_x_reclassification_theorem.json"
NOTE_PATH = CVX / "reports" / "semantic_x_reclassification_theorem.md"

STANDARD_FRONTEND = CVX / "reports" / "standard_tm_public_bit_ram_frontend.json"
PURE_C_NO_ESCAPE = CVX / "reports" / "universal_pure_c_no_escape_report.json"
X_ISOLATION = CVX / "reports" / "universal_x_extractor_isolation_report.json"
X_FRONTIER = CVX / "reports" / "x_extractor_frontier_certificate.json"
X_POLICY = CVX / "reports" / "x_policy_boundary_certificate.json"
MODEL_THEOREM = CVX / "reports" / "p_not_np_model_scoped_theorem.json"


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


def source_row(path: Path, expected_status: str) -> dict[str, Any]:
    data = load_json(path)
    status = data.get("status")
    return {
        "path": rel(path),
        "status": status,
        "expected_status": expected_status,
        "passed": status == expected_status,
        "sha256": sha256(path),
    }


def build_report() -> dict[str, Any]:
    frontend = load_json(STANDARD_FRONTEND)
    pure_c = load_json(PURE_C_NO_ESCAPE)
    x_isolation = load_json(X_ISOLATION)
    x_frontier = load_json(X_FRONTIER)
    x_policy = load_json(X_POLICY)
    model_theorem = load_json(MODEL_THEOREM)

    obligations = {
        "ordinary_public_standard_machines_compile_to_c_only": {
            "passed": frontend.get("decision", {}).get(
                "may_claim_standard_tm_to_public_bit_ram_frontend"
            )
            is True
            and frontend.get("decision", {}).get("may_claim_frontend_opcodes_total_in_cvx_vocab")
            is True,
            "evidence": {
                "frontend_status": frontend.get("status"),
                "frontend_decision": frontend.get("decision"),
            },
            "needed": "Ordinary deterministic public machines must translate into C-only finite_public_bit_ram traces.",
        },
        "pure_c_traces_cannot_recover_hidden_sector": {
            "passed": pure_c.get("decision", {}).get(
                "may_claim_universal_vocabulary_pure_c_no_escape"
            )
            is True,
            "evidence": {
                "pure_c_status": pure_c.get("status"),
                "antecedent": pure_c.get("antecedent"),
                "conclusion": pure_c.get("conditional_conclusion"),
            },
            "needed": "A pure C trace must be unable to recover hidden advice, hidden e33 maps, or non-public parity bases.",
        },
        "extractor_capability_is_isolated_on_x_surface": {
            "passed": x_isolation.get("decision", {}).get(
                "may_claim_universal_vocabulary_x_surface_isolated"
            )
            is True,
            "evidence": {
                "x_isolation_status": x_isolation.get("status"),
                "isolation_witness": x_isolation.get("isolation_witness"),
            },
            "needed": "Extractor-capable operations must be isolated to X surface codes in the finite universal vocabulary.",
        },
        "explicit_hidden_sector_extractor_is_x_not_c": {
            "passed": x_frontier.get("decision", {}).get(
                "may_claim_explicit_polynomial_family_x_extractor"
            )
            is True
            and x_policy.get("decision", {}).get("may_claim_public_p_excludes_x") is True,
            "evidence": {
                "extractor_id": x_frontier.get("extractor", {}).get("id"),
                "x_opcode": x_frontier.get("extractor", {}).get("x_opcode"),
                "x_frontier_status": x_frontier.get("status"),
                "x_policy_status": x_policy.get("status"),
            },
            "needed": "The known polynomial hidden-sector extractor must remain X, not be reclassified as public C.",
        },
        "repo_model_theorem_uses_x_policy_boundary": {
            "passed": model_theorem.get("decision", {}).get("may_claim_repo_model_p_not_np")
            is True
            and model_theorem.get("decision", {}).get("may_claim_standard_global_p_not_np")
            is False,
            "evidence": {
                "model_theorem_status": model_theorem.get("status"),
                "model_theorem_decision": model_theorem.get("decision"),
            },
            "needed": "The semantic theorem must support the model-scoped theorem without silently claiming global standard P != NP.",
        },
    }

    pass_condition = all(item["passed"] for item in obligations.values())

    return {
        "schema": "d20.integrity.semantic_x_reclassification.source_drop",
        "status": (
            "SEMANTIC_X_RECLASSIFICATION_THEOREM_CERTIFIED"
            if pass_condition
            else "SEMANTIC_X_RECLASSIFICATION_THEOREM_BLOCKED"
        ),
        "claim_level": "semantic_interface_classification_theorem",
        "theorem": {
            "name": "Semantic X Reclassification",
            "statement": (
                "For ordinary deterministic public standard-machine executions, the certified frontend "
                "produces C-only finite_public_bit_ram traces. If such an execution is claimed to recover "
                "the hidden e33/sector-33 extractor target, then either the claim contradicts the pure-C "
                "no-escape theorem, or the execution uses a hidden-sector extractor, oracle, advice, or "
                "non-public parity-basis operation and is reclassified as X rather than public P."
            ),
            "case_split": [
                "ordinary public deterministic execution -> C-only frontend trace -> no hidden recovery",
                "hidden recovery channel present -> extractor/oracle/advice/parity-basis access -> X surface",
            ],
        },
        "source_audit": {
            "standard_tm_public_bit_ram_frontend": source_row(
                STANDARD_FRONTEND,
                "STANDARD_TM_TO_PUBLIC_BIT_RAM_FRONTEND_CERTIFIED",
            ),
            "universal_pure_c_no_escape": source_row(
                PURE_C_NO_ESCAPE,
                "UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS",
            ),
            "universal_x_extractor_isolation": source_row(
                X_ISOLATION,
                "UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS",
            ),
            "x_extractor_frontier": source_row(
                X_FRONTIER,
                "X_EXTRACTOR_FRONTIER_EXPLICIT_POLYNOMIAL_FAMILY_EXTRACTOR_PROMOTED",
            ),
            "x_policy_boundary": source_row(
                X_POLICY,
                "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
            ),
            "p_not_np_model_scoped_theorem": source_row(
                MODEL_THEOREM,
                "P_NOT_NP_CVX_MODEL_THEOREM_EXTRACTED",
            ),
        },
        "obligations": obligations,
        "decision": {
            "may_claim_semantic_x_reclassification": pass_condition,
            "may_claim_hidden_recovery_is_public_c": False,
            "may_claim_oracle_or_advice_inside_public_p": False,
            "may_claim_standard_global_p_not_np": False,
            "reason": (
                "Within the repository interface semantics, ordinary standard public executions are C-only "
                "after frontend translation, and hidden recovery is either impossible in pure C or is typed X. "
                "This still leaves formal proof-assistant definitions of P and P_CVX as the remaining standard "
                "promotion gap."
            ),
        },
        "non_claims": [
            "This does not provide proof-assistant definitions of standard P or P_CVX.",
            "This does not put oracle/advice machines inside public P.",
            "This does not reclassify the explicit X extractor as C.",
            "This does not by itself claim a peer-reviewed standard P != NP theorem.",
        ],
        "next_highest_yield_item": {
            "id": "formal_p_and_p_cvx_definitions",
            "action": (
                "Define standard P and P_CVX as proof-assistant machine classes, then package the two "
                "simulation directions plus semantic X theorem as an extensional equivalence."
            ),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Semantic X Reclassification",
        "",
        "## Statement",
        "",
        report["theorem"]["statement"],
        "",
        "## Case Split",
        "",
    ]
    for row in report["theorem"]["case_split"]:
        lines.append(f"- {row}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Semantic X reclassification: `{report['decision']['may_claim_semantic_x_reclassification']}`",
            f"- Hidden recovery is public C: `{report['decision']['may_claim_hidden_recovery_is_public_c']}`",
            f"- Oracle/advice inside public P: `{report['decision']['may_claim_oracle_or_advice_inside_public_p']}`",
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
    return 0 if report["status"] == "SEMANTIC_X_RECLASSIFICATION_THEOREM_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
