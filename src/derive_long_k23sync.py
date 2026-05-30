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


THEOREM_ID = "long_k23sync"
STATUS = "SECTOR33_K23_PROTOCOL_FRONTIER_HANDOFF_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23sync.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23sync.py"
LONG_K23ROLL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23roll" / "report.json"
LONG_K23REP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rep" / "report.json"
LONG_FRONTIER_REPORT = D20_INVARIANTS / "proof_obligations" / "long_frontier" / "report.json"
LONG_CLUSTER_REPORT = D20_INVARIANTS / "proof_obligations" / "long_cluster" / "report.json"

HANDOFF_TEXT_HASH = "e7be2532f47560d01778dc46a2c1b7c713cc5a56ab950b088c797ac8ceb81298"
FRONTIER_TEXT_HASH = "734f1e96ba2fad0b925609fb0b1bf52d518dd25ae8f3ab459b65b5eabb539772"
OBS_TEXT_HASH = "14783d983cb7dd45c692a698dc4dad16d9609b8e150d317003b0cf2fe954efb0"
MATRIX_SHA256 = "e3c1d3570baa90e63f45c14673650ce0360912d1091fc79a035ea504e0fe816c"

HANDOFF_COLUMNS = [
    "handoff_id",
    "role_code",
    "proof_id",
    "status",
    "certified_flag",
    "ready_for_frontier_flag",
    "broad_integration_required_flag",
    "certificate_sha256",
]
FRONTIER_COLUMNS = [
    "frontier_id",
    "guardrail_code",
    "proof_id",
    "status",
    "certified_flag",
    "preserved_current_frontier_flag",
    "broad_refresh_required_flag",
    "certificate_sha256",
]
HANDOFF_NUMERIC_COLUMNS = [
    "handoff_id",
    "role_code",
    "certified_flag",
    "ready_for_frontier_flag",
    "broad_integration_required_flag",
]
FRONTIER_NUMERIC_COLUMNS = [
    "frontier_id",
    "guardrail_code",
    "certified_flag",
    "preserved_current_frontier_flag",
    "broad_refresh_required_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "handoff_row_count",
    "ready_handoff_count",
    "frontier_row_count",
    "frontier_guardrail_count",
    "rollup_merge_point_flag",
    "repeated_round_accounting_flag",
    "repeated_round_max_depth",
    "repeated_round_final_total",
    "frontier_open_count",
    "cluster_reopen_count",
    "cluster_seam_candidate_count",
    "current_frontier_preserved_flag",
    "broad_integration_run_flag",
    "broad_integration_required_flag",
    "hardness_claim_flag",
    "zero_knowledge_claim_flag",
    "final_goal_claim_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

EXPECTED_STATUSES = {
    "long_k23roll": "SECTOR33_K23_SEMANTIC_GAME_PROTOCOL_ROLLUP_CERTIFIED",
    "long_k23rep": "SECTOR33_K23_REPEATED_ROUND_ACCOUNTING_CERTIFIED",
    "long_frontier": "LONG_FRONTIER_CERTIFIED",
    "long_cluster": "LONG_CLUSTER_CERTIFIED",
}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["handoff_numeric_table", "frontier_numeric_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def is_certified(report: dict[str, Any], proof_id: str) -> int:
    return int(
        report.get("status") == EXPECTED_STATUSES[proof_id]
        and report.get("all_checks_pass") is True
    )


def build_rows() -> dict[str, Any]:
    reports = {
        "long_k23roll": load_json(LONG_K23ROLL_REPORT),
        "long_k23rep": load_json(LONG_K23REP_REPORT),
        "long_frontier": load_json(LONG_FRONTIER_REPORT),
        "long_cluster": load_json(LONG_CLUSTER_REPORT),
    }
    handoff_specs = [
        (0, 0, "long_k23roll"),
        (1, 1, "long_k23rep"),
    ]
    handoff_rows = []
    for handoff_id, role_code, proof_id in handoff_specs:
        report = reports[proof_id]
        certified = is_certified(report, proof_id)
        handoff_rows.append(
            {
                "handoff_id": handoff_id,
                "role_code": role_code,
                "proof_id": proof_id,
                "status": str(report.get("status", "")),
                "certified_flag": certified,
                "ready_for_frontier_flag": certified,
                "broad_integration_required_flag": 1,
                "certificate_sha256": str(report.get("certificate_sha256", "")),
            }
        )

    frontier_specs = [
        (0, 0, "long_frontier"),
        (1, 1, "long_cluster"),
    ]
    frontier_summary = summary(reports["long_frontier"])
    cluster_summary = summary(reports["long_cluster"])
    current_frontier_preserved = int(
        frontier_summary.get("next_target") == "long_cluster_top_seam"
        and int(frontier_summary.get("frontier_open_count", -1)) == 1
        and int(cluster_summary.get("reopened_cluster_count", -1)) == 6
    )
    frontier_rows = []
    for frontier_id, guardrail_code, proof_id in frontier_specs:
        report = reports[proof_id]
        certified = is_certified(report, proof_id)
        frontier_rows.append(
            {
                "frontier_id": frontier_id,
                "guardrail_code": guardrail_code,
                "proof_id": proof_id,
                "status": str(report.get("status", "")),
                "certified_flag": certified,
                "preserved_current_frontier_flag": current_frontier_preserved,
                "broad_refresh_required_flag": 1,
                "certificate_sha256": str(report.get("certificate_sha256", "")),
            }
        )

    roll_summary = summary(reports["long_k23roll"])
    rep_summary = summary(reports["long_k23rep"])
    obs = {
        "input_report_count": len(reports),
        "certified_input_count": sum(is_certified(report, proof_id) for proof_id, report in reports.items()),
        "handoff_row_count": len(handoff_rows),
        "ready_handoff_count": sum(row["ready_for_frontier_flag"] for row in handoff_rows),
        "frontier_row_count": len(frontier_rows),
        "frontier_guardrail_count": sum(row["certified_flag"] for row in frontier_rows),
        "rollup_merge_point_flag": int(roll_summary.get("certified_merge_point_flag", 0)),
        "repeated_round_accounting_flag": int(
            rep_summary.get("final_depth_total_strategy_words", 0) == 94_058_496
            and rep_summary.get("final_depth_accepted_strategy_words", 0) == 56
        ),
        "repeated_round_max_depth": int(rep_summary.get("max_round_depth", 0)),
        "repeated_round_final_total": int(rep_summary.get("final_depth_total_strategy_words", 0)),
        "frontier_open_count": int(frontier_summary.get("frontier_open_count", 0)),
        "cluster_reopen_count": int(cluster_summary.get("reopened_cluster_count", 0)),
        "cluster_seam_candidate_count": int(cluster_summary.get("seam_candidate_count", 0)),
        "current_frontier_preserved_flag": current_frontier_preserved,
        "broad_integration_run_flag": 0,
        "broad_integration_required_flag": 1,
        "hardness_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "final_goal_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    handoff_numeric_table = table_from_rows(HANDOFF_NUMERIC_COLUMNS, handoff_rows)
    frontier_numeric_table = table_from_rows(FRONTIER_NUMERIC_COLUMNS, frontier_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "handoff_numeric_table": handoff_numeric_table.astype(np.int64),
        "frontier_numeric_table": frontier_numeric_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "handoff_rows": handoff_rows,
        "frontier_rows": frontier_rows,
        "obs_rows": obs_rows,
        "handoff_numeric_table": handoff_numeric_table,
        "frontier_numeric_table": frontier_numeric_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "handoff_text_hash": hashlib.sha256(digest_text(HANDOFF_COLUMNS, handoff_rows).encode("ascii")).hexdigest(),
        "frontier_text_hash": hashlib.sha256(digest_text(FRONTIER_COLUMNS, frontier_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 4,
        "handoff_ready": (
            obs["handoff_row_count"],
            obs["ready_handoff_count"],
            obs["rollup_merge_point_flag"],
            obs["repeated_round_accounting_flag"],
        )
        == (2, 2, 1, 1),
        "frontier_preserved": (
            obs["frontier_row_count"],
            obs["frontier_guardrail_count"],
            obs["frontier_open_count"],
            obs["cluster_reopen_count"],
            obs["current_frontier_preserved_flag"],
        )
        == (2, 2, 1, 6, 1),
        "broad_integration_not_claimed": (
            obs["broad_integration_run_flag"],
            obs["broad_integration_required_flag"],
        )
        == (0, 1),
        "security_limits_open": (
            obs["hardness_claim_flag"],
            obs["zero_knowledge_claim_flag"],
            obs["final_goal_claim_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_protocol_frontier_handoff",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies focused handoff readiness for the K23 protocol chain while preserving the current frontier boundary.",
    }
    seam_payload = {
        "schema": "long.k23sync.seam@1",
        "status": STATUS,
        "claim": "The K23 protocol-chain rollup and repeated-round accounting are ready focused handoff surfaces; broad integration remains a separate gate.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        proof_id: input_entry(
            path,
            {
                "status": rows["reports"][proof_id].get("status"),
                "certificate_sha256": rows["reports"][proof_id].get("certificate_sha256"),
            },
        )
        for proof_id, path in {
            "long_k23roll": LONG_K23ROLL_REPORT,
            "long_k23rep": LONG_K23REP_REPORT,
            "long_frontier": LONG_FRONTIER_REPORT,
            "long_cluster": LONG_CLUSTER_REPORT,
        }.items()
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23sync.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23sync certifies focused handoff readiness for the K23 semantic/game/protocol chain.",
        "stage_protocol": {
            "draft": "read long_k23roll, long_k23rep, long_frontier, and long_cluster reports",
            "witness": "emit handoff rows, frontier guardrail rows, and observables",
            "coherence": "check input statuses, frontier preservation, and explicit non-claims",
            "closure": "certify local handoff readiness while leaving broad integration and security claims open",
            "emit": "write long_k23sync artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "handoff_rows_csv": relpath(OUT_DIR / "handoff_rows.csv"),
            "frontier_rows_csv": relpath(OUT_DIR / "frontier_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23sync_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "long_k23roll and long_k23rep are certified focused handoff surfaces",
                "long_frontier and long_cluster remain certified guardrails",
                "the current frontier target is preserved until a broad refresh is run",
                "no broad integration, hardness, zero-knowledge, or final-goal claim is made",
            ],
            "does_not_certify": [
                "bundle-wide integration of the new protocol chain",
                "probabilistic soundness",
                "cryptographic hardness",
                "zero knowledge",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Refresh the broad bundle, then define a finite adversary/soundness proof obligation over the certified verifier game.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23sync.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23sync.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "handoff_csv": csv_text(HANDOFF_COLUMNS, rows["handoff_rows"]),
        "frontier_csv": csv_text(FRONTIER_COLUMNS, rows["frontier_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "handoff_numeric_table": rows["handoff_numeric_table"],
        "frontier_numeric_table": rows["frontier_numeric_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "handoff_text_sha256": rows["handoff_text_hash"],
            "frontier_text_sha256": rows["frontier_text_hash"],
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
    (OUT_DIR / "handoff_rows.csv").write_text(payloads["handoff_csv"], encoding="utf-8")
    (OUT_DIR / "frontier_rows.csv").write_text(payloads["frontier_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        handoff_numeric_table=payloads["handoff_numeric_table"],
        frontier_numeric_table=payloads["frontier_numeric_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23sync_matrices.npz", **payloads["matrix_payload"])
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
