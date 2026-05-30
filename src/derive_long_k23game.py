from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23chal import (
        OUT_DIR as LONG_K23CHAL_DIR,
        CHALLENGE_COLUMNS,
        CONTROL_COLUMNS,
    )
    from .derive_long_k23fam import read_csv_rows
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23chal import (
        OUT_DIR as LONG_K23CHAL_DIR,
        CHALLENGE_COLUMNS,
        CONTROL_COLUMNS,
    )
    from derive_long_k23fam import read_csv_rows
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23game"
STATUS = "SECTOR33_K23_VERIFICATION_GAME_TABLE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23game.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23game.py"
LONG_K23CHAL_REPORT = LONG_K23CHAL_DIR / "report.json"
LONG_K23CHAL_CHALLENGES = LONG_K23CHAL_DIR / "challenge_rows.csv"
LONG_K23CHAL_CONTROLS = LONG_K23CHAL_DIR / "control_rows.csv"

GAME_TEXT_HASH = "85b21a7a6849ff9b34c9c5d0eee064fb3cdfb9f7e0f577fd65eddab28e124bc5"
PAYOFF_TEXT_HASH = "91780fe39db766b02eef2f8be9bdded5fa094769b50d7904011c0d5c4994aa3d"
OBS_TEXT_HASH = "f6c167da5dbb69182a005dd1b937e3008e4942fa6af476c5cdd51118951aa0f4"
MATRIX_SHA256 = "9344d3e17b4776c84ffac0eee8267ae118748b54329c3eaec64ee209149e2062"

GAME_COLUMNS = [
    "game_row_id",
    "challenge_id",
    "transcript_id",
    "class_id",
    "opening_id",
    "word_id",
    "prover_move_code",
    "verifier_move_code",
    "expected_accept_flag",
    "actual_accept_flag",
    "prover_payoff",
    "verifier_payoff",
    "payoff_label_code",
    "accepted_truth_flag",
    "rejected_tamper_flag",
]
PAYOFF_COLUMNS = [
    "payoff_label_code",
    "payoff_label",
    "row_count",
    "prover_payoff",
    "verifier_payoff",
    "accept_flag",
    "tamper_flag",
]
PAYOFF_NUMERIC_COLUMNS = [
    "payoff_label_code",
    "row_count",
    "prover_payoff",
    "verifier_payoff",
    "accept_flag",
    "tamper_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23chal_certified_flag",
    "challenge_count",
    "control_count",
    "game_row_count",
    "honest_move_count",
    "tamper_move_count",
    "accepted_truth_count",
    "rejected_tamper_count",
    "unexpected_accept_count",
    "unexpected_reject_count",
    "verifier_payoff_total",
    "prover_payoff_total",
    "payoff_label_count",
    "transcript_count",
    "opening_count",
    "word_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

PAYOFF_LABELS = {
    0: "honest_accept",
    1: "tamper_reject",
    2: "bad_accept",
    3: "bad_reject",
}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["game_table", "payoff_numeric_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def payoff_label_code(prover_move_code: int, expected_accept: int, actual_accept: int) -> int:
    if prover_move_code == 0 and expected_accept == 1 and actual_accept == 1:
        return 0
    if prover_move_code != 0 and expected_accept == 0 and actual_accept == 0:
        return 1
    if expected_accept == 0 and actual_accept == 1:
        return 2
    return 3


def build_rows() -> dict[str, Any]:
    long_k23chal = load_json(LONG_K23CHAL_REPORT)
    challenge_rows = [{key: int(value) if value.lstrip("-").isdigit() else value for key, value in row.items()} for row in read_csv_rows(LONG_K23CHAL_CHALLENGES)]
    control_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23CHAL_CONTROLS)]
    challenge_by_id = {int(row["challenge_id"]): row for row in challenge_rows}

    game_rows = []
    for row in control_rows:
        challenge = challenge_by_id[row["challenge_id"]]
        prover_move_code = row["case_type_code"]
        expected_accept = row["expected_accept_flag"]
        actual_accept = row["actual_accept_flag"]
        label_code = payoff_label_code(prover_move_code, expected_accept, actual_accept)
        game_rows.append(
            {
                "game_row_id": row["control_id"],
                "challenge_id": row["challenge_id"],
                "transcript_id": int(challenge["transcript_id"]),
                "class_id": int(challenge["class_id"]),
                "opening_id": int(challenge["selected_opening_id"]),
                "word_id": int(challenge["selected_word_id"]),
                "prover_move_code": prover_move_code,
                "verifier_move_code": 0,
                "expected_accept_flag": expected_accept,
                "actual_accept_flag": actual_accept,
                "prover_payoff": int(prover_move_code == 0 and actual_accept == 1),
                "verifier_payoff": int(expected_accept == actual_accept),
                "payoff_label_code": label_code,
                "accepted_truth_flag": int(label_code == 0),
                "rejected_tamper_flag": int(label_code == 1),
            }
        )

    payoff_counts = Counter(row["payoff_label_code"] for row in game_rows)
    payoff_rows = [
        {
            "payoff_label_code": label_code,
            "payoff_label": PAYOFF_LABELS[label_code],
            "row_count": payoff_counts[label_code],
            "prover_payoff": 1 if label_code == 0 else 0,
            "verifier_payoff": 1 if label_code in (0, 1) else 0,
            "accept_flag": 1 if label_code in (0, 2) else 0,
            "tamper_flag": 1 if label_code in (1, 2) else 0,
        }
        for label_code in sorted(PAYOFF_LABELS)
    ]
    obs = {
        "long_k23chal_certified_flag": int(
            long_k23chal.get("status") == "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED"
            and long_k23chal.get("all_checks_pass") is True
        ),
        "challenge_count": len(challenge_rows),
        "control_count": len(control_rows),
        "game_row_count": len(game_rows),
        "honest_move_count": sum(int(row["prover_move_code"] == 0) for row in game_rows),
        "tamper_move_count": sum(int(row["prover_move_code"] != 0) for row in game_rows),
        "accepted_truth_count": sum(row["accepted_truth_flag"] for row in game_rows),
        "rejected_tamper_count": sum(row["rejected_tamper_flag"] for row in game_rows),
        "unexpected_accept_count": payoff_counts[2],
        "unexpected_reject_count": payoff_counts[3],
        "verifier_payoff_total": sum(row["verifier_payoff"] for row in game_rows),
        "prover_payoff_total": sum(row["prover_payoff"] for row in game_rows),
        "payoff_label_count": len(PAYOFF_LABELS),
        "transcript_count": len({row["transcript_id"] for row in game_rows}),
        "opening_count": len({row["opening_id"] for row in game_rows}),
        "word_count": len({row["word_id"] for row in game_rows}),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    game_table = table_from_rows(GAME_COLUMNS, game_rows)
    payoff_numeric_table = table_from_rows(PAYOFF_NUMERIC_COLUMNS, payoff_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "game_table": game_table.astype(np.int64),
        "payoff_numeric_table": payoff_numeric_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23chal": long_k23chal,
        "game_rows": game_rows,
        "payoff_rows": payoff_rows,
        "obs_rows": obs_rows,
        "game_table": game_table,
        "payoff_numeric_table": payoff_numeric_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "game_text_hash": hashlib.sha256(digest_text(GAME_COLUMNS, game_rows).encode("ascii")).hexdigest(),
        "payoff_text_hash": hashlib.sha256(digest_text(PAYOFF_COLUMNS, payoff_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["long_k23chal_certified_flag"] == 1,
        "game_profile_matches": (
            obs["challenge_count"],
            obs["control_count"],
            obs["game_row_count"],
            obs["honest_move_count"],
            obs["tamper_move_count"],
        )
        == (56, 336, 336, 56, 280),
        "payoff_profile_matches": (
            obs["accepted_truth_count"],
            obs["rejected_tamper_count"],
            obs["unexpected_accept_count"],
            obs["unexpected_reject_count"],
            obs["verifier_payoff_total"],
            obs["prover_payoff_total"],
        )
        == (56, 280, 0, 0, 336, 56),
        "surface_profile_matches": (
            obs["payoff_label_count"],
            obs["transcript_count"],
            obs["opening_count"],
            obs["word_count"],
        )
        == (4, 56, 56, 56),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_verification_game_table",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the bounded verifier game table induced by the K23 transcript challenge layer.",
    }
    seam_payload = {
        "schema": "long.k23game.seam@1",
        "status": STATUS,
        "claim": "The challenge controls form a finite verification game: honest openings accept, tamper moves reject, and verifier payoff is one on every checked row.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23chal": input_entry(
            LONG_K23CHAL_REPORT,
            {
                "status": rows["long_k23chal"].get("status"),
                "certificate_sha256": rows["long_k23chal"].get("certificate_sha256"),
            },
        ),
        "long_k23chal_challenges": input_entry(LONG_K23CHAL_CHALLENGES),
        "long_k23chal_controls": input_entry(LONG_K23CHAL_CONTROLS),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23game.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23game certifies the finite K23 verification game table.",
        "stage_protocol": {
            "draft": "read long_k23chal challenges and accept/reject controls",
            "witness": "emit game rows, payoff labels, observables, and numeric tables",
            "coherence": "check honest/tamper move counts, payoff labels, and accepted/rejected outcomes",
            "closure": "certify the bounded game table while leaving repeated-game and hardness claims open",
            "emit": "write long_k23game artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "game_rows_csv": relpath(OUT_DIR / "game_rows.csv"),
            "payoff_rows_csv": relpath(OUT_DIR / "payoff_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23game_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "336 bounded game rows induced by 56 challenge rows and 6 prover move families",
                "56 honest opening moves accept",
                "280 tamper moves reject",
                "there are zero unexpected accepts and zero unexpected rejects",
                "verifier payoff is one on all bounded rows",
                "prover payoff is one exactly on honest accepted rows",
            ],
            "does_not_certify": [
                "probabilistic or repeated-game soundness",
                "strategies outside the six bounded prover move families",
                "cryptographic hardness",
                "zero knowledge",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Fuse the semantic/game/protocol chain into a frontier rollup certificate that names the certified merge point and the remaining open cryptologic limits.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23game.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23game.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "game_csv": csv_text(GAME_COLUMNS, rows["game_rows"]),
        "payoff_csv": csv_text(PAYOFF_COLUMNS, rows["payoff_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "game_table": rows["game_table"],
        "payoff_numeric_table": rows["payoff_numeric_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "game_text_sha256": rows["game_text_hash"],
            "payoff_text_sha256": rows["payoff_text_hash"],
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
    (OUT_DIR / "game_rows.csv").write_text(payloads["game_csv"], encoding="utf-8")
    (OUT_DIR / "payoff_rows.csv").write_text(payloads["payoff_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        game_table=payloads["game_table"],
        payoff_numeric_table=payloads["payoff_numeric_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23game_matrices.npz", **payloads["matrix_payload"])
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
