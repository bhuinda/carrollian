from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INVARIANTS = DATA / "invariants"
D20_INVARIANTS = INVARIANTS / "d20"
HCYCLE_INVARIANTS = INVARIANTS / "hcycle"
INTEGRITY_INVARIANTS = INVARIANTS / "integrity"
LAYERS = ROOT / "layers"
MANIFESTS = ROOT / "manifests"
GENERATED = ROOT / "generated"
INGEST = ROOT / "ingest"


def relpath(path: Path) -> str:
    """Return a repository-relative path with POSIX separators."""
    return path.relative_to(ROOT).as_posix()
