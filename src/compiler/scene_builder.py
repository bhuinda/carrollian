from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .actor_lowering import build_actor_trace
from .claim_extractor import claims_to_jsonl, extract_claims
from .common import ROOT, sha256_json, write_json, write_text
from .coordinate_resolver import attach_product_terms_to_support, collect_product_terms, support_coordinate_file_ref
from .core_lock import core_lock_ref, load_or_build_core_lock
from .d20_lowering import lower_scene_ir
from .normalizer import normalize_claims, normalize_obligations, normalize_text
from .obligation_extractor import extract_obligations
from .optimizer import compact_support_ledger, mark_obligations_closed
from .parser import parse_request
from .replay_builder import build_certificate, build_replay, build_turn_lock
from .residue_engine import build_residue_ledger
from .support_resolver import resolve_claim_support
from .verify_turn import verify_payloads, verify_turn


SCENE_IR_SCHEMA = "holotopy.scene_ir"
CONTEXT_SCHEMA = "holotopy.context_manifest"
METRICS_SCHEMA = "holotopy.turn_metrics"

CAPSULE_FILES = [
    "00_request.raw.json",
    "01_context.manifest.json",
    "02_obligations.json",
    "03_claims.jsonl",
    "04_support_ledger.json",
    "05_scene.ir.json",
    "06_actor_trace.json",
    "07_lowered_d20.json",
    "08_residue_ledger.json",
    "09_verification_report.json",
    "10_answer_plan.md",
    "11_final_answer.md",
    "12_turn_certificate.json",
    "13_replay.json",
    "14_failures.jsonl",
    "15_metrics.json",
]


@dataclass(frozen=True)
class TurnCompileConfig:
    turn_id: str
    user_text: str
    answer_text: str
    run_dir: Path | None = None
    mode: str = "scaffold"
    core_lock_path: Path | None = None
    write_core_lock: bool = False
    support_coordinates_file: Path | None = None
    extra_support_files: tuple[Path, ...] = ()


def _extra_support_refs(paths: tuple[Path, ...], *, root: Path) -> list[str]:
    refs: list[str] = []
    for path in paths:
        resolved = path if path.is_absolute() else root / path
        try:
            refs.append(resolved.resolve().relative_to(root.resolve()).as_posix())
        except ValueError:
            refs.append(str(resolved))
    return refs


def _attach_extra_support_files(
    claims: list[dict[str, Any]],
    support_ledger: dict[str, Any],
    refs: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not refs:
        return claims, support_ledger
    updated_claims: list[dict[str, Any]] = []
    updated_ledger = dict(support_ledger)
    support = {str(k): dict(v) for k, v in support_ledger.get("claim_support", {}).items()}
    for claim in claims:
        claim_id = str(claim.get("claim_id"))
        entry = support.setdefault(claim_id, {"files": [], "citations": []})
        files = list(entry.get("files", []))
        for ref in refs:
            if ref not in files:
                files.append(ref)
        entry["files"] = sorted(files)
        updated = dict(claim)
        updated["support"] = entry["files"]
        updated_claims.append(updated)
    updated_ledger["claim_support"] = support
    return updated_claims, updated_ledger


def build_scene_ir(
    turn_id: str,
    *,
    claim_count: int,
    obligation_count: int,
    product_terms: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SCENE_IR_SCHEMA,
        "turn_id": turn_id,
        "support": {
            "context": "01_context.manifest.json",
            "claims": "03_claims.jsonl",
            "support_ledger": "04_support_ledger.json",
            "product_terms": product_terms,
        },
        "effect_field": {
            "operation": "answer_user_request",
            "obligations": "02_obligations.json",
            "obligation_count": obligation_count,
        },
        "public_readout": {
            "target": "final_answer",
            "answer": "11_final_answer.md",
        },
        "shield_transport": {
            "method": "preserve_claim_support",
            "support_ledger": "04_support_ledger.json",
        },
        "sword_cut": {
            "method": "emit_public_answer_without_private_reasoning",
            "claim_count": claim_count,
        },
        "boundary": {
            "visible_output": "11_final_answer.md",
            "lowered_d20": "07_lowered_d20.json",
        },
        "residue": {
            "ledger": "08_residue_ledger.json",
        },
        "certificate": {
            "target": "12_turn_certificate.json",
        },
    }


def build_context_manifest(
    *,
    run_dir: Path,
    core_lock_path: Path | None,
    core_lock_present: bool,
    support_ledger: dict[str, Any],
    extra_file_refs: list[str] | None = None,
) -> dict[str, Any]:
    file_refs = {
            file_ref
            for entry in support_ledger.get("claim_support", {}).values()
            for file_ref in entry.get("files", [])
            if file_ref != "00_request.raw.json"
    }
    if extra_file_refs:
        file_refs.update(extra_file_refs)
    return {
        "schema": CONTEXT_SCHEMA,
        "core_lock": core_lock_ref(core_lock_path, run_dir) if core_lock_present else None,
        "core_lock_present": core_lock_present,
        "memory_refs": [],
        "file_refs": sorted(file_refs),
        "retrieval_refs": [],
        "prior_turn_refs": [],
    }


def build_answer_plan(obligations: dict[str, Any], claims: list[dict[str, Any]], status: str) -> str:
    return "\n".join(
        [
            "# Answer plan",
            "",
            f"- Close {len(obligations.get('obligations', []))} public obligations.",
            f"- Bind {len(claims)} public claims to the support ledger.",
            "- Emit only the public answer boundary.",
            "- Preserve residue and certificate hashes for replay.",
            f"- Verification status target: {status}.",
        ]
    )


def build_failures_jsonl(verification: dict[str, Any], residue_ledger: dict[str, Any]) -> str:
    rows: list[dict[str, Any]] = []
    for error in verification.get("errors", []):
        rows.append({"check": "verification", "status": "FAIL", "reason": error})
    for warning in verification.get("warnings", []):
        rows.append({"check": "verification", "status": "WARN", "reason": warning})
    for residue in residue_ledger.get("residues", []):
        if residue.get("discharged") is not True:
            rows.append(
                {
                    "check": residue.get("kind"),
                    "status": "RESIDUE",
                    "severity": residue.get("severity"),
                    "reason": residue.get("description"),
                }
            )
    return "\n".join(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows) + ("\n" if rows else "")


def build_metrics(claims: list[dict[str, Any]], residue_ledger: dict[str, Any], verification_status: str) -> dict[str, Any]:
    residues = residue_ledger.get("residues", [])
    return {
        "schema": METRICS_SCHEMA,
        "claim_count": len(claims),
        "supported_claim_count": sum(1 for claim in claims if claim.get("support")),
        "residue_count": len(residues),
        "undischarged_residue_count": sum(1 for item in residues if item.get("discharged") is not True),
        "verification_status": verification_status,
    }


def compile_turn(config: TurnCompileConfig, *, root: Path = ROOT) -> dict[str, Any]:
    run_dir = config.run_dir or (root / "runs" / config.turn_id)
    if not run_dir.is_absolute():
        run_dir = root / run_dir
    run_dir.mkdir(parents=True, exist_ok=True)

    core_lock, core_path, core_present = load_or_build_core_lock(
        root,
        core_lock_path=config.core_lock_path,
        write=config.write_core_lock,
    )
    core_hash = core_lock.get("core_hash") if core_present else None
    core_ref = core_lock_ref(core_path, run_dir) if core_present else None

    request = parse_request(turn_id=config.turn_id, user_text=normalize_text(config.user_text))
    obligations = mark_obligations_closed(normalize_obligations(extract_obligations(config.user_text)))
    claims = normalize_claims(extract_claims(config.answer_text))
    claims, support_ledger = resolve_claim_support(claims, root=root, core_lock_ref=core_ref)
    extra_support_refs = _extra_support_refs(config.extra_support_files, root=root)
    claims, support_ledger = _attach_extra_support_files(claims, support_ledger, extra_support_refs)
    product_terms = collect_product_terms(
        request_text=config.user_text,
        answer_text=config.answer_text,
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
    extra_context_refs = (
        [support_coordinate_file_ref(config.support_coordinates_file, root=root)]
        if config.support_coordinates_file
        else []
    )
    extra_context_refs.extend(extra_support_refs)
    context_manifest = build_context_manifest(
        run_dir=run_dir,
        core_lock_path=core_path,
        core_lock_present=core_present,
        support_ledger=support_ledger,
        extra_file_refs=extra_context_refs,
    )
    scene_ir = build_scene_ir(
        config.turn_id,
        claim_count=len(claims),
        obligation_count=len(obligations.get("obligations", [])),
        product_terms=product_terms,
    )
    lowered_d20 = lower_scene_ir(scene_ir, mode=config.mode, root=root)
    residue_ledger = build_residue_ledger(
        mode=config.mode,
        core_lock_present=core_present,
        claims=claims,
        lowered_d20=lowered_d20,
    )
    actor_trace = build_actor_trace(mode=config.mode, claims=claims, residues=residue_ledger.get("residues", []))

    write_json(run_dir / "00_request.raw.json", request)
    write_json(run_dir / "01_context.manifest.json", context_manifest)
    write_json(run_dir / "02_obligations.json", obligations)
    write_text(run_dir / "03_claims.jsonl", claims_to_jsonl(claims))
    write_json(run_dir / "04_support_ledger.json", support_ledger)
    write_json(run_dir / "05_scene.ir.json", scene_ir)
    write_json(run_dir / "06_actor_trace.json", actor_trace)
    write_json(run_dir / "07_lowered_d20.json", lowered_d20)
    write_json(run_dir / "08_residue_ledger.json", residue_ledger)
    write_text(run_dir / "11_final_answer.md", config.answer_text)
    stored_answer_text = (run_dir / "11_final_answer.md").read_text(encoding="utf-8")

    verification = verify_payloads(
        run_dir=run_dir,
        request=request,
        claims=claims,
        support_ledger=support_ledger,
        scene_ir=scene_ir,
        residue_ledger=residue_ledger,
        answer_text=stored_answer_text,
        root=root,
    )
    answer_plan = build_answer_plan(obligations, claims, verification["status"])
    write_json(run_dir / "09_verification_report.json", verification)
    write_text(run_dir / "10_answer_plan.md", answer_plan)

    certificate = build_certificate(
        turn_id=config.turn_id,
        request=request,
        scene_ir=scene_ir,
        answer_text=stored_answer_text,
        residue_ledger=residue_ledger,
        verification_status=verification["status"],
        core_lock_hash=core_hash,
    )
    replay = build_replay(config.turn_id)
    failures = build_failures_jsonl(verification, residue_ledger)
    metrics = build_metrics(claims, residue_ledger, verification["status"])
    write_json(run_dir / "12_turn_certificate.json", certificate)
    write_json(run_dir / "13_replay.json", replay)
    write_text(run_dir / "14_failures.jsonl", failures)
    write_json(run_dir / "15_metrics.json", metrics)

    turn_lock = build_turn_lock(run_dir, CAPSULE_FILES)
    write_json(run_dir / "TURN.lock.json", turn_lock)

    final_verification = verify_turn(run_dir, root=root)
    if not core_present:
        next_item = "Write CORE.lock.json in repo root before using certificates for non-provisional turn replay."
    elif not product_terms:
        next_item = "Supply explicit public product terms such as A985[0] * A985[0] when tensor-backed residue representatives are required."
    else:
        next_item = "Promote support-coordinate declarations into the JSON schema and replay verifier."
    return {
        "schema": "holotopy.turn_compile_result",
        "turn_id": config.turn_id,
        "run_dir": str(run_dir),
        "core_lock": str(core_path) if core_path else None,
        "core_lock_present": core_present,
        "core_lock_hash": core_hash,
        "verification_status": final_verification.get("status"),
        "verification": final_verification,
        "turn_lock_hash": sha256_json({k: v for k, v in turn_lock.items() if k != "turn_hash"}),
        "next_highest_yield_item": next_item,
    }
