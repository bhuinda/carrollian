#!/usr/bin/env python3
"""Readable verifier entrypoint for d20.

The `src.commands.certify` entrypoint remains authoritative. This module exposes
the practical verification modes without hiding file writes behind a default:

* core: validate the mathematical core and layer statuses only;
* audit: validate core plus constructor witness and the file manifest;
* rebuild: regenerate d20.json, refresh hashes, then audit;
  pass --cached-source to reuse checked source artifacts and skip heavy source refresh;
* strict-replay: validate core plus a fresh zero-axiom coorient replay;
* tamper: mutate certified evidence in memory and require verification failure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime import ensure_numpy_runtime  # noqa: E402

ensure_numpy_runtime(ROOT, __file__)

from src.commands import certify  # noqa: E402


MODES = {
    "core": "fast",
    "audit": "audit",
    "rebuild": "rebuild",
    "strict-replay": "strict-replay",
    "tamper": "tamper",
}


def emit(obj: dict[str, Any], pretty: bool) -> None:
    print(json.dumps(obj, indent=2 if pretty else None, sort_keys=True))


def run(command: str, *, pretty: bool) -> int:
    mode = MODES[command]
    result = certify.run(mode)
    return finish(result, pretty)


def rebuild(*, pretty: bool, cached_source: bool = False) -> int:
    regen_info = certify.maybe_regenerate(
        "rebuild",
        pretty,
        True,
        refresh_sources=not cached_source,
    )
    result = certify.run("rebuild")
    result["regeneration"] = regen_info
    return finish(result, pretty)


def finish(result: dict[str, Any], pretty: bool) -> int:
    emit(result, pretty)
    return 0 if result.get("status") == "PASS" else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the d20 bundle.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("core", "audit", "rebuild", "strict-replay", "tamper"):
        p = sub.add_parser(name)
        p.add_argument("--pretty", action="store_true")
        if name == "rebuild":
            p.add_argument(
                "--cached-source",
                action="store_true",
                help="Reuse existing checked source artifacts and skip heavy source refresh.",
            )
    args = parser.parse_args()

    if args.command == "rebuild":
        raise SystemExit(rebuild(pretty=args.pretty, cached_source=args.cached_source))
    raise SystemExit(run(args.command, pretty=args.pretty))


if __name__ == "__main__":
    main()
