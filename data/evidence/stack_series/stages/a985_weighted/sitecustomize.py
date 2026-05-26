from __future__ import annotations

import sys
from pathlib import Path

for parent in Path(__file__).resolve().parents:
    if (parent / "src" / "token_burn_guard.py").exists():
        sys.path.insert(0, str(parent))
        from src.token_burn_guard import install

        install()
        break
