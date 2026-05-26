from __future__ import annotations

from pathlib import Path
from typing import Any

from .algebra_residue import extract_product_terms
from .common import ROOT, read_json, repo_rel


RELATION_COUNT = 985


def _resolve_path(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def support_coordinate_file_ref(path: Path, *, root: Path = ROOT) -> str:
    resolved = _resolve_path(path, root)
    try:
        return repo_rel(resolved, root=root)
    except ValueError:
        return str(resolved)


def _coerce_coordinate(entry: Any, *, claim_id: str | None, source: str, index: int) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError(f"support coordinate {source}[{index}] must be an object")
    resolved_claim_id = str(entry.get("claim_id") or claim_id or "")
    if not resolved_claim_id:
        raise ValueError(f"support coordinate {source}[{index}] is missing claim_id")
    if "alpha" not in entry or "beta" not in entry:
        raise ValueError(f"support coordinate {source}[{index}] is missing alpha or beta")
    alpha = int(entry["alpha"])
    beta = int(entry["beta"])
    term: dict[str, Any] = {
        "term_id": "",
        "source": "support_coordinates_file",
        "claim_id": resolved_claim_id,
        "alpha": alpha,
        "beta": beta,
        "valid": 0 <= alpha < RELATION_COUNT and 0 <= beta < RELATION_COUNT,
        "syntax": f"{source}[{index}]: alpha={alpha}, beta={beta}",
        "file": source,
    }
    if entry.get("label"):
        term["label"] = str(entry["label"])
    return term


def validate_support_coordinate_payload(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["support coordinates payload must be an object"]

    claim_map = payload.get("claims", {})
    coordinates = payload.get("coordinates", [])
    if not claim_map and not coordinates:
        errors.append("support coordinates must define claims or coordinates")

    def check_entry(entry: Any, source: str, *, inherited_claim_id: str | None = None) -> None:
        if not isinstance(entry, dict):
            errors.append(f"{source} must be an object")
            return
        claim_id = entry.get("claim_id") or inherited_claim_id
        if not claim_id:
            errors.append(f"{source} is missing claim_id")
        for field in ("alpha", "beta"):
            value = entry.get(field)
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"{source}.{field} must be an integer")
            elif value < 0 or value >= RELATION_COUNT:
                errors.append(f"{source}.{field} is outside 0..{RELATION_COUNT - 1}")

    if claim_map:
        if not isinstance(claim_map, dict):
            errors.append("support coordinates claims field must be an object")
        else:
            for claim_id, entries in claim_map.items():
                if isinstance(entries, dict):
                    entries = [entries]
                if not isinstance(entries, list):
                    errors.append(f"support coordinates for {claim_id} must be an object or array")
                    continue
                for index, entry in enumerate(entries):
                    check_entry(entry, f"claims.{claim_id}[{index}]", inherited_claim_id=str(claim_id))

    if coordinates:
        if not isinstance(coordinates, list):
            errors.append("support coordinates coordinates field must be an array")
        else:
            for index, entry in enumerate(coordinates):
                check_entry(entry, f"coordinates[{index}]")

    return errors


def load_support_coordinate_terms(path: Path | None, *, root: Path = ROOT) -> list[dict[str, Any]]:
    if path is None:
        return []
    resolved = _resolve_path(path, root)
    payload = read_json(resolved)
    errors = validate_support_coordinate_payload(payload)
    if errors:
        raise ValueError("; ".join(errors))
    source = support_coordinate_file_ref(resolved, root=root)
    terms: list[dict[str, Any]] = []

    claim_map = payload.get("claims", {}) if isinstance(payload, dict) else {}
    if claim_map:
        if not isinstance(claim_map, dict):
            raise ValueError("support coordinates claims field must be an object")
        for claim_id, entries in claim_map.items():
            if isinstance(entries, dict):
                entries = [entries]
            if not isinstance(entries, list):
                raise ValueError(f"support coordinates for {claim_id} must be an object or array")
            for index, entry in enumerate(entries):
                terms.append(_coerce_coordinate(entry, claim_id=str(claim_id), source=source, index=index))

    coordinates = payload.get("coordinates", []) if isinstance(payload, dict) else []
    if coordinates:
        if not isinstance(coordinates, list):
            raise ValueError("support coordinates coordinates field must be an array")
        for index, entry in enumerate(coordinates):
            terms.append(_coerce_coordinate(entry, claim_id=None, source=source, index=index))

    return terms


def _renumber(terms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, term in enumerate(terms, start=1):
        updated = dict(term)
        updated["term_id"] = f"term_{index:03d}"
        out.append(updated)
    return out


def collect_product_terms(
    *,
    request_text: str,
    answer_text: str,
    claims: list[dict[str, Any]],
    support_coordinates_file: Path | None = None,
    root: Path = ROOT,
) -> list[dict[str, Any]]:
    coordinate_terms = load_support_coordinate_terms(support_coordinates_file, root=root)
    claim_terms: list[dict[str, Any]] = []
    for claim in claims:
        claim_id = str(claim.get("claim_id"))
        claim_terms.extend(
            extract_product_terms(
                {"claim": str(claim.get("text", ""))},
                relation_count=RELATION_COUNT,
                claim_id=claim_id,
            )
        )

    global_terms = extract_product_terms(
        {"request": request_text, "answer": answer_text},
        relation_count=RELATION_COUNT,
    )

    selected: list[dict[str, Any]] = []
    seen_claim_terms: set[tuple[str, int, int]] = set()
    linked_pairs: set[tuple[int, int]] = set()
    for term in [*coordinate_terms, *claim_terms]:
        claim_id = str(term.get("claim_id", ""))
        alpha = int(term["alpha"])
        beta = int(term["beta"])
        key = (claim_id, alpha, beta)
        if key in seen_claim_terms:
            continue
        seen_claim_terms.add(key)
        linked_pairs.add((alpha, beta))
        selected.append(term)

    seen_global: set[tuple[int, int]] = set()
    for term in global_terms:
        alpha = int(term["alpha"])
        beta = int(term["beta"])
        key = (alpha, beta)
        if key in linked_pairs or key in seen_global:
            continue
        seen_global.add(key)
        selected.append(term)

    return _renumber(selected)


def attach_product_terms_to_support(
    claims: list[dict[str, Any]],
    support_ledger: dict[str, Any],
    product_terms: list[dict[str, Any]],
    *,
    support_coordinates_file: Path | None = None,
    root: Path = ROOT,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_claim: dict[str, list[dict[str, Any]]] = {}
    for term in product_terms:
        claim_id = term.get("claim_id")
        if claim_id:
            by_claim.setdefault(str(claim_id), []).append(
                {
                    "term_id": term.get("term_id"),
                    "alpha": term.get("alpha"),
                    "beta": term.get("beta"),
                    "source": term.get("source"),
                    "file": term.get("file"),
                    "valid": term.get("valid"),
                }
            )

    file_ref = support_coordinate_file_ref(support_coordinates_file, root=root) if support_coordinates_file else None
    updated_claims: list[dict[str, Any]] = []
    updated_ledger = dict(support_ledger)
    updated_claim_support = {str(k): dict(v) for k, v in support_ledger.get("claim_support", {}).items()}
    for claim in claims:
        claim_id = str(claim.get("claim_id"))
        coordinates = by_claim.get(claim_id, [])
        entry = updated_claim_support.setdefault(claim_id, {"files": [], "citations": []})
        if coordinates:
            entry["coordinates"] = coordinates
            if file_ref:
                files = list(entry.get("files", []))
                if file_ref not in files:
                    files.append(file_ref)
                entry["files"] = sorted(files)
        updated = dict(claim)
        if coordinates:
            updated["support_coordinates"] = coordinates
            updated["support"] = entry.get("files", updated.get("support", []))
        updated_claims.append(updated)

    updated_ledger["claim_support"] = updated_claim_support
    return updated_claims, updated_ledger
