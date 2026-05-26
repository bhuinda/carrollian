from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import sha256_file, sha256_json


CERTIFICATE_SCHEMA = "holotopy.turn_certificate"
REPLAY_SCHEMA = "holotopy.replay"
TURN_LOCK_SCHEMA = "holotopy.turn_lock"


def build_replay(turn_id: str) -> dict[str, Any]:
    return {
        "schema": REPLAY_SCHEMA,
        "turn_id": turn_id,
        "replay_steps": [
            "load CORE.lock.json or record missing-core residue",
            "load 00_request.raw.json",
            "load 05_scene.ir.json",
            "validate 03_claims.jsonl",
            "validate 04_support_ledger.json",
            "validate 08_residue_ledger.json",
            "recompute 12_turn_certificate.json",
            "recompute TURN.lock.json",
        ],
    }


def build_certificate(
    *,
    turn_id: str,
    request: dict[str, Any],
    scene_ir: dict[str, Any],
    answer_text: str,
    residue_ledger: dict[str, Any],
    verification_status: str,
    core_lock_hash: str | None,
) -> dict[str, Any]:
    cert = {
        "schema": CERTIFICATE_SCHEMA,
        "turn_id": turn_id,
        "input_hash": sha256_json(request),
        "scene_ir_hash": sha256_json(scene_ir),
        "answer_hash": sha256_json({"answer": answer_text}),
        "residue_hash": sha256_json(residue_ledger),
        "verification_status": verification_status,
        "core_lock_hash": core_lock_hash,
    }
    cert["proof_hash"] = sha256_json(cert)
    return cert


def build_turn_lock(run_dir: Path, file_names: list[str]) -> dict[str, Any]:
    files = {}
    for name in file_names:
        path = run_dir / name
        if path.exists() and path.is_file():
            files[name] = sha256_file(path)
    lock = {"schema": TURN_LOCK_SCHEMA, "turn_id": run_dir.name, "files": files}
    lock["turn_hash"] = sha256_json(lock)
    return lock
