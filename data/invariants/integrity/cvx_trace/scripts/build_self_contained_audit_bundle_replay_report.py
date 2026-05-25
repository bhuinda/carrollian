from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
BUNDLE_REPORT = CVX / "reports" / "self_contained_external_audit_bundle.json"
REPORT_PATH = CVX / "reports" / "self_contained_audit_bundle_replay_report.json"
SNAPSHOT_PARENT = ROOT / ".replay_tmp"


def rel(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_bundle(bundle_root: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    SNAPSHOT_PARENT.mkdir(exist_ok=True)
    snapshot = Path(tempfile.mkdtemp(prefix=f"carrollian-self-contained-bundle-{timestamp}-", dir=SNAPSHOT_PARENT))
    target = snapshot / "bundle"
    shutil.copytree(
        bundle_root,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.agdai"),
    )
    return target


def run_replay_commands(bundle_root: Path, commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for index, item in enumerate(commands, start=1):
        completed = subprocess.run(
            item["command"].split(),
            cwd=bundle_root,
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
                "command": item["command"],
                "expected_stdout": item["expected_stdout"],
                "observed_stdout": stdout,
                "stderr": stderr,
                "returncode": completed.returncode,
                "passed": completed.returncode == 0 and stdout == item["expected_stdout"],
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
    bundle_report = load_json(BUNDLE_REPORT)
    bundle_root = Path(bundle_report["bundle"]["path"])
    source_pack_path = bundle_root / "data/invariants/integrity/cvx_trace/reports/external_formal_audit_pack.json"
    source_pack = load_json(source_pack_path)
    replay_bundle_root = copy_bundle(bundle_root)
    replay_pack_path = replay_bundle_root / "data/invariants/integrity/cvx_trace/reports/external_formal_audit_pack.json"
    replay_rows = run_replay_commands(replay_bundle_root, source_pack["minimal_replay_plan"]["commands"])
    replayed_pack = load_json(replay_pack_path) if replay_pack_path.exists() else {}
    manifest_comparison = compare_manifests(source_pack, replayed_pack) if replayed_pack else {
        "baseline_count": len(manifest_by_path(source_pack)),
        "replayed_count": 0,
        "mismatch_count": 1,
        "mismatches": [{"path": rel(replay_pack_path, replay_bundle_root), "reason": "replayed audit pack missing"}],
        "passed": False,
    }
    all_commands_passed = all(row["passed"] for row in replay_rows)
    replayed_pack_ready = replayed_pack.get("status") == "EXTERNAL_FORMAL_AUDIT_PACK_READY"
    pass_condition = all_commands_passed and manifest_comparison["passed"] and replayed_pack_ready

    return {
        "schema": "d20.integrity.self_contained_audit_bundle_replay_report.source_drop",
        "status": (
            "SELF_CONTAINED_AUDIT_BUNDLE_REPLAY_PASS"
            if pass_condition
            else "SELF_CONTAINED_AUDIT_BUNDLE_REPLAY_FAIL"
        ),
        "claim_level": "self_contained_bundle_replay",
        "source_bundle_report": rel(BUNDLE_REPORT),
        "bundle": {
            "source_path": str(bundle_root),
            "replay_path": str(replay_bundle_root),
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
            "may_claim_self_contained_bundle_replays": pass_condition,
            "may_claim_external_validation_completed": False,
            "reason": (
                "A fresh copy of the generated self-contained bundle replayed the audit plan and reproduced the hash manifest."
                if pass_condition
                else "The self-contained bundle failed replay or produced hash mismatches."
            ),
        },
        "non_claims": [
            "This is same-machine replay from a portable bundle, not external peer review.",
            "This assumes Python and Agda are installed on the replay machine.",
        ],
        "next_highest_yield_item": {
            "id": "external_clean_machine_replay",
            "action": "Move the generated bundle to a clean machine and replay it there.",
        },
    }


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["decision"]["may_claim_self_contained_bundle_replays"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
