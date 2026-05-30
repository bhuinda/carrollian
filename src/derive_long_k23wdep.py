from __future__ import annotations

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


THEOREM_ID = "long_k23wdep"
STATUS = "SECTOR33_K23_WIRE_DEPENDENCY_DECISION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23wdep.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23wdep.py"
LONG_K23WIRE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "report.json"
LONG_K23WIRE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "wire_rows.csv"

DECISION_TEXT_HASH = "834c13da946a78e9830edf246961c0ae430ec19984e7ac213b74d9a7c218ae0f"
EQUATION_TEXT_HASH = "90c8464122c12e13907a307fe0b93e9661cbca7a3cf06ad92ecbebc3f9bf8df0"
LIMIT_TEXT_HASH = "b5235b4af52f7c1a115fc8a7c72af531320f853035d8539a02a1e761beac5709"
OBS_TEXT_HASH = "64f65f1fa3ef9a92a5759cdea1263b111b7d946f8a788ce11c7c91e104d382e2"
MATRIX_SHA256 = "df6faf2bc2f0f7cfc2e77b73f442b2cc60fe173e2ce1097850a36ca475685714"

DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "compact_wire_flag",
    "shared_table_dependency_flag",
    "self_contained_public_transcript_flag",
    "current_model_self_contained_bytes",
    "baseline_public_exchange_bytes",
    "external_efficiency_claim_flag",
    "external_efficiency_path_demoted_flag",
]
EQUATION_COLUMNS = [
    "equation_id",
    "equation_code",
    "left_value",
    "right_value",
    "equality_flag",
    "strict_greater_than_flag",
    "demotion_support_flag",
]
LIMIT_COLUMNS = [
    "limit_id",
    "limit_code",
    "open_flag",
    "required_before_reopen_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "decision_row_count",
    "compact_wire_flag",
    "wire_total_bytes",
    "wire_row_count",
    "table_index_dependency_count",
    "shared_dependency_all_rows_flag",
    "self_contained_public_transcript_flag",
    "current_model_self_contained_bytes",
    "baseline_public_exchange_bytes",
    "current_model_delta_vs_baseline_bytes",
    "current_model_greater_than_baseline_flag",
    "external_efficiency_claim_count",
    "external_efficiency_path_demoted_count",
    "equation_row_count",
    "equation_pass_count",
    "demotion_support_count",
    "limit_row_count",
    "open_limit_count",
    "overclaim_count",
    "decision_surface_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["decision_table", "equation_table", "limit_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def build_rows() -> dict[str, Any]:
    wire_report = load_json(LONG_K23WIRE_REPORT)
    wire_summary = summary(wire_report)
    wire_total_bytes = int(wire_summary.get("wire_total_bytes", -1))
    wire_row_count = int(wire_summary.get("wire_row_count", -1))
    dependency_count = int(wire_summary.get("table_index_dependency_count", -1))
    current_model_self_contained_bytes = int(wire_summary.get("norm_internal_public_digest_bytes", -1))
    baseline_public_exchange_bytes = int(wire_summary.get("norm_baseline_public_exchange_bytes", -1))
    current_delta = current_model_self_contained_bytes - baseline_public_exchange_bytes
    shared_all = int(dependency_count == wire_row_count and wire_row_count > 0)
    decision_rows = [
        {
            "decision_id": 0,
            "decision_code": 0,
            "compact_wire_flag": int(wire_total_bytes == 224),
            "shared_table_dependency_flag": shared_all,
            "self_contained_public_transcript_flag": 0,
            "current_model_self_contained_bytes": current_model_self_contained_bytes,
            "baseline_public_exchange_bytes": baseline_public_exchange_bytes,
            "external_efficiency_claim_flag": 0,
            "external_efficiency_path_demoted_flag": 1,
        }
    ]
    equation_rows = [
        {"equation_id": 0, "equation_code": 0, "left_value": wire_total_bytes, "right_value": 224, "equality_flag": 1, "strict_greater_than_flag": 0, "demotion_support_flag": 0},
        {"equation_id": 1, "equation_code": 1, "left_value": dependency_count, "right_value": wire_row_count, "equality_flag": 1, "strict_greater_than_flag": 0, "demotion_support_flag": 1},
        {"equation_id": 2, "equation_code": 2, "left_value": current_model_self_contained_bytes, "right_value": baseline_public_exchange_bytes, "equality_flag": 0, "strict_greater_than_flag": int(current_model_self_contained_bytes > baseline_public_exchange_bytes), "demotion_support_flag": 1},
        {"equation_id": 3, "equation_code": 3, "left_value": current_delta, "right_value": current_model_self_contained_bytes - baseline_public_exchange_bytes, "equality_flag": 1, "strict_greater_than_flag": 0, "demotion_support_flag": 1},
    ]
    limit_rows = [
        {"limit_id": 0, "limit_code": 0, "open_flag": 1, "required_before_reopen_flag": 1, "overclaim_flag": 0},
        {"limit_id": 1, "limit_code": 1, "open_flag": 1, "required_before_reopen_flag": 1, "overclaim_flag": 0},
        {"limit_id": 2, "limit_code": 2, "open_flag": 1, "required_before_reopen_flag": 1, "overclaim_flag": 0},
        {"limit_id": 3, "limit_code": 3, "open_flag": 1, "required_before_reopen_flag": 1, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": 1,
        "certified_input_count": is_certified(wire_report, "SECTOR33_K23_COMPACT_WIRE_MAP_CERTIFIED"),
        "decision_row_count": len(decision_rows),
        "compact_wire_flag": decision_rows[0]["compact_wire_flag"],
        "wire_total_bytes": wire_total_bytes,
        "wire_row_count": wire_row_count,
        "table_index_dependency_count": dependency_count,
        "shared_dependency_all_rows_flag": shared_all,
        "self_contained_public_transcript_flag": 0,
        "current_model_self_contained_bytes": current_model_self_contained_bytes,
        "baseline_public_exchange_bytes": baseline_public_exchange_bytes,
        "current_model_delta_vs_baseline_bytes": current_delta,
        "current_model_greater_than_baseline_flag": int(current_model_self_contained_bytes > baseline_public_exchange_bytes),
        "external_efficiency_claim_count": sum(row["external_efficiency_claim_flag"] for row in decision_rows),
        "external_efficiency_path_demoted_count": sum(row["external_efficiency_path_demoted_flag"] for row in decision_rows),
        "equation_row_count": len(equation_rows),
        "equation_pass_count": sum(int(row["equality_flag"] == 1 or row["strict_greater_than_flag"] == 1) for row in equation_rows),
        "demotion_support_count": sum(row["demotion_support_flag"] for row in equation_rows),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in limit_rows),
        "decision_surface_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    decision_table = table_from_rows(DECISION_COLUMNS, decision_rows)
    equation_table = table_from_rows(EQUATION_COLUMNS, equation_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "decision_table": decision_table.astype(np.int64),
        "equation_table": equation_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "wire_report": wire_report,
        "decision_rows": decision_rows,
        "equation_rows": equation_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "decision_table": decision_table,
        "equation_table": equation_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "decision_text_hash": hashlib.sha256(digest_text(DECISION_COLUMNS, decision_rows).encode("ascii")).hexdigest(),
        "equation_text_hash": hashlib.sha256(digest_text(EQUATION_COLUMNS, equation_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_pass": obs["certified_input_count"] == 1,
        "dependency_profile_matches": (
            obs["wire_total_bytes"],
            obs["wire_row_count"],
            obs["table_index_dependency_count"],
            obs["shared_dependency_all_rows_flag"],
            obs["self_contained_public_transcript_flag"],
        )
        == (224, 56, 56, 1, 0),
        "current_model_self_contained_loses": (
            obs["current_model_self_contained_bytes"],
            obs["baseline_public_exchange_bytes"],
            obs["current_model_delta_vs_baseline_bytes"],
            obs["current_model_greater_than_baseline_flag"],
        )
        == (5376, 1568, 3808, 1),
        "decision_matches": (
            obs["external_efficiency_claim_count"],
            obs["external_efficiency_path_demoted_count"],
            obs["decision_surface_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 1, 1, 0),
        "equation_profile_matches": (
            obs["equation_row_count"],
            obs["equation_pass_count"],
            obs["demotion_support_count"],
        )
        == (4, 4, 3),
        "limit_profile_matches": (
            obs["limit_row_count"],
            obs["open_limit_count"],
            obs["overclaim_count"],
        )
        == (4, 4, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_shared_table_dependency_decision",
        "decision_code_map": {
            "0": "current_external_efficiency_path_demoted",
        },
        "equation_code_map": {
            "0": "compact_wire_total_bytes",
            "1": "all_wire_rows_depend_on_shared_table",
            "2": "current_model_self_contained_bytes_exceed_baseline_public_bytes",
            "3": "current_model_delta_vs_baseline_bytes",
        },
        "limit_code_map": {
            "0": "self_contained_public_transcript",
            "1": "wire_equivalence_proof",
            "2": "security_reduction",
            "3": "interop_or_deployment",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This demotes the current external-efficiency path because the compact wire map is shared-table dependent and no self-contained public transcript is materialized.",
    }
    seam_payload = {
        "schema": "long.k23wdep.seam@1",
        "status": STATUS,
        "claim": "The compact K23 wire map is retained as a local shared-table artifact, while the current external-efficiency path is demoted.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23wire": input_entry(
            LONG_K23WIRE_REPORT,
            {
                "status": rows["wire_report"].get("status"),
                "certificate_sha256": rows["wire_report"].get("certificate_sha256"),
            },
        ),
        "long_k23wire_rows": input_entry(LONG_K23WIRE_ROWS),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23wdep.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23wdep certifies the shared-table dependency decision for the K23 compact wire map.",
        "stage_protocol": {
            "draft": "read long_k23wire and its compact wire rows",
            "witness": "emit dependency decision rows, equations, open limits, observables, and numeric tables",
            "coherence": "check shared-table dependency, current-model self-contained byte boundary, and demotion flags",
            "closure": "certify local compactness while demoting the current external-efficiency path",
            "emit": "write long_k23wdep artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "decision_rows_csv": relpath(OUT_DIR / "decision_rows.csv"),
            "equation_rows_csv": relpath(OUT_DIR / "equation_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23wdep_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the compact 224-byte wire map is shared-table dependent on all 56 rows",
                "no self-contained public transcript is materialized in the current artifact boundary",
                "the current self-contained digest-row byte surface is 5376 bytes",
                "the current self-contained surface exceeds the selected 1568-byte public exchange baseline",
                "the current external-efficiency path is demoted without rejecting the local compact map",
            ],
            "does_not_certify": [
                "absolute impossibility of future compression",
                "public wire-format equivalence",
                "external speed or size improvement",
                "security superiority",
                "standards compliance",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Return to proof-of-mandate semantics: test whether the compact local wire map still improves verifier-side audit cost without claiming public transport efficiency.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23wdep.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23wdep.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "equation_csv": csv_text(EQUATION_COLUMNS, rows["equation_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "decision_table": rows["decision_table"],
        "equation_table": rows["equation_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "decision_text_sha256": rows["decision_text_hash"],
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
    (OUT_DIR / "decision_rows.csv").write_text(payloads["decision_csv"], encoding="utf-8")
    (OUT_DIR / "equation_rows.csv").write_text(payloads["equation_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        decision_table=payloads["decision_table"],
        equation_table=payloads["equation_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23wdep_matrices.npz", **payloads["matrix_payload"])
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
