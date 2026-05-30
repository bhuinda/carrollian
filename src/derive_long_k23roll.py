from __future__ import annotations

import hashlib
import json
from pathlib import Path
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


THEOREM_ID = "long_k23roll"
STATUS = "SECTOR33_K23_SEMANTIC_GAME_PROTOCOL_ROLLUP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23roll.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23roll.py"
LONG_K23FAM_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23fam" / "report.json"
LONG_K23POLY_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23poly" / "report.json"
LONG_K23REW_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rew" / "report.json"
LONG_K23COP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "report.json"
LONG_K23CHAL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json"
LONG_K23GAME_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23game" / "report.json"

CHAIN_TEXT_HASH = "5add79318f63944506b17aae5f3ca5001b54844c971005b5fe8499d50c2f556d"
LIMIT_TEXT_HASH = "21c47570a9f4fcf1641ca4e7ff71384035eff1c92a457d2725a880df797e9b66"
OBS_TEXT_HASH = "572cd5b3f7643f1f84571b0034896ac5d8b456337e023d79cc5b92a9e6025fb3"
MATRIX_SHA256 = "3c1b3c3dd171a8e00d6093f2653cbd999395eb2ee8cae9c2739ff86293935a5c"

CHAIN_COLUMNS = [
    "stage_id",
    "layer_code",
    "proof_id",
    "status",
    "certified_flag",
    "primary_count",
    "secondary_count",
    "certificate_sha256",
]
LIMIT_COLUMNS = [
    "limit_id",
    "limit_code",
    "limit_name",
    "certified_negative_flag",
    "claim_flag",
    "source_stage_id",
]
CHAIN_NUMERIC_COLUMNS = [
    "stage_id",
    "layer_code",
    "certified_flag",
    "primary_count",
    "secondary_count",
]
LIMIT_NUMERIC_COLUMNS = [
    "limit_id",
    "limit_code",
    "certified_negative_flag",
    "claim_flag",
    "source_stage_id",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "chain_stage_count",
    "merge_layer_count",
    "minimal_family_obstructed_flag",
    "word_carrier_certified_flag",
    "rewrite_obstructed_flag",
    "commit_open_certified_flag",
    "challenge_certified_flag",
    "game_payoff_certified_flag",
    "certified_merge_point_flag",
    "open_limit_count",
    "hardness_claim_flag",
    "secrecy_claim_flag",
    "zero_knowledge_claim_flag",
    "repeated_soundness_claim_flag",
    "bundle_integration_claim_flag",
    "final_goal_claim_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


EXPECTED_STATUSES = {
    "long_k23fam": "SECTOR33_K23_MINIMAL_REPAIRED_PROJECTION_FAMILY_OBSTRUCTED",
    "long_k23poly": "SECTOR33_K23_CONCATENATIVE_POLYMORPHISM_CARRIER_CERTIFIED",
    "long_k23rew": "SECTOR33_K23_BOUNDED_REWRITE_FINGERPRINT_OBSTRUCTION_CERTIFIED",
    "long_k23cop": "SECTOR33_K23_COMMIT_OPEN_TRANSCRIPT_CERTIFIED",
    "long_k23chal": "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED",
    "long_k23game": "SECTOR33_K23_VERIFICATION_GAME_TABLE_CERTIFIED",
}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["chain_numeric_table", "limit_numeric_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def is_certified(report: dict[str, Any], proof_id: str) -> int:
    return int(
        report.get("status") == EXPECTED_STATUSES[proof_id]
        and report.get("all_checks_pass") is True
    )


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def int_summary(report: dict[str, Any], name: str) -> int:
    return int(summary(report).get(name, 0))


def build_rows() -> dict[str, Any]:
    reports = {
        "long_k23fam": load_json(LONG_K23FAM_REPORT),
        "long_k23poly": load_json(LONG_K23POLY_REPORT),
        "long_k23rew": load_json(LONG_K23REW_REPORT),
        "long_k23cop": load_json(LONG_K23COP_REPORT),
        "long_k23chal": load_json(LONG_K23CHAL_REPORT),
        "long_k23game": load_json(LONG_K23GAME_REPORT),
    }
    chain_specs = [
        (0, 0, "long_k23fam", int_summary(reports["long_k23fam"], "rank_restoring_candidate_count"), int_summary(reports["long_k23fam"], "product_obstructed_candidate_count")),
        (1, 1, "long_k23poly", int_summary(reports["long_k23poly"], "word_count"), int_summary(reports["long_k23poly"], "square_return_word_count")),
        (2, 1, "long_k23rew", int_summary(reports["long_k23rew"], "carrier_class_count"), int_summary(reports["long_k23rew"], "fingerprint_preserving_closing_rewrite_count")),
        (3, 2, "long_k23cop", int_summary(reports["long_k23cop"], "public_transcript_count"), int_summary(reports["long_k23cop"], "opening_row_count")),
        (4, 3, "long_k23chal", int_summary(reports["long_k23chal"], "challenge_count"), int_summary(reports["long_k23chal"], "reject_control_count")),
        (5, 4, "long_k23game", int_summary(reports["long_k23game"], "game_row_count"), int_summary(reports["long_k23game"], "verifier_payoff_total")),
    ]
    chain_rows = []
    for stage_id, layer_code, proof_id, primary_count, secondary_count in chain_specs:
        report = reports[proof_id]
        chain_rows.append(
            {
                "stage_id": stage_id,
                "layer_code": layer_code,
                "proof_id": proof_id,
                "status": str(report.get("status", "")),
                "certified_flag": is_certified(report, proof_id),
                "primary_count": primary_count,
                "secondary_count": secondary_count,
                "certificate_sha256": str(report.get("certificate_sha256", "")),
            }
        )

    limit_names = [
        "hash_collision_resistance",
        "repository_witness_secrecy",
        "zero_knowledge",
        "probabilistic_repeated_soundness",
        "deeper_word_depth",
        "bundle_wide_integration",
        "final_broad_goal_closure",
    ]
    limit_rows = [
        {
            "limit_id": index,
            "limit_code": index,
            "limit_name": name,
            "certified_negative_flag": 0,
            "claim_flag": 0,
            "source_stage_id": min(index, 5),
        }
        for index, name in enumerate(limit_names)
    ]
    obs = {
        "input_report_count": len(reports),
        "certified_input_count": sum(row["certified_flag"] for row in chain_rows),
        "chain_stage_count": len(chain_rows),
        "merge_layer_count": len({row["layer_code"] for row in chain_rows}),
        "minimal_family_obstructed_flag": chain_rows[0]["certified_flag"],
        "word_carrier_certified_flag": chain_rows[1]["certified_flag"],
        "rewrite_obstructed_flag": chain_rows[2]["certified_flag"],
        "commit_open_certified_flag": chain_rows[3]["certified_flag"],
        "challenge_certified_flag": chain_rows[4]["certified_flag"],
        "game_payoff_certified_flag": chain_rows[5]["certified_flag"],
        "certified_merge_point_flag": int(all(row["certified_flag"] for row in chain_rows)),
        "open_limit_count": len(limit_rows),
        "hardness_claim_flag": 0,
        "secrecy_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "repeated_soundness_claim_flag": 0,
        "bundle_integration_claim_flag": 0,
        "final_goal_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    chain_numeric_table = table_from_rows(CHAIN_NUMERIC_COLUMNS, chain_rows)
    limit_numeric_table = table_from_rows(LIMIT_NUMERIC_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "chain_numeric_table": chain_numeric_table.astype(np.int64),
        "limit_numeric_table": limit_numeric_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "chain_rows": chain_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "chain_numeric_table": chain_numeric_table,
        "limit_numeric_table": limit_numeric_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "chain_text_hash": hashlib.sha256(digest_text(CHAIN_COLUMNS, chain_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["input_report_count"],
            obs["certified_input_count"],
            obs["chain_stage_count"],
        )
        == (6, 6, 6),
        "merge_flags_match": (
            obs["minimal_family_obstructed_flag"],
            obs["word_carrier_certified_flag"],
            obs["rewrite_obstructed_flag"],
            obs["commit_open_certified_flag"],
            obs["challenge_certified_flag"],
            obs["game_payoff_certified_flag"],
            obs["certified_merge_point_flag"],
        )
        == (1, 1, 1, 1, 1, 1, 1),
        "open_limits_explicit": (
            obs["open_limit_count"],
            obs["hardness_claim_flag"],
            obs["secrecy_claim_flag"],
            obs["zero_knowledge_claim_flag"],
            obs["repeated_soundness_claim_flag"],
            obs["bundle_integration_claim_flag"],
            obs["final_goal_claim_flag"],
        )
        == (7, 0, 0, 0, 0, 0, 0),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_semantic_game_protocol_rollup",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the bounded merge point where the K23 semantic carrier, transcript protocol, verifier challenge, and finite game payoff cohere.",
    }
    seam_payload = {
        "schema": "long.k23roll.seam@1",
        "status": STATUS,
        "claim": "The finite K23 chain now has a certified merge point from semantic word carrier to transcript protocol to verifier challenge to game payoff.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23fam": input_entry(
            LONG_K23FAM_REPORT,
            {"status": rows["reports"]["long_k23fam"].get("status"), "certificate_sha256": rows["reports"]["long_k23fam"].get("certificate_sha256")},
        ),
        "long_k23poly": input_entry(
            LONG_K23POLY_REPORT,
            {"status": rows["reports"]["long_k23poly"].get("status"), "certificate_sha256": rows["reports"]["long_k23poly"].get("certificate_sha256")},
        ),
        "long_k23rew": input_entry(
            LONG_K23REW_REPORT,
            {"status": rows["reports"]["long_k23rew"].get("status"), "certificate_sha256": rows["reports"]["long_k23rew"].get("certificate_sha256")},
        ),
        "long_k23cop": input_entry(
            LONG_K23COP_REPORT,
            {"status": rows["reports"]["long_k23cop"].get("status"), "certificate_sha256": rows["reports"]["long_k23cop"].get("certificate_sha256")},
        ),
        "long_k23chal": input_entry(
            LONG_K23CHAL_REPORT,
            {"status": rows["reports"]["long_k23chal"].get("status"), "certificate_sha256": rows["reports"]["long_k23chal"].get("certificate_sha256")},
        ),
        "long_k23game": input_entry(
            LONG_K23GAME_REPORT,
            {"status": rows["reports"]["long_k23game"].get("status"), "certificate_sha256": rows["reports"]["long_k23game"].get("certificate_sha256")},
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23roll.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23roll certifies the bounded K23 semantic/game/protocol merge point.",
        "stage_protocol": {
            "draft": "read the focused K23 family, word-carrier, rewrite, transcript, challenge, and game certificates",
            "witness": "emit chain rows, open-limit rows, observables, and numeric tables",
            "coherence": "check all input certificates pass and all open cryptologic limits remain claim-free",
            "closure": "certify the finite merge point while leaving broad and cryptologic claims open",
            "emit": "write long_k23roll artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "chain_rows_csv": relpath(OUT_DIR / "chain_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23roll_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the minimal repaired-projection family is product-action obstructed",
                "the word-level carrier preserves quotient/unit behavior",
                "bounded fingerprint-preserving rewrites cannot close product defects",
                "the commit/open transcript surface is checked",
                "the verifier challenge layer accepts canonical openings and rejects single-field tamper controls",
                "the finite game table has verifier payoff one on all bounded rows",
                "these surfaces form the certified finite merge point of semantics, transcript protocol, and game payoff",
            ],
            "does_not_certify": [
                "cryptographic hardness",
                "secrecy of repository-visible witnesses",
                "zero knowledge",
                "probabilistic repeated soundness",
                "word-depth exhaustiveness beyond the bounded surface",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Feed this rollup back into the focused frontier/oracle index when broad integration is permitted; otherwise extend the finite challenge game with repeated-round accounting.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23roll.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23roll.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "chain_csv": csv_text(CHAIN_COLUMNS, rows["chain_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "chain_numeric_table": rows["chain_numeric_table"],
        "limit_numeric_table": rows["limit_numeric_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "chain_text_sha256": rows["chain_text_hash"],
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
    (OUT_DIR / "chain_rows.csv").write_text(payloads["chain_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        chain_numeric_table=payloads["chain_numeric_table"],
        limit_numeric_table=payloads["limit_numeric_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23roll_matrices.npz", **payloads["matrix_payload"])
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
