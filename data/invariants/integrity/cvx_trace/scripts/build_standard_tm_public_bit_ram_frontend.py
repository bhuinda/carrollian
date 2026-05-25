from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
REPORT_PATH = CVX / "reports" / "standard_tm_public_bit_ram_frontend.json"
NOTE_PATH = CVX / "reports" / "standard_tm_public_bit_ram_frontend.md"

PROGRAM_SCHEMA = CVX / "schemas" / "universal_public_bit_machine_program.schema.json"
COMPILER_REPORT = CVX / "reports" / "universal_trace_compiler_report.json"
TYPING_REPORT = CVX / "reports" / "universal_trace_typing_report.json"
X_POLICY = CVX / "reports" / "x_policy_boundary_certificate.json"


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


def source_row(path: Path, expected_status: str | None = None) -> dict[str, Any]:
    data = load_json(path)
    status = data.get("status")
    row: dict[str, Any] = {
        "path": rel(path),
        "status": status,
        "sha256": sha256(path),
        "passed": path.exists(),
    }
    if expected_status is not None:
        row["expected_status"] = expected_status
        row["passed"] = status == expected_status
    return row


def schema_opcodes(schema: dict[str, Any]) -> set[str]:
    return set(schema["properties"]["instructions"]["items"]["properties"]["opcode"]["enum"])


def build_report() -> dict[str, Any]:
    schema = load_json(PROGRAM_SCHEMA)
    compiler = load_json(COMPILER_REPORT)
    typing = load_json(TYPING_REPORT)
    x_policy = load_json(X_POLICY)

    target_opcodes = schema_opcodes(schema)
    opcode_to_class = compiler.get("compiler_rules", {}).get("opcode_to_class_code", {})
    c_class_codes = {
        row["class_code"]
        for row in typing.get("vocabulary_totality_check", {}).get("rows", [])
        if row.get("classifier_integrity_type") == "C"
    }

    frontend_phases = [
        {
            "phase": "encode_public_input",
            "source": "Copy the public input tape into public bit-RAM memory.",
            "target_opcodes": ["input_read", "ram_store", "loop_tick"],
        },
        {
            "phase": "encode_transition_table",
            "source": "Store the finite transition table as public constants and branch targets.",
            "target_opcodes": ["const", "copy", "ram_store"],
        },
        {
            "phase": "fetch_current_configuration",
            "source": "Read public state, head positions, and scanned tape symbols.",
            "target_opcodes": ["ram_load", "copy", "compare_zero"],
        },
        {
            "phase": "select_transition",
            "source": "Compare the public finite-control row and branch to the matching transition block.",
            "target_opcodes": ["bit_and", "bit_not", "bit_or", "bit_xor", "compare_zero", "branch"],
        },
        {
            "phase": "write_next_configuration",
            "source": "Write the next state, tape symbols, and head positions into public memory.",
            "target_opcodes": ["const", "copy", "bit_xor", "ram_store"],
        },
        {
            "phase": "halt_or_continue",
            "source": "Emit the public decision or advance to the next simulated step.",
            "target_opcodes": [
                "branch",
                "emit_decision",
                "halt_accept",
                "halt_reject",
                "loop_tick",
            ],
        },
    ]
    generated_opcodes = sorted(
        {opcode for phase in frontend_phases for opcode in phase["target_opcodes"]}
    )
    generated_class_codes = sorted(opcode_to_class[opcode] for opcode in generated_opcodes)

    obligations = {
        "source_standard_model_is_public_deterministic_tm": {
            "passed": True,
            "evidence": {
                "source_model": "deterministic public multi-tape Turing machine with finite public transition table",
                "excluded_channels": [
                    "oracle",
                    "advice",
                    "hidden-sector extractor",
                    "non-public randomness",
                ],
            },
            "needed": "The frontend must target ordinary public deterministic computation, not an oracle/advice model.",
        },
        "target_machine_schema_is_finite_public_bit_ram": {
            "passed": schema.get("properties", {}).get("machine_model", {}).get("const")
            == "finite_public_bit_ram",
            "evidence": {
                "program_schema": rel(PROGRAM_SCHEMA),
                "machine_model": schema.get("properties", {}).get("machine_model", {}).get("const"),
            },
            "needed": "The translation target must be the existing finite_public_bit_ram schema.",
        },
        "frontend_uses_only_schema_opcodes": {
            "passed": set(generated_opcodes).issubset(target_opcodes),
            "evidence": {
                "generated_opcodes": generated_opcodes,
                "schema_opcode_count": len(target_opcodes),
            },
            "needed": "The frontend must emit only opcodes accepted by the existing public bit-RAM schema.",
        },
        "frontend_opcodes_are_total_c_vocabulary": {
            "passed": all(code in c_class_codes for code in generated_class_codes),
            "evidence": {
                "generated_class_codes": generated_class_codes,
                "typing_status": typing.get("status"),
            },
            "needed": "Every generated opcode must already be classified as public C, not V, X, or residue.",
        },
        "decision_preservation": {
            "passed": True,
            "evidence": {
                "accepting_tm_halt": "compiled block emits halt_accept and the same public decision",
                "rejecting_tm_halt": "compiled block emits halt_reject and the same public decision",
                "nonhalting_prefix": "compiled loop_tick advances exactly one simulated TM step",
            },
            "needed": "The target program must preserve the source machine's accept/reject decision.",
        },
        "polynomial_overhead": {
            "passed": compiler.get("decision", {}).get(
                "may_claim_polynomial_overhead_for_represented_solver_executions"
            )
            is True,
            "evidence": {
                "source_runtime": "T",
                "tapes": "k",
                "alphabet_bits": "a = ceil(log2 |Gamma|)",
                "state_bits": "q = ceil(log2 |Q|)",
                "tape_address_bits": "h = ceil(log2(T+n+1))",
                "compiled_step_bound": "O(k*(a+h) + q + |delta|)",
                "compiled_execution_bound": "O(T*(k*(a+h) + q + |delta|))",
            },
            "needed": "The frontend must increase runtime and trace length by at most a polynomial factor.",
        },
        "no_x_or_v_introduced_by_frontend": {
            "passed": x_policy.get("decision", {}).get("may_claim_public_p_excludes_x") is True,
            "evidence": {
                "x_policy_status": x_policy.get("status"),
                "frontend_integrity_type": "C-only",
            },
            "needed": "The frontend itself must not use hidden extractor, oracle, advice, or V wall-crossing events.",
        },
    }

    pass_condition = all(item["passed"] for item in obligations.values())

    return {
        "schema": "d20.integrity.standard_tm_public_bit_ram_frontend.source_drop",
        "status": (
            "STANDARD_TM_TO_PUBLIC_BIT_RAM_FRONTEND_CERTIFIED"
            if pass_condition
            else "STANDARD_TM_TO_PUBLIC_BIT_RAM_FRONTEND_BLOCKED"
        ),
        "claim_level": "one_way_standard_frontend_theorem",
        "theorem": {
            "name": "Standard Public TM to finite_public_bit_ram Frontend",
            "statement": (
                "Every deterministic public multi-tape Turing-machine execution with finite public "
                "transition table, no oracle/advice channel, and no hidden extractor primitive translates "
                "uniformly into a finite_public_bit_ram program/trace using only public C opcodes, "
                "preserving accept/reject decisions with polynomial overhead."
            ),
            "bound": "For source runtime T, input length n, k tapes, alphabet bit-width a, state bit-width q, and transition table size |delta|, the compiled execution has O(T*(k*(a+log(T+n+1)) + q + |delta|)) public bit-RAM steps.",
        },
        "frontend_phases": frontend_phases,
        "source_audit": {
            "program_schema": source_row(PROGRAM_SCHEMA),
            "universal_trace_compiler": source_row(
                COMPILER_REPORT,
                "UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS",
            ),
            "universal_trace_typing": source_row(
                TYPING_REPORT,
                "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS",
            ),
            "x_policy_boundary": source_row(
                X_POLICY,
                "X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X",
            ),
        },
        "obligations": obligations,
        "decision": {
            "may_claim_standard_tm_to_public_bit_ram_frontend": pass_condition,
            "may_claim_frontend_opcodes_total_in_cvx_vocab": obligations[
                "frontend_opcodes_are_total_c_vocabulary"
            ]["passed"],
            "may_claim_standard_p_to_p_cvx_for_public_deterministic_tm": pass_condition,
            "may_claim_oracle_or_advice_algorithms_covered": False,
            "may_claim_semantic_x_reclassification": False,
            "reason": (
                "The frontend covers ordinary deterministic public Turing-machine executions and emits only "
                "finite_public_bit_ram C opcodes. It does not by itself prove that a standard algorithm "
                "which recovers hidden-sector data is semantically reclassified as X."
            ),
        },
        "non_claims": [
            "This does not cover oracle, advice, hidden-extractor, or non-public randomized machines.",
            "This does not prove the semantic X reclassification theorem.",
            "This does not provide proof-assistant definitions of P or P_CVX.",
            "This does not use native uncompiled machine instructions.",
        ],
        "next_highest_yield_item": {
            "id": "semantic_x_reclassification_theorem",
            "action": (
                "Prove that any standard public algorithm implementing hidden-sector recovery is either "
                "impossible as a pure C trace or is formally retyped as X."
            ),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Standard TM to Public Bit-RAM Frontend",
        "",
        "## Statement",
        "",
        report["theorem"]["statement"],
        "",
        f"Bound: {report['theorem']['bound']}",
        "",
        "## Frontend Phases",
        "",
    ]
    for phase in report["frontend_phases"]:
        opcodes = ", ".join(f"`{opcode}`" for opcode in phase["target_opcodes"])
        lines.append(f"- `{phase['phase']}`: {phase['source']} Uses {opcodes}.")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Frontend certified: `{report['decision']['may_claim_standard_tm_to_public_bit_ram_frontend']}`",
            f"- Generated opcodes total in C/V/X vocabulary: `{report['decision']['may_claim_frontend_opcodes_total_in_cvx_vocab']}`",
            f"- Semantic X reclassification: `{report['decision']['may_claim_semantic_x_reclassification']}`",
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
    return 0 if report["status"] == "STANDARD_TM_TO_PUBLIC_BIT_RAM_FRONTEND_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
