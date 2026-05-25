from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
REPORT_PATH = CVX / "reports" / "p_cvx_standard_equivalence_witness.json"
NOTE_PATH = CVX / "reports" / "p_cvx_standard_equivalence_witness.md"

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
    "standard_model_identification": (
        CVX / "reports" / "p_cvx_standard_model_identification.json",
        "P_CVX_STANDARD_P_IDENTIFICATION_CERTIFIED",
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
    public_sim = load_json(SOURCES["public_bit_ram_standard_simulation"][0])
    standard_frontend = load_json(SOURCES["standard_tm_public_bit_ram_frontend"][0])
    semantic_x = load_json(SOURCES["semantic_x_reclassification"][0])
    standard_id = load_json(SOURCES["standard_model_identification"][0])

    bindings = {
        "pcvxToStandardP": {
            "formal_field": "PCVXStandardPIdentificationPackage.pcvxToStandardP",
            "bound_by": rel(SOURCES["public_bit_ram_standard_simulation"][0]),
            "status": public_sim.get("status"),
            "passed": public_sim.get("decision", {}).get("may_claim_public_bit_ram_in_standard_p")
            is True
            and public_sim.get("decision", {}).get(
                "may_claim_p_cvx_to_standard_p_for_represented_public_c_traces"
            )
            is True,
            "meaning": "Every represented finite public bit-RAM/C-only P_CVX computation has a polynomial standard machine simulation.",
            "bound": public_sim.get("theorem", {}).get("bound"),
        },
        "standardPToPCVX": {
            "formal_field": "PCVXStandardPIdentificationPackage.standardPToPCVX",
            "bound_by": rel(SOURCES["standard_tm_public_bit_ram_frontend"][0]),
            "status": standard_frontend.get("status"),
            "passed": standard_frontend.get("decision", {}).get(
                "may_claim_standard_p_to_p_cvx_for_public_deterministic_tm"
            )
            is True
            and standard_frontend.get("decision", {}).get(
                "may_claim_frontend_opcodes_total_in_cvx_vocab"
            )
            is True,
            "meaning": "Every ordinary deterministic public standard machine execution has a polynomial C-only finite public bit-RAM frontend.",
            "bound": standard_frontend.get("theorem", {}).get("bound"),
        },
        "semanticXBoundary": {
            "formal_field": "PCVXStandardPIdentificationPackage.semanticXBoundary",
            "bound_by": rel(SOURCES["semantic_x_reclassification"][0]),
            "status": semantic_x.get("status"),
            "passed": semantic_x.get("decision", {}).get("may_claim_semantic_x_reclassification")
            is True,
            "meaning": "Hidden recovery is either impossible in pure C or is reclassified as X rather than public P.",
        },
        "extensionalEquivalence": {
            "formal_field": "PCVXStandardPIdentificationPackage.extensionalEquivalence",
            "bound_by": rel(SOURCES["standard_model_identification"][0]),
            "status": standard_id.get("status"),
            "passed": standard_id.get("decision", {}).get("may_claim_p_cvx_equals_standard_p")
            is True
            and len(standard_id.get("exact_gaps", [])) == 0,
            "meaning": "The two simulation directions plus semantic X boundary package P_CVX = standard P as public machine classes.",
        },
    }
    pass_condition = (
        all(item["passed"] for item in audit.values())
        and all(item["passed"] for item in bindings.values())
        and formal.get("decision", {}).get("may_claim_agda_typechecked") is True
        and formal.get("decision", {}).get("may_claim_equivalence_package_type_defined") is True
    )

    return {
        "schema": "d20.integrity.p_cvx_standard_equivalence_witness.source_drop",
        "status": (
            "P_CVX_STANDARD_P_EQUIVALENCE_WITNESS_BOUND"
            if pass_condition
            else "P_CVX_STANDARD_P_EQUIVALENCE_WITNESS_BLOCKED"
        ),
        "claim_level": "formal_interface_field_binding_to_replayed_certificates",
        "formal_target": {
            "file": formal.get("formal_file", {}).get("path"),
            "package_type": "PCVXStandardPIdentificationPackage",
            "typechecked": formal.get("decision", {}).get("may_claim_agda_typechecked") is True,
        },
        "field_bindings": bindings,
        "source_audit": audit,
        "decision": {
            "may_claim_equivalence_witness_bound": pass_condition,
            "may_claim_p_cvx_equals_standard_p": pass_condition,
            "may_claim_standard_global_p_not_np": False,
            "reason": (
                "The typechecked Agda package fields are bound to the replayed simulation and semantic-X certificates."
                if pass_condition
                else "One or more package fields lacks a replayed source certificate."
            ),
        },
        "non_claims": [
            "This does not prove standard global P != NP by itself.",
            "This does not embed the JSON replay proofs into Agda terms.",
            "This does not include oracle/advice/X extraction inside public P.",
        ],
        "next_highest_yield_item": {
            "id": "standard_p_not_np_promotion_certificate",
            "action": (
                "Use the bound P_CVX/standard-P equivalence, model separation, SAT-complete E(phi), "
                "and standard-NP witness interface to emit the standard-statement promotion certificate."
            ),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P_CVX / Standard P Equivalence Witness",
        "",
        "## Status",
        "",
        f"- `{report['status']}`",
        "",
        "## Bound Fields",
        "",
    ]
    for key, item in report["field_bindings"].items():
        lines.append(f"- `{key}`: passed=`{item['passed']}`; source=`{item['bound_by']}`")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Equivalence witness bound: `{report['decision']['may_claim_equivalence_witness_bound']}`",
            f"- P_CVX equals standard P: `{report['decision']['may_claim_p_cvx_equals_standard_p']}`",
            f"- Standard global P != NP from this artifact alone: `{report['decision']['may_claim_standard_global_p_not_np']}`",
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
    return 0 if report["decision"]["may_claim_equivalence_witness_bound"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
