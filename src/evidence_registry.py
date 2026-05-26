from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .paths import ROOT, relpath
except ImportError:  # Supports direct script execution from src/*.py.
    ROOT = Path(__file__).resolve().parents[1]

    def relpath(path: Path) -> str:
        return path.relative_to(ROOT).as_posix()


EVIDENCE_INDEX_PATH = ROOT / "data" / "evidence" / "index.json"
DEFAULT_EVIDENCE_INDEX = {
    "schema": "d20.evidence.index",
    "status": "EVIDENCE_INDEX_REGISTERED",
    "verifier": "python src/verify.py evidence-index --pretty",
    "evidence_roots": [],
}


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def file_ref(path: Path) -> dict[str, Any]:
    path = repo_path(path)
    return {
        "path": relpath(path),
        "sha256": sha_file(path),
        "size": path.stat().st_size,
    }


def evidence_index_entry(
    *,
    evidence_id: str,
    root: str | Path,
    entrypoint: str | Path,
    status: str,
) -> dict[str, Any]:
    root_ref = relpath(repo_path(root)) if isinstance(root, Path) else root
    entrypoint_path = repo_path(entrypoint)
    return {
        "entrypoint": file_ref(entrypoint_path),
        "id": evidence_id,
        "root": root_ref,
        "status": status,
    }


def load_evidence_index(index_path: Path = EVIDENCE_INDEX_PATH) -> dict[str, Any]:
    if not index_path.exists():
        return json.loads(json.dumps(DEFAULT_EVIDENCE_INDEX))
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evidence index is not a JSON object")
    return payload


def upsert_evidence_index_entry(
    entry: dict[str, Any],
    *,
    index_path: Path = EVIDENCE_INDEX_PATH,
    insert: str = "append",
) -> dict[str, Any]:
    if insert not in {"append", "prepend"}:
        raise ValueError("insert must be 'append' or 'prepend'")
    entry_id = entry.get("id")
    if not isinstance(entry_id, str) or not entry_id:
        raise ValueError("evidence index entry must have a non-empty string id")

    payload = load_evidence_index(index_path)
    payload.setdefault("schema", DEFAULT_EVIDENCE_INDEX["schema"])
    payload.setdefault("status", DEFAULT_EVIDENCE_INDEX["status"])
    payload.setdefault("verifier", DEFAULT_EVIDENCE_INDEX["verifier"])
    entries = payload.setdefault("evidence_roots", [])
    if not isinstance(entries, list):
        raise ValueError("evidence index evidence_roots is not a list")

    next_entries: list[dict[str, Any]] = []
    replaced = False
    for current in entries:
        if isinstance(current, dict) and current.get("id") == entry_id:
            if not replaced:
                next_entries.append(entry)
                replaced = True
            continue
        if isinstance(current, dict):
            next_entries.append(current)
    if not replaced:
        if insert == "prepend":
            next_entries.insert(0, entry)
        else:
            next_entries.append(entry)
    payload["evidence_roots"] = next_entries

    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return payload


def sync_evidence_index_entry(
    *,
    evidence_id: str,
    root: str | Path,
    entrypoint: str | Path,
    status: str,
    insert: str = "append",
    index_path: Path = EVIDENCE_INDEX_PATH,
) -> dict[str, Any]:
    entry = evidence_index_entry(
        evidence_id=evidence_id,
        root=root,
        entrypoint=entrypoint,
        status=status,
    )
    upsert_evidence_index_entry(entry, index_path=index_path, insert=insert)
    entrypoint_ref = entry["entrypoint"]
    return {
        "evidence_index": relpath(index_path),
        "evidence_index_entry_updated": True,
        "evidence_index_entrypoint_sha256": entrypoint_ref["sha256"],
        "evidence_index_entrypoint_size": entrypoint_ref["size"],
    }
