from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity"
CVX = BASE / "cvx_trace"
REPORT_PATH = CVX / "reports" / "p_cvx_standard_model_identification.json"
NOTE_PATH = CVX / "reports" / "p_cvx_standard_model_identification.md"

SOURCES: dict[str, tuple[Path, str]] = {
    "proof_system_ladder": (
        ROOT / "layers" / "integrity" / "proof_system.json",
        "PROOF_SYSTEM_INTEGRITY_LADDER_BUILT",
    ),
    "polynomial_trace_compiler_scope": (
        CVX / "reports" / "polynomial_trace_compiler_scope_certificate.json",
        "POLYNOMIAL_TRACE_COMPILER_UNIVERSAL_MACHINE_WITNESSED",
    ),
    "universal_trace_compiler": (
        CVX / "reports" / "universal_trace_compiler_report.json",
        "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
    ),
    "universal_trace_typing": (
        CVX / "reports" / "universal_trace_typing_report.json",
        "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
    ),
    "x_policy_boundary": (
        CVX / "reports" / "x_policy_boundary_certificate.json",
        "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
    ),
    "p_cvx_formal_machine_interface": (
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
    "p_not_np_model_scoped_theorem": (
        CVX / "reports" / "p_not_np_model_scoped_theorem.json",
        "P_NOT_NP_CVX_MODEL_THEOREM_EXTRACTED",
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


def formal_proof_files() -> list[str]:
    suffixes = {".lean", ".agda", ".v", ".coq", ".idr"}
    ignored_parts = {".git", ".venv", ".replay_tmp", "generated"}
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        relative = path.relative_to(ROOT)
        if any(part in ignored_parts for part in relative.parts):
            continue
        files.append(rel(path))
    return sorted(files)


def build_report() -> dict[str, Any]:
    audit = source_audit()
    proof_system = load_json(SOURCES["proof_system_ladder"][0])
    compiler_scope = load_json(SOURCES["polynomial_trace_compiler_scope"][0])
    universal_compiler = load_json(SOURCES["universal_trace_compiler"][0])
    universal_typing = load_json(SOURCES["universal_trace_typing"][0])
    x_policy = load_json(SOURCES["x_policy_boundary"][0])
    formal_interface = load_json(SOURCES["p_cvx_formal_machine_interface"][0])
    public_simulation = load_json(SOURCES["public_bit_ram_standard_simulation"][0])
    standard_frontend = load_json(SOURCES["standard_tm_public_bit_ram_frontend"][0])
    semantic_x = load_json(SOURCES["semantic_x_reclassification"][0])
    model_theorem = load_json(SOURCES["p_not_np_model_scoped_theorem"][0])
    proof_files = formal_proof_files()

    tier_8 = next(
        (
            row
            for row in proof_system.get("ladder", [])
            if row.get("system") == "Arbitrary polynomial-time Turing machine"
        ),
        {},
    )

    obligations = {
        "standard_p_hprop_or_machine_class_defined": {
            "passed": audit["p_cvx_formal_machine_interface"]["passed"]
            and formal_interface.get("decision", {}).get("may_claim_standard_p_formally_defined")
            is True
            and formal_interface.get("decision", {}).get("may_claim_agda_typechecked") is True,
            "evidence": {
                "formal_files": proof_files,
                "formal_interface_status": formal_interface.get("status"),
                "formal_file": formal_interface.get("formal_file"),
                "definition": formal_interface.get("definitions", {}).get("standard_p"),
            },
            "needed": (
                "A proof-assistant definition of standard P as a Turing-machine, RAM-machine, or "
                "equivalent polynomial-time machine class."
            ),
        },
        "p_cvx_formal_machine_class_defined": {
            "passed": audit["p_cvx_formal_machine_interface"]["passed"]
            and formal_interface.get("decision", {}).get("may_claim_p_cvx_formally_defined")
            is True
            and formal_interface.get("decision", {}).get("may_claim_equivalence_package_type_defined")
            is True
            and formal_interface.get("decision", {}).get("may_claim_agda_typechecked") is True,
            "evidence": {
                "formal_interface_status": formal_interface.get("status"),
                "formal_file": formal_interface.get("formal_file"),
                "formal_definition": formal_interface.get("definitions", {}).get("p_cvx"),
                "equivalence_package": formal_interface.get("definitions", {}).get(
                    "equivalence_package"
                ),
                "model_theorem_status": model_theorem.get("status"),
                "p_cvx_definition": model_theorem.get("definitions", {}).get("P_CVX"),
            },
            "needed": (
                "A proof-assistant definition of P_CVX, not only JSON prose and replayed certificate semantics."
            ),
        },
        "public_bit_ram_to_standard_tm_simulation": {
            "passed": public_simulation.get("decision", {}).get(
                "may_claim_public_bit_ram_in_standard_p"
            )
            is True,
            "evidence": {
                "simulation_status": public_simulation.get("status"),
                "simulation_decision": public_simulation.get("decision"),
                "simulation_bound": public_simulation.get("theorem", {}).get("bound"),
            },
            "needed": (
                "A formal polynomial simulation theorem showing every finite_public_bit_ram C-trace "
                "execution is accepted by a standard polynomial-time Turing/RAM machine."
            ),
        },
        "standard_tm_to_public_bit_ram_frontend": {
            "passed": standard_frontend.get("decision", {}).get(
                "may_claim_standard_tm_to_public_bit_ram_frontend"
            )
            is True,
            "evidence": {
                "frontend_status": standard_frontend.get("status"),
                "frontend_decision": standard_frontend.get("decision"),
                "frontend_bound": standard_frontend.get("theorem", {}).get("bound"),
            },
            "needed": (
                "A uniform polynomial translation from arbitrary standard polynomial-time Turing-machine "
                "executions into finite_public_bit_ram programs/traces, preserving decisions."
            ),
        },
        "native_instruction_totality": {
            "passed": standard_frontend.get("decision", {}).get(
                "may_claim_frontend_opcodes_total_in_cvx_vocab"
            )
            is True,
            "evidence": {
                "may_claim_totality_for_uncompiled_native_machine_instructions": universal_typing.get(
                    "decision", {}
                ).get("may_claim_totality_for_uncompiled_native_machine_instructions"),
                "fallback": universal_typing.get("fallback_fixture"),
                "frontend_opcodes_total": standard_frontend.get("decision", {}).get(
                    "may_claim_frontend_opcodes_total_in_cvx_vocab"
                ),
            },
            "needed": (
                "A proof that every standard-machine instruction appearing after frontend translation lands "
                "inside the finite C/V/X vocabulary, rather than becoming an unclassified residue."
            ),
        },
        "semantic_x_reclassification_excluded_for_standard_algorithms": {
            "passed": semantic_x.get("decision", {}).get("may_claim_semantic_x_reclassification")
            is True,
            "evidence": {
                "semantic_x_status": semantic_x.get("status"),
                "semantic_x_decision": semantic_x.get("decision"),
                "x_policy_status": x_policy.get("status"),
                "x_surface_rule": x_policy.get("policy", {}).get("hidden_extractor_surface"),
                "proof_system_tier_8": tier_8,
            },
            "needed": (
                "A theorem that a standard public polynomial algorithm cannot implement the hidden X "
                "extractor under a different public name without either producing a C-trace contradiction "
                "or being retyped as X by a formal semantic classifier."
            ),
        },
        "repo_model_theorem_available": {
            "passed": model_theorem.get("decision", {}).get("may_claim_repo_model_p_not_np") is True,
            "evidence": {
                "status": model_theorem.get("status"),
                "decision": model_theorem.get("decision"),
            },
            "needed": "The model-scoped theorem must already be extracted before standard promotion is attempted.",
        },
    }

    gap_templates = {
        "standard_p_hprop_or_machine_class_defined": {
            "id": "formal_standard_p_definition_missing",
            "meaning": "Standard P is not currently defined as a proof-assistant object.",
        },
        "p_cvx_formal_machine_class_defined": {
            "id": "formal_p_cvx_definition_missing",
            "meaning": "P_CVX is not currently defined as a proof-assistant object.",
        },
        "public_bit_ram_to_standard_tm_simulation": {
            "id": "public_bit_ram_to_standard_tm_simulation_missing",
            "meaning": (
                "The finite public bit-RAM to standard-machine direction still lacks a replayed "
                "simulation certificate."
            ),
        },
        "standard_tm_to_public_bit_ram_frontend": {
            "id": "standard_tm_to_public_bit_ram_frontend_missing",
            "meaning": (
                "The existing compiler applies to executions already represented in finite_public_bit_ram. "
                "The missing map is a uniform frontend from arbitrary standard polynomial-time machines."
            ),
        },
        "native_instruction_totality": {
            "id": "native_instruction_totality_missing",
            "meaning": (
                "After frontend translation, every standard-machine instruction must land inside the finite "
                "C/V/X vocabulary rather than becoming an unclassified residue."
            ),
        },
        "semantic_x_reclassification_excluded_for_standard_algorithms": {
            "id": "semantic_x_reclassification_theorem_missing",
            "meaning": (
                "A standard public algorithm has no C/V/X labels. The repo still needs a semantic theorem "
                "saying hidden-sector recovery is either impossible in pure C or is formally retyped as X."
            ),
        },
    }
    exact_gaps = [
        gap_templates[key]
        for key, item in obligations.items()
        if key in gap_templates and item["passed"] is False
    ]

    exact_gap_identified = (
        audit["p_not_np_model_scoped_theorem"]["passed"]
        and audit["universal_trace_compiler"]["passed"]
        and audit["universal_trace_typing"]["passed"]
        and obligations["repo_model_theorem_available"]["passed"]
    )
    standard_identified = all(item["passed"] for item in obligations.values())

    return {
        "schema": "d20.integrity.p_cvx_standard_model_identification.source_drop",
        "status": (
            "P_CVX_STANDARD_P_IDENTIFICATION_CERTIFIED"
            if standard_identified
            else "P_CVX_STANDARD_P_IDENTIFICATION_BLOCKED_EXACT_GAPS_IDENTIFIED"
        ),
        "claim_level": "standard_model_promotion_obligation",
        "source_audit": audit,
        "candidate_equivalence": {
            "left": "P_CVX",
            "right": "standard P",
            "target": "P_CVX = standard P as polynomial-time public machine classes",
            "required_directions": [
                "P_CVX -> standard P",
                "standard P -> P_CVX",
            ],
        },
        "obligations": obligations,
        "exact_gaps": exact_gaps,
        "decision": {
            "may_claim_exact_standard_model_gap_identified": exact_gap_identified,
            "may_claim_p_cvx_equals_standard_p": standard_identified,
            "may_claim_standard_global_p_not_np": False,
            "may_claim_conditional_standard_p_not_np": model_theorem.get("decision", {}).get(
                "may_claim_standard_p_not_np_conditional_on_model_equivalence"
            )
            is True,
            "may_claim_repo_model_p_not_np": model_theorem.get("decision", {}).get(
                "may_claim_repo_model_p_not_np"
            )
            is True,
            "reason": (
                "The P_CVX/standard-P identification obligations are certified: the proof-assistant "
                "interface defines both machine classes, the two simulation directions are replayed, and "
                "semantic X reclassification excludes hidden extractor access from ordinary public P."
                if standard_identified
                else "The exact promotion gap is isolated by the failed obligations above. Until those close, "
                "the repo theorem remains P_CVX != NP_CVX."
            ),
        },
        "non_claims": [
            "This does not demote the model-scoped theorem.",
            "This does not prove standard global P != NP.",
            "This does not classify arbitrary uncompiled native machine instructions as C.",
            "This does not allow hidden X extractor access inside standard public P.",
        ],
        "next_highest_yield_item": {
            "id": "standard_p_not_np_promotion_certificate",
            "action": (
                "Package the model-scoped separation, the certified P_CVX/standard-P identification, "
                "and the SAT/NP interface into a standard-statement promotion certificate."
            ),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P_CVX / Standard P Identification Obligation",
        "",
        "## Target",
        "",
        report["candidate_equivalence"]["target"],
        "",
        "## Decision",
        "",
        f"- Exact gap identified: `{report['decision']['may_claim_exact_standard_model_gap_identified']}`",
        f"- P_CVX equals standard P: `{report['decision']['may_claim_p_cvx_equals_standard_p']}`",
        f"- Standard global P != NP: `{report['decision']['may_claim_standard_global_p_not_np']}`",
        f"- Repo model P != NP: `{report['decision']['may_claim_repo_model_p_not_np']}`",
        "",
        "## Exact Gaps",
        "",
    ]
    if report["exact_gaps"]:
        for gap in report["exact_gaps"]:
            lines.append(f"- `{gap['id']}`: {gap['meaning']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Obligations", ""])
    for key, item in report["obligations"].items():
        lines.append(f"- `{key}`: passed=`{item['passed']}`")
        lines.append(f"  Needed: {item['needed']}")
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
    return 0 if report["decision"]["may_claim_exact_standard_model_gap_identified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
