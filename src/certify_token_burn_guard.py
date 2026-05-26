from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import ast
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from .evidence_registry import sync_evidence_index_entry
    from .token_burn_guard import (
        BoundedTextIO,
        DEFAULT_JSON_BYTES,
        DEFAULT_MAX_STDOUT_BYTES,
        TRUNCATION_NOTICE,
        bounded_json_text,
        emit_json,
    )
except ImportError:  # Supports direct script execution.
    from evidence_registry import sync_evidence_index_entry  # type: ignore
    from token_burn_guard import (  # type: ignore
        BoundedTextIO,
        DEFAULT_JSON_BYTES,
        DEFAULT_MAX_STDOUT_BYTES,
        TRUNCATION_NOTICE,
        bounded_json_text,
        emit_json,
    )


ROOT = Path(__file__).resolve().parents[1]
FULL_REPORT_PATH = ROOT / "generated" / "token_burn_guard_audit.json"
COMPACT_CERTIFICATE_PATH = ROOT / "data" / "evidence" / "token_burn_guard" / "certificate.json"
TOKEN_BURN_EVIDENCE_ID = "token_burn_guard"
TOKEN_BURN_EVIDENCE_ROOT = "data/evidence/token_burn_guard"
TOKEN_BURN_CERTIFICATE_STATUS = "TOKEN_BURN_GUARD_CERTIFIED"
ACTIVE_ROOTS = [ROOT / "src", ROOT]
ARCHIVAL_PARTS = {"source_bundles", "source_drops", "archived_roots"}
IGNORED_DIRS = {
    ".codex_deps",
    ".git",
    ".msys-tmp",
    ".mypy_cache",
    ".pacman-db",
    ".pytest_cache",
    ".replay_tmp",
    ".tools",
    ".venv",
    ".venv_four_level",
    "__pycache__",
    "generated",
    "ingress",
    "node_modules",
    "talagrand_python_handoff",
}
BOOTSTRAP_MARKER = "carrollian-token-burn-" "guard-bootstrap"
SHELL_BOOTSTRAP_MARKER = "carrollian-token-burn-" "guard-sh-bootstrap"
NON_PYTHON_SCRIPT_SUFFIXES = {".ps1", ".sh", ".bat", ".cmd", ".js", ".ts", ".mjs", ".cjs", ".r", ".R", ".jl", ".pl", ".rb"}
EXPECTED_ACTIVE_NON_PYTHON_SCRIPTS = {
    "data/evidence/ss_sat/scripts/external_evidence_gate/run_external_solvers.ps1",
    "data/evidence/ss_sat/scripts/external_evidence_gate/run_external_solvers.sh",
}
ARCHIVE_ROOT_PREFIXES = (
    "data/evidence/ss_sat/source_bundles/archived_roots/",
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    import hashlib

    return hashlib.sha256(canonical_json(obj)).hexdigest()


def python_files() -> list[Path]:
    files: list[Path] = []
    for root in (ROOT / "src", ROOT / "data"):
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            files.append(path)
    for path in ROOT.glob("*.py"):
        files.append(path)
    return sorted(set(files))


def is_archival(path: Path) -> bool:
    return bool(ARCHIVAL_PARTS.intersection(path.relative_to(ROOT).parts))


def is_ignored_or_transient(path: Path) -> bool:
    return bool(IGNORED_DIRS.intersection(path.relative_to(ROOT).parts))


def print_risk_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in python_files():
        text = load_text(path)
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            rows.append(
                {
                    "path": rel(path),
                    "line": exc.lineno,
                    "risk": "syntax_unparsed",
                    "archival": is_archival(path),
                }
            )
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node.func, "id", None) != "print":
                continue
            source = ast.get_source_segment(text, node) or ""
            if "json.dumps" in source:
                risk = "json_stdout"
            elif "report" in source or "certificate" in source or "cert" in source:
                risk = "report_or_certificate_stdout"
            elif len(source) > 160:
                risk = "long_print_call"
            else:
                continue
            rows.append(
                {
                    "path": rel(path),
                    "line": int(getattr(node, "lineno", 0) or 0),
                    "risk": risk,
                    "archival": is_archival(path),
                }
            )
    return rows


def subprocess_output_risk_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    risky_names = {"run", "Popen", "check_call"}
    for path in python_files():
        text = load_text(path)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (
                isinstance(func, ast.Attribute)
                and func.attr in risky_names
                and isinstance(func.value, ast.Name)
                and func.value.id == "subprocess"
            ):
                continue
            source = ast.get_source_segment(text, node) or ""
            keyword_names = {kw.arg for kw in node.keywords if kw.arg is not None}
            has_capture_or_redirect = (
                "capture_output" in keyword_names
                or "stdout" in keyword_names
                or "stderr" in keyword_names
            )
            if has_capture_or_redirect:
                continue
            rows.append(
                {
                    "path": rel(path),
                    "line": int(getattr(node, "lineno", 0) or 0),
                    "risk": "subprocess_stdout_stderr_inherits_parent",
                    "archival": is_archival(path),
                    "call": source[:200].replace("\n", " "),
                }
            )
    return rows


def non_python_script_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in NON_PYTHON_SCRIPT_SUFFIXES:
            continue
        if is_ignored_or_transient(path):
            continue
        files.append(path)
    return sorted(files)


def non_python_script_surface() -> dict[str, Any]:
    files = non_python_script_files()
    active = [path for path in files if not is_archival(path)]
    archival = [path for path in files if is_archival(path)]
    active_rel = [rel(path) for path in active]
    archival_shell_missing_guard = [
        rel(path)
        for path in archival
        if path.suffix == ".sh" and SHELL_BOOTSTRAP_MARKER not in load_text(path)
    ]
    unexpected = sorted(set(active_rel) - EXPECTED_ACTIVE_NON_PYTHON_SCRIPTS)
    missing_expected = sorted(EXPECTED_ACTIVE_NON_PYTHON_SCRIPTS - set(active_rel))
    redirect_checks: dict[str, bool] = {}
    for relpath in EXPECTED_ACTIVE_NON_PYTHON_SCRIPTS:
        path = ROOT / relpath
        if not path.exists():
            redirect_checks[relpath] = False
            continue
        text = load_text(path)
        if path.suffix == ".sh":
            redirect_checks[relpath] = all(
                marker in text
                for marker in (
                    '> "$OUT/${base}.cadical.stdout.txt" 2> "$OUT/${base}.cadical.stderr.txt"',
                    '> "$OUT/${base}.kissat.stdout.txt" 2> "$OUT/${base}.kissat.stderr.txt"',
                    '> "$OUT/${base}.minisat.stdout.txt" 2> "$OUT/${base}.minisat.stderr.txt"',
                )
            )
        elif path.suffix == ".ps1":
            redirect_checks[relpath] = all(
                marker in text
                for marker in (
                    '1> (Join-Path $Out "$base.cadical.stdout.txt") 2> (Join-Path $Out "$base.cadical.stderr.txt")',
                    '1> (Join-Path $Out "$base.kissat.stdout.txt") 2> (Join-Path $Out "$base.kissat.stderr.txt")',
                    '1> (Join-Path $Out "$base.minisat.stdout.txt") 2> (Join-Path $Out "$base.minisat.stderr.txt")',
                )
            )
    return {
        "active_count": len(active),
        "archival_count": len(archival),
        "active_scripts": active_rel,
        "archival_scripts": [rel(path) for path in archival],
        "archival_shell_scripts_missing_guard_count": len(archival_shell_missing_guard),
        "archival_shell_scripts_missing_guard": archival_shell_missing_guard[:24],
        "unexpected_active_scripts": unexpected,
        "missing_expected_active_scripts": missing_expected,
        "external_solver_stdout_stderr_redirected_to_files": redirect_checks,
    }


def archive_python_surface() -> dict[str, Any]:
    archive_entrypoints: list[str] = []
    missing_bootstrap: list[str] = []
    dirs_missing_sitecustomize: list[str] = []
    outside_expected_archive_roots: list[str] = []
    entrypoint_dirs: set[Path] = set()
    for path in python_files():
        if not is_archival(path):
            continue
        text = load_text(path)
        if "if __name__" not in text:
            continue
        relpath = rel(path)
        archive_entrypoints.append(relpath)
        entrypoint_dirs.add(path.parent)
        if BOOTSTRAP_MARKER not in text:
            missing_bootstrap.append(relpath)
        if not relpath.startswith(ARCHIVE_ROOT_PREFIXES):
            outside_expected_archive_roots.append(relpath)
    for directory in sorted(entrypoint_dirs):
        if not (directory / "sitecustomize.py").exists():
            dirs_missing_sitecustomize.append(rel(directory))
    return {
        "classification": "tracked_source_archive_not_supported_execution_surface",
        "archive_entrypoint_count": len(archive_entrypoints),
        "archive_entrypoints_missing_bootstrap_count": len(missing_bootstrap),
        "archive_entrypoints_missing_bootstrap_examples": missing_bootstrap[:12],
        "archive_entrypoint_dirs_missing_sitecustomize_count": len(dirs_missing_sitecustomize),
        "archive_entrypoint_dirs_missing_sitecustomize": dirs_missing_sitecustomize[:12],
        "outside_expected_archive_roots_count": len(outside_expected_archive_roots),
        "outside_expected_archive_roots": outside_expected_archive_roots[:12],
    }


def ignored_transient_script_surface() -> dict[str, Any]:
    counts: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in (NON_PYTHON_SCRIPT_SUFFIXES | {".py"}):
            continue
        if not is_ignored_or_transient(path):
            continue
        matched = sorted(IGNORED_DIRS.intersection(path.relative_to(ROOT).parts))
        key = matched[0] if matched else "unknown"
        counts[key] = counts.get(key, 0) + 1
        examples.setdefault(key, [])
        if len(examples[key]) < 4:
            examples[key].append(rel(path))
    return {
        "classification": "ignored_local_or_generated_surface_not_repo_execution_surface",
        "ignored_script_count": sum(counts.values()),
        "counts_by_ignored_part": dict(sorted(counts.items())),
        "examples_by_ignored_part": {key: examples[key] for key in sorted(examples)},
    }


def active_entrypoint_files() -> list[Path]:
    return [
        path
        for path in python_files()
        if not is_archival(path)
        and "if __name__" in load_text(path)
        and path.name != "sitecustomize.py"
    ]


def entrypoint_dirs_missing_sitecustomize() -> list[str]:
    dirs = sorted(path.parent for path in active_entrypoint_files())
    missing = []
    for directory in sorted(set(dirs)):
        if not (directory / "sitecustomize.py").exists():
            missing.append(rel(directory))
    return missing


def entrypoints_missing_bootstrap() -> list[str]:
    missing = []
    for path in active_entrypoint_files():
        if BOOTSTRAP_MARKER not in load_text(path):
            missing.append(rel(path))
    return missing


def stream_guard_selftest() -> dict[str, Any]:
    sink = io.StringIO()
    guarded = BoundedTextIO(sink, limit_bytes=1024, line_limit_bytes=256)
    original_len = guarded.write("x" * 5000)
    guarded.flush()
    output = sink.getvalue()
    return {
        "original_write_length": original_len,
        "output_length": len(output),
        "contains_truncation_notice": TRUNCATION_NOTICE.strip() in output,
        "line_truncated": "line truncated" in output,
        "within_expected_bound": len(output.encode("utf-8")) <= 1024 + len(TRUNCATION_NOTICE) + 128,
    }


def direct_file_execution_selftest() -> dict[str, Any]:
    env = dict(os.environ)
    env["CARROLLIAN_TOKEN_BURN_MAX_STDOUT"] = "2048"
    env["CARROLLIAN_TOKEN_BURN_MAX_STDERR"] = "2048"
    env["CARROLLIAN_TOKEN_BURN_MAX_LINE"] = "512"
    env["CARROLLIAN_TOKEN_BURN_GUARD_PROBE"] = "1"
    env.pop("CARROLLIAN_TOKEN_BURN_ALLOW_FULL_STDOUT", None)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "src" / "certify_token_burn_guard.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
        timeout=15,
        check=False,
    )
    stdout_bytes = len(proc.stdout.encode("utf-8", errors="replace"))
    stderr_bytes = len(proc.stderr.encode("utf-8", errors="replace"))
    return {
        "returncode": proc.returncode,
        "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
        "line_truncated": "line truncated by carrollian-token-burn-guard" in proc.stdout,
        "stream_truncated": TRUNCATION_NOTICE.strip() in proc.stdout,
        "within_probe_bound": stdout_bytes <= 2048 + len(TRUNCATION_NOTICE) + 256,
    }


def python_startup_autoload_probe() -> dict[str, Any]:
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; print('sitecustomize_loaded=' + str('sitecustomize' in sys.modules)); print('stdout_type=' + type(sys.stdout).__name__)",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    stdout = proc.stdout.strip().splitlines()
    return {
        "returncode": proc.returncode,
        "stdout": stdout,
        "repo_local_sitecustomize_auto_loaded": any(line == "sitecustomize_loaded=True" for line in stdout),
        "stdout_guard_auto_installed": any(line == "stdout_type=BoundedTextIO" for line in stdout),
    }


def bounded_json_selftest() -> dict[str, Any]:
    payload = {
        "status": "PASS",
        "errors": [],
        "large": ["x" * 2000 for _ in range(200)],
    }
    text = bounded_json_text(payload, pretty=True, max_bytes=DEFAULT_JSON_BYTES)
    parsed = json.loads(text)
    return {
        "emitted_bytes": len(text.encode("utf-8")),
        "within_default_json_bound": len(text.encode("utf-8")) <= DEFAULT_JSON_BYTES,
        "emits_valid_json": isinstance(parsed, dict),
        "summary_emitted": parsed.get("output_guard", {}).get("summary_emitted") is True,
    }


def validate_token_burn_guard() -> dict[str, Any]:
    sitecustomize_root = ROOT / "sitecustomize.py"
    sitecustomize_src = ROOT / "src" / "sitecustomize.py"
    token_guard = ROOT / "src" / "token_burn_guard.py"
    risk_rows = print_risk_rows()
    subprocess_risks = subprocess_output_risk_rows()
    active_risks = [row for row in risk_rows if not row["archival"]]
    archival_risks = [row for row in risk_rows if row["archival"]]
    active_subprocess_risks = [row for row in subprocess_risks if not row["archival"]]
    archival_subprocess_risks = [row for row in subprocess_risks if row["archival"]]
    dirs_missing_guard = entrypoint_dirs_missing_sitecustomize()
    entrypoints_missing_guard_bootstrap = entrypoints_missing_bootstrap()
    stream_selftest = stream_guard_selftest()
    json_selftest = bounded_json_selftest()
    direct_file_selftest = direct_file_execution_selftest()
    startup_probe = python_startup_autoload_probe()
    non_python_surface = non_python_script_surface()
    archive_surface = archive_python_surface()
    ignored_surface = ignored_transient_script_surface()

    command_entrypoints = {
        "src/verify.py": "emit_json(" in load_text(ROOT / "src" / "verify.py"),
        "src/commands/certify.py": "emit_json(" in load_text(ROOT / "src" / "commands" / "certify.py"),
        "src/commands/construct.py": "emit_json(" in load_text(ROOT / "src" / "commands" / "construct.py"),
    }
    checks = {
        "root_sitecustomize_installs_guard": sitecustomize_root.exists()
        and "token_burn_guard" in load_text(sitecustomize_root),
        "src_sitecustomize_installs_guard": sitecustomize_src.exists()
        and "token_burn_guard" in load_text(sitecustomize_src),
        "token_guard_module_exists": token_guard.exists(),
        "default_stdout_cap_is_finite": DEFAULT_MAX_STDOUT_BYTES <= 8192,
        "stream_guard_selftest_passed": stream_selftest["within_expected_bound"]
        and (stream_selftest["line_truncated"] or stream_selftest["contains_truncation_notice"]),
        "bounded_json_selftest_passed": all(json_selftest.values()),
        "direct_file_execution_guard_selftest_passed": direct_file_selftest["returncode"] == 0
        and direct_file_selftest["within_probe_bound"]
        and (direct_file_selftest["line_truncated"] or direct_file_selftest["stream_truncated"]),
        "primary_command_entrypoints_use_bounded_json": all(command_entrypoints.values()),
        "active_entrypoint_dirs_have_sitecustomize": not dirs_missing_guard,
        "active_entrypoints_import_guard_bootstrap": not entrypoints_missing_guard_bootstrap,
        "active_subprocess_output_is_captured_or_redirected": not active_subprocess_risks,
        "non_python_script_surfaces_reviewed": not non_python_surface["unexpected_active_scripts"]
        and not non_python_surface["missing_expected_active_scripts"]
        and all(non_python_surface["external_solver_stdout_stderr_redirected_to_files"].values())
        and non_python_surface["archival_shell_scripts_missing_guard_count"] == 0,
        "archive_surfaces_are_explicitly_classified": archive_surface["outside_expected_archive_roots_count"] == 0
        and archive_surface["archive_entrypoints_missing_bootstrap_count"] == 0
        and archive_surface["archive_entrypoint_dirs_missing_sitecustomize_count"] == 0,
        "ignored_transient_surfaces_are_explicitly_classified": ignored_surface["ignored_script_count"] >= 0,
    }
    return {
        "schema": "d20.token_burn_guard.audit@1",
        "status": "TOKEN_BURN_GUARD_PASS" if all(checks.values()) else "TOKEN_BURN_GUARD_NEEDS_REVIEW",
        "checks": checks,
        "stream_guard_selftest": stream_selftest,
        "bounded_json_selftest": json_selftest,
        "direct_file_execution_selftest": direct_file_selftest,
        "python_startup_autoload_probe": startup_probe,
        "command_entrypoints": command_entrypoints,
        "stdout_risk_inventory": {
            "active_risk_count": len(active_risks),
            "archival_risk_count": len(archival_risks),
            "active_examples": active_risks[:24],
            "archival_examples": archival_risks[:12],
        },
        "subprocess_output_risk_inventory": {
            "active_risk_count": len(active_subprocess_risks),
            "archival_risk_count": len(archival_subprocess_risks),
            "active_examples": active_subprocess_risks[:24],
            "archival_examples": archival_subprocess_risks[:12],
        },
        "non_python_script_surface": non_python_surface,
        "archive_python_surface": archive_surface,
        "ignored_transient_script_surface": ignored_surface,
        "direct_script_coverage": {
            "active_entrypoint_count": len(active_entrypoint_files()),
            "active_entrypoint_dirs_missing_sitecustomize_count": len(dirs_missing_guard),
            "active_entrypoint_dirs_missing_sitecustomize": dirs_missing_guard[:48],
            "active_entrypoints_missing_bootstrap_count": len(entrypoints_missing_guard_bootstrap),
            "active_entrypoints_missing_bootstrap": entrypoints_missing_guard_bootstrap[:48],
        },
        "policy": {
            "stdout_default_cap_bytes": DEFAULT_MAX_STDOUT_BYTES,
            "bounded_json_default_cap_bytes": DEFAULT_JSON_BYTES,
            "disable_env": "CARROLLIAN_TOKEN_BURN_GUARD=0",
            "full_stdout_escape_hatch": "CARROLLIAN_TOKEN_BURN_ALLOW_FULL_STDOUT=1",
        },
    }


def compact_certificate(result: dict[str, Any]) -> dict[str, Any]:
    certificate = {
        "schema": "d20.token_burn_guard.certificate@1",
        "status": "TOKEN_BURN_GUARD_CERTIFIED" if result.get("status") == "TOKEN_BURN_GUARD_PASS" else "TOKEN_BURN_GUARD_NEEDS_REVIEW",
        "audit_status": result.get("status"),
        "checks": result.get("checks", {}),
        "coverage": {
            "active_python_entrypoint_count": result.get("direct_script_coverage", {}).get("active_entrypoint_count"),
            "active_python_entrypoints_missing_bootstrap": result.get("direct_script_coverage", {}).get("active_entrypoints_missing_bootstrap_count"),
            "active_python_entrypoint_dirs_missing_sitecustomize": result.get("direct_script_coverage", {}).get("active_entrypoint_dirs_missing_sitecustomize_count"),
            "archive_python_entrypoint_count": result.get("archive_python_surface", {}).get("archive_entrypoint_count"),
            "archive_python_entrypoints_missing_bootstrap": result.get("archive_python_surface", {}).get("archive_entrypoints_missing_bootstrap_count"),
            "archive_python_entrypoint_dirs_missing_sitecustomize": result.get("archive_python_surface", {}).get("archive_entrypoint_dirs_missing_sitecustomize_count"),
            "active_subprocess_output_risk_count": result.get("subprocess_output_risk_inventory", {}).get("active_risk_count"),
            "active_non_python_script_count": result.get("non_python_script_surface", {}).get("active_count"),
            "archival_shell_scripts_missing_guard": result.get("non_python_script_surface", {}).get("archival_shell_scripts_missing_guard_count"),
            "ignored_transient_script_count": result.get("ignored_transient_script_surface", {}).get("ignored_script_count"),
        },
        "policy": {
            "default_stdout_cap_bytes": result.get("policy", {}).get("stdout_default_cap_bytes"),
            "bounded_json_default_cap_bytes": result.get("policy", {}).get("bounded_json_default_cap_bytes"),
            "python_entrypoint_requirement": "Every active direct Python entrypoint must import the token-burn guard bootstrap marker.",
            "new_python_entrypoint_gate": "certify.py audit fails when a new active __main__ file lacks the bootstrap or its directory lacks sitecustomize.py.",
            "powershell_policy": "Only explicitly reviewed active PowerShell scripts are allowed; future active .ps1 files fail the token-burn audit until added to the reviewed allowlist or wrapped.",
            "non_python_policy": "Active non-Python scripts are allowlisted and must redirect high-volume external tool output to files.",
            "archive_policy": "Tracked archive Python entrypoints and tracked archive shell scripts are guarded, but source archives remain evidence, not supported execution APIs.",
            "manual_shell_boundary": "Arbitrary user shell commands such as Get-Content hugefile or python -c print(...) are outside repo-defined runner control.",
            "disable_env": result.get("policy", {}).get("disable_env"),
            "full_stdout_escape_hatch": result.get("policy", {}).get("full_stdout_escape_hatch"),
        },
        "startup_probe": result.get("python_startup_autoload_probe", {}),
        "full_generated_report": FULL_REPORT_PATH.relative_to(ROOT).as_posix(),
    }
    certificate["certificate_sha256"] = sha_json({key: value for key, value in certificate.items() if key != "certificate_sha256"})
    return certificate


def sync_token_burn_evidence_index() -> dict[str, Any]:
    return sync_evidence_index_entry(
        evidence_id=TOKEN_BURN_EVIDENCE_ID,
        root=TOKEN_BURN_EVIDENCE_ROOT,
        entrypoint=COMPACT_CERTIFICATE_PATH,
        status=TOKEN_BURN_CERTIFICATE_STATUS,
    )


def write_token_burn_guard_artifacts(result: dict[str, Any]) -> dict[str, Any]:
    FULL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    FULL_REPORT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    certificate = compact_certificate(result)
    COMPACT_CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    COMPACT_CERTIFICATE_PATH.write_text(json.dumps(certificate, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    evidence_index = sync_token_burn_evidence_index()
    return {
        "full_report": rel(FULL_REPORT_PATH),
        "compact_certificate": rel(COMPACT_CERTIFICATE_PATH),
        "compact_certificate_sha256": certificate["certificate_sha256"],
        **evidence_index,
    }


if __name__ == "__main__":
    if os.environ.get("CARROLLIAN_TOKEN_BURN_GUARD_PROBE") == "1":
        print("x" * 5000)
        raise SystemExit(0)
    result = validate_token_burn_guard()
    result["artifacts"] = write_token_burn_guard_artifacts(result)
    emit_json(result, pretty=True)
    if result["status"] != "TOKEN_BURN_GUARD_PASS":
        raise SystemExit(1)
