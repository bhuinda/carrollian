from __future__ import annotations

from pathlib import Path
from typing import Any

from .algebra_residue import compute_q12_section_residues
from .common import ROOT, read_json, repo_rel, sha256_file


LOWERING_SCHEMA = "holotopy.lowered_d20"


def _symbolic_lowering(mode: str, reason: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": LOWERING_SCHEMA,
        "mode": mode,
        "support_algebra": "A985",
        "quotient_path": ["A985", "A42", "A12"],
        "boundary": "D20",
        "boundary_model": "Lambda^3 H6",
        "h6_channel_count": 6,
        "d20_state_count": 20,
        "product_terms": [],
        "readout": {"kind": "symbolic"},
        "residue_class": {"kind": "symbolic"},
    }
    if reason:
        payload["reason"] = reason
    return payload


def lower_scene_ir(scene_ir: dict[str, Any], *, mode: str = "scaffold", root: Path = ROOT) -> dict[str, Any]:
    product_terms = scene_ir.get("support", {}).get("product_terms", [])
    if mode != "tensor_backed":
        payload = _symbolic_lowering("scaffold")
        payload["product_terms"] = product_terms
        return payload

    try:
        import numpy as np

        from src.certify_io import raw_tensor_relpath

        tensor_rel = raw_tensor_relpath()
        tensor_path = root / tensor_rel
        quotient_path = root / "data/raw/quotients.npz"
        constants = read_json(root / "data/raw/constants.json")
        z = np.load(tensor_path, allow_pickle=False)
        q = np.load(quotient_path, allow_pickle=False)
        triples = z["triples"]
        q42 = q["q42_map"]
        q12 = q["q12_map"]
        residue_class = (
            compute_q12_section_residues(product_terms, root=root)
            if product_terms
            else {"kind": "not_computed", "reason": "no public A985 product terms were supplied"}
        )
        return {
            "schema": LOWERING_SCHEMA,
            "mode": "tensor_backed",
            "support_algebra": "A985",
            "quotient_path": ["A985", "A42", "A12"],
            "boundary": "D20",
            "boundary_model": "Lambda^3 H6",
            "h6_channel_count": 6,
            "d20_state_count": 20,
            "product_terms": product_terms,
            "readout": {
                "kind": "tensor_summary",
                "product_term_count": len(product_terms),
                "tensor": {
                    "path": repo_rel(tensor_path, root=root),
                    "sha256": sha256_file(tensor_path),
                    "triples_shape": list(triples.shape),
                    "nonzero_structure_constants": int(triples.shape[0]),
                    "coefficient_total": int(triples[:, 3].sum()),
                },
                "quotients": {
                    "path": repo_rel(quotient_path, root=root),
                    "sha256": sha256_file(quotient_path),
                    "q42_shape": list(q42.shape),
                    "q12_shape": list(q12.shape),
                    "q42_classes": int(len(set(int(x) for x in q42.tolist()))),
                    "q12_classes": int(len(set(int(x) for x in q12.tolist()))),
                },
                "constants": {
                    "orbitals": constants.get("be3", {}).get("orbitals"),
                    "center_dim": constants.get("wedderburn", {}).get("center_dim"),
                    "tensor_shape": constants.get("tensor_shape"),
                },
            },
            "residue_class": residue_class,
        }
    except Exception as exc:
        return _symbolic_lowering("scaffold", f"tensor_backed lowering unavailable: {type(exc).__name__}: {exc}")
