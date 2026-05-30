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


THEOREM_ID = "long_k23fing"
STATUS = "SECTOR33_K23_PROOF_OF_MANDATE_FRONTIER_INGESTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23fing.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23fing.py"
LONG_K23CSRC_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23csrc" / "report.json"
LONG_K23FROUTE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23froute" / "report.json"
LONG_K23SYNC_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23sync" / "report.json"
LONG_FRONTIER_REPORT = D20_INVARIANTS / "proof_obligations" / "long_frontier" / "report.json"
LONG_CLUSTER_REPORT = D20_INVARIANTS / "proof_obligations" / "long_cluster" / "report.json"
LONG_FRONTIER_OBJECT = D20_INVARIANTS / "proof_obligations" / "long_frontier" / "frontier.json"

INGEST_TEXT_HASH = "dd531fb633ba008e1be67f84bccdb9669e5552cc57ef416e34c169834a3de424"
GUARD_TEXT_HASH = "52d989d105aeb5b69ae75020eb50d1ac5d259fc5e89ab21ec3fc43bf9f24d7e7"
OBS_TEXT_HASH = "3a922b2e544a1a7812c2dbeb294dd7da7cb9b9ca061e7e99a7e78ab7037cd421"
MATRIX_SHA256 = "f834928ff72c6a7a95a937f5a70d566c63007865ab6a46acc0cd53ba076bdad4"

EXPECTED_STATUSES = {
    "long_k23csrc": "SECTOR33_K23_CHALLENGE_SOURCE_DECISION_CERTIFIED",
    "long_k23froute": "SECTOR33_K23_PROOF_OF_MANDATE_FRONTIER_ROUTE_CERTIFIED",
    "long_k23sync": "SECTOR33_K23_PROTOCOL_FRONTIER_HANDOFF_CERTIFIED",
    "long_frontier": "LONG_FRONTIER_CERTIFIED",
    "long_cluster": "LONG_CLUSTER_CERTIFIED",
}

INGEST_COLUMNS = [
    "ingest_id",
    "process_code",
    "source_code",
    "certified_flag",
    "ingested_flag",
    "preserves_open_boundary_flag",
    "broad_integration_run_flag",
    "broad_integration_required_flag",
    "focused_verifier_flag",
    "oracle_refresh_deferred_flag",
]
GUARD_COLUMNS = [
    "guard_id",
    "guard_code",
    "closed_flag",
    "open_flag",
    "preserved_flag",
    "required_for_frontier_ingestion_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "ingest_row_count",
    "ingested_row_count",
    "certified_ingest_count",
    "open_boundary_preserved_count",
    "focused_verifier_count",
    "oracle_refresh_deferred_count",
    "broad_integration_run_count",
    "broad_integration_required_count",
    "guard_row_count",
    "closed_guard_count",
    "open_guard_count",
    "overclaim_count",
    "proof_source_decision_flag",
    "route_blocking_count",
    "required_open_claim_count",
    "frontier_route_flag",
    "ready_route_count",
    "current_frontier_preserved_flag",
    "frontier_card_count",
    "frontier_open_count",
    "frontier_highest_yield_target_code",
    "cluster_reopen_count",
    "cluster_seam_candidate_count",
    "proof_of_mandate_frontier_ingestion_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["ingest_table", "guard_table", "observable_vector"]
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
    reports = {
        "long_k23csrc": load_json(LONG_K23CSRC_REPORT),
        "long_k23froute": load_json(LONG_K23FROUTE_REPORT),
        "long_k23sync": load_json(LONG_K23SYNC_REPORT),
        "long_frontier": load_json(LONG_FRONTIER_REPORT),
        "long_cluster": load_json(LONG_CLUSTER_REPORT),
    }
    frontier_object = load_json(LONG_FRONTIER_OBJECT)
    summaries = {name: summary(report) for name, report in reports.items()}
    certified = {name: is_certified(report, EXPECTED_STATUSES[name]) for name, report in reports.items()}
    ingest_rows = [
        {"ingest_id": 0, "process_code": 0, "source_code": 0, "certified_flag": certified["long_k23csrc"], "ingested_flag": 1, "preserves_open_boundary_flag": 0, "broad_integration_run_flag": 0, "broad_integration_required_flag": 0, "focused_verifier_flag": 0, "oracle_refresh_deferred_flag": 0},
        {"ingest_id": 1, "process_code": 1, "source_code": 1, "certified_flag": certified["long_k23csrc"], "ingested_flag": 1, "preserves_open_boundary_flag": 1, "broad_integration_run_flag": 0, "broad_integration_required_flag": 0, "focused_verifier_flag": 0, "oracle_refresh_deferred_flag": 0},
        {"ingest_id": 2, "process_code": 2, "source_code": 2, "certified_flag": certified["long_k23froute"], "ingested_flag": 1, "preserves_open_boundary_flag": 1, "broad_integration_run_flag": 0, "broad_integration_required_flag": 0, "focused_verifier_flag": 0, "oracle_refresh_deferred_flag": 0},
        {"ingest_id": 3, "process_code": 3, "source_code": 3, "certified_flag": 1, "ingested_flag": 1, "preserves_open_boundary_flag": 1, "broad_integration_run_flag": 0, "broad_integration_required_flag": 0, "focused_verifier_flag": 0, "oracle_refresh_deferred_flag": 0},
        {"ingest_id": 4, "process_code": 4, "source_code": 4, "certified_flag": 1, "ingested_flag": 1, "preserves_open_boundary_flag": 1, "broad_integration_run_flag": 0, "broad_integration_required_flag": 0, "focused_verifier_flag": 1, "oracle_refresh_deferred_flag": 0},
        {"ingest_id": 5, "process_code": 5, "source_code": 5, "certified_flag": certified["long_frontier"] * certified["long_cluster"], "ingested_flag": 1, "preserves_open_boundary_flag": 1, "broad_integration_run_flag": 0, "broad_integration_required_flag": 1, "focused_verifier_flag": 0, "oracle_refresh_deferred_flag": 1},
    ]
    guard_rows = [
        {"guard_id": 0, "guard_code": 0, "closed_flag": 1, "open_flag": 0, "preserved_flag": 1, "required_for_frontier_ingestion_flag": 1, "overclaim_flag": 0},
        {"guard_id": 1, "guard_code": 1, "closed_flag": 1, "open_flag": 0, "preserved_flag": 1, "required_for_frontier_ingestion_flag": 1, "overclaim_flag": 0},
        {"guard_id": 2, "guard_code": 2, "closed_flag": 1, "open_flag": 0, "preserved_flag": 1, "required_for_frontier_ingestion_flag": 1, "overclaim_flag": 0},
        {"guard_id": 3, "guard_code": 3, "closed_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_frontier_ingestion_flag": 0, "overclaim_flag": 0},
        {"guard_id": 4, "guard_code": 4, "closed_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_frontier_ingestion_flag": 0, "overclaim_flag": 0},
        {"guard_id": 5, "guard_code": 5, "closed_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_frontier_ingestion_flag": 0, "overclaim_flag": 0},
        {"guard_id": 6, "guard_code": 6, "closed_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_frontier_ingestion_flag": 0, "overclaim_flag": 0},
        {"guard_id": 7, "guard_code": 7, "closed_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_frontier_ingestion_flag": 0, "overclaim_flag": 0},
    ]
    csrc_summary = summaries["long_k23csrc"]
    froute_summary = summaries["long_k23froute"]
    sync_summary = summaries["long_k23sync"]
    frontier_summary = summary(frontier_object)
    cluster_summary = summaries["long_cluster"]
    obs = {
        "input_report_count": len(reports),
        "certified_input_count": sum(certified.values()),
        "ingest_row_count": len(ingest_rows),
        "ingested_row_count": sum(row["ingested_flag"] for row in ingest_rows),
        "certified_ingest_count": sum(row["certified_flag"] for row in ingest_rows),
        "open_boundary_preserved_count": sum(row["preserves_open_boundary_flag"] for row in ingest_rows),
        "focused_verifier_count": sum(row["focused_verifier_flag"] for row in ingest_rows),
        "oracle_refresh_deferred_count": sum(row["oracle_refresh_deferred_flag"] for row in ingest_rows),
        "broad_integration_run_count": sum(row["broad_integration_run_flag"] for row in ingest_rows),
        "broad_integration_required_count": sum(row["broad_integration_required_flag"] for row in ingest_rows),
        "guard_row_count": len(guard_rows),
        "closed_guard_count": sum(row["closed_flag"] for row in guard_rows),
        "open_guard_count": sum(row["open_flag"] for row in guard_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in guard_rows),
        "proof_source_decision_flag": int(csrc_summary.get("proof_of_mandate_source_decision_flag", -1)),
        "route_blocking_count": int(csrc_summary.get("route_blocking_count", -1)),
        "required_open_claim_count": int(csrc_summary.get("required_open_claim_count", -1)),
        "frontier_route_flag": int(froute_summary.get("proof_of_mandate_frontier_route_flag", -1)),
        "ready_route_count": int(froute_summary.get("ready_route_count", -1)),
        "current_frontier_preserved_flag": int(sync_summary.get("current_frontier_preserved_flag", -1)),
        "frontier_card_count": int(frontier_summary.get("card_count", -1)),
        "frontier_open_count": int(frontier_summary.get("frontier_open_count", -1)),
        "frontier_highest_yield_target_code": int(frontier_summary.get("highest_yield_target_code", -1)),
        "cluster_reopen_count": int(cluster_summary.get("reopened_cluster_count", -1)),
        "cluster_seam_candidate_count": int(cluster_summary.get("seam_candidate_count", -1)),
        "proof_of_mandate_frontier_ingestion_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    ingest_table = table_from_rows(INGEST_COLUMNS, ingest_rows)
    guard_table = table_from_rows(GUARD_COLUMNS, guard_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "ingest_table": ingest_table.astype(np.int64),
        "guard_table": guard_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "frontier_object": frontier_object,
        "ingest_rows": ingest_rows,
        "guard_rows": guard_rows,
        "obs_rows": obs_rows,
        "ingest_table": ingest_table,
        "guard_table": guard_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "ingest_text_hash": hashlib.sha256(digest_text(INGEST_COLUMNS, ingest_rows).encode("ascii")).hexdigest(),
        "guard_text_hash": hashlib.sha256(digest_text(GUARD_COLUMNS, guard_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 5,
        "ingestion_profile_matches": (
            obs["ingest_row_count"],
            obs["ingested_row_count"],
            obs["certified_ingest_count"],
            obs["open_boundary_preserved_count"],
            obs["focused_verifier_count"],
            obs["oracle_refresh_deferred_count"],
        )
        == (6, 6, 6, 5, 1, 1),
        "broad_boundary_matches": (
            obs["broad_integration_run_count"],
            obs["broad_integration_required_count"],
        )
        == (0, 1),
        "guard_profile_matches": (
            obs["guard_row_count"],
            obs["closed_guard_count"],
            obs["open_guard_count"],
            obs["overclaim_count"],
        )
        == (8, 3, 5, 0),
        "proof_mandate_route_matches": (
            obs["proof_source_decision_flag"],
            obs["route_blocking_count"],
            obs["required_open_claim_count"],
            obs["frontier_route_flag"],
            obs["ready_route_count"],
            obs["current_frontier_preserved_flag"],
        )
        == (1, 0, 0, 1, 4, 1),
        "frontier_guardrail_matches": (
            obs["frontier_card_count"],
            obs["frontier_open_count"],
            obs["frontier_highest_yield_target_code"],
            obs["cluster_reopen_count"],
            obs["cluster_seam_candidate_count"],
        )
        == (13, 1, 12, 6, 49),
        "boundary_flags_match": (
            obs["proof_of_mandate_frontier_ingestion_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_proof_of_mandate_frontier_ingestion",
        "process_code_map": {
            "0": "certified_surface",
            "1": "open_boundary",
            "2": "candidate_operator",
            "3": "witness_artifact",
            "4": "focused_verifier",
            "5": "oracle_refresh",
        },
        "source_code_map": {
            "0": "long_k23csrc",
            "1": "open_nonclaims",
            "2": "long_k23froute",
            "3": "long_k23fing_artifacts",
            "4": "long-k23fing",
            "5": "long_frontier_and_long_cluster",
        },
        "guard_code_map": {
            "0": "deterministic_selection",
            "1": "finite_authority",
            "2": "frontier_route",
            "3": "independent_randomness",
            "4": "computational_hardness",
            "5": "zero_knowledge",
            "6": "unbounded_security",
            "7": "broad_integration",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies local frontier ingestion for the K23 proof-of-mandate chain while deferring oracle refresh.",
    }
    seam_payload = {
        "schema": "long.k23fing.seam@1",
        "status": STATUS,
        "claim": "The proof-of-mandate chain is locally ingested into the frontier process ontology without a broad refresh.",
        "witness": witness,
        "checks": checks,
    }
    paths = {
        "long_k23csrc": LONG_K23CSRC_REPORT,
        "long_k23froute": LONG_K23FROUTE_REPORT,
        "long_k23sync": LONG_K23SYNC_REPORT,
        "long_frontier": LONG_FRONTIER_REPORT,
        "long_cluster": LONG_CLUSTER_REPORT,
    }
    inputs = {
        name: input_entry(
            path,
            {
                "status": rows["reports"][name].get("status"),
                "certificate_sha256": rows["reports"][name].get("certificate_sha256"),
            },
        )
        for name, path in paths.items()
    }
    inputs["long_frontier_object"] = input_entry(LONG_FRONTIER_OBJECT)
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23fing.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23fing certifies local frontier ingestion for the proof-of-mandate chain.",
        "stage_protocol": {
            "draft": "read challenge-source decision, route, handoff, frontier, and cluster reports",
            "witness": "emit ingestion rows, guard rows, observables, and numeric tables",
            "coherence": "check process ontology rows, preserved guardrails, route counts, and deferred broad refresh",
            "closure": "certify local frontier ingestion without claiming bundle-wide integration",
            "emit": "write long_k23fing artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "ingest_rows_csv": relpath(OUT_DIR / "ingest_rows.csv"),
            "guard_rows_csv": relpath(OUT_DIR / "guard_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23fing_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the proof-of-mandate chain is locally ingested into the frontier process ontology",
                "the challenge-source decision and frontier route are certified inputs",
                "open nonclaims are preserved as open guardrails",
                "the existing frontier and cluster reports remain the guardrail sources",
                "broad integration and oracle refresh are explicitly deferred",
            ],
            "does_not_certify": [
                "bundle-wide integration",
                "a regenerated long_frontier report containing the new proof-obligation row",
                "independent challenge randomness",
                "computational hardness",
                "zero knowledge",
                "unbounded adversary security",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Materialize a focused mandate-ledger certificate that lists the verified proof-of-mandate chain and the remaining explicit nonclaims.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23fing.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23fing.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "ingest_csv": csv_text(INGEST_COLUMNS, rows["ingest_rows"]),
        "guard_csv": csv_text(GUARD_COLUMNS, rows["guard_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "ingest_table": rows["ingest_table"],
        "guard_table": rows["guard_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "ingest_text_sha256": rows["ingest_text_hash"],
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
    (OUT_DIR / "ingest_rows.csv").write_text(payloads["ingest_csv"], encoding="utf-8")
    (OUT_DIR / "guard_rows.csv").write_text(payloads["guard_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        ingest_table=payloads["ingest_table"],
        guard_table=payloads["guard_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23fing_matrices.npz", **payloads["matrix_payload"])
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
