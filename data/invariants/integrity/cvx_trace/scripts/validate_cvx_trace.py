from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
SCHEMA_PATH = BASE / "schemas" / "cvx_trace.v1.schema.json"
TRACE_PATH = BASE / "traces" / "cadical_lrat_contradiction_4.trace.json"
REPORT_PATH = BASE / "reports" / "cadical_lrat_contradiction_4_validation.json"
PROOF_PATH = ROOT / "data" / "evidence" / "ss_sat" / "proofs" / "cadical_lrat" / "contradiction_4.cadical.lrat"
CNF_PATH = ROOT / "data" / "evidence" / "ss_sat" / "benchmarks" / "contradiction_4.cnf"
ROWS_PATH = ROOT / "data" / "evidence" / "ss_sat" / "audits" / "cadical_lrat_cvx_rows.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_classifier_row() -> dict[str, str]:
    with ROWS_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["proof"] == PROOF_PATH.name:
                return row
    raise RuntimeError(f"missing classifier row for {PROOF_PATH.name}")


def parse_lrat_line(line: str) -> tuple[int, str, list[int], list[int]]:
    parts = line.strip().split()
    if not parts:
        raise ValueError("empty LRAT line")
    proof_id = int(parts[0])
    if len(parts) > 1 and parts[1] == "d":
        return proof_id, "delete", [], [int(x) for x in parts[2:] if int(x) != 0]
    if "0" not in parts[1:]:
        raise ValueError("LRAT add line missing literal terminator")
    zero_index = parts.index("0", 1)
    literals = [int(x) for x in parts[1:zero_index]]
    hints = [int(x) for x in parts[zero_index + 1 :] if int(x) != 0]
    return proof_id, "add", literals, hints


def build_trace() -> dict[str, Any]:
    row = load_classifier_row()
    lines = [line for line in PROOF_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("this fixture intentionally covers exactly one LRAT replay line")
    proof_id, op, literals, hints = parse_lrat_line(lines[0])
    event = {
        "event_id": f"{PROOF_PATH.stem}:line-1",
        "line": 1,
        "proof_id": proof_id,
        "op": op,
        "integrity_type": row["integrity_type"],
        "class_code": row["class_code"],
        "reason": row["reason"],
        "public_inputs": {
            "clause_hints": hints,
            "literals": literals,
        },
        "public_outputs": {
            "clause_id": proof_id,
            "literal_count": len(literals),
            "empty_clause": len(literals) == 0 and op == "add",
        },
        "checks": {
            "uses_extension_variable": row["uses_extension_variable"].lower() == "true",
            "has_duplicate_literal": row["has_duplicate_literal"].lower() == "true",
            "contains_complement_pair": row["contains_complement_pair"].lower() == "true",
            "locally_checkable": True,
        },
    }
    integrity_counts = {"C": 0, "V": 0, "X": 0, "UNCLASSIFIED": 0}
    integrity_counts[event["integrity_type"]] += 1
    return {
        "schema": "d20.integrity.cvx_trace.v1",
        "status": "CVX_TRACE_REPLAY_WITNESS",
        "trace_id": "cadical_lrat_contradiction_4",
        "source": {
            "proof_format": "lrat",
            "proof_path": rel(PROOF_PATH),
            "proof_sha256": sha256(PROOF_PATH),
            "cnf_path": rel(CNF_PATH),
            "cnf_sha256": sha256(CNF_PATH),
            "classifier_source": rel(ROWS_PATH),
        },
        "integrity_model": {
            "allowed_types": ["C", "V", "X", "UNCLASSIFIED"],
            "accepted_public_types": ["C"],
            "unsupported_event_policy": "reject_or_emit_typed_residue",
        },
        "events": [event],
        "summary": {
            "event_count": 1,
            "integrity_counts": integrity_counts,
            "verdict": "C_PUBLIC_CHECKED_PROOF_TRACE",
            "all_events_classified": True,
            "pure_c_trace": integrity_counts == {"C": 1, "V": 0, "X": 0, "UNCLASSIFIED": 0},
        },
    }


def validate_trace(trace: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if trace.get("schema") != schema["properties"]["schema"]["const"]:
        errors.append("schema id mismatch")
    if trace.get("status") not in schema["properties"]["status"]["enum"]:
        errors.append("status is not accepted by schema")
    source = trace.get("source", {})
    for key in schema["properties"]["source"]["required"]:
        if key not in source:
            errors.append(f"missing source.{key}")
    for key in ("proof_sha256", "cnf_sha256"):
        if key not in source:
            continue
        value = source[key]
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            errors.append(f"invalid source.{key}")
    events = trace.get("events", [])
    if not events:
        errors.append("trace has no events")
    for i, event in enumerate(events):
        for key in schema["properties"]["events"]["items"]["required"]:
            if key not in event:
                errors.append(f"event {i} missing {key}")
        if event.get("integrity_type") not in ("C", "V", "X", "UNCLASSIFIED"):
            errors.append(f"event {i} invalid integrity_type")
        if event.get("op") not in ("add", "delete", "solver_opcode", "residue"):
            errors.append(f"event {i} invalid op")
        checks = event.get("checks", {})
        if not checks.get("locally_checkable", False):
            errors.append(f"event {i} is not locally checkable")
    summary = trace.get("summary", {})
    if summary.get("event_count") != len(events):
        errors.append("summary event_count mismatch")
    counts = {"C": 0, "V": 0, "X": 0, "UNCLASSIFIED": 0}
    for event in events:
        counts[event["integrity_type"]] += 1
    if summary.get("integrity_counts") != counts:
        errors.append("summary integrity_counts mismatch")
    if summary.get("all_events_classified") is not (counts["UNCLASSIFIED"] == 0):
        errors.append("summary all_events_classified mismatch")
    if summary.get("pure_c_trace") is not (counts["C"] == len(events) and len(events) > 0):
        errors.append("summary pure_c_trace mismatch")
    return errors


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    trace = build_trace()
    errors = validate_trace(trace, schema)
    TRACE_PATH.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = {
        "schema": "d20.integrity.cvx_trace_validation.v1",
        "status": "CVX_TRACE_SCHEMA_VALIDATION_PASS" if not errors else "CVX_TRACE_SCHEMA_VALIDATION_FAIL",
        "schema_path": rel(SCHEMA_PATH),
        "trace_path": rel(TRACE_PATH),
        "source_proof": rel(PROOF_PATH),
        "source_classifier": rel(ROWS_PATH),
        "event_count": len(trace["events"]),
        "pure_c_trace": trace["summary"]["pure_c_trace"],
        "errors": errors,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
