from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .claim_extractor import extract_claims
from .common import ROOT, sha256_bytes, sha256_json, utc_timestamp, write_json
from .coordinate_resolver import attach_product_terms_to_support, collect_product_terms
from .d20_lowering import lower_scene_ir
from .normalizer import normalize_text
from .optimizer import compact_support_ledger
from .residue_engine import residue_status
from .support_resolver import resolve_claim_support


SCENE_PROGRAM_SCHEMA = "d20.scene_program"
SCENE_IR_SCHEMA = "holotopy.scene_ir"
SCENE_COMPILER_ID = "d20.scene.compiler"
SCENE_SELFTEST_SCHEMA = "d20.scene_compiler_selftest"
DEFAULT_SCENE_PROGRAM_FILE = "scene_program.json"
SCENE_ADMISSION_LEDGER_SCHEMA = "d20.scene_admission_ledger"
SCENE_OBSERVATION_LEDGER_SCHEMA = "d20.scene_observation_ledger"
SCENE_RECEIPT_LEDGER_SCHEMA = "d20.scene_receipt_ledger"
SCENE_VERIFICATION_SCHEMA = "d20.scene_verification_report"
SCENE_EXTERNAL_RECEIPT_LEDGER_SCHEMA = "d20.scene_external_receipt_ledger"
DEFAULT_SCENE_VERIFICATION_FILE = "scene_verification.json"
CLAIM_BOUNDARY = (
    "Compiles source text into candidate d20 scene structure. It does not execute tools, "
    "predict events, or settle truth."
)

SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_'-]*")
RELATION_VERB_RE = re.compile(
    r"\b("
    r"is|are|was|were|becomes?|has|have|needs?|requires?|"
    r"compiles?|lowers?|maps?|links?|relates?|supports?|verifies?|"
    r"emits?|records?|captures?|observes?|receipts?|normalizes?"
    r")\b",
    re.IGNORECASE,
)
SCENE_OBLIGATION_RE = re.compile(
    r"\b("
    r"need|needs|must|always|required|requires?|"
    r"goal|invariant|verify|verified|verification|checks?|"
    r"distinguish|preserve|compile|compiles?"
    r")\b",
    re.IGNORECASE,
)
QUESTION_START = {
    "what",
    "why",
    "when",
    "where",
    "who",
    "whom",
    "whose",
    "which",
    "how",
    "can",
    "could",
    "would",
    "should",
    "do",
    "does",
    "did",
    "is",
    "are",
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "then",
    "there",
    "this",
    "to",
    "with",
}


@dataclass(frozen=True)
class SceneCompileConfig:
    text: str
    scene_id: str | None = None
    source_name: str | None = None
    timestamp: str | None = None
    mode: str = "scaffold"
    support_coordinates_file: Path | None = None
    max_terms_per_clause: int = 24


def _clean_clause(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" \t-*:")


def _clause_candidates(text: str) -> list[str]:
    normalized = normalize_text(text)
    clauses: list[str] = []
    for raw_line in normalized.splitlines():
        line = _clean_clause(raw_line)
        if not line or line.startswith("```"):
            continue
        for part in SENTENCE_END.split(line):
            clause = _clean_clause(part)
            if clause:
                clauses.append(clause)
    if not clauses and normalized:
        clauses.append(_clean_clause(normalized))
    return clauses


def _stable_key(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _dedupe_text(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = _stable_key(item)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _obligation_candidates(text: str) -> list[str]:
    return [
        clause
        for clause in _dedupe_text(_clause_candidates(text))
        if SCENE_OBLIGATION_RE.search(clause)
    ]


def _terms(text: str, *, limit: int) -> list[str]:
    seen: set[str] = set()
    terms: list[str] = []
    for match in TOKEN_RE.finditer(text):
        term = match.group(0).strip("_'-").casefold()
        if len(term) < 2 or term in STOPWORDS or term in seen:
            continue
        seen.add(term)
        terms.append(term)
        if len(terms) >= limit:
            break
    return terms


def _leading_word(text: str) -> str:
    match = TOKEN_RE.search(text)
    return match.group(0).casefold() if match else ""


def _clause_kind(text: str) -> str:
    if text.rstrip().endswith("?") or _leading_word(text) in QUESTION_START:
        return "question"
    if SCENE_OBLIGATION_RE.search(text):
        return "obligation"
    return "assertion"


def _trim_phrase(text: str, *, max_words: int = 12) -> str:
    words = [match.group(0) for match in TOKEN_RE.finditer(text)]
    if not words:
        return _clean_clause(text)
    selected = words[-max_words:] if len(words) > max_words else words
    return " ".join(selected)


def _relation_from_clause(text: str) -> dict[str, Any] | None:
    match = RELATION_VERB_RE.search(text)
    if not match:
        return None
    subject = _trim_phrase(text[: match.start()])
    object_text = _trim_phrase(text[match.end() :])
    if not subject or not object_text:
        return None
    return {
        "predicate": match.group(0).casefold(),
        "subject": subject,
        "object": object_text,
        "source_text": text,
    }


def _append_instruction(
    instructions: list[dict[str, Any]],
    *,
    op: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    item = {
        "id": f"ins_{len(instructions) + 1:04d}",
        "op": op,
        **payload,
    }
    instructions.append(item)
    return item


def _compile_clauses(
    raw_clauses: list[str],
    *,
    max_terms_per_clause: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    clauses: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    instructions: list[dict[str, Any]] = []
    for idx, text in enumerate(raw_clauses, start=1):
        clause_id = f"clause_{idx:04d}"
        clause = {
            "clause_id": clause_id,
            "kind": _clause_kind(text),
            "text": text,
            "terms": _terms(text, limit=max(1, max_terms_per_clause)),
        }
        clauses.append(clause)
        _append_instruction(
            instructions,
            op="observe_scene_clause",
            payload=clause,
        )
        relation = _relation_from_clause(text)
        if relation:
            relation_id = f"rel_{len(relations) + 1:04d}"
            relation = {"relation_id": relation_id, "clause_id": clause_id, **relation}
            relations.append(relation)
            _append_instruction(
                instructions,
                op="emit_scene_relation",
                payload={
                    "relation_id": relation_id,
                    "clause_id": clause_id,
                    "predicate": relation["predicate"],
                    "subject": relation["subject"],
                    "object": relation["object"],
                },
            )
    return clauses, relations, instructions


def _compile_obligations(text: str, instructions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    obligations: list[dict[str, Any]] = []
    for idx, obligation_text in enumerate(_obligation_candidates(text), start=1):
        obligation = {
            "obligation_id": f"obl_{idx:03d}",
            "kind": "validation" if re.search(r"\b(check|verify)\b", obligation_text, re.IGNORECASE) else "constraint",
            "text": normalize_text(obligation_text),
            "status": "open",
            "source": "source_text",
        }
        obligations.append(obligation)
        _append_instruction(instructions, op="emit_scene_obligation", payload=obligation)
    return obligations


def _compile_claims(text: str, instructions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    seen: set[str] = set()
    for claim in extract_claims(text):
        claim_text = normalize_text(str(claim.get("text", "")))
        key = _stable_key(claim_text)
        if not claim_text or key in seen:
            continue
        seen.add(key)
        compiled = {
            "claim_id": claim.get("claim_id"),
            "text": claim_text,
            "risk": claim.get("risk", "medium"),
            "requires_residue_coordinate": bool(claim.get("requires_residue_coordinate")),
        }
        claims.append(compiled)
        _append_instruction(instructions, op="emit_scene_claim", payload=compiled)
    return claims


def _source_support(
    claims: list[dict[str, Any]],
    *,
    source_sha256: str,
    root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    resolved_claims, support_ledger = resolve_claim_support(claims, root=root)
    claim_support = {}
    updated_claims: list[dict[str, Any]] = []
    for claim in resolved_claims:
        claim_id = str(claim.get("claim_id"))
        entry = dict(support_ledger.get("claim_support", {}).get(claim_id, {}))
        files = [path for path in entry.get("files", []) if path != "00_request.raw.json"]
        entry["files"] = files
        entry["source"] = {"kind": "source_text", "sha256": source_sha256}
        claim_support[claim_id] = entry
        updated = dict(claim)
        updated["support"] = files
        updated["source_sha256"] = source_sha256
        updated_claims.append(updated)
    return updated_claims, compact_support_ledger({"schema": support_ledger.get("schema"), "claim_support": claim_support})


def _build_scene_ir(
    *,
    scene_id: str,
    source_sha256: str,
    clauses: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    obligations: list[dict[str, Any]],
    support_ledger: dict[str, Any],
    product_terms: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SCENE_IR_SCHEMA,
        "scene_id": scene_id,
        "support": {
            "source_text_sha256": source_sha256,
            "clauses": clauses,
            "claims": claims,
            "relations": relations,
            "support_ledger": support_ledger,
            "product_terms": product_terms,
        },
        "effect_field": {
            "operation": "compile_source_text_to_d20_scene",
            "obligations": obligations,
            "obligation_count": len(obligations),
        },
        "public_readout": {
            "target": "d20_scene_program",
            "claim_count": len(claims),
            "relation_count": len(relations),
        },
        "shield_transport": {
            "method": "preserve_source_hash_and_candidate_status",
            "support_ledger": "support.claims",
        },
        "sword_cut": {
            "method": "emit_scene_without_settling_truth",
            "claim_count": len(claims),
            "relation_count": len(relations),
        },
        "boundary": {
            "visible_output": "scene_program",
            "lowered_d20": "lowered_d20",
            "d20_boundary": "D20",
        },
        "residue": {
            "ledger": "residue_ledger",
        },
        "certificate": {
            "target": "program_hash",
        },
    }


def _scene_residue_ledger(
    *,
    mode: str,
    lowered_d20: dict[str, Any],
    claims: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> dict[str, Any]:
    residues: list[dict[str, Any]] = []
    if lowered_d20.get("boundary") != "D20":
        residues.append(
            {
                "id": f"res_{len(residues) + 1:03d}",
                "kind": "missing_d20_boundary",
                "description": "Scene lowering did not expose the D20 boundary.",
                "severity": "high",
                "discharged": False,
            }
        )
    if mode != "tensor_backed" or lowered_d20.get("mode") != "tensor_backed":
        residues.append(
            {
                "id": f"res_{len(residues) + 1:03d}",
                "kind": "symbolic_d20_lowering",
                "description": "Scene lowered through the symbolic D20 scaffold rather than tensor-backed residue representatives.",
                "severity": "medium",
                "discharged": False,
            }
        )
    if claims:
        residues.append(
            {
                "id": f"res_{len(residues) + 1:03d}",
                "kind": "candidate_claims_need_admission",
                "description": "Scene claims remain candidate evidence until admitted, observed, verified, and receipted.",
                "severity": "medium",
                "claim_ids": [claim.get("claim_id") for claim in claims],
                "discharged": False,
            }
        )
    if not relations:
        residues.append(
            {
                "id": f"res_{len(residues) + 1:03d}",
                "kind": "no_scene_relations_detected",
                "description": "No explicit scene relation verb was detected in the source text.",
                "severity": "medium",
                "discharged": False,

            }
        )
    return {"schema": "holotopy.residue_ledger", "residues": residues}


def _target_id(kind: str, payload: dict[str, Any], index: int) -> str:
    for key in ("claim_id", "relation_id", "obligation_id", "clause_id", "id"):
        value = payload.get(key)
        if value:
            return str(value)
    return f"{kind}_{index:04d}"


def _build_observation_ledger(
    *,
    scene_id: str,
    source_text: str,
    source_sha256: str,
    clauses: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    obligations: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    support_ledger: dict[str, Any],
    scene_ir: dict[str, Any],
    lowered_d20: dict[str, Any],
    residue_ledger: dict[str, Any],
) -> dict[str, Any]:
    observations: list[dict[str, Any]] = [
        {
            "observation_id": "obs_0001",
            "kind": "source_text",
            "target_id": scene_id,
            "raw_sha256": source_sha256,
            "normalized_sha256": sha256_bytes(normalize_text(source_text).encode("utf-8")),
            "raw_text": source_text,
            "normalized_text": normalize_text(source_text),
        }
    ]
    observed_groups = [
        ("scene_clause", clauses),
        ("scene_relation", relations),
        ("scene_obligation", obligations),
        ("scene_claim", claims),
        ("scene_residue", residue_ledger.get("residues", [])),
    ]
    for kind, rows in observed_groups:
        for row in rows:
            observations.append(
                {
                    "observation_id": f"obs_{len(observations) + 1:04d}",
                    "kind": kind,
                    "target_id": _target_id(kind, row, len(observations) + 1),
                    "payload_hash": sha256_json(row),
                    "payload_ref": kind,
                    "status": "observed",
                }
            )
    for kind, payload in [
        ("support_ledger", support_ledger),
        ("scene_ir", scene_ir),
        ("lowered_d20", lowered_d20),
        ("residue_ledger", residue_ledger),
    ]:
        observations.append(
            {
                "observation_id": f"obs_{len(observations) + 1:04d}",
                "kind": kind,
                "target_id": scene_id,
                "payload_hash": sha256_json(payload),
                "payload_ref": kind,
                "status": "observed",
            }
        )
    return {"schema": SCENE_OBSERVATION_LEDGER_SCHEMA, "scene_id": scene_id, "observations": observations}


def _observation_ids_by_target(observation_ledger: dict[str, Any]) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    for observation in observation_ledger.get("observations", []):
        out[(str(observation.get("kind")), str(observation.get("target_id")))] = str(observation.get("observation_id"))
    return out


def _build_admission_ledger(
    *,
    scene_id: str,
    relations: list[dict[str, Any]],
    obligations: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    residue_ledger: dict[str, Any],
    observation_ledger: dict[str, Any],
) -> dict[str, Any]:
    observation_ids = _observation_ids_by_target(observation_ledger)
    admissions: list[dict[str, Any]] = []
    for kind, rows in [
        ("scene_relation", relations),
        ("scene_obligation", obligations),
        ("scene_claim", claims),
        ("scene_residue", residue_ledger.get("residues", [])),
    ]:
        for row in rows:
            target_id = _target_id(kind, row, len(admissions) + 1)
            status = "candidate_pending_verification" if kind in {"scene_claim", "scene_residue"} else "admitted_candidate"
            admissions.append(
                {
                    "admission_id": f"adm_{len(admissions) + 1:04d}",
                    "kind": kind,
                    "target_id": target_id,
                    "status": status,
                    "observation_id": observation_ids.get((kind, target_id)),
                    "policy": "scene_compiler_candidate_only",
                    "truth_status": "unsettled",
                }
            )
    return {"schema": SCENE_ADMISSION_LEDGER_SCHEMA, "scene_id": scene_id, "admissions": admissions}


def _build_receipt_ledger(
    *,
    scene_id: str,
    source_sha256: str,
    support_ledger: dict[str, Any],
    scene_ir: dict[str, Any],
    lowered_d20: dict[str, Any],
    residue_ledger: dict[str, Any],
    observation_ledger: dict[str, Any],
    admission_ledger: dict[str, Any],
) -> dict[str, Any]:
    receipts = [
        {"receipt_id": "rec_0001", "kind": "source_hash_bound", "status": "VERIFIED", "sha256": source_sha256},
        {"receipt_id": "rec_0002", "kind": "support_ledger_hash", "status": "VERIFIED", "sha256": sha256_json(support_ledger)},
        {"receipt_id": "rec_0003", "kind": "scene_ir_hash", "status": "VERIFIED", "sha256": sha256_json(scene_ir)},
        {"receipt_id": "rec_0004", "kind": "lowered_d20_hash", "status": "VERIFIED", "sha256": sha256_json(lowered_d20)},
        {"receipt_id": "rec_0005", "kind": "d20_boundary_present", "status": "VERIFIED" if lowered_d20.get("boundary") == "D20" else "FAILED"},
        {"receipt_id": "rec_0006", "kind": "residue_ledger_hash", "status": "VERIFIED", "sha256": sha256_json(residue_ledger)},
        {"receipt_id": "rec_0007", "kind": "observation_count", "status": "VERIFIED", "count": len(observation_ledger.get("observations", []))},
        {"receipt_id": "rec_0008", "kind": "admission_count", "status": "VERIFIED", "count": len(admission_ledger.get("admissions", []))},
    ]
    return {"schema": SCENE_RECEIPT_LEDGER_SCHEMA, "scene_id": scene_id, "receipts": receipts}


def compile_scene(config: SceneCompileConfig, *, root: Path = ROOT) -> dict[str, Any]:
    source_bytes = config.text.encode("utf-8")
    source_sha256 = sha256_bytes(source_bytes)
    scene_id = config.scene_id or f"scene_{source_sha256[:12]}"
    mode = config.mode if config.mode in {"scaffold", "tensor_backed"} else "scaffold"
    raw_clauses = _dedupe_text(_clause_candidates(config.text))
    clauses, relations, instructions = _compile_clauses(raw_clauses, max_terms_per_clause=config.max_terms_per_clause)
    obligations = _compile_obligations(config.text, instructions)
    claims = _compile_claims(config.text, instructions)
    claims, support_ledger = _source_support(claims, source_sha256=source_sha256, root=root)
    product_terms = collect_product_terms(
        request_text=config.text,
        answer_text="",
        claims=claims,
        support_coordinates_file=config.support_coordinates_file,
        root=root,
    )
    claims, support_ledger = attach_product_terms_to_support(
        claims,
        support_ledger,
        product_terms,
        support_coordinates_file=config.support_coordinates_file,
        root=root,
    )
    support_ledger = compact_support_ledger(support_ledger)
    scene_ir = _build_scene_ir(
        scene_id=scene_id,
        source_sha256=source_sha256,
        clauses=clauses,
        claims=claims,
        relations=relations,
        obligations=obligations,
        support_ledger=support_ledger,
        product_terms=product_terms,
    )
    lowered_d20 = lower_scene_ir(scene_ir, mode=mode, root=root)
    _append_instruction(
        instructions,
        op="lower_scene_to_d20",
        payload={
            "mode": lowered_d20.get("mode"),
            "boundary": lowered_d20.get("boundary"),
            "support_algebra": lowered_d20.get("support_algebra"),
            "product_term_count": len(product_terms),
        },
    )
    residue_ledger = _scene_residue_ledger(
        mode=mode,
        lowered_d20=lowered_d20,
        claims=claims,
        relations=relations,
    )
    observation_ledger = _build_observation_ledger(
        scene_id=scene_id,
        source_text=config.text,
        source_sha256=source_sha256,
        clauses=clauses,
        relations=relations,
        obligations=obligations,
        claims=claims,
        support_ledger=support_ledger,
        scene_ir=scene_ir,
        lowered_d20=lowered_d20,
        residue_ledger=residue_ledger,
    )
    admission_ledger = _build_admission_ledger(
        scene_id=scene_id,
        relations=relations,
        obligations=obligations,
        claims=claims,
        residue_ledger=residue_ledger,
        observation_ledger=observation_ledger,
    )
    receipt_ledger = _build_receipt_ledger(
        scene_id=scene_id,
        source_sha256=source_sha256,
        support_ledger=support_ledger,
        scene_ir=scene_ir,
        lowered_d20=lowered_d20,
        residue_ledger=residue_ledger,
        observation_ledger=observation_ledger,
        admission_ledger=admission_ledger,
    )
    warnings: list[str] = []
    if not config.text.strip():
        warnings.append("Input text is empty; no scene facts were compiled.")
    if config.mode != mode:
        warnings.append(f"Unknown mode {config.mode!r}; used scaffold.")
    summary = {
        "clause_count": len(clauses),
        "relation_count": len(relations),
        "obligation_count": len(obligations),
        "candidate_claim_count": len(claims),
        "product_term_count": len(product_terms),
        "instruction_count": len(instructions),
        "residue_count": len(residue_ledger.get("residues", [])),
        "observation_count": len(observation_ledger.get("observations", [])),
        "admission_count": len(admission_ledger.get("admissions", [])),
        "receipt_count": len(receipt_ledger.get("receipts", [])),
        "warning_count": len(warnings),
        "status": residue_status(residue_ledger),
    }
    program: dict[str, Any] = {
        "schema": SCENE_PROGRAM_SCHEMA,
        "scene_id": scene_id,
        "manifest": {
            "compiler_id": SCENE_COMPILER_ID,
            "created_at": config.timestamp or utc_timestamp(),
            "source_name": config.source_name,
            "source_sha256": source_sha256,
            "source_bytes": len(source_bytes),
            "claim_boundary": CLAIM_BOUNDARY,
        },
        "clauses": clauses,
        "obligations": obligations,
        "claims": claims,
        "relations": relations,
        "support_ledger": support_ledger,
        "scene_ir": scene_ir,
        "lowered_d20": lowered_d20,
        "residue_ledger": residue_ledger,
        "observation_ledger": observation_ledger,
        "admission_ledger": admission_ledger,
        "receipt_ledger": receipt_ledger,
        "instructions": instructions,
        "summary": summary,
        "warnings": warnings,
        "next_highest_yield_item": "Run the admission ledger through a verifier that can promote candidate scene claims into external receipts.",
    }
    program["program_hash"] = sha256_json(program)
    return program


def write_scene_program(program: dict[str, Any], out: Path, *, root: Path = ROOT, pretty: bool = True) -> Path:
    out_path = out
    if not out_path.is_absolute():
        out_path = root / out_path
    if out_path.suffix.lower() != ".json":
        out_path = out_path / DEFAULT_SCENE_PROGRAM_FILE
    write_json(out_path, program, pretty=pretty)
    return out_path



def _index_rows(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if value is not None:
            out[str(value)] = row
    return out


def _observations_by_kind_target(observation_ledger: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for observation in observation_ledger.get("observations", []):
        out[(str(observation.get("kind")), str(observation.get("target_id")))] = observation
    return out


def _admissions_by_kind_target(admission_ledger: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for admission in admission_ledger.get("admissions", []):
        out[(str(admission.get("kind")), str(admission.get("target_id")))] = admission
    return out


def _receipt_by_kind(receipt_ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for receipt in receipt_ledger.get("receipts", []):
        kind = receipt.get("kind")
        if kind is not None:
            out[str(kind)] = receipt
    return out


def _support_path_exists(path_ref: str, *, root: Path) -> bool:
    path = Path(path_ref)
    return path.exists() if path.is_absolute() else (root / path).exists()


def _computed_residue_claim_ids(lowered_d20: dict[str, Any]) -> set[str]:
    residue_class = lowered_d20.get("residue_class", {})
    if residue_class.get("schema") not in {"holotopy.q12_section_residue", "holotopy.quotient_tower_residue"}:
        return set()
    computed: set[str] = set()
    for term in residue_class.get("terms", []):
        q12_residue = term.get("q12", {}).get("residue", term.get("residue", {}))
        a42_residue = term.get("a42", {}).get("residue", {})
        d20 = term.get("d20", {})
        ok = (
            term.get("status") == "COMPUTED"
            and q12_residue.get("q12_boundary_zero") is True
            and a42_residue.get("q42_boundary_zero") is True
            and a42_residue.get("q12_transport_boundary_zero") is True
            and d20.get("q12_residue_boundary_zero") is True
            and d20.get("a42_residue_boundary_zero") is True
            and d20.get("graph_valid") is True
        )
        if ok and term.get("claim_id"):
            computed.add(str(term.get("claim_id")))
    return computed


def _check_report_item(name: str, passed: bool, message: str) -> dict[str, Any]:
    return {"name": name, "status": "PASS" if passed else "FAIL", "message": message}


def verify_scene_program(program: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    scene_id = str(program.get("scene_id") or "")
    manifest = program.get("manifest", {})
    source_sha256 = str(manifest.get("source_sha256") or "")
    scene_ir = program.get("scene_ir", {})
    lowered_d20 = program.get("lowered_d20", {})
    residue_ledger = program.get("residue_ledger", {})
    observation_ledger = program.get("observation_ledger", {})
    admission_ledger = program.get("admission_ledger", {})
    receipt_ledger = program.get("receipt_ledger", {})
    support_ledger = program.get("support_ledger", {})

    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    def record(name: str, passed: bool, message: str, *, error: bool = True) -> None:
        checks.append(_check_report_item(name, passed, message))
        if not passed:
            (errors if error else warnings).append(message)

    record("program_schema", program.get("schema") == SCENE_PROGRAM_SCHEMA, "Program schema must be d20.scene_program.")
    program_hash = program.get("program_hash")
    if program_hash:
        hashed_program = dict(program)
        hashed_program.pop("program_hash", None)
        record("program_hash", sha256_json(hashed_program) == program_hash, "Program hash must match the program body.")
    else:
        record("program_hash", False, "Program has no program_hash.")
    record("source_hash_present", bool(source_sha256), "Manifest must include source_sha256.")
    record("scene_ir_schema", scene_ir.get("schema") == SCENE_IR_SCHEMA, "SceneIR schema must be holotopy.scene_ir.")
    record("lowered_d20_schema", lowered_d20.get("schema") == "holotopy.lowered_d20", "Lowering schema must be holotopy.lowered_d20.")
    record("d20_boundary", lowered_d20.get("boundary") == "D20", "Lowering must expose the D20 boundary.")
    record(
        "observation_ledger_schema",
        observation_ledger.get("schema") == SCENE_OBSERVATION_LEDGER_SCHEMA,
        "Observation ledger schema must be d20.scene_observation_ledger.",
    )
    record(
        "admission_ledger_schema",
        admission_ledger.get("schema") == SCENE_ADMISSION_LEDGER_SCHEMA,
        "Admission ledger schema must be d20.scene_admission_ledger.",
    )
    record(
        "receipt_ledger_schema",
        receipt_ledger.get("schema") == SCENE_RECEIPT_LEDGER_SCHEMA,
        "Receipt ledger schema must be d20.scene_receipt_ledger.",
    )
    record("observations_present", bool(observation_ledger.get("observations")), "Observation ledger must contain observations.")
    record("admissions_present", bool(admission_ledger.get("admissions")), "Admission ledger must contain admissions.")
    record("receipts_present", bool(receipt_ledger.get("receipts")), "Receipt ledger must contain receipts.")

    observations = _observations_by_kind_target(observation_ledger)
    source_observation = observations.get(("source_text", scene_id))
    source_observation_ok = bool(source_observation and source_observation.get("raw_sha256") == source_sha256)
    if source_observation_ok and source_observation and "raw_text" in source_observation:
        source_observation_ok = sha256_bytes(str(source_observation.get("raw_text", "")).encode("utf-8")) == source_sha256
    record("source_observation_hash", source_observation_ok, "Source observation must bind the manifest source hash.")

    receipt_index = _receipt_by_kind(receipt_ledger)
    hash_receipts = [
        ("support_ledger_hash", support_ledger),
        ("scene_ir_hash", scene_ir),
        ("lowered_d20_hash", lowered_d20),
        ("residue_ledger_hash", residue_ledger),
    ]
    for receipt_kind, payload in hash_receipts:
        receipt = receipt_index.get(receipt_kind, {})
        record(
            receipt_kind,
            receipt.get("status") == "VERIFIED" and receipt.get("sha256") == sha256_json(payload),
            f"{receipt_kind} receipt must match the current payload.",
        )
    failed_receipts = [receipt for receipt in receipt_ledger.get("receipts", []) if receipt.get("status") == "FAILED"]
    record("receipt_ledger_passed", not failed_receipts, "Compiler receipt ledger must not contain failed receipts.")

    claims = _index_rows(program.get("claims", []), "claim_id")
    admissions = _admissions_by_kind_target(admission_ledger)
    support_map = support_ledger.get("claim_support", {})
    computed_residue_claims = _computed_residue_claim_ids(lowered_d20)
    external_receipts: list[dict[str, Any]] = []
    pending_claims: list[dict[str, Any]] = []
    claim_admissions = [
        admission
        for admission in admission_ledger.get("admissions", [])
        if admission.get("kind") == "scene_claim"
    ]

    for admission in claim_admissions:
        claim_id = str(admission.get("target_id"))
        claim = claims.get(claim_id)
        support_entry = dict(support_map.get(claim_id, {}))
        files = [str(item) for item in support_entry.get("files", [])]
        coordinates = support_entry.get("coordinates") or (claim or {}).get("support_coordinates", [])
        missing_files = [path for path in files if not _support_path_exists(path, root=root)]
        source_bound = support_entry.get("source", {}).get("sha256") == source_sha256
        observation = observations.get(("scene_claim", claim_id))
        residue_ok = claim_id in computed_residue_claims
        residue_required = bool((claim or {}).get("requires_residue_coordinate"))
        reasons: list[str] = []
        if not claim:
            reasons.append("claim not present in program claims")
        if not observation:
            reasons.append("claim observation not present")
        if admissions.get(("scene_claim", claim_id)) is None:
            reasons.append("claim admission not present")
        if not source_bound:
            reasons.append("claim support is not bound to the source hash")
        if not files and not coordinates:
            reasons.append("claim has no external support files or coordinates")
        if missing_files:
            reasons.append("claim support files are missing")
        if residue_required and not residue_ok:
            reasons.append("claim requires a computed residue coordinate")

        if reasons:
            pending_claims.append(
                {
                    "claim_id": claim_id,
                    "admission_id": admission.get("admission_id"),
                    "status": "PENDING",
                    "reasons": reasons,
                    "missing_files": missing_files,
                }
            )
            continue

        support_receipt = {
            "receipt_id": f"extrec_{len(external_receipts) + 1:04d}",
            "kind": "scene_claim_external_support",
            "status": "PROMOTED",
            "claim_id": claim_id,
            "claim_hash": sha256_json(claim),
            "support_hash": sha256_json(support_entry),
            "support_files": files,
            "support_coordinates": coordinates,
            "observation_id": observation.get("observation_id") if observation else None,
            "admission_id": admission.get("admission_id"),
            "promotion_policy": "source_hash_observation_admission_external_support_and_residue_if_required",
        }
        external_receipts.append(support_receipt)

    if not claim_admissions:
        warnings.append("No candidate scene claims were admitted for promotion.")

    external_receipt_ledger = {
        "schema": SCENE_EXTERNAL_RECEIPT_LEDGER_SCHEMA,
        "scene_id": scene_id,
        "receipts": external_receipts,
    }
    status = "FAIL" if errors else "PASS_WITH_PENDING_CLAIMS" if pending_claims else "PASS"
    return {
        "schema": SCENE_VERIFICATION_SCHEMA,
        "scene_id": scene_id,
        "status": status,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "pending_claims": pending_claims,
        "external_receipt_ledger": external_receipt_ledger,
        "promoted_claim_count": len(external_receipts),
        "pending_claim_count": len(pending_claims),
        "next_highest_yield_item": "Attach verify-scene output to the repository receipt registry or turn-level verifier.",
    }


def write_scene_verification(report: dict[str, Any], out: Path, *, root: Path = ROOT, pretty: bool = True) -> Path:
    out_path = out
    if not out_path.is_absolute():
        out_path = root / out_path
    if out_path.suffix.lower() != ".json":
        out_path = out_path / DEFAULT_SCENE_VERIFICATION_FILE
    write_json(out_path, report, pretty=pretty)
    return out_path


def run_scene_selftest() -> dict[str, Any]:
    program = compile_scene(
        SceneCompileConfig(
            text=(
                "Compile this source text into a d20 scene. "
                "The scene records obligations and emits relations for later verification."
            ),
            scene_id="scene_compiler_selftest",
            source_name="selftest",
            timestamp="1970-01-01T00:00:00Z",
        )
    )
    summary = program.get("summary", {})
    verification = verify_scene_program(program)
    checks = {
        "schema": program.get("schema") == SCENE_PROGRAM_SCHEMA,
        "scene_ir_schema": program.get("scene_ir", {}).get("schema") == SCENE_IR_SCHEMA,
        "d20_boundary": program.get("lowered_d20", {}).get("boundary") == "D20",
        "has_source_hash": bool(program.get("manifest", {}).get("source_sha256")),
        "has_instructions": summary.get("instruction_count", 0) > 0,
        "has_relation": summary.get("relation_count", 0) > 0,
        "has_residue_ledger": "residues" in program.get("residue_ledger", {}),
        "has_observation_ledger": bool(program.get("observation_ledger", {}).get("observations")),
        "has_admission_ledger": bool(program.get("admission_ledger", {}).get("admissions")),
        "has_receipt_ledger": bool(program.get("receipt_ledger", {}).get("receipts")),
        "verify_scene": verification.get("status") == "PASS",
        "verify_scene_promotes_claims": verification.get("promoted_claim_count", 0) > 0,
        "has_claim_boundary": bool(program.get("manifest", {}).get("claim_boundary")),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    return {
        "schema": SCENE_SELFTEST_SCHEMA,
        "status": status,
        "checks": checks,
        "program_hash": program.get("program_hash"),
        "verification": verification,
        "summary": summary,
    }
