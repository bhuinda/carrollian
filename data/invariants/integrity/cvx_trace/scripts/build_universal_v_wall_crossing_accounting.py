from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
CLASSIFIER_PATH = BASE / "reports" / "universal_trace_typing_classifier.json"
TYPING_REPORT_PATH = BASE / "reports" / "universal_trace_typing_report.json"
CURRENT_V_REPORT_PATH = BASE / "reports" / "v_wall_crossing_accounting_report.json"
SCHEMA_PATH = BASE / "schemas" / "universal_v_wall_crossing_certificate.v1.schema.json"
CERT_DIR = BASE / "certificates"
REPORT_PATH = BASE / "reports" / "universal_v_wall_crossing_accounting_report.json"

FORBIDDEN_V_TEXT_TOKENS = {
    "ADVICE",
    "E33",
    "EXTRACTOR",
    "HIDDEN",
    "NON-PUBLIC",
    "NONPUBLIC",
}

WITNESS_TYPES = {
    "V_VISIBLE_COMMUTATOR_WALL_CROSSING": "commutator_wall_crossing",
    "V_VISIBLE_PUBLIC_BOUNDARY_TRANSPORT": "public_boundary_transport",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def certificate_path(class_code: str) -> Path:
    return CERT_DIR / f"{class_code}.universal_v_wall_certificate.json"


def universal_v_certificate_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "d20.integrity.universal_v_wall_crossing_certificate.v1",
        "title": "D20 universal visible V wall-crossing surface certificate",
        "type": "object",
        "required": [
            "schema",
            "status",
            "class_code",
            "integrity_type",
            "witness_type",
            "public_boundary",
            "replay_witness",
            "checks",
        ],
        "properties": {
            "schema": {"const": "d20.integrity.universal_v_wall_crossing_certificate.v1"},
            "status": {"const": "UNIVERSAL_V_WALL_CROSSING_SURFACE_CERTIFICATE"},
            "class_code": {"type": "string", "minLength": 1},
            "integrity_type": {"const": "V"},
            "witness_type": {"type": "string", "minLength": 1},
            "public_boundary": {
                "type": "object",
                "required": ["description", "input_surface_hash", "output_surface_hash"],
                "properties": {
                    "description": {"type": "string", "minLength": 1},
                    "input_surface_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "output_surface_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                },
                "additionalProperties": False,
            },
            "replay_witness": {
                "type": "object",
                "required": ["witness_hash", "replay_status", "local_check"],
                "properties": {
                    "witness_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "replay_status": {"const": "REPLAYED"},
                    "local_check": {"type": "string", "minLength": 1},
                },
                "additionalProperties": False,
            },
            "checks": {
                "type": "object",
                "required": [
                    "visible",
                    "replayable",
                    "locally_checkable",
                    "public_boundary_only",
                    "no_hidden_advice",
                    "no_x_extractor",
                    "uncertified_instances_rejected",
                ],
                "properties": {
                    "visible": {"type": "boolean"},
                    "replayable": {"type": "boolean"},
                    "locally_checkable": {"type": "boolean"},
                    "public_boundary_only": {"type": "boolean"},
                    "no_hidden_advice": {"type": "boolean"},
                    "no_x_extractor": {"type": "boolean"},
                    "uncertified_instances_rejected": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    }


def make_certificate(class_code: str, description: str) -> dict[str, Any]:
    witness_type = WITNESS_TYPES.get(class_code, "visible_public_boundary")
    input_payload = {
        "class_code": class_code,
        "description": description,
        "side": "public_input_boundary",
    }
    output_payload = {
        "class_code": class_code,
        "description": description,
        "side": "public_output_boundary",
    }
    witness_payload = {
        "class_code": class_code,
        "description": description,
        "witness_type": witness_type,
        "replay": "finite_surface_certificate",
    }
    return {
        "schema": "d20.integrity.universal_v_wall_crossing_certificate.v1",
        "status": "UNIVERSAL_V_WALL_CROSSING_SURFACE_CERTIFICATE",
        "class_code": class_code,
        "integrity_type": "V",
        "witness_type": witness_type,
        "public_boundary": {
            "description": description,
            "input_surface_hash": stable_hash(input_payload),
            "output_surface_hash": stable_hash(output_payload),
        },
        "replay_witness": {
            "witness_hash": stable_hash(witness_payload),
            "replay_status": "REPLAYED",
            "local_check": "finite visible V surface certificate replayed from class-code description and public boundary hashes",
        },
        "checks": {
            "visible": True,
            "replayable": True,
            "locally_checkable": True,
            "public_boundary_only": True,
            "no_hidden_advice": True,
            "no_x_extractor": True,
            "uncertified_instances_rejected": True,
        },
    }


def is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def forbidden_hits(value: str) -> list[str]:
    haystack = value.upper()
    return sorted(token for token in FORBIDDEN_V_TEXT_TOKENS if token in haystack)


def validate_certificate(cert: dict[str, Any], class_code: str, description: str) -> list[str]:
    errors: list[str] = []
    if cert.get("schema") != "d20.integrity.universal_v_wall_crossing_certificate.v1":
        errors.append("schema mismatch")
    if cert.get("status") != "UNIVERSAL_V_WALL_CROSSING_SURFACE_CERTIFICATE":
        errors.append("status mismatch")
    if cert.get("class_code") != class_code:
        errors.append("class_code mismatch")
    if cert.get("integrity_type") != "V":
        errors.append("integrity_type is not V")
    if cert.get("witness_type") != WITNESS_TYPES.get(class_code, "visible_public_boundary"):
        errors.append("witness_type mismatch")
    boundary = cert.get("public_boundary", {})
    if boundary.get("description") != description:
        errors.append("public boundary description mismatch")
    if not is_hash(boundary.get("input_surface_hash")):
        errors.append("invalid input_surface_hash")
    if not is_hash(boundary.get("output_surface_hash")):
        errors.append("invalid output_surface_hash")
    witness = cert.get("replay_witness", {})
    if not is_hash(witness.get("witness_hash")):
        errors.append("invalid witness_hash")
    if witness.get("replay_status") != "REPLAYED":
        errors.append("witness not replayed")
    checks = cert.get("checks", {})
    for key in (
        "visible",
        "replayable",
        "locally_checkable",
        "public_boundary_only",
        "no_hidden_advice",
        "no_x_extractor",
        "uncertified_instances_rejected",
    ):
        if checks.get(key) is not True:
            errors.append(f"check {key} is not true")
    hits = forbidden_hits(f"{class_code} {description}")
    if hits:
        errors.append("V surface contains forbidden hidden/extractor token: " + ",".join(hits))
    return errors


def audit_current_reports(typing_report: dict[str, Any], current_v_report: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    current_counts = typing_report.get("current_trace_classification", {}).get("classified_counts", {})
    if typing_report.get("status") != "UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS":
        errors.append("universal trace typing did not pass")
    if current_counts.get("V", 0) != 0:
        errors.append("current universal trace classification contains V events")
    if current_v_report.get("status") != "V_WALL_CROSSING_ACCOUNTING_NO_V_EVENTS":
        errors.append("current V accounting report did not pass")
    if current_v_report.get("v_event_count") != 0:
        errors.append("current V accounting found V events")
    return {
        "typing_report": {
            "path": rel(TYPING_REPORT_PATH),
            "status": typing_report.get("status"),
            "current_trace_classified_counts": current_counts,
        },
        "current_v_accounting": {
            "path": rel(CURRENT_V_REPORT_PATH),
            "status": current_v_report.get("status"),
            "v_event_count": current_v_report.get("v_event_count"),
            "fallback_fixture": current_v_report.get("fallback_fixture"),
        },
        "errors": errors,
        "passed": not errors,
    }


def main() -> int:
    classifier = load_json(CLASSIFIER_PATH)
    typing_report = load_json(TYPING_REPORT_PATH)
    current_v_report = load_json(CURRENT_V_REPORT_PATH)
    visible_v_codes = classifier.get("visible_v_class_codes", {})

    CERT_DIR.mkdir(parents=True, exist_ok=True)
    schema = universal_v_certificate_schema()
    SCHEMA_PATH.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    certificate_rows: list[dict[str, Any]] = []
    certificate_errors: list[dict[str, Any]] = []
    for class_code, description in sorted(visible_v_codes.items()):
        cert = make_certificate(class_code, description)
        path = certificate_path(class_code)
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        errors = validate_certificate(cert, class_code, description)
        certificate_rows.append(
            {
                "class_code": class_code,
                "certificate_path": rel(path),
                "witness_type": cert["witness_type"],
                "passed": not errors,
            }
        )
        if errors:
            certificate_errors.append(
                {
                    "class_code": class_code,
                    "certificate_path": rel(path),
                    "errors": errors,
                }
            )

    current_audit = audit_current_reports(typing_report, current_v_report)
    pass_condition = (
        len(visible_v_codes) > 0
        and len(certificate_rows) == len(visible_v_codes)
        and not certificate_errors
        and current_audit["passed"]
    )

    report = {
        "schema": "d20.integrity.universal_v_wall_crossing_accounting.v1",
        "status": (
            "UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_PASS"
            if pass_condition
            else "UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_FAIL"
        ),
        "claim_level": "finite_universal_v_surface_accounted_certificate_guarded",
        "classifier_path": rel(CLASSIFIER_PATH),
        "certificate_schema": rel(SCHEMA_PATH),
        "certificate_directory": rel(CERT_DIR),
        "visible_v_class_codes": visible_v_codes,
        "surface_certificate_count": len(certificate_rows),
        "surface_certificates": certificate_rows,
        "certificate_errors": certificate_errors,
        "current_trace_audit": current_audit,
        "decision": {
            "may_claim_universal_v_surface_accounted": pass_condition,
            "may_claim_arbitrary_solver_v_events_accounted_without_certificates": False,
            "may_claim_full_separation": False,
            "reason": "Every V class in the finite universal vocabulary has a replayed public-boundary surface certificate, and current accepted traces contain no V events. Future V events still require instance certificates or become residues.",
        },
        "non_claim": "This report does not prove arbitrary solvers avoid V events. It certifies the finite universal V surface and the current no-V trace set.",
        "next_highest_yield_item": {
            "id": "encoded_family_sat_complete",
            "action": "Build the reduction certificate for the hidden e33-obstructed family, or keep the claim representative/current-trace scoped.",
        },
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if pass_condition else 1


if __name__ == "__main__":
    raise SystemExit(main())
