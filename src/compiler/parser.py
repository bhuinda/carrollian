from __future__ import annotations

from typing import Any

from .common import utc_timestamp


REQUEST_SCHEMA = "holotopy.request"


def parse_request(
    *,
    turn_id: str,
    user_text: str,
    attachments: list[dict[str, Any]] | None = None,
    conversation_refs: list[str] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": REQUEST_SCHEMA,
        "turn_id": turn_id,
        "user_text": user_text,
        "attachments": attachments or [],
        "conversation_refs": conversation_refs or [],
        "timestamp": timestamp or utc_timestamp(),
    }
