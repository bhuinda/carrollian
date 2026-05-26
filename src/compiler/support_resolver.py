from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .common import ROOT


SUPPORT_LEDGER_SCHEMA = "holotopy.support_ledger"

KEYWORD_SUPPORT: tuple[tuple[re.Pattern[str], tuple[str, ...]], ...] = (
    (
        re.compile(r"\b(A985|985|tensor|orbitals?|structure constants?)\b", re.IGNORECASE),
        ("data/raw/constants.json", "data/raw/Halloween.npz"),
    ),
    (
        re.compile(r"\b(A42|A12|A236|quotient|quotients?|readout)\b", re.IGNORECASE),
        ("data/raw/quotients.npz", "data/raw/simple_branching_matrices.npz", "data/quotient/terminal_quotient_selector.json"),
    ),
    (
        re.compile(r"\b(D20|boundary|Lambda|H6|faces?|public)\b", re.IGNORECASE),
        ("data/invariants/d20/d20_d6_selector_derivation.json",),
    ),
    (
        re.compile(r"\b(certificate|hash|lock|manifest|replay|verify|validation)\b", re.IGNORECASE),
        ("certificate.json", "manifests/file_hashes.json"),
    ),
    (
        re.compile(r"\b(scene|compiler|capsule|claim|obligation|residue|support)\b", re.IGNORECASE),
        ("src/compiler/grammar.ebnf", "src/compiler/scene_builder.py"),
    ),
)


def _existing(paths: tuple[str, ...], root: Path) -> list[str]:
    return [path for path in paths if (root / path).exists()]


def resolve_claim_support(
    claims: list[dict[str, Any]],
    *,
    root: Path = ROOT,
    core_lock_ref: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    claim_support: dict[str, Any] = {}
    resolved_claims: list[dict[str, Any]] = []
    for claim in claims:
        files: list[str] = ["00_request.raw.json"]
        text = str(claim.get("text", ""))
        for pattern, support_paths in KEYWORD_SUPPORT:
            if pattern.search(text):
                files.extend(_existing(support_paths, root))
        if core_lock_ref:
            files.append(core_lock_ref)
        files = sorted(dict.fromkeys(files))
        claim_id = str(claim.get("claim_id"))
        claim_support[claim_id] = {"files": files, "citations": []}
        updated = dict(claim)
        updated["support"] = files
        resolved_claims.append(updated)
    return resolved_claims, {"schema": SUPPORT_LEDGER_SCHEMA, "claim_support": claim_support}
