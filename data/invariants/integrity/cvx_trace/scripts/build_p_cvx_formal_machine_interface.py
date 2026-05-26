from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
FORMAL_PATH = CVX / "formal" / "PcvxStandardMachineInterface.agda"
REPORT_PATH = CVX / "reports" / "p_cvx_formal_machine_interface.json"
NOTE_PATH = CVX / "reports" / "p_cvx_formal_machine_interface.md"
AGDA_VALIDATION_COMMAND = (
    "agda -v0 -i data/invariants/integrity/cvx_trace/formal "
    "data/invariants/integrity/cvx_trace/formal/PcvxStandardMachineInterface.agda"
)
AGDA_COMMAND = [
    "agda",
    "-v0",
    "-i",
    "data/invariants/integrity/cvx_trace/formal",
    "data/invariants/integrity/cvx_trace/formal/PcvxStandardMachineInterface.agda",
]

REQUIRED_DECLARATIONS = {
    "Language": "Language : Set",
    "StandardMachine": "record StandardMachine : Set1 where",
    "StandardP": "StandardP : Language -> Set1",
    "StandardNP": "StandardNP : Language -> Set1",
    "CvxProgram": "record CvxProgram : Set where",
    "COnlyTrace": "data COnlyTrace : List CvxEventKind -> Set where",
    "NoXTrace": "data NoXTrace : List CvxEventKind -> Set where",
    "P_CVX": "P_CVX : Language -> Set",
    "NP_CVX": "NP_CVX : Language -> Set1",
    "PCVXStandardPEquivalence": "PCVXStandardPEquivalence : Set1",
    "SemanticXBoundary": "record SemanticXBoundary : Set1 where",
    "PCVXStandardPIdentificationPackage": "record PCVXStandardPIdentificationPackage : Set1 where",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def declaration_audit(source: str) -> dict[str, Any]:
    rows = {}
    for name, needle in REQUIRED_DECLARATIONS.items():
        rows[name] = {
            "needle": needle,
            "passed": needle in source,
        }
    return rows


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
    exists = FORMAL_PATH.exists()
    source = FORMAL_PATH.read_text(encoding="utf-8") if exists else ""
    declarations = declaration_audit(source)
    typecheck = typecheck_audit() if exists else {
        "command": " ".join(AGDA_COMMAND),
        "returncode": None,
        "stdout": "",
        "stderr": "formal file is missing",
        "passed": False,
    }
    declarations_pass = exists and all(row["passed"] for row in declarations.values())
    pass_condition = declarations_pass and typecheck["passed"]

    return {
        "schema": "d20.integrity.p_cvx_formal_machine_interface.source_drop",
        "status": (
            "P_CVX_STANDARD_P_FORMAL_MACHINE_INTERFACE_DEFINED"
            if pass_condition
            else "P_CVX_STANDARD_P_FORMAL_MACHINE_INTERFACE_INCOMPLETE"
        ),
        "claim_level": "proof_assistant_definition_interface",
        "formal_file": {
            "path": rel(FORMAL_PATH),
            "exists": exists,
            "language": "Agda",
            "sha256": sha256(FORMAL_PATH) if exists else None,
            "validation_command": AGDA_VALIDATION_COMMAND,
        },
        "typecheck_audit": typecheck,
        "declaration_audit": declarations,
        "definitions": {
            "standard_p": (
                "StandardP is a language-indexed proof-assistant machine class witnessed by a public "
                "standard machine, a polynomial time bound, and a decision proof."
            ),
            "p_cvx": (
                "P_CVX is a language-indexed proof-assistant machine class witnessed by a finite public "
                "C/V/X program whose traces are C-only/no-X and decide the language."
            ),
            "equivalence_package": (
                "PCVXStandardPIdentificationPackage names the two class maps plus the semantic X boundary "
                "needed to package an extensional equivalence."
            ),
        },
        "decision": {
            "may_claim_standard_p_formally_defined": declarations["StandardP"]["passed"],
            "may_claim_p_cvx_formally_defined": declarations["P_CVX"]["passed"],
            "may_claim_agda_typechecked": typecheck["passed"],
            "may_claim_np_interfaces_formally_defined": (
                declarations["StandardNP"]["passed"] and declarations["NP_CVX"]["passed"]
            ),
            "may_claim_equivalence_package_type_defined": declarations[
                "PCVXStandardPIdentificationPackage"
            ]["passed"],
            "may_claim_standard_global_p_not_np": False,
            "reason": (
                "The proof-assistant interface now defines the machine classes and the equivalence package "
                "type. The file is an interface layer; theorem-level standard P != NP promotion still depends "
                "on replayed certificates and external/proof-assistant review."
            ),
        },
        "non_claims": [
            "This interface does not by itself prove standard global P != NP.",
            "This interface does not certify the replayed JSON artifacts inside Agda.",
            "This interface does not postulate oracle, advice, or hidden extractor access as public P.",
        ],
        "next_highest_yield_item": {
            "id": "formal_equivalence_witness_binding",
            "action": (
                "Bind the certified P_CVX-to-standard and standard-to-P_CVX simulation reports to the "
                "PCVXStandardPIdentificationPackage fields."
            ),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P_CVX / Standard P Formal Machine Interface",
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
        "## Definitions",
        "",
    ]
    for key, text in report["definitions"].items():
        lines.append(f"- `{key}`: {text}")
    lines.extend(["", "## Declaration Audit", ""])
    for key, item in report["declaration_audit"].items():
        lines.append(f"- `{key}`: passed=`{item['passed']}`")
    lines.extend(["", "## Next", "", report["next_highest_yield_item"]["action"], ""])
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    NOTE_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(report["status"])
    return 0 if report["status"] == "P_CVX_STANDARD_P_FORMAL_MACHINE_INTERFACE_DEFINED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
