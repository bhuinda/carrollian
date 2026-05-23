#!/usr/bin/env python3
"""One-command d20 regeneration and certification.

Normal use:
    python d20.py

This rebuilds d20.json, refreshes hashes, and audits the bundle.
Pass any certify.py arguments after this command if needed.
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
args = sys.argv[1:] or ["--mode", "rebuild"]
cmd = [sys.executable, str(ROOT / "certify.py"), *args]
raise SystemExit(subprocess.call(cmd, cwd=ROOT))
