from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from src.compiler.common import ROOT, read_json, sha256_json, write_json
    from src.compiler.scene_builder import TurnCompileConfig, compile_turn
    from src.compiler.verify_turn import verify_turn
except ModuleNotFoundError:  # Supports `python src/compiler_a42_d20_replay_test.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.compiler.common import ROOT, read_json, sha256_json, write_json
    from src.compiler.scene_builder import TurnCompileConfig, compile_turn
    from src.compiler.verify_turn import verify_turn


TEST_ID = "compiler_a42_d20_replay_test"
BASE = ROOT / "temp" / TEST_ID
CORE_LOCK = BASE / "CORE.lock.json"
ANSWER = "Claim-level support verifies the quotient tower residue through A42 and D20."
REQUEST = "Verify a claim-level A42 and D20 residue witness."


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _compile(run_name: str, *, support_coordinates_file: Path | None = None, write_core_lock: bool = False) -> dict[str, Any]:
    return compile_turn(
        TurnCompileConfig(
            turn_id=f"{TEST_ID}_{run_name}",
            user_text=REQUEST,
            answer_text=ANSWER,
            run_dir=BASE / run_name,
            mode="tensor_backed",
            core_lock_path=CORE_LOCK,
            write_core_lock=write_core_lock,
            support_coordinates_file=support_coordinates_file,
        ),
        root=ROOT,
    )


def _quotient_residue(run_dir: Path) -> dict[str, Any]:
    ledger = read_json(run_dir / "08_residue_ledger.json")
    residues = [
        item
        for item in ledger.get("residues", [])
        if item.get("kind") == "quotient_tower_residue" and item.get("claim_id") == "c001"
    ]
    _assert(len(residues) == 1, "expected exactly one c001 quotient-tower residue")
    return residues[0]


def _check_positive(coordinates_file: Path) -> dict[str, Any]:
    result = _compile("positive", support_coordinates_file=coordinates_file, write_core_lock=True)
    _assert(result.get("verification_status") == "PASS_WITH_RESIDUE", "positive compile did not pass with residue")
    verify = verify_turn(BASE / "positive", root=ROOT)
    _assert(verify.get("status") == "PASS_WITH_RESIDUE", "positive replay verification did not pass")
    residue = _quotient_residue(BASE / "positive")
    expected_flags = {
        "q42_boundary_zero": True,
        "a42_to_q12_boundary_zero": True,
        "q12_boundary_zero": True,
        "d20_q12_boundary_zero": True,
        "d20_a42_boundary_zero": True,
        "d20_graph_valid": True,
        "discharged": True,
    }
    for key, expected in expected_flags.items():
        _assert(residue.get(key) is expected, f"positive residue flag mismatch: {key}")
    return {
        "compile_status": result.get("verification_status"),
        "verify_status": verify.get("status"),
        "residue_flags": expected_flags,
        "residue_sha256": residue.get("q12_residue_sha256"),
    }


def _check_missing_coordinate() -> dict[str, Any]:
    result = _compile("missing_coordinate")
    _assert(result.get("verification_status") == "BLOCKED_WITH_RESIDUE", "missing coordinate compile did not block")
    verify = verify_turn(BASE / "missing_coordinate", root=ROOT)
    _assert(verify.get("status") == "BLOCKED_WITH_RESIDUE", "missing coordinate replay did not block")
    ledger = read_json(BASE / "missing_coordinate" / "08_residue_ledger.json")
    missing = [
        item
        for item in ledger.get("residues", [])
        if item.get("kind") == "claim_residue_coordinate_missing" and item.get("claim_ids") == ["c001"]
    ]
    _assert(len(missing) == 1, "missing coordinate residue was not recorded")
    return {
        "compile_status": result.get("verification_status"),
        "verify_status": verify.get("status"),
        "missing_residue_id": missing[0].get("id"),
    }


def _check_tamper(coordinates_file: Path) -> dict[str, Any]:
    result = _compile("tampered_coordinate", support_coordinates_file=coordinates_file)
    _assert(result.get("verification_status") == "PASS_WITH_RESIDUE", "tamper setup compile did not pass")
    ledger_path = BASE / "tampered_coordinate" / "04_support_ledger.json"
    ledger = read_json(ledger_path)
    ledger["claim_support"]["c001"]["coordinates"][0]["alpha"] = 1
    write_json(ledger_path, ledger)
    verify = verify_turn(BASE / "tampered_coordinate", root=ROOT)
    errors = verify.get("errors", [])
    _assert(verify.get("status") == "FAIL", "tampered coordinate replay did not fail")
    _assert(
        any("support coordinate alpha/beta mismatch" in error for error in errors),
        "tampered coordinate mismatch was not reported",
    )
    return {
        "setup_status": result.get("verification_status"),
        "tampered_verify_status": verify.get("status"),
        "error_count": len(errors),
    }


def run_test() -> dict[str, Any]:
    BASE.mkdir(parents=True, exist_ok=True)
    coordinates_file = BASE / "support_coordinates.json"
    write_json(
        coordinates_file,
        {
            "claims": {
                "c001": [
                    {
                        "alpha": 0,
                        "beta": 0,
                        "label": "A42/D20 replay test coordinate",
                    }
                ]
            }
        },
    )
    checks = {
        "positive_a42_d20_coordinate_replay": _check_positive(coordinates_file),
        "missing_coordinate_blocks": _check_missing_coordinate(),
        "tampered_coordinate_fails_replay": _check_tamper(coordinates_file),
    }
    report = {
        "schema": "holotopy.compiler_a42_d20_replay_test",
        "status": "PASS",
        "checks": checks,
        "output_dir": str(BASE),
    }
    report["certificate_sha256"] = sha256_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def main() -> None:
    try:
        report = run_test()
    except Exception as exc:
        report = {
            "schema": "holotopy.compiler_a42_d20_replay_test",
            "status": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
            "output_dir": str(BASE),
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        raise SystemExit(1)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
