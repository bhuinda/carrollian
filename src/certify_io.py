from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable

try:
    from .certificate_registry import certificate_relpath
except ImportError:  # Supports `python src/certify_core.py`.
    from certificate_registry import certificate_relpath


ROOT = Path(__file__).resolve().parents[1]
CORE_CERTIFICATE = certificate_relpath('core.a985')
RAW_DATA_INDEX = 'data/raw/index.json'
RAW_TENSOR_FALLBACKS = (
    'data/raw/Halloween.npz',
    'data/raw/T_985.npz',
    'data/raw/tensor_sparse.npz',
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def h_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def h_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(rel: str) -> Any:
    with (ROOT / rel).open('r', encoding='utf-8') as f:
        return json.load(f)


def existing_relpath(*candidates: str) -> str:
    for rel in candidates:
        if (ROOT / rel).exists():
            return rel
    raise FileNotFoundError(candidates[0] if candidates else '')


def raw_data_index() -> Dict[str, Any]:
    path = ROOT / RAW_DATA_INDEX
    if not path.exists():
        return {"roles": {}}
    return load_json(RAW_DATA_INDEX)


def raw_data_relpath(role: str) -> str:
    roles = raw_data_index().get("roles", {})
    entry = roles.get(role, {}) if isinstance(roles, dict) else {}
    candidates: list[str] = []
    if isinstance(entry, dict):
        path = entry.get("path")
        aliases = entry.get("aliases", [])
        if isinstance(path, str):
            candidates.append(path)
        if isinstance(aliases, list):
            candidates.extend(x for x in aliases if isinstance(x, str))
    if role == "raw_tensor":
        candidates.extend(RAW_TENSOR_FALLBACKS)
    return existing_relpath(*candidates)


def raw_tensor_relpath() -> str:
    return raw_data_relpath("raw_tensor")


def cached_core_block(name: str) -> Dict[str, Any] | None:
    p = ROOT / CORE_CERTIFICATE
    if not p.exists():
        return None
    cert = load_json(CORE_CERTIFICATE)
    block = cert.get('blocks', {}).get(name)
    return block if isinstance(block, dict) else None


def file_manifest(core_files: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    out = {}
    for rel in core_files:
        p = ROOT / rel
        if not p.exists():
            raise FileNotFoundError(rel)
        out[rel] = {'bytes': p.stat().st_size, 'sha256': h_file(p)}
    return out
