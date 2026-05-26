from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import ROOT, write_json
from .core_lock import build_core_lock
from .scene_builder import TurnCompileConfig, compile_turn
from .selftest import run_selftest
from .verify_turn import verify_turn


def _read_arg(value: str | None, file_value: str | None) -> str:
    if file_value:
        return Path(file_value).read_text(encoding="utf-8")
    return value or ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile public proof-carrying scene capsules.")
    sub = parser.add_subparsers(dest="command", required=True)

    compile_parser = sub.add_parser("compile", help="Compile a request and final answer into a turn capsule.")
    compile_parser.add_argument("--turn-id", required=True)
    compile_parser.add_argument("--request")
    compile_parser.add_argument("--request-file")
    compile_parser.add_argument("--answer")
    compile_parser.add_argument("--answer-file")
    compile_parser.add_argument("--out", help="Run directory. Defaults to runs/<turn-id>.")
    compile_parser.add_argument("--mode", choices=["scaffold", "tensor_backed"], default="scaffold")
    compile_parser.add_argument("--core-lock", help="Path to CORE.lock.json.")
    compile_parser.add_argument("--write-core-lock", action="store_true")
    compile_parser.add_argument("--support-coordinates-file", help="JSON claim-to-A985 product coordinate declarations.")
    compile_parser.add_argument("--support-file", action="append", default=[], help="Additional public support file to attach to every claim.")
    compile_parser.add_argument("--pretty", action="store_true")

    verify_parser = sub.add_parser("verify", help="Verify a compiled turn capsule.")
    verify_parser.add_argument("run_dir")
    verify_parser.add_argument("--pretty", action="store_true")

    lock_parser = sub.add_parser("core-lock", help="Emit a CORE.lock.json payload.")
    lock_parser.add_argument("--out")
    lock_parser.add_argument("--pretty", action="store_true")

    selftest_parser = sub.add_parser("selftest", help="Run a compiler smoke test.")
    selftest_parser.add_argument("--pretty", action="store_true")

    args = parser.parse_args()

    if args.command == "compile":
        request = _read_arg(args.request, args.request_file)
        answer = _read_arg(args.answer, args.answer_file)
        result = compile_turn(
            TurnCompileConfig(
                turn_id=args.turn_id,
                user_text=request,
                answer_text=answer,
                run_dir=Path(args.out) if args.out else None,
                mode=args.mode,
                core_lock_path=Path(args.core_lock) if args.core_lock else None,
                write_core_lock=args.write_core_lock,
                support_coordinates_file=Path(args.support_coordinates_file) if args.support_coordinates_file else None,
                extra_support_files=tuple(Path(item) for item in args.support_file),
            )
        )
        print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=args.pretty))
        raise SystemExit(0 if result.get("verification_status") in {"PASS", "PASS_WITH_RESIDUE"} else 1)

    if args.command == "verify":
        result = verify_turn(args.run_dir)
        print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=args.pretty))
        raise SystemExit(0 if result.get("status") in {"PASS", "PASS_WITH_RESIDUE"} else 1)

    if args.command == "core-lock":
        payload = build_core_lock(ROOT)
        if args.out:
            out = Path(args.out)
            if not out.is_absolute():
                out = ROOT / out
            write_json(out, payload, pretty=args.pretty)
        print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=args.pretty))
        raise SystemExit(0 if payload.get("status") == "LOCKED" else 1)

    result = run_selftest()
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=args.pretty))
    raise SystemExit(0 if result.get("status") in {"PASS", "PASS_WITH_RESIDUE"} else 1)


if __name__ == "__main__":
    main()
