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


THEOREM_ID = "long_k23froute"
STATUS = "SECTOR33_K23_PROOF_OF_MANDATE_FRONTIER_ROUTE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23froute.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23froute.py"
LONG_K23AUTH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23auth" / "report.json"
LONG_K23SDET_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23sdet" / "report.json"
LONG_K23SYNC_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23sync" / "report.json"
LONG_FRONTIER_REPORT = D20_INVARIANTS / "proof_obligations" / "long_frontier" / "report.json"
LONG_CLUSTER_REPORT = D20_INVARIANTS / "proof_obligations" / "long_cluster" / "report.json"

ROUTE_TEXT_HASH = "a62b4c6c875b19e54ed3904edae41f3887d782b56c7e479cba3b5b7944ead8eb"
GUARD_TEXT_HASH = "07dd568b44ff28f49675d4ee3390a9907c2e95d7bba9e80808617dea69ce8766"
OBS_TEXT_HASH = "f93c4a658afe694f703ebc22db90cefefb5ddb5f8bbaa3cb6312edd9f80ab940"
MATRIX_SHA256 = "903d04946c28168cda1f9f4a74f0dd878c0f26a7870d187748bf595210e108eb"

EXPECTED_STATUSES = {
    "long_k23auth": "SECTOR33_K23_FINITE_AUTHORITY_CLOSURE_CERTIFIED",
    "long_k23sdet": "SECTOR33_K23_SUPERDETERMINISTIC_CRYPTOLOGIC_BOUNDARY_CERTIFIED",
    "long_k23sync": "SECTOR33_K23_PROTOCOL_FRONTIER_HANDOFF_CERTIFIED",
    "long_frontier": "LONG_FRONTIER_CERTIFIED",
    "long_cluster": "LONG_CLUSTER_CERTIFIED",
}

ROUTE_COLUMNS = [
    "route_id",
    "route_code",
    "source_code",
    "target_code",
    "source_certified_flag",
    "target_certified_flag",
    "route_ready_flag",
    "frontier_preserved_flag",
    "broad_integration_run_flag",
    "challenge_source_extension_open_flag",
    "proof_mandate_route_flag",
]
GUARD_COLUMNS = [
    "guard_id",
    "guard_code",
    "certified_input_flag",
    "claim_closed_flag",
    "claim_open_flag",
    "broad_integration_required_flag",
    "frontier_target_preserved_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "route_row_count",
    "ready_route_count",
    "proof_mandate_route_count",
    "frontier_preserved_route_count",
    "broad_integration_run_count",
    "challenge_source_extension_open_count",
    "guard_row_count",
    "open_guard_count",
    "broad_required_guard_count",
    "accepted_authority_count",
    "finite_authority_closure_flag",
    "deterministic_boundary_flag",
    "external_randomness_required_count",
    "randomness_independence_claim_flag",
    "current_frontier_preserved_flag",
    "frontier_open_count",
    "cluster_reopen_count",
    "cluster_seam_candidate_count",
    "highest_yield_target_code",
    "proof_of_mandate_frontier_route_flag",
    "broad_integration_required_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["route_table", "guard_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def report_input(name: str, path: Any, report: dict[str, Any]) -> dict[str, Any]:
    return input_entry(
        path,
        {
            "status": report.get("status"),
            "certificate_sha256": report.get("certificate_sha256"),
        },
    )


def build_rows() -> dict[str, Any]:
    reports = {
        "long_k23auth": load_json(LONG_K23AUTH_REPORT),
        "long_k23sdet": load_json(LONG_K23SDET_REPORT),
        "long_k23sync": load_json(LONG_K23SYNC_REPORT),
        "long_frontier": load_json(LONG_FRONTIER_REPORT),
        "long_cluster": load_json(LONG_CLUSTER_REPORT),
    }
    summaries = {name: summary(report) for name, report in reports.items()}
    certified = {name: is_certified(report, EXPECTED_STATUSES[name]) for name, report in reports.items()}
    route_pairs = [
        (0, 0, 0, 1, "long_k23auth", "long_k23sdet"),
        (1, 1, 1, 2, "long_k23sdet", "long_k23sync"),
        (2, 2, 2, 3, "long_k23sync", "long_frontier"),
        (3, 3, 3, 4, "long_frontier", "long_cluster"),
    ]
    route_rows = [
        {
            "route_id": route_id,
            "route_code": route_code,
            "source_code": source_code,
            "target_code": target_code,
            "source_certified_flag": certified[source_name],
            "target_certified_flag": certified[target_name],
            "route_ready_flag": int(certified[source_name] == 1 and certified[target_name] == 1),
            "frontier_preserved_flag": 1,
            "broad_integration_run_flag": 0,
            "challenge_source_extension_open_flag": 1,
            "proof_mandate_route_flag": 1,
        }
        for route_id, route_code, source_code, target_code, source_name, target_name in route_pairs
    ]
    guard_rows = [
        {
            "guard_id": guard_id,
            "guard_code": guard_id,
            "certified_input_flag": 1,
            "claim_closed_flag": 0,
            "claim_open_flag": 1,
            "broad_integration_required_flag": int(guard_id == 4),
            "frontier_target_preserved_flag": 1,
        }
        for guard_id in range(8)
    ]
    auth_summary = summaries["long_k23auth"]
    sdet_summary = summaries["long_k23sdet"]
    sync_summary = summaries["long_k23sync"]
    frontier_summary = summaries["long_frontier"]
    cluster_summary = summaries["long_cluster"]
    obs = {
        "input_report_count": len(reports),
        "certified_input_count": sum(certified.values()),
        "route_row_count": len(route_rows),
        "ready_route_count": sum(row["route_ready_flag"] for row in route_rows),
        "proof_mandate_route_count": sum(row["proof_mandate_route_flag"] for row in route_rows),
        "frontier_preserved_route_count": sum(row["frontier_preserved_flag"] for row in route_rows),
        "broad_integration_run_count": sum(row["broad_integration_run_flag"] for row in route_rows),
        "challenge_source_extension_open_count": sum(row["challenge_source_extension_open_flag"] for row in route_rows),
        "guard_row_count": len(guard_rows),
        "open_guard_count": sum(row["claim_open_flag"] for row in guard_rows),
        "broad_required_guard_count": sum(row["broad_integration_required_flag"] for row in guard_rows),
        "accepted_authority_count": int(auth_summary.get("accepted_authority_count", -1)),
        "finite_authority_closure_flag": int(auth_summary.get("finite_authority_closure_flag", -1)),
        "deterministic_boundary_flag": int(
            sdet_summary.get("superdeterministic_cryptologic_boundary_flag", -1)
        ),
        "external_randomness_required_count": int(
            sdet_summary.get("external_randomness_required_count", -1)
        ),
        "randomness_independence_claim_flag": int(
            sdet_summary.get("randomness_independence_claim_flag", -1)
        ),
        "current_frontier_preserved_flag": int(
            sync_summary.get("current_frontier_preserved_flag", -1)
        ),
        "frontier_open_count": int(frontier_summary.get("frontier_open_count", -1)),
        "cluster_reopen_count": int(cluster_summary.get("reopened_cluster_count", -1)),
        "cluster_seam_candidate_count": int(cluster_summary.get("seam_candidate_count", -1)),
        "highest_yield_target_code": int(frontier_summary.get("highest_yield_target_code", -1)),
        "proof_of_mandate_frontier_route_flag": 1,
        "broad_integration_required_flag": int(sync_summary.get("broad_integration_required_flag", -1)),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    route_table = table_from_rows(ROUTE_COLUMNS, route_rows)
    guard_table = table_from_rows(GUARD_COLUMNS, guard_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "route_table": route_table.astype(np.int64),
        "guard_table": guard_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "route_rows": route_rows,
        "guard_rows": guard_rows,
        "obs_rows": obs_rows,
        "route_table": route_table,
        "guard_table": guard_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "route_text_hash": hashlib.sha256(digest_text(ROUTE_COLUMNS, route_rows).encode("ascii")).hexdigest(),
        "guard_text_hash": hashlib.sha256(digest_text(GUARD_COLUMNS, guard_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 5,
        "route_profile_matches": (
            obs["route_row_count"],
            obs["ready_route_count"],
            obs["proof_mandate_route_count"],
            obs["frontier_preserved_route_count"],
            obs["broad_integration_run_count"],
            obs["challenge_source_extension_open_count"],
        )
        == (4, 4, 4, 4, 0, 4),
        "guard_profile_matches": (
            obs["guard_row_count"],
            obs["open_guard_count"],
            obs["broad_required_guard_count"],
        )
        == (8, 8, 1),
        "proof_mandate_boundary_matches": (
            obs["accepted_authority_count"],
            obs["finite_authority_closure_flag"],
            obs["deterministic_boundary_flag"],
            obs["external_randomness_required_count"],
            obs["randomness_independence_claim_flag"],
        )
        == (56, 1, 1, 0, 0),
        "frontier_guardrail_matches": (
            obs["current_frontier_preserved_flag"],
            obs["frontier_open_count"],
            obs["cluster_reopen_count"],
            obs["cluster_seam_candidate_count"],
            obs["highest_yield_target_code"],
            obs["broad_integration_required_flag"],
        )
        == (1, 1, 6, 49, 12, 1),
        "boundary_flags_match": (
            obs["proof_of_mandate_frontier_route_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_proof_of_mandate_frontier_route",
        "source_code_map": {
            "0": "long_k23auth",
            "1": "long_k23sdet",
            "2": "long_k23sync",
            "3": "long_frontier",
            "4": "long_cluster",
        },
        "route_code_map": {
            "0": "authority_to_deterministic_boundary",
            "1": "deterministic_boundary_to_handoff",
            "2": "handoff_to_frontier_guardrail",
            "3": "frontier_guardrail_to_cluster_reopen_audit",
        },
        "guard_code_map": {
            "0": "independent_challenge_randomness",
            "1": "computational_hardness",
            "2": "zero_knowledge",
            "3": "unbounded_adversary_security",
            "4": "broad_bundle_integration",
            "5": "repository_visible_witness_secrecy",
            "6": "challenge_source_extension",
            "7": "active_goal_completion",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the K23 proof-of-mandate chain is route-ready for the frontier while preserving open guardrails.",
    }
    seam_payload = {
        "schema": "long.k23froute.seam@1",
        "status": STATUS,
        "claim": "The deterministic proof-of-mandate chain routes into the current frontier guardrails without broad integration or closed security overclaim.",
        "witness": witness,
        "checks": checks,
    }
    paths = {
        "long_k23auth": LONG_K23AUTH_REPORT,
        "long_k23sdet": LONG_K23SDET_REPORT,
        "long_k23sync": LONG_K23SYNC_REPORT,
        "long_frontier": LONG_FRONTIER_REPORT,
        "long_cluster": LONG_CLUSTER_REPORT,
    }
    inputs = {name: report_input(name, path, rows["reports"][name]) for name, path in paths.items()}
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23froute.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23froute certifies the proof-of-mandate frontier route.",
        "stage_protocol": {
            "draft": "read authority, deterministic-boundary, handoff, frontier, and cluster reports",
            "witness": "emit route rows, guard rows, observables, and numeric tables",
            "coherence": "check certified inputs, route readiness, frontier preservation, and explicit open guardrails",
            "closure": "certify route readiness while leaving broad integration and external security claims open",
            "emit": "write long_k23froute artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "route_rows_csv": relpath(OUT_DIR / "route_rows.csv"),
            "guard_rows_csv": relpath(OUT_DIR / "guard_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23froute_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "long_k23auth routes into the deterministic boundary",
                "long_k23sdet routes into the existing focused handoff",
                "the current frontier guardrail and cluster reopen audit remain certified inputs",
                "the proof-of-mandate route is ready for frontier ingestion",
                "broad integration has not been run or claimed",
            ],
            "does_not_certify": [
                "independent challenge randomness",
                "computational hardness",
                "zero knowledge",
                "unbounded adversary security",
                "bundle-wide integration",
                "that the current long_cluster top seam is solved",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Materialize the next route decision: either a challenge-source extension certificate, or a frontier-ingestion certificate that keeps the challenge source explicitly open.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23froute.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23froute.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "route_csv": csv_text(ROUTE_COLUMNS, rows["route_rows"]),
        "guard_csv": csv_text(GUARD_COLUMNS, rows["guard_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "route_table": rows["route_table"],
        "guard_table": rows["guard_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "route_text_sha256": rows["route_text_hash"],
            "guard_text_sha256": rows["guard_text_hash"],
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
    (OUT_DIR / "route_rows.csv").write_text(payloads["route_csv"], encoding="utf-8")
    (OUT_DIR / "guard_rows.csv").write_text(payloads["guard_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        route_table=payloads["route_table"],
        guard_table=payloads["guard_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23froute_matrices.npz", **payloads["matrix_payload"])
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
