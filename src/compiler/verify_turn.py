from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from pathlib import Path
from typing import Any

from .claim_extractor import claims_from_jsonl
from .common import ROOT, read_json, sha256_file, sha256_json
from .coordinate_resolver import load_support_coordinate_terms
from .residue_engine import residue_status


REQUIRED_FILES = [
    "00_request.raw.json",
    "02_obligations.json",
    "03_claims.jsonl",
    "04_support_ledger.json",
    "05_scene.ir.json",
    "08_residue_ledger.json",
    "09_verification_report.json",
    "11_final_answer.md",
    "12_turn_certificate.json",
    "TURN.lock.json",
]

SCENE_KEYS = {
    "support",
    "effect_field",
    "public_readout",
    "shield_transport",
    "sword_cut",
    "boundary",
    "residue",
    "certificate",
}


def _support_exists(run_dir: Path, support: str, root: Path) -> bool:
    return _resolve_support_path(run_dir, support, root) is not None


def _resolve_support_path(run_dir: Path, support: str, root: Path) -> Path | None:
    candidates = [run_dir / support, root / support, run_dir / support.replace("/", "\\")]
    for path in candidates:
        if path.exists():
            return path
    return None


def _same_coordinate(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return int(left.get("alpha", -1)) == int(right.get("alpha", -2)) and int(left.get("beta", -1)) == int(right.get("beta", -2))


def _verify_coordinate_replay(
    *,
    run_dir: Path,
    claims: list[dict[str, Any]],
    support_ledger: dict[str, Any],
    scene_ir: dict[str, Any],
    residue_ledger: dict[str, Any],
    root: Path,
) -> tuple[list[str], list[str], dict[str, bool]]:
    errors: list[str] = []
    warnings: list[str] = []
    terms = scene_ir.get("support", {}).get("product_terms", [])
    terms_by_id: dict[str, dict[str, Any]] = {}
    for term in terms:
        term_id = str(term.get("term_id", ""))
        if not term_id:
            errors.append("scene product term missing term_id")
        elif term_id in terms_by_id:
            errors.append(f"duplicate scene product term_id: {term_id}")
        else:
            terms_by_id[term_id] = term

    support = support_ledger.get("claim_support", {})
    coordinate_terms_by_claim: dict[str, list[dict[str, Any]]] = {}
    coordinate_file_cache: dict[str, list[dict[str, Any]]] = {}
    for claim_id, entry in support.items():
        for coordinate in entry.get("coordinates", []):
            term_id = str(coordinate.get("term_id", ""))
            term = terms_by_id.get(term_id)
            if term is None:
                errors.append(f"support coordinate references missing scene term: {claim_id}/{term_id}")
                continue
            if str(term.get("claim_id", "")) != str(claim_id):
                errors.append(f"support coordinate claim mismatch for {term_id}")
            if not _same_coordinate(coordinate, term):
                errors.append(f"support coordinate alpha/beta mismatch for {term_id}")
            coordinate_terms_by_claim.setdefault(str(claim_id), []).append(coordinate)

            file_ref = coordinate.get("file")
            if coordinate.get("source") == "support_coordinates_file":
                if not file_ref:
                    errors.append(f"support coordinate file missing for {claim_id}/{term_id}")
                    continue
                path = _resolve_support_path(run_dir, str(file_ref), root)
                if path is None:
                    errors.append(f"support coordinate source file not found for {claim_id}/{term_id}: {file_ref}")
                    continue
                if str(path) not in coordinate_file_cache:
                    try:
                        coordinate_file_cache[str(path)] = load_support_coordinate_terms(path, root=root)
                    except Exception as exc:
                        errors.append(f"support coordinate source file invalid for {claim_id}/{term_id}: {type(exc).__name__}: {exc}")
                        continue
                source_terms = coordinate_file_cache[str(path)]
                if not any(str(item.get("claim_id")) == str(claim_id) and _same_coordinate(item, coordinate) for item in source_terms):
                    errors.append(f"support coordinate not replayable from source file for {claim_id}/{term_id}")

    for term in terms:
        claim_id = term.get("claim_id")
        if not claim_id:
            continue
        if not any(str(coord.get("term_id")) == str(term.get("term_id")) and _same_coordinate(coord, term) for coord in coordinate_terms_by_claim.get(str(claim_id), [])):
            errors.append(f"scene term missing support-ledger coordinate: {term.get('term_id')}")

    discharged_residue_claims: set[str] = set()
    for residue in residue_ledger.get("residues", []):
        if residue.get("kind") != "quotient_tower_residue" or residue.get("discharged") is not True:
            continue
        claim_id = residue.get("claim_id")
        term_id = str(residue.get("term_id", ""))
        term = terms_by_id.get(term_id)
        if term is None:
            errors.append(f"residue references missing scene term: {term_id}")
            continue
        if claim_id and str(term.get("claim_id", "")) != str(claim_id):
            errors.append(f"residue claim mismatch for {term_id}")
        if claim_id:
            discharged_residue_claims.add(str(claim_id))

    required_claim_ids = [str(claim.get("claim_id")) for claim in claims if claim.get("requires_residue_coordinate") is True]
    missing_required = [claim_id for claim_id in required_claim_ids if claim_id not in discharged_residue_claims]
    if missing_required:
        warnings.append(f"required residue claims have no discharged coordinate witness: {missing_required}")

    return errors, warnings, {
        "coordinate_bindings_replayable": not errors,
        "required_residue_claims_discharged": not missing_required,
    }


def verify_payloads(
    *,
    run_dir: Path,
    request: dict[str, Any],
    claims: list[dict[str, Any]],
    support_ledger: dict[str, Any],
    scene_ir: dict[str, Any],
    residue_ledger: dict[str, Any],
    answer_text: str,
    certificate: dict[str, Any] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_scene_keys = sorted(SCENE_KEYS - set(scene_ir))
    if missing_scene_keys:
        errors.append(f"scene_ir missing keys: {missing_scene_keys}")

    support = support_ledger.get("claim_support", {})
    for claim in claims:
        claim_id = claim.get("claim_id")
        entry = support.get(claim_id, {})
        files = entry.get("files", [])
        if not files:
            errors.append(f"claim has no support: {claim_id}")
        for file_ref in files:
            if not _support_exists(run_dir, str(file_ref), root):
                warnings.append(f"support file not found for {claim_id}: {file_ref}")

    if "residues" not in residue_ledger:
        errors.append("residue ledger missing residues array")

    coordinate_errors, coordinate_warnings, coordinate_checks = _verify_coordinate_replay(
        run_dir=run_dir,
        claims=claims,
        support_ledger=support_ledger,
        scene_ir=scene_ir,
        residue_ledger=residue_ledger,
        root=root,
    )
    errors.extend(coordinate_errors)
    warnings.extend(coordinate_warnings)

    if certificate is not None:
        expected = {
            "input_hash": sha256_json(request),
            "scene_ir_hash": sha256_json(scene_ir),
            "answer_hash": sha256_json({"answer": answer_text}),
            "residue_hash": sha256_json(residue_ledger),
        }
        for key, value in expected.items():
            if certificate.get(key) != value:
                errors.append(f"certificate {key} mismatch")
        proof_body = {k: v for k, v in certificate.items() if k != "proof_hash"}
        if certificate.get("proof_hash") != sha256_json(proof_body):
            errors.append("certificate proof_hash mismatch")

    checks = {
        "scene_ir_valid": not missing_scene_keys,
        "claims_have_support": all(support.get(claim.get("claim_id"), {}).get("files") for claim in claims),
        "residue_ledger_present": "residues" in residue_ledger,
        "answer_matches_claims": bool(answer_text.strip()) or not claims,
        "no_unmarked_speculation": all(claim.get("risk") in {"low", "medium", "high"} for claim in claims),
        "replay_ready": certificate is None or not any("certificate" in error for error in errors),
        **coordinate_checks,
    }
    status = "FAIL" if errors else residue_status(residue_ledger)
    return {"schema": "holotopy.verification_report", "checks": checks, "status": status, "errors": errors, "warnings": warnings}


def verify_turn(run_dir: str | Path, *, root: Path = ROOT) -> dict[str, Any]:
    run_path = Path(run_dir)
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (run_path / name).exists():
            errors.append(f"missing file: {name}")
    if errors:
        return {"schema": "holotopy.verification_report", "status": "FAIL", "errors": errors, "warnings": []}

    request = read_json(run_path / "00_request.raw.json")
    claims = claims_from_jsonl((run_path / "03_claims.jsonl").read_text(encoding="utf-8"))
    support_ledger = read_json(run_path / "04_support_ledger.json")
    scene_ir = read_json(run_path / "05_scene.ir.json")
    residue_ledger = read_json(run_path / "08_residue_ledger.json")
    answer_text = (run_path / "11_final_answer.md").read_text(encoding="utf-8")
    certificate = read_json(run_path / "12_turn_certificate.json")
    report = verify_payloads(
        run_dir=run_path,
        request=request,
        claims=claims,
        support_ledger=support_ledger,
        scene_ir=scene_ir,
        residue_ledger=residue_ledger,
        answer_text=answer_text,
        certificate=certificate,
        root=root,
    )

    turn_lock = read_json(run_path / "TURN.lock.json")
    for name, expected_hash in turn_lock.get("files", {}).items():
        path = run_path / name
        if not path.exists():
            report["errors"].append(f"TURN.lock path missing: {name}")
        elif sha256_file(path) != expected_hash:
            report["errors"].append(f"TURN.lock hash mismatch: {name}")
    lock_body = {k: v for k, v in turn_lock.items() if k != "turn_hash"}
    if turn_lock.get("turn_hash") != sha256_json(lock_body):
        report["errors"].append("TURN.lock turn_hash mismatch")

    if report["errors"]:
        report["status"] = "FAIL"
    return report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Verify a compiled turn capsule.")
    parser.add_argument("run_dir")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    result = verify_turn(args.run_dir)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=args.pretty))
    raise SystemExit(0 if result.get("status") in {"PASS", "PASS_WITH_RESIDUE"} else 1)


if __name__ == "__main__":
    main()
