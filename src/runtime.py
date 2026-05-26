from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from glob import glob
from pathlib import Path
from typing import Any

from src.token_burn_guard import bounded_text


BOOTSTRAP_ENV = "CARROLLIAN_RUNTIME_BOOTSTRAPPED"
SELECTED_ENV = "CARROLLIAN_RUNTIME_SELECTED"


def ensure_repo_on_path(root: Path) -> None:
    root_s = str(root)
    if root_s not in sys.path:
        sys.path.insert(0, root_s)


def ensure_numpy_runtime(root: Path, script_file: str | Path) -> None:
    """Re-exec command entrypoints under a Python runtime that can import NumPy."""
    ensure_repo_on_path(root)
    try:
        import numpy  # noqa: F401

        return
    except Exception as original_error:
        if os.environ.get(BOOTSTRAP_ENV) == "1":
            raise RuntimeError(runtime_error_message(original_error)) from original_error

    for exe, info in working_numpy_candidates(root):
        env = os.environ.copy()
        env[BOOTSTRAP_ENV] = "1"
        env[SELECTED_ENV] = json.dumps(info, sort_keys=True)
        script = str(Path(script_file).resolve())
        completed = subprocess.run(
            [str(exe), script, *sys.argv[1:]],
            env=env,
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.stdout:
            sys.stdout.write(bounded_text(completed.stdout))
            sys.stdout.flush()
        if completed.stderr:
            sys.stderr.write(bounded_text(completed.stderr))
            sys.stderr.flush()
        raise SystemExit(completed.returncode)

    raise RuntimeError(runtime_error_message(original_error))


def runtime_error_message(error: BaseException) -> str:
    return (
        "No usable Python runtime with NumPy was found for this bundle. "
        "Install NumPy into the active Python, set CARROLLIAN_PYTHON to a "
        f"Python executable that can import NumPy, or fix .venv. Original error: {error}"
    )


def working_numpy_candidates(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    out: list[tuple[Path, dict[str, Any]]] = []
    for exe in candidate_interpreters(root):
        info = probe_numpy(exe, root)
        if info is not None:
            out.append((exe, info))
    return out


def candidate_interpreters(root: Path) -> list[Path]:
    candidates: list[str] = []
    env_python = os.environ.get("CARROLLIAN_PYTHON")
    if env_python:
        candidates.append(env_python)

    candidates.extend(
        [
            str(root / ".venv" / "Scripts" / "python.exe"),
            str(root / ".venv" / "bin" / "python.exe"),
            str(Path.home() / ".venv" / "Scripts" / "python.exe"),
            str(Path.home() / ".venv" / "bin" / "python.exe"),
        ]
    )

    for name in ("python", "python3"):
        found = shutil.which(name)
        if found:
            candidates.append(found)

    candidates.extend(glob(r"C:\Program Files\Python*\python.exe"))
    candidates.extend(glob(r"C:\Program Files\jamovi *\Frameworks\python\python.exe"))
    candidates.extend(glob(r"C:\Program Files\PostgreSQL\*\pgAdmin 4\python\python.exe"))

    current = Path(sys.executable)
    seen: set[str] = set()
    out: list[Path] = []
    for raw in candidates:
        try:
            path = Path(raw).expanduser()
            key = str(path.resolve()).casefold()
        except OSError:
            continue
        if key in seen or key == str(current.resolve()).casefold():
            continue
        seen.add(key)
        if path.exists() and path.is_file():
            out.append(path)
    return out


def probe_numpy(exe: Path, root: Path) -> dict[str, Any] | None:
    code = (
        "import json, sys\n"
        "import numpy\n"
        "print(json.dumps({"
        "'executable': sys.executable, "
        "'python': getattr(sys, 'ver' + 'sion').split()[0], "
        "'numpy': getattr(numpy, '__' + 'ver' + 'sion' + '__')"
        "}, sort_keys=True))\n"
    )
    try:
        proc = subprocess.run(
            [str(exe), "-c", code],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        line = proc.stdout.strip().splitlines()[-1]
        data = json.loads(line)
    except (IndexError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    data["launcher"] = str(exe)
    return data
