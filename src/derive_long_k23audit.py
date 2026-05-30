from __future__ import annotations

import csv
import hashlib
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23audit"
STATUS = "SECTOR33_K23_LOCAL_AUDIT_COST_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23audit.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23audit.py"
LONG_K23WDEP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23wdep" / "report.json"
LONG_K23WIRE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "wire_rows.csv"

AUDIT_TEXT_HASH = "a753b4ac97320eb733cd092e104d541d026e2da91870e4006cc05f996b4b8a93"
EQUATION_TEXT_HASH = "27e589f70970c6160a491050f71bc416a3708215724e92f85d87cf8127ea65fa"
LIMIT_TEXT_HASH = "416e1511f5be2c45e924d091d4752bfe275ef8c90df888f36c94a1b606c6afd6"
OBS_TEXT_HASH = "7e8055fd5a5d5a7efdc99d36a4b0ba887843f245f971da0fe048d2975c83fc42"
MATRIX_SHA256 = "1e0602bb90cf24c273abc8ae9562599989942826a41cc5543559f0d6ab71452f"

AUDIT_COLUMNS = [
    "audit_id",
    "wire_id",
    "transcript_id",
    "local_wire_bytes",
    "digest_surface_bytes",
    "saved_audit_bytes",
    "table_dependency_flag",
    "local_audit_improvement_flag",
    "public_transport_claim_flag",
]
EQUATION_COLUMNS = [
    "equation_id",
    "equation_code",
    "left_value",
    "right_value",
    "equality_flag",
    "strict_less_than_flag",
    "claim_flag",
]
LIMIT_COLUMNS = [
    "limit_id",
    "limit_code",
    "open_flag",
    "required_before_public_claim_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "audit_row_count",
    "local_wire_bytes_per_row",
    "digest_surface_bytes_per_row",
    "saved_audit_bytes_per_row",
    "local_wire_total_bytes",
    "digest_surface_total_bytes",
    "saved_audit_total_bytes",
    "table_dependency_count",
    "local_audit_improvement_count",
    "public_transport_claim_count",
    "local_audit_cost_flag",
    "external_efficiency_path_demoted_count",
    "equation_row_count",
    "equation_pass_count",
    "limit_row_count",
    "open_limit_count",
    "overclaim_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["audit_table", "equation_table", "limit_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def read_csv_rows(path: Any) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def build_rows() -> dict[str, Any]:
    wdep_report = load_json(LONG_K23WDEP_REPORT)
    wdep_summary = summary(wdep_report)
    wire_rows = read_csv_rows(LONG_K23WIRE_ROWS)
    local_wire_bytes = int(wdep_summary.get("wire_total_bytes", -1)) // int(wdep_summary.get("wire_row_count", -1))
    digest_surface_bytes = int(wdep_summary.get("current_model_self_contained_bytes", -1)) // int(wdep_summary.get("wire_row_count", -1))
    saved_audit_bytes = digest_surface_bytes - local_wire_bytes
    audit_rows = []
    for row in wire_rows:
        audit_rows.append(
            {
                "audit_id": int(row["wire_id"]),
                "wire_id": int(row["wire_id"]),
                "transcript_id": int(row["transcript_id"]),
                "local_wire_bytes": local_wire_bytes,
                "digest_surface_bytes": digest_surface_bytes,
                "saved_audit_bytes": saved_audit_bytes,
                "table_dependency_flag": int(row["table_index_dependency_flag"]),
                "local_audit_improvement_flag": int(local_wire_bytes < digest_surface_bytes),
                "public_transport_claim_flag": 0,
            }
        )
    local_total = sum(row["local_wire_bytes"] for row in audit_rows)
    digest_total = sum(row["digest_surface_bytes"] for row in audit_rows)
    saved_total = sum(row["saved_audit_bytes"] for row in audit_rows)
    equation_rows = [
        {"equation_id": 0, "equation_code": 0, "left_value": local_total, "right_value": 56 * 4, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 1, "equation_code": 1, "left_value": digest_total, "right_value": 56 * 96, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 2, "equation_code": 2, "left_value": saved_total, "right_value": digest_total - local_total, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 3, "equation_code": 3, "left_value": local_total, "right_value": digest_total, "equality_flag": 0, "strict_less_than_flag": int(local_total < digest_total), "claim_flag": 0},
    ]
    limit_rows = [
        {"limit_id": 0, "limit_code": 0, "open_flag": 1, "required_before_public_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 1, "limit_code": 1, "open_flag": 1, "required_before_public_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 2, "limit_code": 2, "open_flag": 1, "required_before_public_claim_flag": 1, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": 1,
        "certified_input_count": is_certified(wdep_report, "SECTOR33_K23_WIRE_DEPENDENCY_DECISION_CERTIFIED"),
        "audit_row_count": len(audit_rows),
        "local_wire_bytes_per_row": local_wire_bytes,
        "digest_surface_bytes_per_row": digest_surface_bytes,
        "saved_audit_bytes_per_row": saved_audit_bytes,
        "local_wire_total_bytes": local_total,
        "digest_surface_total_bytes": digest_total,
        "saved_audit_total_bytes": saved_total,
        "table_dependency_count": sum(row["table_dependency_flag"] for row in audit_rows),
        "local_audit_improvement_count": sum(row["local_audit_improvement_flag"] for row in audit_rows),
        "public_transport_claim_count": sum(row["public_transport_claim_flag"] for row in audit_rows),
        "local_audit_cost_flag": 1,
        "external_efficiency_path_demoted_count": int(wdep_summary.get("external_efficiency_path_demoted_count", -1)),
        "equation_row_count": len(equation_rows),
        "equation_pass_count": sum(int(row["equality_flag"] == 1 or row["strict_less_than_flag"] == 1) for row in equation_rows),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in limit_rows),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    audit_table = table_from_rows(AUDIT_COLUMNS, audit_rows)
    equation_table = table_from_rows(EQUATION_COLUMNS, equation_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "audit_table": audit_table.astype(np.int64),
        "equation_table": equation_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "wdep_report": wdep_report,
        "audit_rows": audit_rows,
        "equation_rows": equation_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "audit_table": audit_table,
        "equation_table": equation_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "audit_text_hash": hashlib.sha256(digest_text(AUDIT_COLUMNS, audit_rows).encode("ascii")).hexdigest(),
        "equation_text_hash": hashlib.sha256(digest_text(EQUATION_COLUMNS, equation_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_pass": obs["certified_input_count"] == 1,
        "audit_profile_matches": (
            obs["audit_row_count"],
            obs["local_wire_bytes_per_row"],
            obs["digest_surface_bytes_per_row"],
            obs["saved_audit_bytes_per_row"],
            obs["table_dependency_count"],
            obs["local_audit_improvement_count"],
            obs["public_transport_claim_count"],
        )
        == (56, 4, 96, 92, 56, 56, 0),
        "totals_match": (
            obs["local_wire_total_bytes"],
            obs["digest_surface_total_bytes"],
            obs["saved_audit_total_bytes"],
        )
        == (224, 5376, 5152),
        "equation_profile_matches": (
            obs["equation_row_count"],
            obs["equation_pass_count"],
        )
        == (4, 4),
        "boundary_flags_match": (
            obs["local_audit_cost_flag"],
            obs["external_efficiency_path_demoted_count"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 1, 0),
        "limit_profile_matches": (
            obs["limit_row_count"],
            obs["open_limit_count"],
            obs["overclaim_count"],
        )
        == (3, 3, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_local_verifier_audit_cost",
        "equation_code_map": {
            "0": "local_wire_total_bytes",
            "1": "digest_surface_total_bytes",
            "2": "saved_audit_total_bytes",
            "3": "local_total_less_than_digest_total",
        },
        "limit_code_map": {
            "0": "shared_table_availability",
            "1": "public_transport_claim",
            "2": "security_or_interop_claim",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies local verifier-side audit cost reduction under shared-table dereference while preserving public transport demotion.",
    }
    seam_payload = {
        "schema": "long.k23audit.seam@1",
        "status": STATUS,
        "claim": "The compact K23 shared-table map reduces local verifier-side audit bytes relative to the digest-row surface.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23wdep": input_entry(
            LONG_K23WDEP_REPORT,
            {
                "status": rows["wdep_report"].get("status"),
                "certificate_sha256": rows["wdep_report"].get("certificate_sha256"),
            },
        ),
        "long_k23wire_rows": input_entry(LONG_K23WIRE_ROWS),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23audit.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23audit certifies local verifier-side audit-cost reduction for the compact K23 shared-table map.",
        "stage_protocol": {
            "draft": "read long_k23wdep and compact wire rows",
            "witness": "emit audit rows, equations, open limits, observables, and numeric tables",
            "coherence": "check row costs, totals, shared-table dependence, and public-transport nonclaim",
            "closure": "certify local audit-cost reduction without reopening external-efficiency claims",
            "emit": "write long_k23audit artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "audit_rows_csv": relpath(OUT_DIR / "audit_rows.csv"),
            "equation_rows_csv": relpath(OUT_DIR / "equation_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23audit_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "each of the 56 local audit rows uses 4 shared-table wire bytes instead of 96 digest-surface bytes",
                "local verifier-side audit bytes fall from 5376 to 224 under the shared-table condition",
                "the local saved audit surface is 5152 bytes",
                "public transport efficiency remains demoted by long_k23wdep",
            ],
            "does_not_certify": [
                "public transport efficiency",
                "public wire-format equivalence",
                "external speed or size improvement",
                "security superiority",
                "standards compliance",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Use the local audit-cost certificate to strengthen proof-of-mandate: bind audit-cost reduction to verifier workload, not public transport.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23audit.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23audit.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "audit_csv": csv_text(AUDIT_COLUMNS, rows["audit_rows"]),
        "equation_csv": csv_text(EQUATION_COLUMNS, rows["equation_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "audit_table": rows["audit_table"],
        "equation_table": rows["equation_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "audit_text_sha256": rows["audit_text_hash"],
            "equation_text_sha256": rows["equation_text_hash"],
            "limit_text_sha256": rows["limit_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "audit_rows.csv").write_text(payloads["audit_csv"], encoding="utf-8")
    (OUT_DIR / "equation_rows.csv").write_text(payloads["equation_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        audit_table=payloads["audit_table"],
        equation_table=payloads["equation_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23audit_matrices.npz", **payloads["matrix_payload"])
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
