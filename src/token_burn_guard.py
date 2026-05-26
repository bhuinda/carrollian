from __future__ import annotations

import json
import os
import sys
import io
from collections.abc import Mapping, Sequence
from typing import Any, TextIO


DISABLE_ENV = "CARROLLIAN_TOKEN_BURN_GUARD"
MAX_STDOUT_ENV = "CARROLLIAN_TOKEN_BURN_MAX_STDOUT"
MAX_STDERR_ENV = "CARROLLIAN_TOKEN_BURN_MAX_STDERR"
MAX_LINE_ENV = "CARROLLIAN_TOKEN_BURN_MAX_LINE"
FULL_STDOUT_ENV = "CARROLLIAN_TOKEN_BURN_ALLOW_FULL_STDOUT"

DEFAULT_MAX_STDOUT_BYTES = 8192
DEFAULT_MAX_STDERR_BYTES = 8192
DEFAULT_MAX_LINE_BYTES = 2048
DEFAULT_JSON_BYTES = 8192
TRUNCATION_NOTICE = "\n[carrollian-token-burn-guard: output truncated; full data belongs in files]\n"


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(1024, value)


def guard_enabled() -> bool:
    return os.environ.get(DISABLE_ENV, "1").lower() not in {"0", "false", "no", "off"}


class BoundedTextIO:
    def __init__(self, wrapped: TextIO, *, limit_bytes: int, line_limit_bytes: int) -> None:
        self._wrapped = wrapped
        self._limit_bytes = limit_bytes
        self._line_limit_bytes = line_limit_bytes
        self._written_bytes = 0
        self._truncated = False

    def write(self, text: str) -> int:
        if not isinstance(text, str):
            text = str(text)
        original_len = len(text)
        if self._truncated:
            return original_len

        text = self._cap_long_line(text)
        encoded = text.encode(getattr(self._wrapped, "encoding", None) or "utf-8", errors="replace")
        remaining = self._limit_bytes - self._written_bytes
        if len(encoded) <= remaining:
            self._wrapped.write(text)
            self._written_bytes += len(encoded)
            return original_len

        if remaining > 0:
            safe = encoded[:remaining].decode(
                getattr(self._wrapped, "encoding", None) or "utf-8",
                errors="ignore",
            )
            self._wrapped.write(safe)
            self._written_bytes += len(safe.encode(getattr(self._wrapped, "encoding", None) or "utf-8", errors="replace"))
        self._wrapped.write(TRUNCATION_NOTICE)
        self._truncated = True
        return original_len

    def _cap_long_line(self, text: str) -> str:
        out: list[str] = []
        for line in text.splitlines(keepends=True):
            newline = ""
            body = line
            if line.endswith("\r\n"):
                body = line[:-2]
                newline = "\r\n"
            elif line.endswith("\n") or line.endswith("\r"):
                body = line[:-1]
                newline = line[-1]
            encoded = body.encode(getattr(self._wrapped, "encoding", None) or "utf-8", errors="replace")
            if len(encoded) > self._line_limit_bytes:
                body = encoded[: self._line_limit_bytes].decode(
                    getattr(self._wrapped, "encoding", None) or "utf-8",
                    errors="ignore",
                )
                body += " [line truncated by carrollian-token-burn-guard]"
            out.append(body + newline)
        return "".join(out)

    def flush(self) -> None:
        self._wrapped.flush()

    def isatty(self) -> bool:
        return self._wrapped.isatty()

    @property
    def encoding(self) -> str | None:
        return self._wrapped.encoding

    @property
    def errors(self) -> str | None:
        return getattr(self._wrapped, "errors", None)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._wrapped, name)


def install() -> None:
    if not guard_enabled() or os.environ.get(FULL_STDOUT_ENV) == "1":
        return
    if not isinstance(sys.stdout, BoundedTextIO):
        sys.stdout = BoundedTextIO(
            sys.stdout,
            limit_bytes=_env_int(MAX_STDOUT_ENV, DEFAULT_MAX_STDOUT_BYTES),
            line_limit_bytes=_env_int(MAX_LINE_ENV, DEFAULT_MAX_LINE_BYTES),
        )
    if not isinstance(sys.stderr, BoundedTextIO):
        sys.stderr = BoundedTextIO(
            sys.stderr,
            limit_bytes=_env_int(MAX_STDERR_ENV, DEFAULT_MAX_STDERR_BYTES),
            line_limit_bytes=_env_int(MAX_LINE_ENV, DEFAULT_MAX_LINE_BYTES),
        )


def _shorten_scalar(value: Any) -> Any:
    if isinstance(value, str):
        if len(value) <= 240:
            return value
        return value[:240] + f"...[string omitted {len(value) - 240} chars]"
    return value


def summarize_for_stdout(value: Any, *, depth: int = 0) -> Any:
    if depth >= 4:
        if isinstance(value, Mapping):
            return {"_omitted_mapping_keys": len(value)}
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return {"_omitted_sequence_items": len(value)}
        return _shorten_scalar(value)

    if isinstance(value, Mapping):
        preferred = [
            "status",
            "mode",
            "headline",
            "claim",
            "report",
            "report_sha256",
            "certificate_sha256",
            "all_checks_pass",
            "errors",
            "checks",
            "summary",
            "next_highest_yield_item",
        ]
        keys = [key for key in preferred if key in value]
        keys.extend(key for key in value.keys() if key not in keys)
        limited = keys[:24]
        out = {str(key): summarize_for_stdout(value[key], depth=depth + 1) for key in limited}
        omitted = len(value) - len(limited)
        if omitted > 0:
            out["_omitted_mapping_keys"] = omitted
        return out

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        limited_items = list(value[:8])
        out = [summarize_for_stdout(item, depth=depth + 1) for item in limited_items]
        omitted = len(value) - len(limited_items)
        if omitted > 0:
            out.append({"_omitted_sequence_items": omitted})
        return out

    return _shorten_scalar(value)


def bounded_json_text(obj: Any, *, pretty: bool = False, max_bytes: int = DEFAULT_JSON_BYTES) -> str:
    text = json.dumps(obj, indent=2 if pretty else None, sort_keys=True, allow_nan=False)
    if len(text.encode("utf-8")) <= max_bytes:
        return text

    output_guard = {
        "full_output_bytes": len(text.encode("utf-8")),
        "max_stdout_json_bytes": max_bytes,
        "summary_emitted": True,
        "note": "stdout is bounded to avoid token burn; inspect written report artifacts for full data",
    }
    summary = {
        "status": obj.get("status") if isinstance(obj, Mapping) else None,
        "output_guard": output_guard,
        "summary": summarize_for_stdout(obj),
    }
    summary_text = json.dumps(summary, indent=2 if pretty else None, sort_keys=True, allow_nan=False)
    if len(summary_text.encode("utf-8")) <= max_bytes:
        return summary_text

    output_guard["summary_truncated"] = True
    emergency_summary: dict[str, Any] = {
        "status": obj.get("status") if isinstance(obj, Mapping) else None,
        "output_guard": output_guard,
    }
    if isinstance(obj, Mapping):
        checks = obj.get("checks")
        if isinstance(checks, Mapping):
            emergency_summary["checks"] = checks
        for key in (
            "direct_script_coverage",
            "stdout_risk_inventory",
            "subprocess_output_risk_inventory",
            "non_python_script_surface",
        ):
            value = obj.get(key)
            if isinstance(value, Mapping):
                emergency_summary[key] = {
                    subkey: subvalue
                    for subkey, subvalue in value.items()
                    if subkey.endswith("_count") or subkey in {"active_count", "archival_count", "status"}
                }
        emergency_summary["top_level_keys"] = [str(key) for key in list(obj.keys())[:24]]
    emergency_text = json.dumps(
        emergency_summary,
        indent=2 if pretty else None,
        sort_keys=True,
        allow_nan=False,
    )
    if len(emergency_text.encode("utf-8")) <= max_bytes:
        return emergency_text
    return json.dumps(
        {
            "status": obj.get("status") if isinstance(obj, Mapping) else None,
            "output_guard": output_guard,
            "summary_error": "minimal bounded JSON summary exceeded stdout cap",
        },
        indent=2 if pretty else None,
        sort_keys=True,
        allow_nan=False,
    )


def emit_json(obj: Any, *, pretty: bool = False, max_bytes: int = DEFAULT_JSON_BYTES) -> None:
    print(bounded_json_text(obj, pretty=pretty, max_bytes=max_bytes))


def bounded_text(
    text: str,
    *,
    max_bytes: int = DEFAULT_MAX_STDOUT_BYTES,
    line_limit_bytes: int = DEFAULT_MAX_LINE_BYTES,
) -> str:
    sink = io.StringIO()
    guarded = BoundedTextIO(sink, limit_bytes=max_bytes, line_limit_bytes=line_limit_bytes)
    guarded.write(text)
    guarded.flush()
    return sink.getvalue()
