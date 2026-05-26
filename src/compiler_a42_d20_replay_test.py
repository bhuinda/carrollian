from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

try:
    from src.compiler.common import ROOT, read_json, sha256_file, sha256_json, write_json
    from src.compiler.scene_builder import TurnCompileConfig, compile_turn
    from src.compiler.verify_turn import verify_turn
    from src.evidence_registry import sync_evidence_index_entry
except ModuleNotFoundError:  # Supports `python src/compiler_a42_d20_replay_test.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.compiler.common import ROOT, read_json, sha256_file, sha256_json, write_json
    from src.compiler.scene_builder import TurnCompileConfig, compile_turn
    from src.compiler.verify_turn import verify_turn
    from src.evidence_registry import sync_evidence_index_entry


TEST_ID = "compiler_a42_d20_replay_test"
STATUS = "COMPILER_A42_D20_REPLAY_CERTIFIED"
BASE = ROOT / "data" / "evidence" / TEST_ID
LOCK_FILE = BASE / ".write.lock"
STAGING_ROOT = BASE / ".staging"
CORE_LOCK = BASE / "CORE.lock.json"
REPORT = BASE / "report.json"
MANIFEST = BASE / "manifest.json"
ANSWER = "Claim-level support verifies the quotient tower residue through A42 and D20."
REQUEST = "Verify a claim-level A42 and D20 residue witness."


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _repo_ref(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _file_ref(path: Path) -> dict[str, Any]:
    return {
        "path": _repo_ref(path),
        "sha256": sha256_file(path),
        "size": path.stat().st_size,
    }


def _public_file_ref(path: Path, public_path: Path) -> dict[str, Any]:
    ref = _file_ref(path)
    ref["path"] = _repo_ref(public_path)
    return ref


class EvidenceWriteLock:
    def __init__(self, path: Path, *, timeout_seconds: float = 30.0) -> None:
        self.path = path
        self.timeout_seconds = timeout_seconds

    def __enter__(self) -> "EvidenceWriteLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout_seconds
        payload = f"pid={os.getpid()}\n"
        while True:
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out waiting for evidence write lock: {_repo_ref(self.path)}")
                time.sleep(0.1)
                continue
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
            return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def _clear_staging_dir(path: Path) -> None:
    staging_root = STAGING_ROOT.resolve()
    resolved = path.resolve()
    if resolved != staging_root and staging_root not in resolved.parents:
        raise ValueError(f"refusing to clear non-staging path: {path}")
    if path.exists():
        shutil.rmtree(path)


def _promote_staged_tree(staging_dir: Path) -> None:
    files = [path for path in staging_dir.rglob("*") if path.is_file()]
    files.sort(key=lambda path: (path.relative_to(staging_dir).as_posix() == "manifest.json", path.relative_to(staging_dir).as_posix()))
    for source in files:
        relative = source.relative_to(staging_dir)
        target = BASE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, target)


def _compile(
    run_name: str,
    *,
    base: Path = BASE,
    support_coordinates_file: Path | None = None,
    write_core_lock: bool = False,
) -> dict[str, Any]:
    return compile_turn(
        TurnCompileConfig(
            turn_id=f"{TEST_ID}_{run_name}",
            user_text=REQUEST,
            answer_text=ANSWER,
            run_dir=base / run_name,
            mode="tensor_backed",
            core_lock_path=base / "CORE.lock.json",
            write_core_lock=write_core_lock,
            support_coordinates_file=support_coordinates_file,
            timestamp="1970-01-01T00:00:00Z",
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


def _check_positive(base: Path, coordinates_file: Path) -> dict[str, Any]:
    result = _compile("positive", base=base, support_coordinates_file=coordinates_file, write_core_lock=True)
    _assert(result.get("verification_status") == "PASS_WITH_RESIDUE", "positive compile did not pass with residue")
    verify = verify_turn(base / "positive", root=ROOT)
    _assert(verify.get("status") == "PASS_WITH_RESIDUE", "positive replay verification did not pass")
    residue = _quotient_residue(base / "positive")
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


def _check_missing_coordinate(base: Path) -> dict[str, Any]:
    result = _compile("missing_coordinate", base=base)
    _assert(result.get("verification_status") == "BLOCKED_WITH_RESIDUE", "missing coordinate compile did not block")
    verify = verify_turn(base / "missing_coordinate", root=ROOT)
    _assert(verify.get("status") == "BLOCKED_WITH_RESIDUE", "missing coordinate replay did not block")
    ledger = read_json(base / "missing_coordinate" / "08_residue_ledger.json")
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


def _check_tamper(base: Path, coordinates_file: Path) -> dict[str, Any]:
    result = _compile("tampered_coordinate", base=base, support_coordinates_file=coordinates_file)
    _assert(result.get("verification_status") == "PASS_WITH_RESIDUE", "tamper setup compile did not pass")
    ledger_path = base / "tampered_coordinate" / "04_support_ledger.json"
    ledger = read_json(ledger_path)
    ledger["claim_support"]["c001"]["coordinates"][0]["alpha"] = 1
    write_json(ledger_path, ledger)
    verify = verify_turn(base / "tampered_coordinate", root=ROOT)
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


def build_manifest(
    report: dict[str, Any],
    *,
    artifact_base: Path = BASE,
    public_base: Path = BASE,
) -> dict[str, Any]:
    checks = report.get("checks", {})
    manifest: dict[str, Any] = {
        "schema": "holotopy.compiler_a42_d20_replay_manifest",
        "status": STATUS if report.get("status") == "PASS" else "FAIL",
        "test_id": TEST_ID,
        "purpose": "Replay-gated A42 and D20 coordinate witness coverage for compiler turn capsules.",
        "entrypoint": _public_file_ref(artifact_base / "report.json", public_base / "report.json"),
        "artifacts": {
            "report": _public_file_ref(artifact_base / "report.json", public_base / "report.json"),
            "core_lock": _public_file_ref(artifact_base / "CORE.lock.json", public_base / "CORE.lock.json"),
            "support_coordinates": _public_file_ref(
                artifact_base / "support_coordinates.json",
                public_base / "support_coordinates.json",
            ),
            "positive_turn_lock": _public_file_ref(
                artifact_base / "positive" / "TURN.lock.json",
                public_base / "positive" / "TURN.lock.json",
            ),
            "positive_residue_ledger": _public_file_ref(
                artifact_base / "positive" / "08_residue_ledger.json",
                public_base / "positive" / "08_residue_ledger.json",
            ),
            "missing_coordinate_residue_ledger": _public_file_ref(
                artifact_base / "missing_coordinate" / "08_residue_ledger.json",
                public_base / "missing_coordinate" / "08_residue_ledger.json",
            ),
            "tampered_coordinate_support_ledger": _public_file_ref(
                artifact_base / "tampered_coordinate" / "04_support_ledger.json",
                public_base / "tampered_coordinate" / "04_support_ledger.json",
            ),
        },
        "runs": {
            "positive": _repo_ref(public_base / "positive"),
            "missing_coordinate": _repo_ref(public_base / "missing_coordinate"),
            "tampered_coordinate": _repo_ref(public_base / "tampered_coordinate"),
        },
        "commands": {
            "regenerate": "python src/compiler_a42_d20_replay_test.py",
            "verify": "python src/verify.py compiler-a42-d20-replay --pretty",
        },
        "promotion": {
            "method": "locked_staging_then_file_replace",
            "lock_file": _repo_ref(LOCK_FILE),
            "manifest_promoted_last": True,
        },
        "checks": {
            "positive_a42_d20_coordinate_replay": checks.get("positive_a42_d20_coordinate_replay", {}).get(
                "verify_status"
            )
            == "PASS_WITH_RESIDUE",
            "missing_coordinate_blocks": checks.get("missing_coordinate_blocks", {}).get("verify_status")
            == "BLOCKED_WITH_RESIDUE",
            "tampered_coordinate_fails_replay": checks.get("tampered_coordinate_fails_replay", {}).get(
                "tampered_verify_status"
            )
            == "FAIL",
        },
    }
    manifest["manifest_sha256"] = sha256_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    return manifest


def _run_test_payload(base: Path, *, public_base: Path = BASE) -> dict[str, Any]:
    base.mkdir(parents=True, exist_ok=True)
    coordinates_file = base / "support_coordinates.json"
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
        "positive_a42_d20_coordinate_replay": _check_positive(base, coordinates_file),
        "missing_coordinate_blocks": _check_missing_coordinate(base),
        "tampered_coordinate_fails_replay": _check_tamper(base, coordinates_file),
    }
    report = {
        "schema": "holotopy.compiler_a42_d20_replay_test",
        "status": "PASS",
        "checks": checks,
        "output_dir": _repo_ref(public_base),
    }
    report["certificate_sha256"] = sha256_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    write_json(base / "report.json", report)
    manifest = build_manifest(report, artifact_base=base, public_base=public_base)
    write_json(base / "manifest.json", manifest)
    return report


def run_test() -> dict[str, Any]:
    BASE.mkdir(parents=True, exist_ok=True)
    with EvidenceWriteLock(LOCK_FILE):
        staging_dir = STAGING_ROOT / f"pid_{os.getpid()}"
        _clear_staging_dir(staging_dir)
        try:
            report = _run_test_payload(staging_dir, public_base=BASE)
            _promote_staged_tree(staging_dir)
            sync_evidence_index_entry(
                evidence_id=TEST_ID,
                root=BASE,
                entrypoint=MANIFEST,
                status=STATUS,
            )
            return report
        finally:
            _clear_staging_dir(staging_dir)


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
