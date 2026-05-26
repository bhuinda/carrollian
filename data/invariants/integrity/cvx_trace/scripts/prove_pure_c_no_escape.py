from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
TRACE_PATHS = [
    BASE / "traces" / "cadical_lrat_contradiction_4.trace.json",
    BASE / "traces" / "public_dpll_contradiction_4.trace.json",
]
TOTALITY_REPORT = BASE / "reports" / "solver_opcode_totality_report.json"
REPORT_PATH = BASE / "reports" / "pure_c_no_escape_report.json"


PUBLIC_CLASS_PREFIX = "C_PUBLIC_"
ALLOWED_PUBLIC_FORMATS = {"lrat", "solver_opcode"}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_trace(path: Path) -> dict[str, Any]:
    trace = load_json(path)
    errors: list[str] = []
    summary = trace.get("summary", {})
    counts = summary.get("integrity_counts", {})
    events = trace.get("events", [])

    if summary.get("event_count") != len(events):
        errors.append("event_count does not match events")
    if summary.get("pure_c_trace") is not True:
        errors.append("trace summary is not pure C")
    if summary.get("all_events_classified") is not True:
        errors.append("trace summary is not fully classified")
    if counts.get("C", 0) != len(events):
        errors.append("C count does not equal event count")
    for key in ("V", "X", "UNCLASSIFIED"):
        if counts.get(key, 0) != 0:
            errors.append(f"{key} count is nonzero")
    proof_format = trace.get("source", {}).get("proof_format")
    if proof_format not in ALLOWED_PUBLIC_FORMATS:
        errors.append(f"unsupported public proof/source format: {proof_format}")

    event_failures: list[dict[str, Any]] = []
    class_codes: set[str] = set()
    for event in events:
        event_errors: list[str] = []
        class_code = event.get("class_code", "")
        class_codes.add(class_code)
        if event.get("integrity_type") != "C":
            event_errors.append("event is not C")
        if not class_code.startswith(PUBLIC_CLASS_PREFIX):
            event_errors.append("class code is not public C")
        checks = event.get("checks", {})
        if checks.get("uses_extension_variable") is not False:
            event_errors.append("event uses extension variable")
        if checks.get("locally_checkable") is not True:
            event_errors.append("event is not locally checkable")
        if event.get("op") == "residue":
            event_errors.append("residue event cannot enter pure-C no-escape antecedent")
        if event_errors:
            event_failures.append(
                {
                    "event_id": event.get("event_id"),
                    "class_code": class_code,
                    "errors": event_errors,
                }
            )

    return {
        "trace_path": rel(path),
        "trace_id": trace.get("trace_id"),
        "event_count": len(events),
        "verdict": summary.get("verdict"),
        "class_codes": sorted(class_codes),
        "antecedent_holds": not errors and not event_failures,
        "errors": errors,
        "event_failures": event_failures,
    }


def check_totality() -> dict[str, Any]:
    totality = load_json(TOTALITY_REPORT)
    errors: list[str] = []
    if totality.get("status") != "SOLVER_OPCODE_TOTALITY_WITNESS_PASS":
        errors.append("totality witness did not pass")
    if totality.get("accepted_trace_residue_count") != 0:
        errors.append("accepted trace has residues")
    if totality.get("fallback_fixture", {}).get("status") != "residue":
        errors.append("unsupported fallback fixture did not emit residue")
    if totality.get("fallback_fixture", {}).get("integrity_type") != "UNCLASSIFIED":
        errors.append("unsupported fallback fixture is not UNCLASSIFIED")
    return {
        "path": rel(TOTALITY_REPORT),
        "status": totality.get("status"),
        "antecedent_holds": not errors,
        "errors": errors,
    }


def main() -> int:
    trace_checks = [check_trace(path) for path in TRACE_PATHS]
    totality_check = check_totality()
    all_trace_antecedents = all(item["antecedent_holds"] for item in trace_checks)
    antecedent_holds = all_trace_antecedents and totality_check["antecedent_holds"]
    event_count = sum(item["event_count"] for item in trace_checks)
    class_codes = sorted({code for item in trace_checks for code in item["class_codes"]})
    report = {
        "schema": "d20.integrity.pure_c_no_escape_report.source_drop",
        "status": "PURE_C_NO_ESCAPE_WITNESS_PASS" if antecedent_holds else "PURE_C_NO_ESCAPE_WITNESS_FAIL",
        "theorem_replayed": "No Public Extractor Theorem",
        "antecedent": "All accepted trace events are public C, locally checkable, non-residue, and contain no extension-variable or extractor step.",
        "conditional_conclusion": "For these accepted traces, the certified No Public Extractor theorem applies: the traces do not recover the hidden e33 obstruction and remain within public-integral consequences.",
        "non_claim": "This report does not prove arbitrary polynomial-time no-escape, an X-extractor lower bound, or P != NP. It only checks the current accepted pure-C traces.",
        "trace_count": len(trace_checks),
        "event_count": event_count,
        "public_class_codes": class_codes,
        "trace_checks": trace_checks,
        "totality_check": totality_check,
        "accepted_antecedent_holds": antecedent_holds,
        "next_blocker": "x_extractor_lower_bound",
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["status"].endswith("_PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
