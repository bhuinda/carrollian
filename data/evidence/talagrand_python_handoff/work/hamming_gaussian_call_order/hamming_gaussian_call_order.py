#!/usr/bin/env python3
"""
Hamming-Gaussian one-dimensional convex-order call-probe audit.

This script refines the fourth-moment Hamming-Gaussian bridge by checking the
full one-dimensional convex-order condition for the canonical four-coordinate
projections L_S = sum_{i in S} Y_i, |S|=4.

For each four-subset S, the distribution of L_S is determined by whether the
indicator 1_S is a codeword:
  root:    P(-4)=1/8, P(0)=6/8, P(4)=1/8
  nonroot: Binomial/Rademacher sum over four independent signs

Convex order against G_S ~ N(0,4) in one dimension is equivalent to call-option
inequalities E[(X-t)_+] <= E[(G_S-t)_+] for all thresholds t.

The audit computes exact candidate extrema of the call defect and critical
shrinking scales c such that c L_S is dominated by N(0,4) for this four-probe family.
"""
from __future__ import annotations
from itertools import product, combinations
from math import comb, exp, sqrt, pi, isfinite
from statistics import NormalDist
import json, hashlib, zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parent
N = 24
TOTAL_FOUR = comb(N, 4)
ND = NormalDist()
GAUSS_SIGMA = 2.0  # sum of 4 independent standard Gaussians has variance 4

ROOT_DIST = {-4.0: 1/8, 0.0: 6/8, 4.0: 1/8}
NONROOT_DIST = {-4.0: 1/16, -2.0: 4/16, 0.0: 6/16, 2.0: 4/16, 4.0: 1/16}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def bits_to_int(bits):
    x = 0
    for i,b in enumerate(bits):
        if b:
            x |= 1 << i
    return x


def wt(x: int) -> int:
    return int(x).bit_count()


def rm13_h8() -> list[int]:
    pts = list(product([0,1], repeat=3))
    C=[]
    for a in product([0,1], repeat=3):
        for b in [0,1]:
            C.append(bits_to_int([(sum(ai*pi for ai,pi in zip(a,p))+b)%2 for p in pts]))
    return sorted(set(C))


def direct_sum(codes: list[list[int]], lengths: list[int]) -> list[int]:
    res=[0]; shift=0
    for C,L in zip(codes,lengths):
        res=[r | (c<<shift) for r in res for c in C]
        shift += L
    return sorted(set(res))


def vector_from_one_based_support(support: list[int]) -> int:
    x=0
    for j in support:
        x |= 1 << (j-1)
    return x


def type_ii_neighbor(C: list[int], x: int) -> list[int]:
    C0=[c for c in C if wt(c & x)%2==0]
    return sorted(set(C0 + [c ^ x for c in C0]))


def weight_hist(C: list[int]) -> dict[int,int]:
    h={}
    for c in C:
        h[wt(c)] = h.get(wt(c),0)+1
    return dict(sorted(h.items()))


def gf2_rank(rows: list[int], n: int) -> int:
    rows=rows[:]
    rank=0
    for col in range(n-1,-1,-1):
        pivot=None
        for r in range(rank,len(rows)):
            if (rows[r]>>col)&1:
                pivot=r; break
        if pivot is None: continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        for r in range(len(rows)):
            if r!=rank and ((rows[r]>>col)&1):
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def basis_from_code(C: list[int], n: int) -> list[int]:
    basis=[]; rank=0
    for c in sorted(C):
        if c==0: continue
        r=gf2_rank(basis+[c], n)
        if r>rank:
            basis.append(c); rank=r
        if rank==12: break
    return basis


def self_orthogonal(C: list[int]) -> bool:
    B=basis_from_code(C,N)
    return all(wt(a&b)%2==0 for a in B for b in B)


def codeword_sha(C: list[int]) -> str:
    return sha256_bytes("\n".join(f"{c:06x}" for c in sorted(C)).encode())


def supports_one_based(v: int) -> str:
    return " ".join(str(i+1) for i in range(N) if (v>>i)&1)


def call_gaussian(t: float, sigma: float = GAUSS_SIGMA) -> float:
    z=t/sigma
    phi=exp(-0.5*z*z)/sqrt(2*pi)
    tail=1-ND.cdf(z)
    return sigma*phi - t*tail


def call_discrete(dist: dict[float,float], t: float, scale: float = 1.0) -> float:
    return sum(p*max(scale*x-t, 0.0) for x,p in dist.items())


def candidate_thresholds_for_call_extrema(dist: dict[float,float], scale: float = 1.0) -> list[float]:
    atoms=sorted(scale*x for x in dist)
    probs={scale*x:p for x,p in dist.items()}
    pts=[]
    intervals=[(-float('inf'), atoms[0])] + [(atoms[i], atoms[i+1]) for i in range(len(atoms)-1)] + [(atoms[-1], float('inf'))]
    for a,b in intervals:
        mid = ((a+b)/2.0 if isfinite(a) and isfinite(b) else (b-1.0 if not isfinite(a) else a+1.0))
        pgt=sum(p for x,p in probs.items() if x>mid)
        if 0.0 < pgt < 1.0:
            t=GAUSS_SIGMA * ND.inv_cdf(1-pgt)
            if t>a and t<b:
                pts.append(t)
    # include atoms and one-sided representatives for nondifferentiable places
    eps=1e-10
    pts.extend(atoms)
    for a in atoms:
        pts.append(a-eps)
        pts.append(a+eps)
    pts.append(0.0)
    # deterministic unique-ish
    return sorted(set(round(p, 15) for p in pts))


def max_call_defect(dist: dict[float,float], scale: float = 1.0) -> dict:
    pts=candidate_thresholds_for_call_extrema(dist, scale)
    best_val=-10**9; best_t=None
    for t in pts:
        d=call_discrete(dist, t, scale) - call_gaussian(t)
        if d>best_val:
            best_val=d; best_t=t
    return {"max_defect": best_val, "argmax_threshold": best_t, "candidate_count": len(pts)}


def critical_scale(dist: dict[float,float], tol: float = 1e-12) -> dict:
    lo, hi = 0.0, 1.0
    # lo good, hi may be bad; if hi not bad then hi is threshold.
    if max_call_defect(dist, hi)["max_defect"] <= tol:
        return {"critical_scale": hi, "defect_at_scale": max_call_defect(dist, hi)}
    for _ in range(80):
        mid=(lo+hi)/2
        d=max_call_defect(dist, mid)["max_defect"]
        if d <= tol:
            lo=mid
        else:
            hi=mid
    return {"critical_scale": lo, "defect_at_scale": max_call_defect(dist, lo), "first_bad_scale": hi, "defect_at_first_bad_scale": max_call_defect(dist, hi)}


def distribution_stats(dist: dict[float,float]) -> dict:
    def moment(k): return sum(p*(x**k) for x,p in dist.items())
    return {
        "support": {str(k):v for k,v in sorted(dist.items())},
        "mean": moment(1),
        "variance": moment(2),
        "fourth_moment": moment(4),
        "sixth_moment": moment(6),
        "eighth_moment": moment(8),
        "max_call_defect_unit_scale": max_call_defect(dist, 1.0),
        "critical_scale_for_call_domination_by_N_0_4": critical_scale(dist),
    }


def build_chain() -> list[tuple[str, list[int], list[int] | None]]:
    neighbor_supports = [
        [2,4,9,10,12,13,14,16,17,18,20,22],
        [3,4,9,13,15,16,19,20],
        [2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23],
    ]
    H8=rm13_h8()
    C=direct_sum([H8,H8,H8], [8,8,8])
    stages=[("C0_H8_oplus_3", C, None)]
    for idx,supp in enumerate(neighbor_supports, start=1):
        C=type_ii_neighbor(C, vector_from_one_based_support(supp))
        label="C3_Golay_endpoint" if idx==3 else f"C{idx}_neighbor_{idx}"
        stages.append((label, C, supp))
    return stages


def stage_record(label: str, C: list[int], root_stats: dict, nonroot_stats: dict, supp=None) -> dict:
    roots=sorted(c for c in C if wt(c)==4)
    r=len(roots)
    non=TOTAL_FOUR-r
    root_unit=root_stats["max_call_defect_unit_scale"]["max_defect"]
    non_unit=nonroot_stats["max_call_defect_unit_scale"]["max_defect"]
    root_threshold=root_stats["critical_scale_for_call_domination_by_N_0_4"]["critical_scale"]
    non_threshold=nonroot_stats["critical_scale_for_call_domination_by_N_0_4"]["critical_scale"]
    max_family_defect = root_unit if r>0 else non_unit
    critical_family_scale = root_threshold if r>0 else non_threshold
    return {
        "label": label,
        "neighbor_support_one_based": supp,
        "code_sha256": codeword_sha(C),
        "size": len(C),
        "dimension": gf2_rank(C,N),
        "self_dual": gf2_rank(C,N)==12 and self_orthogonal(C),
        "doubly_even": all(wt(c)%4==0 for c in C),
        "weight_histogram": {str(k):v for k,v in weight_hist(C).items()},
        "four_subset_count": TOTAL_FOUR,
        "root_count_weight4": r,
        "nonroot_four_subset_count": non,
        "max_call_defect_over_four_coordinate_probes_unit_scale": max_family_defect,
        "critical_scale_for_all_four_coordinate_call_probes": critical_family_scale,
        "root_specific_extra_call_defect_per_root": root_unit - non_unit,
        "root_specific_extra_call_defect_total": r * (root_unit - non_unit),
        "aggregate_call_defect_mass_unit_scale": r*root_unit + non*non_unit,
        "root_call_defect_mass_unit_scale": r*root_unit,
        "nonroot_call_defect_mass_unit_scale": non*non_unit,
        "first_12_roots_one_based": [supports_one_based(v) for v in roots[:12]],
    }


def write_outputs():
    root_stats = distribution_stats(ROOT_DIST)
    nonroot_stats = distribution_stats(NONROOT_DIST)
    stages=build_chain()
    records=[stage_record(label,C,root_stats,nonroot_stats,supp) for label,C,supp in stages]
    root_sequence=[r["root_count_weight4"] for r in records]
    extra_sequence=[r["root_specific_extra_call_defect_total"] for r in records]
    scale_sequence=[r["critical_scale_for_all_four_coordinate_call_probes"] for r in records]
    status="HAMMING_GAUSSIAN_CALL_ORDER_PROBE_PASS"
    if root_sequence != [42,18,6,0]: status="HAMMING_GAUSSIAN_CALL_ORDER_PROBE_FAIL"
    cert={
        "status": status,
        "scope": "Full one-dimensional convex-order call-option audit for all four-coordinate projections in the H8^3 -> Golay neighbor chain. It upgrades the quartic moment probe to exact 1D convex-order call functions for the root/nonroot four-channel marginal types. It does not prove full multivariate convex order.",
        "reference_gaussian": "N(0,4), i.e. sum of four independent standard Gaussians",
        "convex_order_criterion_1d": "X <=cx G iff E[(X-t)_+] <= E[(G-t)_+] for every real t, assuming equal means.",
        "root_distribution": root_stats,
        "nonroot_distribution": nonroot_stats,
        "interpretation": {
            "key_correction": "The Golay endpoint kills the root-specific quartic/Hermite obstruction, but unit-scale four-coordinate call convex order is still stricter: nonroot Rademacher four-sums also have a positive call defect relative to N(0,4).",
            "root_removal_effect": "The critical contraction scale for the four-coordinate call family improves from the root threshold to the nonroot threshold once the wt4 roots vanish.",
            "critical_scales": {
                "if_wt4_roots_present": root_stats["critical_scale_for_call_domination_by_N_0_4"]["critical_scale"],
                "if_no_wt4_roots": nonroot_stats["critical_scale_for_call_domination_by_N_0_4"]["critical_scale"],
            },
        },
        "root_sequence": root_sequence,
        "root_specific_extra_call_defect_sequence": extra_sequence,
        "critical_scale_sequence": scale_sequence,
        "records": records,
        "remaining_obligations": [
            "Extend from all four-coordinate one-dimensional projections to all sparse/sign-linear projections.",
            "Extend from one-dimensional call convex order to full multivariate convex order.",
            "Construct a martingale/Laguerre partition realizing the Hamming-Gaussian coupling after the necessary contraction scale.",
            "Relate the nonroot baseline call defect to Talagrand's universal contraction constant and separate it from the Hamming root-specific obstruction.",
        ],
    }
    (OUT/"hamming_gaussian_call_order_certificate.json").write_text(json.dumps(cert, indent=2, sort_keys=True))
    with (OUT/"call_order_stage_profile.csv").open("w") as f:
        f.write("stage,wt4_roots,critical_scale_four_call_family,max_unit_call_defect,root_extra_total,root_extra_per_root,aggregate_unit_call_defect,root_mass,nonroot_mass,self_dual,doubly_even\n")
        for r in records:
            f.write(f"{r['label']},{r['root_count_weight4']},{r['critical_scale_for_all_four_coordinate_call_probes']:.15f},{r['max_call_defect_over_four_coordinate_probes_unit_scale']:.15f},{r['root_specific_extra_call_defect_total']:.15f},{r['root_specific_extra_call_defect_per_root']:.15f},{r['aggregate_call_defect_mass_unit_scale']:.15f},{r['root_call_defect_mass_unit_scale']:.15f},{r['nonroot_call_defect_mass_unit_scale']:.15f},{r['self_dual']},{r['doubly_even']}\n")
    # Threshold profile files
    for name,dist,stats in [("root",ROOT_DIST,root_stats),("nonroot",NONROOT_DIST,nonroot_stats)]:
        with (OUT/f"{name}_call_defect_profile.csv").open("w") as f:
            f.write("threshold,call_discrete,call_gaussian,defect\n")
            pts=candidate_thresholds_for_call_extrema(dist,1.0)
            for t in pts:
                f.write(f"{t:.15f},{call_discrete(dist,t):.15f},{call_gaussian(t):.15f},{call_discrete(dist,t)-call_gaussian(t):.15f}\n")
    # Report
    md=[]
    md.append("# Hamming Gaussian call-order probe audit\n\n")
    md.append(f"Status: `{status}`\n\n")
    md.append("## Main result\n\n")
    md.append("The quartic obstruction has now been refined to the full one-dimensional convex-order call-function test for the canonical four-coordinate projections.\n\n")
    md.append("For each four-subset `S`, the marginal `L_S=sum_{i in S}Y_i` has one of two distributions:\n\n")
    md.append("- root type if `1_S in C`: `P(-4)=1/8, P(0)=6/8, P(4)=1/8`;\n")
    md.append("- nonroot type otherwise: four-independent-Rademacher sum.\n\n")
    md.append("Against the Gaussian reference `N(0,4)`, the maximum call defects at unit scale are:\n\n")
    md.append(f"- root type: `{root_stats['max_call_defect_unit_scale']['max_defect']:.15f}` at threshold `{root_stats['max_call_defect_unit_scale']['argmax_threshold']:.15f}`;\n")
    md.append(f"- nonroot type: `{nonroot_stats['max_call_defect_unit_scale']['max_defect']:.15f}` at threshold `{nonroot_stats['max_call_defect_unit_scale']['argmax_threshold']:.15f}`.\n\n")
    md.append("The critical contraction scales for domination by `N(0,4)` over this one-dimensional call family are:\n\n")
    md.append(f"- root type: `{root_stats['critical_scale_for_call_domination_by_N_0_4']['critical_scale']:.15f}`;\n")
    md.append(f"- nonroot type: `{nonroot_stats['critical_scale_for_call_domination_by_N_0_4']['critical_scale']:.15f}`.\n\n")
    md.append("## Stage profile\n\n")
    md.append("| stage | wt4 roots | critical scale for all 4-call probes | max unit call defect | root-specific extra defect |\n")
    md.append("|---|---:|---:|---:|---:|\n")
    for r in records:
        md.append(f"| {r['label']} | {r['root_count_weight4']} | {r['critical_scale_for_all_four_coordinate_call_probes']:.12f} | {r['max_call_defect_over_four_coordinate_probes_unit_scale']:.12f} | {r['root_specific_extra_call_defect_total']:.12f} |\n")
    md.append("\n## Interpretation\n\n")
    md.append("This is a correction and strengthening of the fourth-moment result. The Golay endpoint kills the root-specific fourth-order/Hermite obstruction, but full one-dimensional convex order is stricter than fourth moments: even a nonroot four-Rademacher marginal has a small positive call defect relative to the matching Gaussian at unit scale.\n\n")
    md.append("Thus root killing should be read as improving the necessary contraction scale from the root threshold to the nonroot threshold, not as proving full unit-scale convex order.\n\n")
    md.append("## Boundary\n\n")
    md.append("This audit proves exact one-dimensional call-order data for all four-coordinate probes by symmetry/type. It does not prove full multivariate convex order or the Talagrand theorem. It isolates the root-specific obstruction from the universal nonroot Rademacher baseline.\n")
    (OUT/"hamming_gaussian_call_order_report.md").write_text("".join(md))
    # manifest and zip
    files=["hamming_gaussian_call_order.py","hamming_gaussian_call_order_certificate.json","hamming_gaussian_call_order_report.md","call_order_stage_profile.csv","root_call_defect_profile.csv","nonroot_call_defect_profile.csv"]
    manifest={fn:sha256_bytes((OUT/fn).read_bytes()) for fn in files}
    (OUT/"manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    files.append("manifest.json")
    zpath=OUT.parent/"hamming_gaussian_call_order_package.zip"
    with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
        for fn in files:
            z.write(OUT/fn, arcname=f"hamming_gaussian_call_order/{fn}")
    print(json.dumps({"status": status, "root_sequence": root_sequence, "critical_scale_sequence": scale_sequence, "zip": str(zpath)}, indent=2))

if __name__ == "__main__":
    write_outputs()
