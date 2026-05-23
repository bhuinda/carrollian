from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAYER_INDEX = ROOT / "layers" / "index.json"


@lru_cache(maxsize=1)
def load_layer_registry() -> dict[str, Any]:
    with LAYER_INDEX.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("layer registry is not a JSON object")
    return data


def layer_entries(registry: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = load_layer_registry() if registry is None else registry
    entries = data.get("layers", [])
    if not isinstance(entries, list):
        raise ValueError("layer registry missing layers list")
    return [entry for entry in entries if isinstance(entry, dict)]


def layer_entry(layer_id: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    for entry in layer_entries(registry):
        if entry.get("id") == layer_id:
            return entry
    raise KeyError(f"unknown layer id: {layer_id}")


def layer_relpath(layer_id: str, registry: dict[str, Any] | None = None) -> str:
    rel = layer_entry(layer_id, registry).get("path")
    if not isinstance(rel, str):
        raise ValueError(f"layer {layer_id} has no path")
    return rel


def layer_path(layer_id: str, registry: dict[str, Any] | None = None, *, root: Path | None = None) -> Path:
    return (ROOT if root is None else root) / layer_relpath(layer_id, registry)
