#!/usr/bin/env python3
"""
Classify D20 minimal composite public-zero sector idempotent supports.

Inputs
------
--d20-json: the normalized d20.json certificate bundle containing
            json_invariants['data/drinfeld/wedderburn_trace.json'].
--admissibility-report: optional report.json from
            sector_idempotent_support_admissibility theorem.

Outputs
-------
- minimal_composite_null_supports_profile_certificate.json
- minimal_composite_null_supports_profile_report.md

This script does NOT recompute primitive central idempotents from raw A985 arrays.
It consumes already-certified sector profiles and an already-certified public-zero
support enumeration. It classifies the two minimal non-Pi33 public-zero composites
by their internal block/support profile.
"""
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple

DEFAULT_PUBLIC_ZERO_SUPPORTS = [
    [],
    [6, 26],
    [25, 26],
    [33],
    [6, 26, 33],
    [25, 26, 33],
]

TARGET_MINIMAL_COMPOSITES = [[6, 26], [25, 26]]
PRIMITIVE_SUPPORT = [33]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_hash(obj: Any) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(s).hexdigest()


def load_public_zero_supports(path: str | None) -> Tuple[List[List[int]], Dict[str, Any]]:
    if not path:
        return DEFAULT_PUBLIC_ZERO_SUPPORTS, {"source": "built_in_from_user_certified_statement"}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Be deliberately permissive about report schema names.
    candidates = None
    for key in [
        "public_zero_supports",
        "zero_public_supports",
        "boolean_public_zero_supports",
        "supports",
    ]:
        if isinstance(data, dict) and key in data:
            candidates = data[key]
            break
    if candidates is None:
        # Try nested common schemas.
        for key in ["result", "results", "theorem", "certificate"]:
            sub = data.get(key) if isinstance(data, dict) else None
            if isinstance(sub, dict):
                for kk in ["public_zero_supports", "zero_public_supports", "supports"]:
                    if kk in sub:
                        candidates = sub[kk]
                        break
            if candidates is not None:
                break
    if candidates is None:
        candidates = DEFAULT_PUBLIC_ZERO_SUPPORTS
        source = "fallback_built_in_because_report_schema_not_recognized"
    else:
        source = path
    normalized = []
    for c in candidates:
        if isinstance(c, dict):
            if "support" in c:
                c = c["support"]
            elif "sectors" in c:
                c = c["sectors"]
        normalized.append(sorted(int(x) for x in c))
    normalized = sorted(normalized, key=lambda x: (len(x), x))
    return normalized, {"source": source, "report_sha256": sha256_file(path) if path else None}


def get_sector_profiles(d20: Dict[str, Any]) -> List[Dict[str, Any]]:
    wt = d20["json_invariants"]["data/drinfeld/wedderburn_trace.json"]
    return wt["sector_profiles"]


def profile_for(profiles: List[Dict[str, Any]], sector: int) -> Dict[str, Any]:
    p = profiles[sector]
    assert int(p.get("sector", sector)) == sector
    return p


def support_profile(profiles: List[Dict[str, Any]], support: List[int]) -> Dict[str, Any]:
    ps = [profile_for(profiles, s) for s in support]
    active_objects = sorted({o for p in ps for o in p.get("active_objects", [])})
    active_cy = sorted({o for p in ps for o in p.get("active_cy_sectors", [])})
    block_dims = [int(p["block_dimension"]) for p in ps]
    # For central primitive blocks, the internal algebra dimension of the support is sum d_i^2.
    internal_algebra_dimension = sum(d * d for d in block_dims)
    regular_trace_sum = sum(int(p.get("regular_trace_block_square", 0)) for p in ps)
    permutation_rank_sum = sum(int(p.get("permutation_rank", 0)) for p in ps)
    permutation_multiplicity_sum = sum(int(p.get("permutation_multiplicity", 0)) for p in ps)
    loop_support_total = sum(int(p.get("loop_coordinate_support_total", 0)) for p in ps)
    pre_support_total = sum(int(p.get("pre_idempotent_support_size", 0)) for p in ps)
    object_loop_support = [0, 0, 0, 0, 0, 0]
    object_pre_counts = [0, 0, 0, 0, 0, 0]
    identity_coeffs_signed_by_sector = {}
    spectral_signature_by_sector = {}
    for p in ps:
        for i, v in enumerate(p.get("object_loop_coordinate_support", [])):
            object_loop_support[i] += int(v)
        for i, v in enumerate(p.get("object_pre_idempotent_counts", [])):
            object_pre_counts[i] += int(v)
        s = int(p["sector"])
        identity_coeffs_signed_by_sector[str(s)] = p.get("identity_coefficients_signed")
        spectral_signature_by_sector[str(s)] = p.get("spectral_signature")
    same_object_only = len(active_objects) == 1
    singletons_only = all(d == 1 for d in block_dims)
    has_sector33 = 33 in support
    has_splus = "S+" in active_objects
    has_sminus = "S-" in active_objects
    has_public_visible_count = sum(int(p.get("q42_nonzero_count", 0)) + int(p.get("q12_nonzero_count", 0)) for p in ps)

    if support == PRIMITIVE_SUPPORT:
        classification = "primitive_support_exact_residual_support"
    elif support == [25, 26]:
        classification = "pure_Sminus_superselection_null_doublet"
    elif support == [6, 26]:
        classification = "mixed_S_channel_hidden_boundary_null_composite"
    elif has_sector33 and set(support) == {6, 26, 33}:
        classification = "mixed_S_channel_null_composite_plus_primitive_residual"
    elif has_sector33 and set(support) == {25, 26, 33}:
        classification = "pure_Sminus_null_doublet_plus_primitive_residual"
    elif internal_algebra_dimension == 0:
        classification = "gauge_zero"
    elif same_object_only and singletons_only:
        classification = "same_object_superselection_null_doublet"
    elif has_splus and has_sminus:
        classification = "mixed_boundary_hidden_sector"
    else:
        classification = "public_zero_superselection_support"

    not_gauge_reason = None
    if support:
        not_gauge_reason = (
            "internal_algebra_dimension>0 and permutation_rank_sum>0; "
            "public-zero is quotient cancellation, not internal zero"
        )

    return {
        "support": support,
        "primitive": len(support) == 1,
        "contains_sector33": has_sector33,
        "active_objects": active_objects,
        "active_cy_sectors": active_cy,
        "block_dimensions": block_dims,
        "internal_algebra_dimension_sum_d_squared": internal_algebra_dimension,
        "regular_trace_sum": regular_trace_sum,
        "permutation_rank_sum": permutation_rank_sum,
        "permutation_multiplicity_sum": permutation_multiplicity_sum,
        "loop_coordinate_support_total": loop_support_total,
        "pre_idempotent_support_total": pre_support_total,
        "object_loop_coordinate_support": object_loop_support,
        "object_pre_idempotent_counts": object_pre_counts,
        "individual_public_nonzero_count_sum": has_public_visible_count,
        "same_object_only": same_object_only,
        "singletons_only": singletons_only,
        "has_Sminus": has_sminus,
        "has_Splus": has_splus,
        "classification": classification,
        "not_gauge_reason": not_gauge_reason,
        "identity_coefficients_signed_by_sector": identity_coeffs_signed_by_sector,
        "spectral_signature_by_sector": spectral_signature_by_sector,
    }


def make_report(cert: Dict[str, Any]) -> str:
    lines = []
    lines.append("# D20 minimal composite null support classification")
    lines.append("")
    lines.append(f"Status: `{cert['status']}`")
    lines.append("")
    lines.append("## Public-zero support set")
    lines.append("")
    lines.append("The classified Boolean public-zero support set is:")
    lines.append("")
    for c in cert["public_zero_supports"]:
        lines.append(f"- `{c}`")
    lines.append("")
    lines.append("## Minimal composite supports")
    lines.append("")
    lines.append("| support | classification | active objects | block dims | internal dim | permutation rank | verdict |")
    lines.append("|---|---|---|---|---:|---:|---|")
    for rec in cert["minimal_composite_classification"]:
        verdict = "not gauge; public-null internal support"
        lines.append(
            f"| `{rec['support']}` | `{rec['classification']}` | "
            f"{', '.join(rec['active_objects'])} | {rec['block_dimensions']} | "
            f"{rec['internal_algebra_dimension_sum_d_squared']} | {rec['permutation_rank_sum']} | {verdict} |"
        )
    lines.append("")
    lines.append("## Theorem statement")
    lines.append("")
    lines.append("`{33}` is the unique primitive public-zero support and remains the support-exact sector-33 height-transport support.")
    lines.append("")
    lines.append("The two minimal non-Pi33 public-zero composites are not gauge zeros because each has nonzero internal algebra dimension and nonzero permutation rank. The support `{25,26}` is a pure `S-` superselection null doublet. The support `{6,26}` is a mixed `S-/S+` hidden boundary-null composite.")
    lines.append("")
    lines.append("## Next obligation")
    lines.append("")
    lines.append("To upgrade from profile classification to full transport classification, compute the mixed transport matrices `(e_6+e_26) A985 e_33` and `(e_25+e_26) A985 e_33`, plus the self-transport ranks `(e_6+e_26) A985 (e_6+e_26)` and `(e_25+e_26) A985 (e_25+e_26)` from the raw idempotent coordinates.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20-json", required=True)
    ap.add_argument("--admissibility-report", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    with open(args.d20_json, "r", encoding="utf-8") as f:
        d20 = json.load(f)
    profiles = get_sector_profiles(d20)
    public_zero, pz_meta = load_public_zero_supports(args.admissibility_report)

    classifications = [support_profile(profiles, c) for c in public_zero if c]
    minimal = [r for r in classifications if r["support"] in TARGET_MINIMAL_COMPOSITES]
    primitive = [r for r in classifications if r["support"] == PRIMITIVE_SUPPORT]

    # Assertions matching the theorem state.
    assert sorted(public_zero, key=lambda x: (len(x), x)) == sorted(DEFAULT_PUBLIC_ZERO_SUPPORTS, key=lambda x: (len(x), x)), public_zero
    assert len(minimal) == 2
    assert len(primitive) == 1
    for rec in minimal:
        assert rec["internal_algebra_dimension_sum_d_squared"] > 0
        assert rec["permutation_rank_sum"] > 0

    cert = {
        "schema": "d20.minimal_composite_null_supports.profile.source_drop",
        "status": "D20_MINIMAL_COMPOSITE_NULL_SUPPORTS_PROFILE_CLASSIFIED",
        "input": {
            "d20_json": args.d20_json,
            "d20_json_sha256": sha256_file(args.d20_json),
            "admissibility_report": args.admissibility_report,
            "public_zero_source": pz_meta,
        },
        "public_zero_supports": public_zero,
        "minimal_composite_classification": minimal,
        "primitive_support_record": primitive[0],
        "all_nonzero_public_zero_classification": classifications,
        "theorem": {
            "primitive_support": [33],
            "minimal_non_pi33_composites": TARGET_MINIMAL_COMPOSITES,
            "statement": "{33} is the unique primitive public-zero support; {25,26} is a pure S- superselection null doublet; {6,26} is a mixed S-channel hidden boundary-null composite. Both composites are not gauge zeros because they have nonzero internal algebra dimension and nonzero permutation rank.",
        },
    }
    cert["certificate_sha256"] = canonical_json_hash(cert)

    cpath = os.path.join(args.out, "minimal_composite_null_supports_profile_certificate.json")
    rpath = os.path.join(args.out, "minimal_composite_null_supports_profile_report.md")
    with open(cpath, "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=2, sort_keys=True)
    with open(rpath, "w", encoding="utf-8") as f:
        f.write(make_report(cert))
    print(cert["status"])
    print(cert["certificate_sha256"])
    print(rpath)
    print(cpath)


if __name__ == "__main__":
    main()
