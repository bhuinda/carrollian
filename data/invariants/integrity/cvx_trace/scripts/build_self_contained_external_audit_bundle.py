from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
CVX = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
AUDIT_PACK = CVX / "reports" / "external_formal_audit_pack.json"
REPORT_PATH = CVX / "reports" / "self_contained_external_audit_bundle.json"
NOTE_PATH = CVX / "reports" / "self_contained_external_audit_bundle.md"
BUNDLE_PARENT = ROOT / "generated" / "external_audit_bundle"
BUNDLE_ROOT = BUNDLE_PARENT / "carrollian_external_audit_bundle"

ROOTS_TO_COPY = [
    ROOT / "data",
    ROOT / "layers",
]
ROOT_FILES_TO_COPY = [
    ROOT / "README.md",
    ROOT / "requirements.txt",
]
IGNORE_PATTERNS = shutil.ignore_patterns(
    "__pycache__",
    "*.pyc",
    "*.agdai",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
)


def rel(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reset_bundle_root() -> None:
    parent = BUNDLE_PARENT.resolve()
    target = BUNDLE_ROOT.resolve()
    if parent == target or parent not in target.parents:
        raise RuntimeError(f"refusing to reset unsafe bundle path: {target}")
    if BUNDLE_ROOT.exists():
        shutil.rmtree(BUNDLE_ROOT)
    BUNDLE_ROOT.mkdir(parents=True)


def copy_surface() -> list[dict[str, Any]]:
    copied = []
    for source in ROOTS_TO_COPY:
        destination = BUNDLE_ROOT / rel(source)
        shutil.copytree(source, destination, ignore=IGNORE_PATTERNS)
        copied.append(
            {
                "source": rel(source),
                "destination": destination.relative_to(BUNDLE_ROOT).as_posix(),
                "kind": "tree",
            }
        )
    for source in ROOT_FILES_TO_COPY:
        if not source.exists():
            continue
        destination = BUNDLE_ROOT / rel(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(
            {
                "source": rel(source),
                "destination": destination.relative_to(BUNDLE_ROOT).as_posix(),
                "kind": "file",
            }
        )
    return copied


def write_bundle_readme(pack: dict[str, Any]) -> None:
    lines = [
        "# Carrollian External Audit Bundle",
        "",
        "This directory is a self-contained replay surface for the external formal audit pack.",
        "",
        "Run replay commands from this directory. The minimal replay plan is stored in:",
        "",
        "- `data/invariants/integrity/cvx_trace/reports/external_formal_audit_pack.json`",
        "",
        "The bundle includes the repo `data` and `layers` trees plus small root metadata files. It does not bundle external executables.",
        "",
        "Required tools on PATH:",
        "",
        "- `python`",
        "- `agda`",
        "",
        "Replay command count:",
        "",
        f"- `{len(pack.get('minimal_replay_plan', {}).get('commands', []))}`",
        "",
    ]
    (BUNDLE_ROOT / "AUDIT_BUNDLE_README.md").write_text("\n".join(lines), encoding="utf-8")


def write_replay_script(pack: dict[str, Any]) -> None:
    commands = pack.get("minimal_replay_plan", {}).get("commands", [])
    lines = [
        "$ErrorActionPreference = 'Stop'",
        "$root = Split-Path -Parent $MyInvocation.MyCommand.Path",
        "Set-Location $root",
        "$failures = 0",
    ]
    for command in commands:
        step = command["step"]
        expected = command["expected_stdout"]
        lines.extend(
            [
                f"Write-Host '[{step}] {command['command']}'",
                f"$out = (& {command['command']} 2>&1 | Out-String).Trim()",
                f"if ($LASTEXITCODE -ne 0 -or $out -ne '{expected}') {{",
                f"  Write-Host 'FAILED {step}'",
                "  Write-Host $out",
                "  $failures += 1",
                "} else {",
                f"  Write-Host 'PASSED {step}'",
                "}",
            ]
        )
    lines.extend(
        [
            "if ($failures -ne 0) { exit 1 }",
            "exit 0",
        ]
    )
    (BUNDLE_ROOT / "run_replay.ps1").write_text("\n".join(lines) + "\n", encoding="utf-8")


def file_manifest() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(p for p in BUNDLE_ROOT.rglob("*") if p.is_file()):
        rows.append(
            {
                "path": path.relative_to(BUNDLE_ROOT).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return rows


def bundle_path_exists(relative_path: str) -> bool:
    return (BUNDLE_ROOT / relative_path).exists()


def audit_pack_coverage(pack: dict[str, Any]) -> dict[str, Any]:
    artifact_paths = [
        item["path"]
        for item in pack.get("artifact_hash_manifest", [])
        if item.get("exists") is True
    ]
    command_script_paths = [
        item["script"]
        for item in pack.get("minimal_replay_plan", {}).get("commands", [])
        if item.get("script")
    ]
    required_paths = sorted(set(artifact_paths + command_script_paths))
    missing = [path for path in required_paths if not bundle_path_exists(path)]
    return {
        "required_path_count": len(required_paths),
        "missing_count": len(missing),
        "missing_paths": missing,
        "passed": not missing and bool(required_paths),
    }


def build_report() -> dict[str, Any]:
    pack = load_json(AUDIT_PACK)
    reset_bundle_root()
    copied = copy_surface()
    write_bundle_readme(pack)
    write_replay_script(pack)
    manifest = file_manifest()
    coverage = audit_pack_coverage(pack)
    total_size = sum(item["size_bytes"] for item in manifest)
    pass_condition = coverage["passed"] and bundle_path_exists(rel(AUDIT_PACK))

    return {
        "schema": "d20.integrity.self_contained_external_audit_bundle.source_drop",
        "status": (
            "SELF_CONTAINED_EXTERNAL_AUDIT_BUNDLE_BUILT"
            if pass_condition
            else "SELF_CONTAINED_EXTERNAL_AUDIT_BUNDLE_INCOMPLETE"
        ),
        "claim_level": "portable_replay_surface_packaging",
        "bundle": {
            "path": str(BUNDLE_ROOT),
            "relative_path": rel(BUNDLE_ROOT),
            "file_count": len(manifest),
            "total_size_bytes": total_size,
            "total_size_mib": round(total_size / (1024 * 1024), 3),
            "readme": "AUDIT_BUNDLE_README.md",
            "replay_script": "run_replay.ps1",
        },
        "copied_surface": copied,
        "coverage": coverage,
        "source_audit_pack": {
            "path": rel(AUDIT_PACK),
            "status": pack.get("status"),
            "sha256": sha256(AUDIT_PACK),
            "command_count": len(pack.get("minimal_replay_plan", {}).get("commands", [])),
            "artifact_count": len(pack.get("artifact_hash_manifest", [])),
        },
        "file_manifest_sample": manifest[:25],
        "decision": {
            "may_claim_self_contained_bundle_built": pass_condition,
            "may_claim_bundle_contains_all_audit_pack_paths": coverage["passed"],
            "may_claim_external_tools_bundled": False,
            "reason": (
                "The bundle contains every audit-pack artifact and replay script path under its own root."
                if pass_condition
                else "The bundle is missing one or more audit-pack artifact or replay script paths."
            ),
        },
        "non_claims": [
            "This does not bundle Python or Agda executables.",
            "This does not replace independent external review.",
            "This does not include ignored local caches or proof-assistant interface cache files.",
        ],
        "next_highest_yield_item": {
            "id": "self_contained_bundle_replay",
            "action": "Replay the audit command list from a fresh copy of the self-contained bundle.",
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Self-Contained External Audit Bundle",
        "",
        "## Status",
        "",
        f"- `{report['status']}`",
        "",
        "## Bundle",
        "",
        f"- Path: `{report['bundle']['relative_path']}`",
        f"- Files: `{report['bundle']['file_count']}`",
        f"- Size MiB: `{report['bundle']['total_size_mib']}`",
        "",
        "## Coverage",
        "",
        f"- Required paths: `{report['coverage']['required_path_count']}`",
        f"- Missing paths: `{report['coverage']['missing_count']}`",
        "",
        "## Boundary",
        "",
    ]
    for item in report["non_claims"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next", "", report["next_highest_yield_item"]["action"], ""])
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    NOTE_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(report["status"])
    return 0 if report["decision"]["may_claim_self_contained_bundle_built"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
