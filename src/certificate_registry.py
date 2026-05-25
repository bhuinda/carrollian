from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE_INDEX = ROOT / "data" / "certificates.json"


@lru_cache(maxsize=1)
def load_certificate_registry() -> dict[str, Any]:
    with CERTIFICATE_INDEX.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("certificate registry is not a JSON object")
    return data


def certificate_entries(registry: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = load_certificate_registry() if registry is None else registry
    entries = data.get("certificates", [])
    if not isinstance(entries, list):
        raise ValueError("certificate registry missing certificates list")
    return [entry for entry in entries if isinstance(entry, dict)]


def certificate_entry(certificate_id: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    for entry in certificate_entries(registry):
        if entry.get("id") == certificate_id:
            return entry
    raise KeyError(f"unknown certificate id: {certificate_id}")


def certificate_relpath(certificate_id: str, registry: dict[str, Any] | None = None) -> str:
    rel = certificate_entry(certificate_id, registry).get("path")
    if not isinstance(rel, str):
        raise ValueError(f"certificate {certificate_id} has no path")
    return rel


def certificate_path(certificate_id: str, registry: dict[str, Any] | None = None, *, root: Path | None = None) -> Path:
    return (ROOT if root is None else root) / certificate_relpath(certificate_id, registry)
