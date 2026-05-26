from __future__ import annotations

import re
from typing import Any


OBLIGATION_SCHEMA = "holotopy.obligations"
OBLIGATION_WORDS = re.compile(
    r"\b(need|needs|must|always|required|require|goal|invariant|verify|check|distinguish|preserve|compile)\b",
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" -:\t")


def candidate_lines(user_text: str) -> list[str]:
    lines: list[str] = []
    for raw in user_text.splitlines():
        line = _clean(raw)
        if not line or line.startswith("```"):
            continue
        if OBLIGATION_WORDS.search(line):
            lines.append(line)
    return lines


def extract_obligations(user_text: str, *, max_obligations: int = 12) -> dict[str, Any]:
    selected = candidate_lines(user_text)
    if not selected:
        selected = [_clean(user_text)[:240] or "Handle the visible user request."]

    obligations = []
    for idx, text in enumerate(selected[:max_obligations], start=1):
        obligations.append(
            {
                "id": f"obl_{idx:03d}",
                "kind": "answer" if idx == 1 else "constraint",
                "text": text,
                "source": "00_request.raw.json",
                "status": "open",
            }
        )

    if not any("verify" in item["text"].lower() or "check" in item["text"].lower() for item in obligations):
        obligations.append(
            {
                "id": f"obl_{len(obligations) + 1:03d}",
                "kind": "validation",
                "text": "Run the available compiler checks before closure.",
                "source": "AGENTS.md instructions supplied in visible context",
                "status": "open",
            }
        )

    return {"schema": OBLIGATION_SCHEMA, "obligations": obligations}
