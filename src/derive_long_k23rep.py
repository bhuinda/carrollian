from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23fam import read_csv_rows
    from .derive_long_k23game import OUT_DIR as LONG_K23GAME_DIR
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23fam import read_csv_rows
    from derive_long_k23game import OUT_DIR as LONG_K23GAME_DIR
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23rep"
STATUS = "SECTOR33_K23_REPEATED_ROUND_ACCOUNTING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23rep.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23rep.py"
LONG_K23GAME_REPORT = LONG_K23GAME_DIR / "report.json"
LONG_K23GAME_ROWS = LONG_K23GAME_DIR / "game_rows.csv"
LONG_K23GAME_PAYOFF = LONG_K23GAME_DIR / "payoff_rows.csv"

ROUND_TEXT_HASH = "c410844dd24fd05f2b4e7aa7cd5bc5ff03a6b883fb3b94334fa98973a622ea99"
OBS_TEXT_HASH = "751c42da29f1b073ffeed6e5a0eac3e42aa901dff0d0ae3211b4bf5549a2153a"
MATRIX_SHA256 = "79ecac40e9a94ef032a43113b02e1909567dfd965b08ae96abe1691aed1b8fb5"
MAX_ROUND_DEPTH = 8

ROUND_COLUMNS = [
    "round_depth",
    "transcript_count",
    "move_family_count",
    "honest_move_family_count",
    "tamper_move_family_count",
    "strategy_words_per_transcript",
    "accepted_words_per_transcript",
    "rejected_words_per_transcript",
    "total_strategy_words",
    "accepted_strategy_words",
    "rejected_strategy_words",
    "verifier_payoff_total",
    "prover_payoff_total",
    "accept_ratio_numerator",
    "accept_ratio_denominator",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23game_certified_flag",
    "round_depth_count",
    "max_round_depth",
    "transcript_count",
    "move_family_count",
    "honest_move_family_count",
    "tamper_move_family_count",
    "one_round_game_row_count",
    "final_depth_total_strategy_words",
    "final_depth_accepted_strategy_words",
    "final_depth_rejected_strategy_words",
    "all_depth_total_strategy_words",
    "all_depth_accepted_strategy_words",
    "all_depth_rejected_strategy_words",
    "probability_soundness_claim_flag",
    "hardness_claim_flag",
    "strategy_exhaustiveness_beyond_bounded_moves_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["round_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23game = load_json(LONG_K23GAME_REPORT)
    game_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23GAME_ROWS)]
    payoff_rows = read_csv_rows(LONG_K23GAME_PAYOFF)
    transcripts = sorted({row["transcript_id"] for row in game_rows})
    move_families = sorted({row["prover_move_code"] for row in game_rows})
    label_counts = Counter(row["payoff_label"] for row in payoff_rows for _ in range(int(row["row_count"])))
    honest_move_count = len([move for move in move_families if move == 0])
    tamper_move_count = len([move for move in move_families if move != 0])
    transcript_count = len(transcripts)
    move_family_count = len(move_families)

    round_rows = []
    for depth in range(1, MAX_ROUND_DEPTH + 1):
        strategy_words_per_transcript = move_family_count**depth
        accepted_words_per_transcript = honest_move_count**depth
        rejected_words_per_transcript = strategy_words_per_transcript - accepted_words_per_transcript
        total_strategy_words = transcript_count * strategy_words_per_transcript
        accepted_strategy_words = transcript_count * accepted_words_per_transcript
        rejected_strategy_words = transcript_count * rejected_words_per_transcript
        round_rows.append(
            {
                "round_depth": depth,
                "transcript_count": transcript_count,
                "move_family_count": move_family_count,
                "honest_move_family_count": honest_move_count,
                "tamper_move_family_count": tamper_move_count,
                "strategy_words_per_transcript": strategy_words_per_transcript,
                "accepted_words_per_transcript": accepted_words_per_transcript,
                "rejected_words_per_transcript": rejected_words_per_transcript,
                "total_strategy_words": total_strategy_words,
                "accepted_strategy_words": accepted_strategy_words,
                "rejected_strategy_words": rejected_strategy_words,
                "verifier_payoff_total": total_strategy_words,
                "prover_payoff_total": accepted_strategy_words,
                "accept_ratio_numerator": accepted_words_per_transcript,
                "accept_ratio_denominator": strategy_words_per_transcript,
            }
        )

    final_row = round_rows[-1]
    obs = {
        "long_k23game_certified_flag": int(
            long_k23game.get("status") == "SECTOR33_K23_VERIFICATION_GAME_TABLE_CERTIFIED"
            and long_k23game.get("all_checks_pass") is True
        ),
        "round_depth_count": len(round_rows),
        "max_round_depth": MAX_ROUND_DEPTH,
        "transcript_count": transcript_count,
        "move_family_count": move_family_count,
        "honest_move_family_count": honest_move_count,
        "tamper_move_family_count": tamper_move_count,
        "one_round_game_row_count": len(game_rows),
        "final_depth_total_strategy_words": final_row["total_strategy_words"],
        "final_depth_accepted_strategy_words": final_row["accepted_strategy_words"],
        "final_depth_rejected_strategy_words": final_row["rejected_strategy_words"],
        "all_depth_total_strategy_words": sum(row["total_strategy_words"] for row in round_rows),
        "all_depth_accepted_strategy_words": sum(row["accepted_strategy_words"] for row in round_rows),
        "all_depth_rejected_strategy_words": sum(row["rejected_strategy_words"] for row in round_rows),
        "probability_soundness_claim_flag": 0,
        "hardness_claim_flag": 0,
        "strategy_exhaustiveness_beyond_bounded_moves_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    if label_counts["honest_accept"] != transcript_count:
        raise AssertionError("one-round honest accept count mismatch")
    if label_counts["tamper_reject"] != transcript_count * tamper_move_count:
        raise AssertionError("one-round tamper reject count mismatch")
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    round_table = table_from_rows(ROUND_COLUMNS, round_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "round_table": round_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23game": long_k23game,
        "round_rows": round_rows,
        "obs_rows": obs_rows,
        "round_table": round_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "round_text_hash": hashlib.sha256(digest_text(ROUND_COLUMNS, round_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["long_k23game_certified_flag"] == 1,
        "round_profile_matches": (
            obs["round_depth_count"],
            obs["max_round_depth"],
            obs["transcript_count"],
            obs["move_family_count"],
            obs["honest_move_family_count"],
            obs["tamper_move_family_count"],
            obs["one_round_game_row_count"],
        )
        == (8, 8, 56, 6, 1, 5, 336),
        "final_depth_accounting_matches": (
            obs["final_depth_total_strategy_words"],
            obs["final_depth_accepted_strategy_words"],
            obs["final_depth_rejected_strategy_words"],
        )
        == (94_058_496, 56, 94_058_440),
        "all_depth_accounting_matches": (
            obs["all_depth_total_strategy_words"],
            obs["all_depth_accepted_strategy_words"],
            obs["all_depth_rejected_strategy_words"],
        )
        == (112_870_128, 448, 112_869_680),
        "no_broad_cryptologic_claims": (
            obs["probability_soundness_claim_flag"],
            obs["hardness_claim_flag"],
            obs["strategy_exhaustiveness_beyond_bounded_moves_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_repeated_round_accounting",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies exact repeated-round accounting for the bounded K23 verification game through depth eight.",
    }
    seam_payload = {
        "schema": "long.k23rep.seam@1",
        "status": STATUS,
        "claim": "The bounded K23 verification game has exact repeated-round strategy counts: only all-honest move words accept, while any tamper move is accounted as rejected.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23game": input_entry(
            LONG_K23GAME_REPORT,
            {
                "status": rows["long_k23game"].get("status"),
                "certificate_sha256": rows["long_k23game"].get("certificate_sha256"),
            },
        ),
        "long_k23game_rows": input_entry(LONG_K23GAME_ROWS),
        "long_k23game_payoff": input_entry(LONG_K23GAME_PAYOFF),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23rep.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23rep certifies bounded repeated-round accounting for the K23 verification game.",
        "stage_protocol": {
            "draft": "read the certified K23 verification game table and payoff labels",
            "witness": "emit repeated-round accounting rows and observables",
            "coherence": "check exact powers of the six-move bounded game alphabet through depth eight",
            "closure": "certify finite repeated-round accounting while leaving probabilistic soundness and hardness open",
            "emit": "write long_k23rep artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "round_rows_csv": relpath(OUT_DIR / "round_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23rep_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the bounded move alphabet has one honest move family and five tamper move families",
                "for depths one through eight, total strategy words per transcript are 6^depth",
                "for each transcript and each depth, exactly one all-honest strategy word accepts",
                "for each transcript and each depth, every non-all-honest strategy word is accounted as rejected",
                "depth-eight total strategy words are 94,058,496 over 56 transcripts",
            ],
            "does_not_certify": [
                "probabilistic repeated soundness",
                "uniform random challenge semantics",
                "strategies outside the six bounded prover move families",
                "cryptographic hardness",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Feed long_k23roll and long_k23rep into the focused frontier/oracle index when broad integration is permitted.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23rep.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23rep.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "round_csv": csv_text(ROUND_COLUMNS, rows["round_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "round_table": rows["round_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "round_text_sha256": rows["round_text_hash"],
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
    (OUT_DIR / "round_rows.csv").write_text(payloads["round_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        round_table=payloads["round_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23rep_matrices.npz", **payloads["matrix_payload"])
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
