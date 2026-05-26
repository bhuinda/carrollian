from __future__ import annotations

from typing import Any

from .common import ROOT, utc_timestamp
from .scene_builder import TurnCompileConfig, compile_turn


def run_selftest() -> dict[str, Any]:
    stamp = utc_timestamp().replace(":", "").replace("-", "")
    turn_id = f"compiler_selftest_{stamp}"
    base = ROOT / "temp" / "compiler_selftest"
    core_lock = base / "CORE.lock.json"
    run_dir = base / "runs" / turn_id
    result = compile_turn(
        TurnCompileConfig(
            turn_id=turn_id,
            user_text="Compile a public proof-carrying scene trace and verify the capsule.",
            answer_text=(
                "The compiler writes a turn capsule with request, obligations, claims, support ledger, "
                "SceneIR, D20 lowering, residue ledger, verification report, final answer, certificate, "
                "replay instructions, metrics, and TURN.lock."
            ),
            run_dir=run_dir,
            mode="scaffold",
            core_lock_path=core_lock,
            write_core_lock=True,
        ),
        root=ROOT,
    )
    return {
        "schema": "holotopy.compiler_selftest",
        "status": result.get("verification_status"),
        "run_dir": result.get("run_dir"),
        "core_lock": str(core_lock),
        "result": result,
    }


def main() -> None:
    import json

    result = run_selftest()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result.get("status") in {"PASS", "PASS_WITH_RESIDUE"} else 1)


if __name__ == "__main__":
    main()
