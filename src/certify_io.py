from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable


ROOT = Path(__file__).resolve().parents[1]
CORE_LAYER_CERTIFICATE = 'layers/00_core/certificate.json'


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


def cached_core_block(name: str) -> Dict[str, Any] | None:
    p = ROOT / CORE_LAYER_CERTIFICATE
    if not p.exists():
        return None
    cert = load_json(CORE_LAYER_CERTIFICATE)
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
