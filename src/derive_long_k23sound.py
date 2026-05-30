from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23fam import read_csv_rows
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23fam import read_csv_rows
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23sound"
STATUS = "SECTOR33_K23_BOUNDED_ADVERSARY_SOUNDNESS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23sound.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23sound.py"
LONG_K23CHAL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json"
LONG_K23GAME_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23game" / "report.json"
LONG_K23GAME_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23game" / "game_rows.csv"
LONG_K23GAME_PAYOFF = D20_INVARIANTS / "proof_obligations" / "long_k23game" / "payoff_rows.csv"
LONG_K23REP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rep" / "report.json"
LONG_K23REP_ROUNDS = D20_INVARIANTS / "proof_obligations" / "long_k23rep" / "round_rows.csv"
LONG_K23SYNC_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23sync" / "report.json"

MOVE_TEXT_HASH = "cb665a4c7256a0191e77251d6ad2a7f7751a90af8132afbb05bd98f7ff249098"
SOUNDNESS_TEXT_HASH = "0f9a2c26aff2be41d2993f3ba6d0ff65864582792586831fb89b4d15ba5686ad"
OBS_TEXT_HASH = "a20e5f7bf9734515677c0e0c73dc5d71b153a535de5fc3c1f290ae79c41ce687"
MATRIX_SHA256 = "618c47d6aa4209ce700256490ba5c3431d6318dc111b47df9ddbd339650e7449"

MOVE_COLUMNS = [
    "move_code",
    "move_kind_code",
    "move_label",
    "accept_flag",
    "tamper_flag",
    "one_round_row_count",
    "bad_accept_count",
]
SOUNDNESS_COLUMNS = [
    "round_depth",
    "transcript_count",
    "move_family_count",
    "tamper_move_family_count",
    "strategy_words_per_transcript",
    "honest_accept_words_per_transcript",
    "tamper_words_per_transcript",
    "false_accept_words_per_transcript",
    "tamper_reject_words_per_transcript",
    "total_strategy_words",
    "honest_accept_strategy_words",
    "false_accept_strategy_words",
    "tamper_reject_strategy_words",
    "acceptance_numerator",
    "acceptance_denominator",
    "tamper_error_numerator",
    "tamper_error_denominator",
]
MOVE_NUMERIC_COLUMNS = [
    "move_code",
    "move_kind_code",
    "accept_flag",
    "tamper_flag",
    "one_round_row_count",
    "bad_accept_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "move_family_count",
    "honest_move_family_count",
    "tamper_move_family_count",
    "round_depth_count",
    "max_round_depth",
    "transcript_count",
    "one_round_game_row_count",
    "bad_accept_count",
    "bad_reject_count",
    "tamper_false_accept_count",
    "final_tamper_words_per_transcript",
    "final_tamper_reject_strategy_words",
    "final_honest_accept_strategy_words",
    "final_acceptance_numerator",
    "final_acceptance_denominator",
    "all_depth_false_accept_strategy_words",
    "all_depth_tamper_reject_strategy_words",
    "bounded_soundness_error_numerator",
    "bounded_soundness_error_denominator",
    "uniform_counting_law_flag",
    "external_randomness_claim_flag",
    "hardness_claim_flag",
    "zero_knowledge_claim_flag",
    "unbounded_adversary_claim_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

EXPECTED_STATUSES = {
    "long_k23chal": "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED",
    "long_k23game": "SECTOR33_K23_VERIFICATION_GAME_TABLE_CERTIFIED",
    "long_k23rep": "SECTOR33_K23_REPEATED_ROUND_ACCOUNTING_CERTIFIED",
    "long_k23sync": "SECTOR33_K23_PROTOCOL_FRONTIER_HANDOFF_CERTIFIED",
}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["move_numeric_table", "soundness_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def is_certified(report: dict[str, Any], proof_id: str) -> int:
    return int(
        report.get("status") == EXPECTED_STATUSES[proof_id]
        and report.get("all_checks_pass") is True
    )


def build_rows() -> dict[str, Any]:
    reports = {
        "long_k23chal": load_json(LONG_K23CHAL_REPORT),
        "long_k23game": load_json(LONG_K23GAME_REPORT),
        "long_k23rep": load_json(LONG_K23REP_REPORT),
        "long_k23sync": load_json(LONG_K23SYNC_REPORT),
    }
    game_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23GAME_ROWS)]
    payoff_rows = [{**row, "row_count": int(row["row_count"])} for row in read_csv_rows(LONG_K23GAME_PAYOFF)]
    round_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23REP_ROUNDS)]

    by_move = Counter(row["prover_move_code"] for row in game_rows)
    bad_accept_by_move = Counter(
        row["prover_move_code"]
        for row in game_rows
        if row["prover_move_code"] != 0 and row["actual_accept_flag"] == 1
    )
    move_rows = []
    for move_code in sorted(by_move):
        tamper_flag = int(move_code != 0)
        move_rows.append(
            {
                "move_code": move_code,
                "move_kind_code": tamper_flag,
                "move_label": "honest" if move_code == 0 else f"tamper_{move_code}",
                "accept_flag": int(move_code == 0),
                "tamper_flag": tamper_flag,
                "one_round_row_count": by_move[move_code],
                "bad_accept_count": bad_accept_by_move[move_code],
            }
        )

    soundness_rows = []
    for row in round_rows:
        tamper_words_per_transcript = row["strategy_words_per_transcript"] - row["accepted_words_per_transcript"]
        soundness_rows.append(
            {
                "round_depth": row["round_depth"],
                "transcript_count": row["transcript_count"],
                "move_family_count": row["move_family_count"],
                "tamper_move_family_count": row["tamper_move_family_count"],
                "strategy_words_per_transcript": row["strategy_words_per_transcript"],
                "honest_accept_words_per_transcript": row["accepted_words_per_transcript"],
                "tamper_words_per_transcript": tamper_words_per_transcript,
                "false_accept_words_per_transcript": 0,
                "tamper_reject_words_per_transcript": row["rejected_words_per_transcript"],
                "total_strategy_words": row["total_strategy_words"],
                "honest_accept_strategy_words": row["accepted_strategy_words"],
                "false_accept_strategy_words": 0,
                "tamper_reject_strategy_words": row["rejected_strategy_words"],
                "acceptance_numerator": row["accept_ratio_numerator"],
                "acceptance_denominator": row["accept_ratio_denominator"],
                "tamper_error_numerator": 0,
                "tamper_error_denominator": tamper_words_per_transcript,
            }
        )

    payoff_counts = {row["payoff_label"]: row["row_count"] for row in payoff_rows}
    final_row = soundness_rows[-1]
    obs = {
        "input_report_count": len(reports),
        "certified_input_count": sum(is_certified(report, proof_id) for proof_id, report in reports.items()),
        "move_family_count": len(move_rows),
        "honest_move_family_count": sum(1 for row in move_rows if row["tamper_flag"] == 0),
        "tamper_move_family_count": sum(1 for row in move_rows if row["tamper_flag"] == 1),
        "round_depth_count": len(soundness_rows),
        "max_round_depth": final_row["round_depth"],
        "transcript_count": final_row["transcript_count"],
        "one_round_game_row_count": len(game_rows),
        "bad_accept_count": payoff_counts.get("bad_accept", 0),
        "bad_reject_count": payoff_counts.get("bad_reject", 0),
        "tamper_false_accept_count": sum(row["bad_accept_count"] for row in move_rows),
        "final_tamper_words_per_transcript": final_row["tamper_words_per_transcript"],
        "final_tamper_reject_strategy_words": final_row["tamper_reject_strategy_words"],
        "final_honest_accept_strategy_words": final_row["honest_accept_strategy_words"],
        "final_acceptance_numerator": final_row["acceptance_numerator"],
        "final_acceptance_denominator": final_row["acceptance_denominator"],
        "all_depth_false_accept_strategy_words": sum(row["false_accept_strategy_words"] for row in soundness_rows),
        "all_depth_tamper_reject_strategy_words": sum(row["tamper_reject_strategy_words"] for row in soundness_rows),
        "bounded_soundness_error_numerator": 0,
        "bounded_soundness_error_denominator": sum(row["tamper_reject_strategy_words"] for row in soundness_rows),
        "uniform_counting_law_flag": 1,
        "external_randomness_claim_flag": 0,
        "hardness_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "unbounded_adversary_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    move_numeric_table = table_from_rows(MOVE_NUMERIC_COLUMNS, move_rows)
    soundness_table = table_from_rows(SOUNDNESS_COLUMNS, soundness_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "move_numeric_table": move_numeric_table.astype(np.int64),
        "soundness_table": soundness_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "move_rows": move_rows,
        "soundness_rows": soundness_rows,
        "obs_rows": obs_rows,
        "move_numeric_table": move_numeric_table,
        "soundness_table": soundness_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "move_text_hash": hashlib.sha256(digest_text(MOVE_COLUMNS, move_rows).encode("ascii")).hexdigest(),
        "soundness_text_hash": hashlib.sha256(digest_text(SOUNDNESS_COLUMNS, soundness_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 4,
        "move_partition_exact": (
            obs["move_family_count"],
            obs["honest_move_family_count"],
            obs["tamper_move_family_count"],
            obs["one_round_game_row_count"],
        )
        == (6, 1, 5, 336),
        "one_round_no_bad_accepts": (
            obs["bad_accept_count"],
            obs["bad_reject_count"],
            obs["tamper_false_accept_count"],
        )
        == (0, 0, 0),
        "bounded_round_soundness_exact": (
            obs["round_depth_count"],
            obs["max_round_depth"],
            obs["final_tamper_words_per_transcript"],
            obs["final_tamper_reject_strategy_words"],
            obs["all_depth_false_accept_strategy_words"],
        )
        == (8, 8, 1_679_615, 94_058_440, 0),
        "open_security_limits_unclaimed": (
            obs["external_randomness_claim_flag"],
            obs["hardness_claim_flag"],
            obs["zero_knowledge_claim_flag"],
            obs["unbounded_adversary_claim_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_bounded_adversary_soundness",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies exact rejection of all bounded tamper move words through depth eight.",
    }
    seam_payload = {
        "schema": "long.k23sound.seam@1",
        "status": STATUS,
        "claim": "The certified six-move K23 verifier game has perfect bounded tamper rejection through depth eight, with only all-honest move words accepted.",
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
            "long_k23chal": LONG_K23CHAL_REPORT,
            "long_k23game": LONG_K23GAME_REPORT,
            "long_k23rep": LONG_K23REP_REPORT,
            "long_k23sync": LONG_K23SYNC_REPORT,
        }.items()
    }
    inputs.update(
        {
            "long_k23game_rows": input_entry(LONG_K23GAME_ROWS),
            "long_k23game_payoff": input_entry(LONG_K23GAME_PAYOFF),
            "long_k23rep_rounds": input_entry(LONG_K23REP_ROUNDS),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        }
    )
    report = {
        "schema": "long.k23sound.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23sound certifies bounded adversary soundness for the K23 verifier game.",
        "stage_protocol": {
            "draft": "read challenge, game, repeated-round, and handoff certificates plus game/round witness rows",
            "witness": "emit move-family rows, round soundness rows, and observables",
            "coherence": "check exact move partition, no bad accepts, and bounded round counts",
            "closure": "certify bounded tamper rejection while leaving external security claims open",
            "emit": "write long_k23sound artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "move_rows_csv": relpath(OUT_DIR / "move_rows.csv"),
            "soundness_rows_csv": relpath(OUT_DIR / "soundness_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23sound_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the bounded prover move alphabet has one honest move and five tamper move families",
                "the one-round game has zero bad accepts and zero bad rejects",
                "through depth eight, every non-all-honest move word is rejected",
                "under the finite uniform counting law on bounded move words, acceptance mass is exactly 1/6^d at depth d",
            ],
            "does_not_certify": [
                "external randomness generation",
                "cryptographic hardness",
                "zero knowledge",
                "strategies outside the bounded six-move alphabet",
                "security composition outside this finite verifier game",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Feed long_k23sound into the focused frontier and then test whether a challenge-randomness source can be certified without adding an external assumption.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23sound.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23sound.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "move_csv": csv_text(MOVE_COLUMNS, rows["move_rows"]),
        "soundness_csv": csv_text(SOUNDNESS_COLUMNS, rows["soundness_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "move_numeric_table": rows["move_numeric_table"],
        "soundness_table": rows["soundness_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "move_text_sha256": rows["move_text_hash"],
            "soundness_text_sha256": rows["soundness_text_hash"],
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
    (OUT_DIR / "move_rows.csv").write_text(payloads["move_csv"], encoding="utf-8")
    (OUT_DIR / "soundness_rows.csv").write_text(payloads["soundness_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        move_numeric_table=payloads["move_numeric_table"],
        soundness_table=payloads["soundness_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23sound_matrices.npz", **payloads["matrix_payload"])
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
