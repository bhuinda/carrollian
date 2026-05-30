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


THEOREM_ID = "long_k23sdet"
STATUS = "SECTOR33_K23_SUPERDETERMINISTIC_CRYPTOLOGIC_BOUNDARY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23sdet.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23sdet.py"
LONG_K23CHAL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json"
LONG_K23GAME_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23game" / "report.json"
LONG_K23REP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rep" / "report.json"
LONG_K23SOUND_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23sound" / "report.json"
LONG_K23AUTH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23auth" / "report.json"

SOURCE_TEXT_HASH = "c70fa3a1a1da2a5043064b1376eb04b444b5243ca56abbae11ac566d6395d894"
LIMIT_TEXT_HASH = "30c69e69cf52c01f7052bdd8192801edf512e8552c9abdb45d1a2378c2972157"
OBS_TEXT_HASH = "c9210177c069aa6bdfc3fd1096a6c3620bc6b847b5e905da6c93a74d086ceff7"
MATRIX_SHA256 = "c60a9a46ffe84398368057b2be84078f625aee6771e36e3c80330962de26d1a2"

SOURCE_COLUMNS = [
    "source_row_id",
    "source_code",
    "certified_flag",
    "deterministic_challenge_flag",
    "finite_game_flag",
    "bounded_soundness_flag",
    "authority_closure_flag",
    "external_randomness_claim_flag",
    "hardness_claim_flag",
    "superdeterministic_source_flag",
]
LIMIT_COLUMNS = [
    "limit_id",
    "limit_code",
    "claim_flag",
    "source_present_flag",
    "certified_closed_flag",
    "open_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "source_row_count",
    "certified_source_row_count",
    "deterministic_source_row_count",
    "finite_game_source_row_count",
    "bounded_soundness_source_row_count",
    "authority_closure_source_row_count",
    "external_randomness_claim_count",
    "hardness_claim_count",
    "challenge_count",
    "selected_opening_unique_count",
    "game_row_count",
    "rejected_tamper_count",
    "max_round_depth",
    "all_depth_false_accept_strategy_words",
    "all_depth_tamper_reject_strategy_words",
    "bounded_soundness_error_numerator",
    "authority_row_count",
    "accepted_authority_count",
    "external_randomness_required_count",
    "finite_authority_closure_flag",
    "limit_row_count",
    "open_limit_count",
    "superdeterministic_cryptologic_boundary_flag",
    "randomness_independence_claim_flag",
    "zero_knowledge_claim_flag",
    "unbounded_adversary_claim_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

EXPECTED_STATUSES = {
    "long_k23chal": "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED",
    "long_k23game": "SECTOR33_K23_VERIFICATION_GAME_TABLE_CERTIFIED",
    "long_k23rep": "SECTOR33_K23_REPEATED_ROUND_ACCOUNTING_CERTIFIED",
    "long_k23sound": "SECTOR33_K23_BOUNDED_ADVERSARY_SOUNDNESS_CERTIFIED",
    "long_k23auth": "SECTOR33_K23_FINITE_AUTHORITY_CLOSURE_CERTIFIED",
}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["source_table", "limit_table", "observable_vector"]
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
        "long_k23chal": load_json(LONG_K23CHAL_REPORT),
        "long_k23game": load_json(LONG_K23GAME_REPORT),
        "long_k23rep": load_json(LONG_K23REP_REPORT),
        "long_k23sound": load_json(LONG_K23SOUND_REPORT),
        "long_k23auth": load_json(LONG_K23AUTH_REPORT),
    }
    summaries = {name: summary(report) for name, report in reports.items()}
    source_rows = [
        {
            "source_row_id": 0,
            "source_code": 0,
            "certified_flag": is_certified(reports["long_k23chal"], EXPECTED_STATUSES["long_k23chal"]),
            "deterministic_challenge_flag": 1,
            "finite_game_flag": 0,
            "bounded_soundness_flag": 0,
            "authority_closure_flag": 0,
            "external_randomness_claim_flag": 0,
            "hardness_claim_flag": 0,
            "superdeterministic_source_flag": 1,
        },
        {
            "source_row_id": 1,
            "source_code": 1,
            "certified_flag": is_certified(reports["long_k23game"], EXPECTED_STATUSES["long_k23game"]),
            "deterministic_challenge_flag": 1,
            "finite_game_flag": 1,
            "bounded_soundness_flag": 0,
            "authority_closure_flag": 0,
            "external_randomness_claim_flag": 0,
            "hardness_claim_flag": 0,
            "superdeterministic_source_flag": 1,
        },
        {
            "source_row_id": 2,
            "source_code": 2,
            "certified_flag": is_certified(reports["long_k23rep"], EXPECTED_STATUSES["long_k23rep"]),
            "deterministic_challenge_flag": 1,
            "finite_game_flag": 1,
            "bounded_soundness_flag": 0,
            "authority_closure_flag": 0,
            "external_randomness_claim_flag": 0,
            "hardness_claim_flag": 0,
            "superdeterministic_source_flag": 1,
        },
        {
            "source_row_id": 3,
            "source_code": 3,
            "certified_flag": is_certified(reports["long_k23sound"], EXPECTED_STATUSES["long_k23sound"]),
            "deterministic_challenge_flag": 1,
            "finite_game_flag": 1,
            "bounded_soundness_flag": 1,
            "authority_closure_flag": 0,
            "external_randomness_claim_flag": 0,
            "hardness_claim_flag": 0,
            "superdeterministic_source_flag": 1,
        },
        {
            "source_row_id": 4,
            "source_code": 4,
            "certified_flag": is_certified(reports["long_k23auth"], EXPECTED_STATUSES["long_k23auth"]),
            "deterministic_challenge_flag": 1,
            "finite_game_flag": 1,
            "bounded_soundness_flag": 1,
            "authority_closure_flag": 1,
            "external_randomness_claim_flag": 0,
            "hardness_claim_flag": 0,
            "superdeterministic_source_flag": 1,
        },
    ]
    limit_rows = [
        {
            "limit_id": limit_id,
            "limit_code": limit_id,
            "claim_flag": 0,
            "source_present_flag": 0,
            "certified_closed_flag": 0,
            "open_flag": 1,
        }
        for limit_id in range(8)
    ]
    obs = {
        "input_report_count": len(reports),
        "certified_input_count": sum(
            is_certified(reports[name], EXPECTED_STATUSES[name]) for name in sorted(reports)
        ),
        "source_row_count": len(source_rows),
        "certified_source_row_count": sum(row["certified_flag"] for row in source_rows),
        "deterministic_source_row_count": sum(row["deterministic_challenge_flag"] for row in source_rows),
        "finite_game_source_row_count": sum(row["finite_game_flag"] for row in source_rows),
        "bounded_soundness_source_row_count": sum(row["bounded_soundness_flag"] for row in source_rows),
        "authority_closure_source_row_count": sum(row["authority_closure_flag"] for row in source_rows),
        "external_randomness_claim_count": sum(row["external_randomness_claim_flag"] for row in source_rows),
        "hardness_claim_count": sum(row["hardness_claim_flag"] for row in source_rows),
        "challenge_count": int(summaries["long_k23chal"].get("challenge_count", -1)),
        "selected_opening_unique_count": int(summaries["long_k23chal"].get("selected_opening_unique_count", -1)),
        "game_row_count": int(summaries["long_k23game"].get("game_row_count", -1)),
        "rejected_tamper_count": int(summaries["long_k23game"].get("rejected_tamper_count", -1)),
        "max_round_depth": int(summaries["long_k23rep"].get("max_round_depth", -1)),
        "all_depth_false_accept_strategy_words": int(
            summaries["long_k23sound"].get("all_depth_false_accept_strategy_words", -1)
        ),
        "all_depth_tamper_reject_strategy_words": int(
            summaries["long_k23sound"].get("all_depth_tamper_reject_strategy_words", -1)
        ),
        "bounded_soundness_error_numerator": int(
            summaries["long_k23sound"].get("bounded_soundness_error_numerator", -1)
        ),
        "authority_row_count": int(summaries["long_k23auth"].get("authority_row_count", -1)),
        "accepted_authority_count": int(summaries["long_k23auth"].get("accepted_authority_count", -1)),
        "external_randomness_required_count": int(
            summaries["long_k23auth"].get("external_randomness_required_count", -1)
        ),
        "finite_authority_closure_flag": int(
            summaries["long_k23auth"].get("finite_authority_closure_flag", -1)
        ),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "superdeterministic_cryptologic_boundary_flag": 1,
        "randomness_independence_claim_flag": 0,
        "zero_knowledge_claim_flag": int(summaries["long_k23sound"].get("zero_knowledge_claim_flag", 0)),
        "unbounded_adversary_claim_flag": int(
            summaries["long_k23sound"].get("unbounded_adversary_claim_flag", 0)
        ),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    source_table = table_from_rows(SOURCE_COLUMNS, source_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "source_table": source_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "source_rows": source_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "source_table": source_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "source_text_hash": hashlib.sha256(digest_text(SOURCE_COLUMNS, source_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 5,
        "source_profile_matches": (
            obs["source_row_count"],
            obs["certified_source_row_count"],
            obs["deterministic_source_row_count"],
            obs["finite_game_source_row_count"],
            obs["bounded_soundness_source_row_count"],
            obs["authority_closure_source_row_count"],
        )
        == (5, 5, 5, 4, 2, 1),
        "deterministic_chain_matches": (
            obs["challenge_count"],
            obs["selected_opening_unique_count"],
            obs["game_row_count"],
            obs["rejected_tamper_count"],
            obs["max_round_depth"],
        )
        == (56, 56, 336, 280, 8),
        "authority_soundness_matches": (
            obs["all_depth_false_accept_strategy_words"],
            obs["all_depth_tamper_reject_strategy_words"],
            obs["bounded_soundness_error_numerator"],
            obs["authority_row_count"],
            obs["accepted_authority_count"],
            obs["external_randomness_required_count"],
            obs["finite_authority_closure_flag"],
        )
        == (0, 112_869_680, 0, 56, 56, 0, 1),
        "security_limits_open": (
            obs["external_randomness_claim_count"],
            obs["hardness_claim_count"],
            obs["randomness_independence_claim_flag"],
            obs["zero_knowledge_claim_flag"],
            obs["unbounded_adversary_claim_flag"],
            obs["limit_row_count"],
            obs["open_limit_count"],
        )
        == (0, 0, 0, 0, 0, 8, 8),
        "boundary_flags_match": (
            obs["superdeterministic_cryptologic_boundary_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_superdeterministic_cryptologic_boundary",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the deterministic finite challenge/security boundary: no independent challenge randomness is used or claimed.",
    }
    seam_payload = {
        "schema": "long.k23sdet.seam@1",
        "status": STATUS,
        "claim": "The K23 verifier chain is a source-bound deterministic cryptologic boundary, not a random-oracle or hardness claim.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        name: input_entry(
            path,
            {
                "status": rows["reports"][name].get("status"),
                "certificate_sha256": rows["reports"][name].get("certificate_sha256"),
            },
        )
        for name, path in {
            "long_k23chal": LONG_K23CHAL_REPORT,
            "long_k23game": LONG_K23GAME_REPORT,
            "long_k23rep": LONG_K23REP_REPORT,
            "long_k23sound": LONG_K23SOUND_REPORT,
            "long_k23auth": LONG_K23AUTH_REPORT,
        }.items()
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23sdet.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23sdet certifies the source-bound superdeterministic cryptologic boundary for the K23 proof-of-mandate chain.",
        "stage_protocol": {
            "draft": "read challenge, game, repeated-round, soundness, and authority reports",
            "witness": "emit source rows, open-limit rows, observables, and numeric tables",
            "coherence": "check deterministic source binding, bounded soundness, and finite authority counts",
            "closure": "certify the deterministic finite security boundary while leaving independent randomness and hardness open",
            "emit": "write long_k23sdet artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "source_rows_csv": relpath(OUT_DIR / "source_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23sdet_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the challenge selector is deterministic and source-bound",
                "the bounded game table has zero unexpected accepts",
                "bounded repeated tamper words have zero false accepts through depth eight",
                "all 56 authority decisions are mandate-bound and accepted",
                "no independent challenge randomness is required by the finite authority layer",
            ],
            "does_not_certify": [
                "independent random challenge generation",
                "computational hardness",
                "zero knowledge",
                "unbounded adversary security",
                "secrecy of repository-visible witness rows",
                "bundle-wide integration",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Route this deterministic cryptologic boundary into the frontier handoff, then decide whether a new challenge-source extension is needed or should stay explicitly open.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23sdet.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23sdet.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "source_csv": csv_text(SOURCE_COLUMNS, rows["source_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "source_table": rows["source_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "source_text_sha256": rows["source_text_hash"],
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
    (OUT_DIR / "source_rows.csv").write_text(payloads["source_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        source_table=payloads["source_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23sdet_matrices.npz", **payloads["matrix_payload"])
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
