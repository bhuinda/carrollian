from __future__ import annotations

import re
from typing import Any


CLAIM_SCHEMA = "holotopy.claims"
SPECULATIVE_WORDS = re.compile(r"\b(might|may|could|proposal|provisional|symbolic|scaffold|unproven)\b", re.IGNORECASE)
RESIDUE_COORDINATE_DOMAIN_WORDS = re.compile(
    r"\b(A985|A42|A12|D20|quotient[- ]tower|tensor[- ]backed|boundary zero)\b",
    re.IGNORECASE,
)
RESIDUE_COORDINATE_ASSERTION_WORDS = re.compile(
    r"\b(verif(?:y|ies|ied)|checks?|zero|witness|computed|discharg(?:e|es|ed))\b",
    re.IGNORECASE,
)
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _strip_code_blocks(text: str) -> str:
    return re.sub(r"```.*?```", " ", text, flags=re.DOTALL)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" -\t")


def _requires_residue_coordinate(text: str) -> bool:
    return bool(RESIDUE_COORDINATE_DOMAIN_WORDS.search(text) and RESIDUE_COORDINATE_ASSERTION_WORDS.search(text))


def _claim_candidates(answer_text: str) -> list[str]:
    text = _strip_code_blocks(answer_text)
    candidates: list[str] = []
    for line in text.splitlines():
        line = _clean(line)
        if not line or line.startswith(("#", "|")):
            continue
        if line.startswith(("-", "*")):
            candidates.append(_clean(line[1:]))
            continue
        candidates.extend(_clean(part) for part in SENTENCE_END.split(line) if _clean(part))
    return [item for item in candidates if len(item) >= 16]


def extract_claims(answer_text: str, *, max_claims: int = 64) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in _claim_candidates(answer_text):
        key = candidate.casefold()
        if key in seen:
            continue
        seen.add(key)
        idx = len(claims) + 1
        claims.append(
            {
                "schema": CLAIM_SCHEMA,
                "claim_id": f"c{idx:03d}",
                "text": candidate,
                "support": [],
                "risk": "medium" if SPECULATIVE_WORDS.search(candidate) else "low",
                "requires_residue_coordinate": _requires_residue_coordinate(candidate),
            }
        )
        if len(claims) >= max_claims:
            break
    if not claims and answer_text.strip():
        claims.append(
            {
                "schema": CLAIM_SCHEMA,
                "claim_id": "c001",
                "text": _clean(answer_text)[:500],
                "support": [],
                "risk": "medium",
                "requires_residue_coordinate": _requires_residue_coordinate(answer_text),
            }
        )
    return claims


def claims_to_jsonl(claims: list[dict[str, Any]]) -> str:
    import json

    return "\n".join(json.dumps(claim, sort_keys=True, ensure_ascii=False) for claim in claims) + ("\n" if claims else "")


def claims_from_jsonl(text: str) -> list[dict[str, Any]]:
    import json

    return [json.loads(line) for line in text.splitlines() if line.strip()]
