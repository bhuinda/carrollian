from __future__ import annotations

import re
from typing import Any


def normalize_text(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text.replace("\r\n", "\n")).strip()


def normalize_obligations(payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    seen: set[str] = set()
    obligations = []
    for item in payload.get("obligations", []):
        text = normalize_text(str(item.get("text", "")))
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        updated = dict(item)
        updated["text"] = text
        obligations.append(updated)
    out["obligations"] = obligations
    return out


def normalize_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for claim in claims:
        text = normalize_text(str(claim.get("text", "")))
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        updated = dict(claim)
        updated["claim_id"] = f"c{len(out) + 1:03d}"
        updated["text"] = text
        out.append(updated)
    return out
