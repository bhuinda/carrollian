from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
TRACE_PATHS = [
    BASE / "traces" / "cadical_lrat_contradiction_4.trace.json",
    BASE / "traces" / "public_dpll_contradiction_4.trace.json",
]
CLASSIFIER_PATH = BASE / "reports" / "solver_opcode_totality_classifier.json"
CERT_SCHEMA_PATH = BASE / "schemas" / "v_wall_crossing_certificate.v1.schema.json"
CERT_DIR = BASE / "certificates"
REPORT_PATH = BASE / "reports" / "v_wall_crossing_accounting_report.json"
RESIDUE_PATH = BASE / "residues" / "uncertified_v_wall_crossing_residue.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def certificate_name(event_id: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in event_id).strip("_")
    return f"{safe}.v_wall_certificate.json"


def validate_certificate(cert: dict[str, Any], *, event: dict[str, Any], trace_path: Path) -> list[str]:
    errors: list[str] = []
    if cert.get("schema") != "d20.integrity.v_wall_crossing_certificate.v1":
        errors.append("certificate schema mismatch")
    if cert.get("status") != "V_WALL_CROSSING_CERTIFICATE":
        errors.append("certificate status mismatch")
    if cert.get("event_id") != event.get("event_id"):
        errors.append("certificate event_id mismatch")
    if cert.get("trace_path") != rel(trace_path):
        errors.append("certificate trace_path mismatch")
    if cert.get("integrity_type") != "V":
        errors.append("certificate integrity_type mismatch")
    if cert.get("class_code") != "V_VISIBLE_COMMUTATOR_WALL_CROSSING":
        errors.append("certificate class_code mismatch")
    boundary = cert.get("public_boundary", {})
    witness = cert.get("commutator_witness", {})
    for key in ("public_input_hash", "public_output_hash"):
        value = boundary.get(key, "")
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            errors.append(f"invalid public_boundary.{key}")
    value = witness.get("witness_hash", "")
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        errors.append("invalid commutator_witness.witness_hash")
    if witness.get("replay_status") != "REPLAYED":
        errors.append("commutator witness was not replayed")
    checks = cert.get("checks", {})
    for key in ("visible", "replayable", "locally_checkable", "no_hidden_advice", "no_x_extractor"):
        if checks.get(key) is not True:
            errors.append(f"check {key} is not true")
    return errors


def residue_for(event: dict[str, Any], trace_path: Path, reason: str) -> dict[str, Any]:
    return {
        "schema": "d20.integrity.v_wall_crossing_residue.v1",
        "status": "V_WALL_CROSSING_UNCERTIFIED_TYPED_RESIDUE",
        "residue_type": "UNCERTIFIED_VISIBLE_WALL_CROSSING",
        "source_trace": rel(trace_path),
        "event_id": event.get("event_id", "unknown"),
        "integrity_type": event.get("integrity_type", "unknown"),
        "class_code": event.get("class_code", "unknown"),
        "reason": reason,
        "policy": "visible V events require a replayed wall-crossing certificate before entering accepted no-escape accounting",
    }


def fixture_v_event() -> dict[str, Any]:
    return {
        "event_id": "uncertified-v-wall-fixture:0001",
        "line": 1,
        "proof_id": 1,
        "op": "solver_opcode",
        "integrity_type": "V",
        "class_code": "V_VISIBLE_COMMUTATOR_WALL_CROSSING",
        "reason": "fixture event used to witness residue fallback for missing V certificate",
        "public_inputs": {"clause_hints": [], "literals": []},
        "public_outputs": {"clause_id": 1, "literal_count": 0, "empty_clause": False},
        "checks": {
            "uses_extension_variable": False,
            "has_duplicate_literal": False,
            "contains_complement_pair": False,
            "locally_checkable": False,
        },
    }


def main() -> int:
    classifier = load_json(CLASSIFIER_PATH)
    visible_v_codes = set(classifier.get("visible_v_class_codes", {}))
    traces = [(path, load_json(path)) for path in TRACE_PATHS]

    v_events: list[dict[str, Any]] = []
    residues: list[dict[str, Any]] = []
    certificates: list[dict[str, Any]] = []
    certificate_errors: list[dict[str, Any]] = []

    for trace_path, trace in traces:
        for event in trace.get("events", []):
            if event.get("integrity_type") != "V" and event.get("class_code") not in visible_v_codes:
                continue
            row = {
                "trace_path": rel(trace_path),
                "trace_id": trace.get("trace_id"),
                "event_id": event.get("event_id"),
                "integrity_type": event.get("integrity_type"),
                "class_code": event.get("class_code"),
            }
            v_events.append(row)
            if event.get("integrity_type") != "V" or event.get("class_code") not in visible_v_codes:
                residues.append(residue_for(event, trace_path, "event is V-like but not a recognized visible V wall crossing"))
                continue
            cert_path = CERT_DIR / certificate_name(str(event.get("event_id")))
            if not cert_path.exists():
                residues.append(residue_for(event, trace_path, "missing visible V wall-crossing certificate"))
                continue
            cert = load_json(cert_path)
            errors = validate_certificate(cert, event=event, trace_path=trace_path)
            certificates.append({"event_id": event.get("event_id"), "certificate_path": rel(cert_path)})
            if errors:
                certificate_errors.append(
                    {
                        "event_id": event.get("event_id"),
                        "certificate_path": rel(cert_path),
                        "errors": errors,
                    }
                )

    fixture_residue = residue_for(
        fixture_v_event(),
        TRACE_PATHS[-1],
        "missing visible V wall-crossing certificate",
    )
    RESIDUE_PATH.write_text(json.dumps(fixture_residue, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    pass_condition = (
        len(v_events) == 0
        and len(residues) == 0
        and len(certificate_errors) == 0
        and fixture_residue["status"] == "V_WALL_CROSSING_UNCERTIFIED_TYPED_RESIDUE"
        and "V_VISIBLE_COMMUTATOR_WALL_CROSSING" in visible_v_codes
    )
    report = {
        "schema": "d20.integrity.v_wall_crossing_accounting.v1",
        "status": (
            "V_WALL_CROSSING_ACCOUNTING_NO_V_EVENTS"
            if pass_condition
            else "V_WALL_CROSSING_ACCOUNTING_REQUIRES_REVIEW"
        ),
        "certificate_schema": rel(CERT_SCHEMA_PATH),
        "certificate_directory": rel(CERT_DIR),
        "trace_paths": [rel(path) for path in TRACE_PATHS],
        "visible_v_class_codes": sorted(visible_v_codes),
        "v_event_count": len(v_events),
        "v_events": v_events,
        "accepted_certificate_count": len(certificates),
        "accepted_certificates": certificates,
        "residue_count": len(residues),
        "residues": residues,
        "certificate_errors": certificate_errors,
        "fallback_fixture": {
            "status": fixture_residue["status"],
            "residue_path": rel(RESIDUE_PATH),
            "policy": fixture_residue["policy"],
        },
        "result": {
            "visible_v_events_present": bool(v_events),
            "uncertified_v_events_present": bool(residues or certificate_errors),
            "v_accounting_passed": pass_condition,
        },
        "non_claim": "This accounts for visible V events on the current accepted trace set. It does not prove arbitrary solver traces have no V wall crossings.",
        "next_blocker": "full_no_escape_closure",
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if pass_condition else 1


if __name__ == "__main__":
    raise SystemExit(main())
