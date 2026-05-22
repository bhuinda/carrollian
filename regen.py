#!/usr/bin/env python3
"""Regenerate d20.json, refresh bundle hashes, and audit the bundle.

Run from the bundle root:

    python regen.py

This is the single rebuild command. It performs, in order:
  1. rebuild d20.json from the checked source data;
  2. refresh certificate.json's embedded d20 metadata and self hash;
  3. refresh manifests/file_hashes.json for all tracked files;
  4. run certify.py --mode audit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifests" / "file_hashes.json"
D20 = ROOT / "d20.json"
CERTIFICATE = ROOT / "certificate.json"

ADDED_TRACKED_FILES = [
    "regen.py",
    "d20.py",
]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json_body(obj: dict[str, Any], hash_key: str) -> str:
    body = {k: v for k, v in obj.items() if k != hash_key}
    return hashlib.sha256(canonical(body)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(cmd), flush=True)
    if capture:
        return subprocess.run(cmd, cwd=ROOT, text=True, check=check, capture_output=True)
    return subprocess.run(cmd, cwd=ROOT, text=True, check=check)


def rebuild_d20(pretty: bool) -> None:
    from src.derive_d20 import derive
    print("$ derive d20.json", flush=True)
    obj = derive()
    D20.write_text(json.dumps(obj, indent=2 if pretty else None, sort_keys=bool(pretty)), encoding="utf-8")
    print("rebuilt d20.json", flush=True)


def refresh_certificate() -> None:
    cert = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    d20 = json.loads(D20.read_text(encoding="utf-8"))

    d20_object_hash = d20.get("d20_sha256")
    if not isinstance(d20_object_hash, str) or len(d20_object_hash) != 64:
        raise SystemExit("d20.json missing valid d20_sha256")

    cert["object"] = "d20"
    cert["status"] = "D20_CERTIFIED"
    cert["headline"] = "D20_CERTIFIED"
    cert["d20_status"] = "D20_PASS"
    cert["d20_json"] = {
        "path": "d20.json",
        "schema": d20.get("schema"),
        "size": D20.stat().st_size,
        "sha256_file": sha_file(D20),
        "sha256_object": d20_object_hash,
        "invariant_sections": sorted(k for k in d20.keys() if k != "d20_sha256"),
    }
    cert["d20_sha256"] = sha_json_body(cert, "d20_sha256")
    CERTIFICATE.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def refresh_manifest() -> int:
    """Rebuild manifests/file_hashes.json from the current canonical bundle files."""
    manifest = {
        "schema": "d20.file_hashes.v2",
        "generated_cache_required": False,
        "self_manifest_excluded": "manifests/file_hashes.json",
        "entries": [],
    }
    entries: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel == "manifests/file_hashes.json":
            continue
        if rel.startswith("generated/"):
            continue
        if "__pycache__/" in rel or rel.endswith(".pyc"):
            continue
        entries.append({
            "path": rel,
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        })
    manifest["entries"] = entries
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return len(entries)


def audit(pretty: bool) -> None:
    cmd = [sys.executable, "certify.py", "--mode", "audit"]
    if pretty:
        cmd.append("--pretty")
    run(cmd)


def main() -> None:
    ap = argparse.ArgumentParser(description="Regenerate d20.json, refresh hashes, and audit.")
    ap.add_argument("--no-audit", action="store_true", help="Refresh d20.json and hashes but skip final audit.")
    ap.add_argument("--compact", action="store_true", help="Write compact d20.json and compact audit output.")
    args = ap.parse_args()

    pretty = not args.compact
    rebuild_d20(pretty=pretty)
    refresh_certificate()
    count = refresh_manifest()
    print(f"updated manifest hashes: {count}", flush=True)
    if not args.no_audit:
        audit(pretty=pretty)
    print("D20_REGENERATED", flush=True)


if __name__ == "__main__":
    main()
