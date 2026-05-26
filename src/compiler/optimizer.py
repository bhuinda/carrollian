from __future__ import annotations

from typing import Any


def compact_support_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    out = dict(ledger)
    support = {}
    for claim_id, entry in ledger.get("claim_support", {}).items():
        files = sorted(dict.fromkeys(entry.get("files", [])))
        support[claim_id] = {**entry, "files": files}
    out["claim_support"] = support
    return out


def mark_obligations_closed(obligations: dict[str, Any]) -> dict[str, Any]:
    out = dict(obligations)
    out["obligations"] = [{**item, "status": "closed"} for item in obligations.get("obligations", [])]
    return out
