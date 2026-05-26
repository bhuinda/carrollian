from __future__ import annotations

from typing import Any


RESIDUE_SCHEMA = "holotopy.residue_ledger"


def build_residue_ledger(
    *,
    mode: str,
    core_lock_present: bool,
    claims: list[dict[str, Any]],
    lowered_d20: dict[str, Any],
) -> dict[str, Any]:
    residues: list[dict[str, Any]] = []
    computed_residue_claims: set[str] = set()
    if not core_lock_present:
        residues.append(
            {
                "id": "res_001",
                "kind": "missing_core_lock",
                "description": "No CORE.lock.json was present or written, so the capsule is provisional.",
                "severity": "high",
                "discharged": False,
            }
        )

    residue_class = lowered_d20.get("residue_class", {})
    if mode != "tensor_backed" or lowered_d20.get("mode") != "tensor_backed":
        residues.append(
            {
                "id": f"res_{len(residues) + 1:03d}",
                "kind": "symbolic_tensor_lowering",
                "description": "The turn lowered through the symbolic D20 scaffold rather than computing tensor-backed residue representatives.",
                "severity": "medium",
                "discharged": False,
            }
        )
    elif residue_class.get("schema") in {"holotopy.q12_section_residue", "holotopy.quotient_tower_residue"}:
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
            residues.append(
                {
                    "id": f"res_{len(residues) + 1:03d}",
                    "kind": "quotient_tower_residue",
                    "description": f"Computed A985 product residue through A42, A12, and D20 for {term.get('syntax')}.",
                    "severity": "info" if ok else "high",
                    "term_id": term.get("term_id"),
                    "claim_id": term.get("claim_id"),
                    "a42_residue_sha256": a42_residue.get("sha256"),
                    "q12_residue_sha256": q12_residue.get("sha256"),
                    "q42_boundary_zero": a42_residue.get("q42_boundary_zero"),
                    "q12_boundary_zero": q12_residue.get("q12_boundary_zero"),
                    "a42_to_q12_boundary_zero": a42_residue.get("q12_transport_boundary_zero"),
                    "d20_q12_boundary_zero": d20.get("q12_residue_boundary_zero"),
                    "d20_a42_boundary_zero": d20.get("a42_residue_boundary_zero"),
                    "d20_graph_valid": d20.get("graph_valid"),
                    "discharged": bool(ok),
                }
            )
            if ok and term.get("claim_id"):
                computed_residue_claims.add(str(term.get("claim_id")))
        for term in residue_class.get("invalid_terms", []):
            residues.append(
                {
                    "id": f"res_{len(residues) + 1:03d}",
                    "kind": "invalid_product_term",
                    "description": f"Invalid public A985 product term: {term.get('syntax')}.",
                    "severity": "high",
                    "term_id": term.get("term_id"),
                    "claim_id": term.get("claim_id"),
                    "discharged": False,
                }
            )
    elif residue_class.get("kind") == "not_computed":
        residues.append(
            {
                "id": f"res_{len(residues) + 1:03d}",
                "kind": "residue_representatives_not_computed",
                "description": "Tensor and quotient summaries were loaded, but claim-level residue representatives were not computed.",
                "severity": "medium",
                "discharged": False,
            }
        )

    if mode == "tensor_backed" and lowered_d20.get("mode") == "tensor_backed":
        missing_residue_witness = [
            claim.get("claim_id")
            for claim in claims
            if claim.get("requires_residue_coordinate") is True and str(claim.get("claim_id")) not in computed_residue_claims
        ]
        if missing_residue_witness:
            residues.append(
                {
                    "id": f"res_{len(residues) + 1:03d}",
                    "kind": "claim_residue_coordinate_missing",
                    "description": "One or more residue/A42/D20 claims have no valid computed public support coordinate.",
                    "severity": "high",
                    "claim_ids": missing_residue_witness,
                    "discharged": False,
                }
            )

    unsupported = [claim.get("claim_id") for claim in claims if not claim.get("support")]
    if unsupported:
        residues.append(
            {
                "id": f"res_{len(residues) + 1:03d}",
                "kind": "unsupported_claims",
                "description": "One or more public claims have no support files.",
                "severity": "high",
                "claim_ids": unsupported,
                "discharged": False,
            }
        )

    risky = [claim.get("claim_id") for claim in claims if claim.get("risk") != "low"]
    if risky:
        residues.append(
            {
                "id": f"res_{len(residues) + 1:03d}",
                "kind": "claim_risk_marked",
                "description": "Speculative or provisional wording is explicitly marked in the claim ledger.",
                "severity": "low",
                "claim_ids": risky,
                "discharged": True,
            }
        )

    return {"schema": RESIDUE_SCHEMA, "residues": residues}


def residue_status(residue_ledger: dict[str, Any]) -> str:
    residues = residue_ledger.get("residues", [])
    if not residues:
        return "PASS"
    high = any(item.get("severity") == "high" and item.get("discharged") is not True for item in residues)
    if high:
        return "BLOCKED_WITH_RESIDUE"
    return "PASS_WITH_RESIDUE"
