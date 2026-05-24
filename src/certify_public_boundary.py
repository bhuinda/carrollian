from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


def validate_public_boundary_graph_invariants() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/public_boundary_graph_invariants/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("public_boundary_graph_invariants")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 public-boundary graph certificate")

    if rec.get("status") != "D20_PUBLIC_BOUNDARY_GRAPH_INVARIANTS_CERTIFIED":
        raise AssertionError("public-boundary graph status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("public-boundary graph checks did not pass")

    derived = rec.get("derived", {})
    graph = derived.get("public_graph", {})
    if int(graph.get("vertices")) != 20 or int(graph.get("edges")) != 30:
        raise AssertionError("public-boundary graph size mismatch")
    if graph.get("degree_histogram") != {"3": 20}:
        raise AssertionError("public-boundary graph degree histogram mismatch")
    if graph.get("connected") is not True or int(graph.get("diameter")) != 5:
        raise AssertionError("public-boundary graph connectivity/diameter mismatch")
    if graph.get("dodecahedral_isomorphism_found") is not True:
        raise AssertionError("public-boundary dodecahedral check mismatch")

    cycle = derived.get("cycle_space", {})
    if int(cycle.get("cycle_rank")) != 11:
        raise AssertionError("public-boundary cycle rank mismatch")

    automorphisms = derived.get("automorphisms", {})
    if int(automorphisms.get("aut_gamma_order")) != 120:
        raise AssertionError("public-boundary automorphism order mismatch")

    sandpile = derived.get("sandpile", {})
    if sandpile.get("invariant_factors") != [2, 12, 60, 60, 60]:
        raise AssertionError("public-boundary sandpile factors mismatch")
    if int(sandpile.get("spanning_tree_count")) != 5_184_000:
        raise AssertionError("public-boundary spanning-tree count mismatch")

    dynamics = derived.get("symbolic_dynamics", {})
    if int(dynamics.get("legal_public_history_branching_base")) != 3:
        raise AssertionError("public-boundary shift entropy base mismatch")
    if int(dynamics.get("nonbacktracking_branching_base")) != 2:
        raise AssertionError("public-boundary nonbacktracking entropy base mismatch")

    fourier = derived.get("fourier_screen", {})
    if int(fourier.get("best_nontrivial_defect_count")) != 2:
        raise AssertionError("public-boundary Fourier screen defect count mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("public-boundary graph self hash mismatch")
    return rec
