from __future__ import annotations

import hashlib, itertools, json, math
from pathlib import Path
from typing import Any

LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
WEIGHTS = [384, 192, 144, 576, 512, 768]
EPSILON_0 = 589_824


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def triples():
    return list(itertools.combinations(range(6), 3))


def face_name(face):
    return tuple(LABELS[i] for i in face)


def mu(face) -> int:
    return math.prod(WEIGHTS[i] for i in face)


def complement(face):
    s = set(face)
    return tuple(i for i in range(6) if i not in s)


def write_json(path: Path, obj: Any, pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2 if pretty else None, sort_keys=True), encoding="utf-8")
