from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
AUDIT_PACK = CVX / "reports" / "external_formal_audit_pack.json"
REPORT_PATH = CVX / "reports" / "independent_external_replay_report.json"
SNAPSHOT_PARENT = ROOT / ".replay_tmp"


def rel(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_replay_surface() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    SNAPSHOT_PARENT.mkdir(exist_ok=True)
    snapshot = Path(tempfile.mkdtemp(prefix=f"carrollian-independent-replay-{timestamp}-", dir=SNAPSHOT_PARENT))
    shutil.copytree(
        ROOT / "data",
        snapshot / "data",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.agdai"),
    )
    shutil.copytree(
        ROOT / "layers",
        snapshot / "layers",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    return snapshot


def run_replay_commands(snapshot: Path, commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for index, item in enumerate(commands, start=1):
        command = item["command"]
        expected_stdout = item["expected_stdout"]
        completed = subprocess.run(
            command.split(),
            cwd=snapshot,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        rows.append(
            {
                "index": index,
                "step": item["step"],
                "command": command,
                "expected_stdout": expected_stdout,
                "observed_stdout": stdout,
                "stderr": stderr,
                "returncode": completed.returncode,
                "passed": completed.returncode == 0 and stdout == expected_stdout,
            }
        )
    return rows


def manifest_by_path(pack: dict[str, Any]) -> dict[str, str | None]:
    return {
        item["path"]: item.get("sha256")
        for item in pack.get("artifact_hash_manifest", [])
        if item.get("exists") is True
    }


def compare_manifests(baseline_pack: dict[str, Any], replayed_pack: dict[str, Any]) -> dict[str, Any]:
    baseline = manifest_by_path(baseline_pack)
    replayed = manifest_by_path(replayed_pack)
    paths = sorted(set(baseline) | set(replayed))
    mismatches = [
        {
            "path": path,
            "baseline_sha256": baseline.get(path),
            "replayed_sha256": replayed.get(path),
        }
        for path in paths
        if baseline.get(path) != replayed.get(path)
    ]
    return {
        "baseline_count": len(baseline),
        "replayed_count": len(replayed),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "passed": not mismatches and bool(paths),
    }


def build_report() -> dict[str, Any]:
    baseline_pack = load_json(AUDIT_PACK)
    snapshot = copy_replay_surface()
    commands = baseline_pack["minimal_replay_plan"]["commands"]
    replay_rows = run_replay_commands(snapshot, commands)
    replayed_pack_path = snapshot / rel(AUDIT_PACK)
    replayed_pack = load_json(replayed_pack_path) if replayed_pack_path.exists() else {}
    manifest_comparison = (
        compare_manifests(baseline_pack, replayed_pack) if replayed_pack else {
            "baseline_count": len(manifest_by_path(baseline_pack)),
            "replayed_count": 0,
            "mismatch_count": 1,
            "mismatches": [{"path": rel(AUDIT_PACK), "reason": "replayed audit pack missing"}],
            "passed": False,
        }
    )
    all_commands_passed = all(row["passed"] for row in replay_rows)
    replayed_pack_ready = replayed_pack.get("status") == "EXTERNAL_FORMAL_AUDIT_PACK_READY"
    pass_condition = all_commands_passed and manifest_comparison["passed"] and replayed_pack_ready

    return {
        "schema": "d20.integrity.independent_external_replay_report.source_drop",
        "status": "INDEPENDENT_EXTERNAL_REPLAY_PASS" if pass_condition else "INDEPENDENT_EXTERNAL_REPLAY_FAIL",
        "claim_level": "same_machine_isolated_snapshot_replay",
        "source_audit_pack": rel(AUDIT_PACK),
        "snapshot": {
            "path": str(snapshot),
            "surface": "data and layers trees copied into an ignored local replay directory; .git and virtual environments excluded",
            "retained_for_inspection": True,
        },
        "command_replay": {
            "command_count": len(replay_rows),
            "passed_count": sum(1 for row in replay_rows if row["passed"]),
            "failed_count": sum(1 for row in replay_rows if not row["passed"]),
            "rows": replay_rows,
        },
        "artifact_hash_comparison": manifest_comparison,
        "decision": {
            "may_claim_same_machine_clean_snapshot_replay": pass_condition,
            "may_claim_external_validation_completed": False,
            "may_claim_clean_checkout_hash_replay": pass_condition,
            "reason": (
                "The audit-pack command list replayed in an isolated snapshot and reproduced the artifact hash manifest."
                if pass_condition
                else "One or more replay commands failed, the audit pack was not rebuilt, or hashes diverged."
            ),
        },
        "non_claims": [
            "This is not peer review.",
            "This is not theorem-level proof-assistant verification beyond the typechecked interface definitions.",
            "This is not a different-machine or different-implementation replay.",
        ],
        "next_highest_yield_item": {
            "id": "proof_assistant_formalization_or_external_reviewer",
            "action": "Move the theorem and replay relation into a proof assistant or hand the audit pack to an independent reviewer.",
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["decision"]["may_claim_same_machine_clean_snapshot_replay"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
