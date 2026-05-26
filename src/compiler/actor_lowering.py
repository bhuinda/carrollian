from __future__ import annotations

from typing import Any


ACTOR_TRACE_SCHEMA = "holotopy.actor_trace"


def build_actor_trace(*, mode: str, claims: list[dict[str, Any]], residues: list[dict[str, Any]]) -> dict[str, Any]:
    actors = [
        {
            "actor_id": "obligation_extractor",
            "role_shadow": "maps visible request constraints to public obligations",
            "geon_condition": {"public_boundary_zero": False, "residue_nonzero": False},
        },
        {
            "actor_id": "claim_extractor",
            "role_shadow": "maps public answer text to public claim rows",
            "geon_condition": {"public_boundary_zero": False, "residue_nonzero": any(c.get("risk") != "low" for c in claims)},
        },
        {
            "actor_id": "support_resolver",
            "role_shadow": "maps claims to visible files and request support",
            "geon_condition": {"public_boundary_zero": False, "residue_nonzero": False},
        },
        {
            "actor_id": "residue_checker",
            "role_shadow": "records missing evidence, symbolic lowering, and uncertainty",
            "geon_condition": {"public_boundary_zero": False, "residue_nonzero": bool(residues)},
        },
    ]
    if mode == "tensor_backed":
        actors.append(
            {
                "actor_id": "d20_lowering",
                "role_shadow": "loads tensor and quotient summaries for public readout",
                "geon_condition": {"public_boundary_zero": False, "residue_nonzero": False},
            }
        )
    return {"schema": ACTOR_TRACE_SCHEMA, "actors": actors}
