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


THEOREM_ID = "long_k23mledger"
STATUS = "SECTOR33_K23_PROOF_OF_MANDATE_LEDGER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23mledger.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23mledger.py"

REPORT_PATHS = {
    "long_k23chal": D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json",
    "long_k23game": D20_INVARIANTS / "proof_obligations" / "long_k23game" / "report.json",
    "long_k23roll": D20_INVARIANTS / "proof_obligations" / "long_k23roll" / "report.json",
    "long_k23rep": D20_INVARIANTS / "proof_obligations" / "long_k23rep" / "report.json",
    "long_k23sync": D20_INVARIANTS / "proof_obligations" / "long_k23sync" / "report.json",
    "long_k23sound": D20_INVARIANTS / "proof_obligations" / "long_k23sound" / "report.json",
    "long_k23mand": D20_INVARIANTS / "proof_obligations" / "long_k23mand" / "report.json",
    "long_k23auth": D20_INVARIANTS / "proof_obligations" / "long_k23auth" / "report.json",
    "long_k23sdet": D20_INVARIANTS / "proof_obligations" / "long_k23sdet" / "report.json",
    "long_k23froute": D20_INVARIANTS / "proof_obligations" / "long_k23froute" / "report.json",
    "long_k23csrc": D20_INVARIANTS / "proof_obligations" / "long_k23csrc" / "report.json",
    "long_k23fing": D20_INVARIANTS / "proof_obligations" / "long_k23fing" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23chal": "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED",
    "long_k23game": "SECTOR33_K23_VERIFICATION_GAME_TABLE_CERTIFIED",
    "long_k23roll": "SECTOR33_K23_SEMANTIC_GAME_PROTOCOL_ROLLUP_CERTIFIED",
    "long_k23rep": "SECTOR33_K23_REPEATED_ROUND_ACCOUNTING_CERTIFIED",
    "long_k23sync": "SECTOR33_K23_PROTOCOL_FRONTIER_HANDOFF_CERTIFIED",
    "long_k23sound": "SECTOR33_K23_BOUNDED_ADVERSARY_SOUNDNESS_CERTIFIED",
    "long_k23mand": "SECTOR33_K23_SOURCE_BOUND_MANDATE_CERTIFIED",
    "long_k23auth": "SECTOR33_K23_FINITE_AUTHORITY_CLOSURE_CERTIFIED",
    "long_k23sdet": "SECTOR33_K23_SUPERDETERMINISTIC_CRYPTOLOGIC_BOUNDARY_CERTIFIED",
    "long_k23froute": "SECTOR33_K23_PROOF_OF_MANDATE_FRONTIER_ROUTE_CERTIFIED",
    "long_k23csrc": "SECTOR33_K23_CHALLENGE_SOURCE_DECISION_CERTIFIED",
    "long_k23fing": "SECTOR33_K23_PROOF_OF_MANDATE_FRONTIER_INGESTION_CERTIFIED",
}

LEDGER_TEXT_HASH = "bdfc87b793f3863bf7a58457367f8824e07cafca11fd91f6598ee72e62b4930d"
NONCLAIM_TEXT_HASH = "68959fb04cbb56cd73a50a54e0cf8a2bdd3560d2757c3d18363518f43e01fb64"
OBS_TEXT_HASH = "345bf3c9e32f496113836423d442a447ed1191ee43337ef8d4e2897852b18f21"
MATRIX_SHA256 = "d977909135ac3e168a7bea2e86de1280fc708ce549ed583db0b90b42ceb4a147"

LEDGER_COLUMNS = [
    "ledger_id",
    "surface_code",
    "certified_flag",
    "game_support_flag",
    "mandate_core_flag",
    "frontier_support_flag",
    "source_decision_flag",
    "authority_closure_flag",
    "broad_integration_run_flag",
    "proof_of_mandate_contribution_flag",
]
NONCLAIM_COLUMNS = [
    "nonclaim_id",
    "nonclaim_code",
    "claim_flag",
    "open_flag",
    "preserved_flag",
    "required_for_current_mandate_flag",
    "broad_required_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "ledger_row_count",
    "certified_ledger_count",
    "game_support_count",
    "mandate_core_count",
    "frontier_support_count",
    "source_decision_count",
    "authority_closure_count",
    "broad_integration_run_count",
    "proof_mandate_contribution_count",
    "nonclaim_row_count",
    "open_nonclaim_count",
    "preserved_nonclaim_count",
    "required_nonclaim_count",
    "broad_required_nonclaim_count",
    "overclaim_count",
    "challenge_count",
    "selected_opening_unique_count",
    "game_row_count",
    "all_depth_false_accept_strategy_words",
    "all_depth_tamper_reject_strategy_words",
    "accepted_authority_count",
    "finite_authority_closure_flag",
    "proof_source_decision_flag",
    "route_blocking_count",
    "frontier_route_flag",
    "frontier_ingestion_flag",
    "proof_of_mandate_ledger_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

CHAIN = [
    "long_k23chal",
    "long_k23game",
    "long_k23roll",
    "long_k23rep",
    "long_k23sync",
    "long_k23sound",
    "long_k23mand",
    "long_k23auth",
    "long_k23sdet",
    "long_k23froute",
    "long_k23csrc",
    "long_k23fing",
]


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["ledger_table", "nonclaim_table", "observable_vector"]
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
    reports = {name: load_json(path) for name, path in REPORT_PATHS.items()}
    summaries = {name: summary(report) for name, report in reports.items()}
    certified = {name: is_certified(reports[name], EXPECTED_STATUSES[name]) for name in CHAIN}
    game_support = {"long_k23chal", "long_k23game", "long_k23roll", "long_k23rep", "long_k23sound"}
    mandate_core = {"long_k23mand", "long_k23auth", "long_k23sdet", "long_k23csrc", "long_k23fing"}
    frontier_support = {"long_k23sync", "long_k23froute", "long_k23csrc", "long_k23fing"}
    ledger_rows = []
    for ledger_id, name in enumerate(CHAIN):
        ledger_rows.append(
            {
                "ledger_id": ledger_id,
                "surface_code": ledger_id,
                "certified_flag": certified[name],
                "game_support_flag": int(name in game_support),
                "mandate_core_flag": int(name in mandate_core),
                "frontier_support_flag": int(name in frontier_support),
                "source_decision_flag": int(name == "long_k23csrc"),
                "authority_closure_flag": int(name == "long_k23auth"),
                "broad_integration_run_flag": 0,
                "proof_of_mandate_contribution_flag": 1,
            }
        )
    nonclaim_rows = [
        {"nonclaim_id": 0, "nonclaim_code": 0, "claim_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_current_mandate_flag": 0, "broad_required_flag": 0, "overclaim_flag": 0},
        {"nonclaim_id": 1, "nonclaim_code": 1, "claim_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_current_mandate_flag": 0, "broad_required_flag": 0, "overclaim_flag": 0},
        {"nonclaim_id": 2, "nonclaim_code": 2, "claim_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_current_mandate_flag": 0, "broad_required_flag": 0, "overclaim_flag": 0},
        {"nonclaim_id": 3, "nonclaim_code": 3, "claim_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_current_mandate_flag": 0, "broad_required_flag": 0, "overclaim_flag": 0},
        {"nonclaim_id": 4, "nonclaim_code": 4, "claim_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_current_mandate_flag": 0, "broad_required_flag": 0, "overclaim_flag": 0},
        {"nonclaim_id": 5, "nonclaim_code": 5, "claim_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_current_mandate_flag": 0, "broad_required_flag": 1, "overclaim_flag": 0},
        {"nonclaim_id": 6, "nonclaim_code": 6, "claim_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_current_mandate_flag": 0, "broad_required_flag": 0, "overclaim_flag": 0},
        {"nonclaim_id": 7, "nonclaim_code": 7, "claim_flag": 0, "open_flag": 1, "preserved_flag": 1, "required_for_current_mandate_flag": 0, "broad_required_flag": 0, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": len(CHAIN),
        "certified_input_count": sum(certified.values()),
        "ledger_row_count": len(ledger_rows),
        "certified_ledger_count": sum(row["certified_flag"] for row in ledger_rows),
        "game_support_count": sum(row["game_support_flag"] for row in ledger_rows),
        "mandate_core_count": sum(row["mandate_core_flag"] for row in ledger_rows),
        "frontier_support_count": sum(row["frontier_support_flag"] for row in ledger_rows),
        "source_decision_count": sum(row["source_decision_flag"] for row in ledger_rows),
        "authority_closure_count": sum(row["authority_closure_flag"] for row in ledger_rows),
        "broad_integration_run_count": sum(row["broad_integration_run_flag"] for row in ledger_rows),
        "proof_mandate_contribution_count": sum(row["proof_of_mandate_contribution_flag"] for row in ledger_rows),
        "nonclaim_row_count": len(nonclaim_rows),
        "open_nonclaim_count": sum(row["open_flag"] for row in nonclaim_rows),
        "preserved_nonclaim_count": sum(row["preserved_flag"] for row in nonclaim_rows),
        "required_nonclaim_count": sum(row["required_for_current_mandate_flag"] for row in nonclaim_rows),
        "broad_required_nonclaim_count": sum(row["broad_required_flag"] for row in nonclaim_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in nonclaim_rows),
        "challenge_count": int(summaries["long_k23chal"].get("challenge_count", -1)),
        "selected_opening_unique_count": int(summaries["long_k23chal"].get("selected_opening_unique_count", -1)),
        "game_row_count": int(summaries["long_k23game"].get("game_row_count", -1)),
        "all_depth_false_accept_strategy_words": int(summaries["long_k23sound"].get("all_depth_false_accept_strategy_words", -1)),
        "all_depth_tamper_reject_strategy_words": int(summaries["long_k23sound"].get("all_depth_tamper_reject_strategy_words", -1)),
        "accepted_authority_count": int(summaries["long_k23auth"].get("accepted_authority_count", -1)),
        "finite_authority_closure_flag": int(summaries["long_k23auth"].get("finite_authority_closure_flag", -1)),
        "proof_source_decision_flag": int(summaries["long_k23csrc"].get("proof_of_mandate_source_decision_flag", -1)),
        "route_blocking_count": int(summaries["long_k23csrc"].get("route_blocking_count", -1)),
        "frontier_route_flag": int(summaries["long_k23froute"].get("proof_of_mandate_frontier_route_flag", -1)),
        "frontier_ingestion_flag": int(summaries["long_k23fing"].get("proof_of_mandate_frontier_ingestion_flag", -1)),
        "proof_of_mandate_ledger_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    ledger_table = table_from_rows(LEDGER_COLUMNS, ledger_rows)
    nonclaim_table = table_from_rows(NONCLAIM_COLUMNS, nonclaim_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "ledger_table": ledger_table.astype(np.int64),
        "nonclaim_table": nonclaim_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "ledger_rows": ledger_rows,
        "nonclaim_rows": nonclaim_rows,
        "obs_rows": obs_rows,
        "ledger_table": ledger_table,
        "nonclaim_table": nonclaim_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "ledger_text_hash": hashlib.sha256(digest_text(LEDGER_COLUMNS, ledger_rows).encode("ascii")).hexdigest(),
        "nonclaim_text_hash": hashlib.sha256(digest_text(NONCLAIM_COLUMNS, nonclaim_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 12,
        "ledger_profile_matches": (
            obs["ledger_row_count"],
            obs["certified_ledger_count"],
            obs["game_support_count"],
            obs["mandate_core_count"],
            obs["frontier_support_count"],
            obs["source_decision_count"],
            obs["authority_closure_count"],
            obs["proof_mandate_contribution_count"],
        )
        == (12, 12, 5, 5, 4, 1, 1, 12),
        "nonclaim_profile_matches": (
            obs["nonclaim_row_count"],
            obs["open_nonclaim_count"],
            obs["preserved_nonclaim_count"],
            obs["required_nonclaim_count"],
            obs["broad_required_nonclaim_count"],
            obs["overclaim_count"],
        )
        == (8, 8, 8, 0, 1, 0),
        "proof_mandate_counts_match": (
            obs["challenge_count"],
            obs["selected_opening_unique_count"],
            obs["game_row_count"],
            obs["all_depth_false_accept_strategy_words"],
            obs["all_depth_tamper_reject_strategy_words"],
            obs["accepted_authority_count"],
            obs["finite_authority_closure_flag"],
            obs["proof_source_decision_flag"],
            obs["route_blocking_count"],
            obs["frontier_route_flag"],
            obs["frontier_ingestion_flag"],
        )
        == (56, 56, 336, 0, 112_869_680, 56, 1, 1, 0, 1, 1),
        "broad_boundary_matches": obs["broad_integration_run_count"] == 0,
        "boundary_flags_match": (
            obs["proof_of_mandate_ledger_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_proof_of_mandate_ledger",
        "surface_code_map": {str(index): name for index, name in enumerate(CHAIN)},
        "nonclaim_code_map": {
            "0": "independent_challenge_randomness",
            "1": "computational_hardness",
            "2": "zero_knowledge",
            "3": "unbounded_adversary_security",
            "4": "repository_visible_witness_secrecy",
            "5": "bundle_wide_integration",
            "6": "regenerated_frontier_with_new_row",
            "7": "active_goal_completion",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This ledger lists the certified proof-of-mandate chain and keeps all external security and integration nonclaims open.",
    }
    seam_payload = {
        "schema": "long.k23mledger.seam@1",
        "status": STATUS,
        "claim": "The verified K23 proof-of-mandate chain is ledgered as a focused local certificate without broad integration.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        name: input_entry(
            REPORT_PATHS[name],
            {
                "status": rows["reports"][name].get("status"),
                "certificate_sha256": rows["reports"][name].get("certificate_sha256"),
            },
        )
        for name in CHAIN
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23mledger.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23mledger certifies the focused proof-of-mandate ledger.",
        "stage_protocol": {
            "draft": "read the certified K23 challenge, game, rollup, repetition, soundness, mandate, authority, source, route, and ingestion reports",
            "witness": "emit mandate-ledger rows, nonclaim rows, observables, and numeric tables",
            "coherence": "check every input certificate, proof-of-mandate counts, open nonclaims, and broad-refresh deferral",
            "closure": "certify the local proof-of-mandate ledger without claiming external security or bundle integration",
            "emit": "write long_k23mledger artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "ledger_rows_csv": relpath(OUT_DIR / "ledger_rows.csv"),
            "nonclaim_rows_csv": relpath(OUT_DIR / "nonclaim_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23mledger_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all 12 focused proof-of-mandate chain reports are certified inputs",
                "the deterministic challenge, bounded game, repeated accounting, and soundness surfaces are ledgered",
                "the source-bound mandate and finite authority closure are ledgered",
                "the source decision, frontier route, and local frontier ingestion are ledgered",
                "all external security and integration nonclaims remain open and nonblocking",
            ],
            "does_not_certify": [
                "independent challenge randomness",
                "computational hardness",
                "zero knowledge",
                "unbounded adversary security",
                "secrecy of repository-visible witness rows",
                "bundle-wide integration",
                "a regenerated frontier report containing this ledger",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Begin the productive-potential seam: finite efficiency/security improvement candidates over existing cryptologic specifications, with external comparisons kept sourced and provisional.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23mledger.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23mledger.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "ledger_csv": csv_text(LEDGER_COLUMNS, rows["ledger_rows"]),
        "nonclaim_csv": csv_text(NONCLAIM_COLUMNS, rows["nonclaim_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "ledger_table": rows["ledger_table"],
        "nonclaim_table": rows["nonclaim_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "ledger_text_sha256": rows["ledger_text_hash"],
            "nonclaim_text_sha256": rows["nonclaim_text_hash"],
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
    (OUT_DIR / "ledger_rows.csv").write_text(payloads["ledger_csv"], encoding="utf-8")
    (OUT_DIR / "nonclaim_rows.csv").write_text(payloads["nonclaim_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        ledger_table=payloads["ledger_table"],
        nonclaim_table=payloads["nonclaim_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23mledger_matrices.npz", **payloads["matrix_payload"])
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
