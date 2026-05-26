from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import json
from pathlib import Path
from typing import Any

from .common import ROOT, relative_path, repo_rel, sha256_file, sha256_json, write_json


CORE_LOCK_SCHEMA = "holotopy.core_lock"
CORE_VERSION = "0.1.0"

BASE_CORE_FILES = (
    "certificate.json",
    "d20.json",
    "data/raw/constants.json",
    "data/raw/index.json",
    "data/raw/Halloween.npz",
    "data/raw/quotients.npz",
    "data/raw/simple_branching_matrices.npz",
    "data/quotient/terminal_quotient_selector.json",
    "src/compiler/core/sigma_q12.json",
    "data/invariants/d20/d20_d6_selector_derivation.json",
)

COMPILER_FILE_SUFFIXES = {".py", ".ebnf", ".json"}


def compiler_files(root: Path = ROOT) -> list[str]:
    base = root / "src" / "compiler"
    if not base.exists():
        return []
    files: list[str] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix in COMPILER_FILE_SUFFIXES:
            files.append(repo_rel(path, root=root))
    return files


def default_core_files(root: Path = ROOT) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for rel in [*BASE_CORE_FILES, *compiler_files(root)]:
        if rel not in seen:
            out.append(rel)
            seen.add(rel)
    return out


def build_core_lock(root: Path = ROOT, *, version: str = CORE_VERSION) -> dict[str, Any]:
    files: dict[str, str] = {}
    missing_files: list[str] = []
    for rel in default_core_files(root):
        path = root / rel
        if path.exists() and path.is_file():
            files[rel] = sha256_file(path)
        else:
            missing_files.append(rel)

    body = {
        "schema": CORE_LOCK_SCHEMA,
        "version": version,
        "files": files,
        "missing_files": missing_files,
    }
    body["core_hash"] = sha256_json(body)
    body["status"] = "LOCKED" if not missing_files else "INCOMPLETE"
    return body


def load_or_build_core_lock(
    root: Path = ROOT,
    *,
    core_lock_path: Path | None = None,
    write: bool = False,
) -> tuple[dict[str, Any], Path | None, bool]:
    path = core_lock_path or (root / "CORE.lock.json")
    if not path.is_absolute():
        path = root / path
    if path.exists() and not write:
        return json.loads(path.read_text(encoding="utf-8")), path, True
    lock = build_core_lock(root)
    if write:
        write_json(path, lock)
        return lock, path, True
    return lock, path, False


def core_lock_ref(path: Path | None, base: Path) -> str | None:
    if path is None:
        return None
    return relative_path(path, base)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the public scene compiler core lock.")
    parser.add_argument("--out", default="CORE.lock.json")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    lock = build_core_lock(ROOT)
    write_json(out, lock, pretty=args.pretty)
    print(lock["core_hash"])


if __name__ == "__main__":
    main()
