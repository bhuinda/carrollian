from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


def validate_sandpile_critical_group() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/sandpile_critical_group/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("sandpile_critical_group")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 sandpile critical-group certificate")

    if rec.get("status") != "D20_SANDPILE_CRITICAL_GROUP_CERTIFIED":
        raise AssertionError("sandpile critical-group status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("sandpile critical-group checks did not pass")

    graph = rec.get("derived", {}).get("graph", {})
    if int(graph.get("vertices")) != 20 or int(graph.get("edges")) != 30:
        raise AssertionError("sandpile graph size mismatch")
    if graph.get("degree_histogram") != {"3": 20}:
        raise AssertionError("sandpile graph degree histogram mismatch")
    if graph.get("connected") is not True:
        raise AssertionError("sandpile graph connectivity mismatch")

    snf = rec.get("derived", {}).get("smith_normal_form", {})
    if snf.get("diagonal_multiplicities") != {"1": 14, "2": 1, "12": 1, "60": 3}:
        raise AssertionError("sandpile SNF diagonal multiplicities mismatch")
    if snf.get("nonunit_invariant_factors") != [2, 12, 60, 60, 60]:
        raise AssertionError("sandpile critical-group invariant factors mismatch")
    if int(snf.get("rank")) != 19:
        raise AssertionError("sandpile reduced Laplacian rank mismatch")
    if int(snf.get("zero_invariant_factors_full_laplacian")) != 1:
        raise AssertionError("sandpile full Laplacian nullity mismatch")

    critical = rec.get("derived", {}).get("critical_group", {})
    if critical.get("presentation") != "Z/2 x Z/12 x Z/60^3":
        raise AssertionError("sandpile critical-group presentation mismatch")
    if int(critical.get("order")) != 5_184_000:
        raise AssertionError("sandpile critical-group order mismatch")
    if int(critical.get("spanning_tree_count")) != 5_184_000:
        raise AssertionError("sandpile spanning-tree count mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("sandpile critical-group self hash mismatch")
    return rec
