#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime import ensure_numpy_runtime

ensure_numpy_runtime(ROOT, __file__)

from src.commands.certify import main


args = sys.argv[1:] or ["--mode", "rebuild"]
sys.argv = [sys.argv[0], *args]
main()
