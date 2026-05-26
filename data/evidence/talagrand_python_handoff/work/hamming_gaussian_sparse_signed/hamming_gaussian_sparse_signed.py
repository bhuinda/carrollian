#!/usr/bin/env python3
"""
Hamming-Gaussian sparse signed convex-order probe audit.

This script extends the Hamming-Gaussian morphism audits from unsigned
four-coordinate projections to all signed sparse linear projections

    L_{S,eps} = sum_{j in S} eps_j Y_j,

where Y_j=(-1)^{c_j}, c is uniform in a stage code C <= F_2^24, eps_j in {+-1},
and |S| <= K_MAX.  For each distribution of L_{S,eps}, it checks the one-dimensional
convex-order call probes against N(0, |S|):

    E[(L-t)_+] <= E[(G-t)_+] for all t.

It records exact distribution-type counts, maximum unit-scale call defect, and the
critical contraction scale required for call domination by the matching Gaussian.

Scope: exact exhaustive signed probes up to K_MAX=5 by default. This is a finite
sparse-probe certificate, not a full multivariate convex-order theorem.
"""
from __future__ import annotations
from itertools import product, combinations
from math import exp, sqrt, pi, isfinite, comb
from statistics import NormalDist
from collections import Counter, defaultdict
from pathlib import Path
import argparse, csv, hashlib, json, zipfile

N = 24
ND = NormalDist()
DEFAULT_KMAX = 5
OUT = Path(__file__).resolve().parent

# ---------- code construction ----------

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def bits_to_int(bits):
    x = 0
    for i, b in enumerate(bits):
        if b:
            x |= 1 << i
    return x


def wt(x: int) -> int:
    return int(x).bit_count()


def rm13_h8() -> list[int]:
    pts = list(product([0, 1], repeat=3))
    C = []
    for a in product([0, 1], repeat=3):
        for b in [0, 1]:
            C.append(bits_to_int([(sum(ai * pi for ai, pi in zip(a, p)) + b) % 2 for p in pts]))
    return sorted(set(C))


def direct_sum(codes: list[list[int]], lengths: list[int]) -> list[int]:
    res = [0]
    shift = 0
    for C, L in zip(codes, lengths):
        res = [r | (c << shift) for r in res for c in C]
        shift += L
    return sorted(set(res))


def vector_from_one_based_support(support: list[int]) -> int:
    x = 0
    for j in support:
        x |= 1 << (j - 1)
    return x


def type_ii_neighbor(C: list[int], x: int) -> list[int]:
    C0 = [c for c in C if wt(c & x) % 2 == 0]
    return sorted(set(C0 + [c ^ x for c in C0]))


def gf2_rank(rows: list[int], n: int) -> int:
    rows = rows[:]
    rank = 0
    for col in range(n - 1, -1, -1):
        pivot = None
        for r in range(rank, len(rows)):
            if (rows[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for r in range(len(rows)):
            if r != rank and ((rows[r] >> col) & 1):
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def basis_from_code(C: list[int], n: int) -> list[int]:
    basis = []
    rank = 0
    for c in sorted(C):
        if c == 0:
            continue
        r = gf2_rank(basis + [c], n)
        if r > rank:
            basis.append(c)
            rank = r
        if rank == 12:
            break
    return basis


def self_orthogonal(C: list[int]) -> bool:
    B = basis_from_code(C, N)
    return all(wt(a & b) % 2 == 0 for a in B for b in B)


def weight_hist(C: list[int]) -> dict[int, int]:
    h = Counter(wt(c) for c in C)
    return dict(sorted(h.items()))


def codeword_sha(C: list[int]) -> str:
    return sha256_bytes("\n".join(f"{c:06x}" for c in sorted(C)).encode())


def build_chain() -> list[tuple[str, list[int], list[int] | None]]:
    # Same canonical neighbor supports used in prior Hamming-Gaussian packages.
    neighbor_supports = [
        [2, 4, 9, 10, 12, 13, 14, 16, 17, 18, 20, 22],
        [3, 4, 9, 13, 15, 16, 19, 20],
        [2, 5, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23],
    ]
    H8 = rm13_h8()
    C = direct_sum([H8, H8, H8], [8, 8, 8])
    stages = [("C0_H8_oplus_3", C, None)]
    for idx, supp in enumerate(neighbor_supports, start=1):
        C = type_ii_neighbor(C, vector_from_one_based_support(supp))
        label = "C3_Golay_endpoint" if idx == 3 else f"C{idx}_neighbor_{idx}"
        stages.append((label, C, supp))
    return stages

# ---------- projection and distribution ----------

def restrict_word_to_support(word: int, support: tuple[int, ...]) -> int:
    """Return k-bit projection in support order. support uses zero-based coordinates."""
    x = 0
    for j, coord in enumerate(support):
        if (word >> coord) & 1:
            x |= 1 << j
    return x


def projected_subspace_key(code_basis: list[int], support: tuple[int, ...]) -> tuple[int, ...]:
    rows = [restrict_word_to_support(b, support) for b in code_basis]
    # reduce basis in k-bit space and enumerate the span as canonical key
    k = len(support)
    # row echelon basis
    basis = []
    rank = 0
    for r in rows:
        if r == 0:
            continue
        if gf2_rank(basis + [r], k) > rank:
            basis.append(r)
            rank += 1
    span = {0}
    for b in basis:
        span |= {x ^ b for x in list(span)}
    return tuple(sorted(span))


def signed_distribution_from_subspace(subspace: tuple[int, ...], k: int, sign_mask: int) -> tuple[tuple[int, int], ...]:
    """Distribution key as ((value,count),...), uniform denominator len(subspace)."""
    cnt = Counter()
    for u in subspace:
        s = 0
        for j in range(k):
            eps = -1 if ((sign_mask >> j) & 1) else 1
            y = -1 if ((u >> j) & 1) else 1
            s += eps * y
        cnt[s] += 1
    return tuple(sorted(cnt.items()))


def dist_key_to_prob(dist_key: tuple[tuple[int, int], ...]) -> dict[float, float]:
    den = sum(c for _, c in dist_key)
    return {float(v): c / den for v, c in dist_key}

# ---------- call-order probe ----------

def call_gaussian(t: float, sigma: float) -> float:
    z = t / sigma
    phi = exp(-0.5 * z * z) / sqrt(2 * pi)
    tail = 1 - ND.cdf(z)
    return sigma * phi - t * tail


def call_discrete(dist: dict[float, float], t: float, scale: float = 1.0) -> float:
    return sum(p * max(scale * x - t, 0.0) for x, p in dist.items())


def candidate_thresholds_for_call_extrema(dist: dict[float, float], sigma: float, scale: float = 1.0) -> list[float]:
    atoms = sorted(scale * x for x in dist)
    probs = {scale * x: p for x, p in dist.items()}
    pts = []
    intervals = [(-float("inf"), atoms[0])] + [(atoms[i], atoms[i + 1]) for i in range(len(atoms) - 1)] + [(atoms[-1], float("inf"))]
    for a, b in intervals:
        mid = ((a + b) / 2.0 if isfinite(a) and isfinite(b) else (b - 1.0 if not isfinite(a) else a + 1.0))
        pgt = sum(p for x, p in probs.items() if x > mid)
        if 0.0 < pgt < 1.0:
            t = sigma * ND.inv_cdf(1 - pgt)
            if t > a and t < b:
                pts.append(t)
    eps = 1e-10
    pts.extend(atoms)
    for a in atoms:
        pts.append(a - eps)
        pts.append(a + eps)
    pts.append(0.0)
    # De-duplicate at stable precision.
    return sorted(set(round(p, 15) for p in pts))


def max_call_defect(dist: dict[float, float], sigma: float, scale: float = 1.0) -> dict:
    pts = candidate_thresholds_for_call_extrema(dist, sigma=sigma, scale=scale)
    best_val = -10**9
    best_t = None
    for t in pts:
        d = call_discrete(dist, t, scale) - call_gaussian(t, sigma=sigma)
        if d > best_val:
            best_val = d
            best_t = t
    return {"max_defect": best_val, "argmax_threshold": best_t, "candidate_count": len(pts)}


def critical_scale(dist: dict[float, float], sigma: float, tol: float = 1e-12) -> dict:
    lo, hi = 0.0, 1.0
    hi_def = max_call_defect(dist, sigma=sigma, scale=hi)
    if hi_def["max_defect"] <= tol:
        return {"critical_scale": hi, "defect_at_scale": hi_def}
    for _ in range(80):
        mid = (lo + hi) / 2.0
        d = max_call_defect(dist, sigma=sigma, scale=mid)["max_defect"]
        if d <= tol:
            lo = mid
        else:
            hi = mid
    return {
        "critical_scale": lo,
        "defect_at_scale": max_call_defect(dist, sigma=sigma, scale=lo),
        "first_bad_scale": hi,
        "defect_at_first_bad_scale": max_call_defect(dist, sigma=sigma, scale=hi),
    }


def distribution_stats(dist_key: tuple[tuple[int, int], ...], k: int) -> dict:
    dist = dist_key_to_prob(dist_key)
    sigma = sqrt(k)
    def moment(m: int) -> float:
        return sum(p * (x**m) for x, p in dist.items())
    unit = max_call_defect(dist, sigma=sigma, scale=1.0)
    crit = critical_scale(dist, sigma=sigma)
    return {
        "dist_key": ";".join(f"{v}:{c}" for v, c in dist_key),
        "support_values": [v for v, _ in dist_key],
        "denominator": sum(c for _, c in dist_key),
        "mean": moment(1),
        "variance": moment(2),
        "fourth_moment": moment(4),
        "sixth_moment": moment(6),
        "max_call_defect_unit_scale": unit["max_defect"],
        "argmax_threshold_unit_scale": unit["argmax_threshold"],
        "critical_scale": crit["critical_scale"],
        "critical_scale_detail": crit,
    }


def stage_sparse_signed_profiles(label: str, C: list[int], kmax: int) -> dict:
    B = basis_from_code(C, N)
    subspace_cache: dict[tuple[int, ...], list[tuple[tuple[int, int], int]]] = {}
    # subspace key -> list[(dist_key, sign_multiplicity among sign masks)]
    per_k_dist_counts = {k: Counter() for k in range(1, kmax + 1)}
    per_k_subspace_counts = {k: Counter() for k in range(1, kmax + 1)}

    for k in range(1, kmax + 1):
        for support in combinations(range(N), k):
            skey = projected_subspace_key(B, support)
            per_k_subspace_counts[k][skey] += 1
            if skey not in subspace_cache:
                dc = Counter()
                for sm in range(1 << k):
                    dc[signed_distribution_from_subspace(skey, k, sm)] += 1
                subspace_cache[skey] = list(dc.items())
            for dkey, sign_mult in subspace_cache[skey]:
                per_k_dist_counts[k][dkey] += sign_mult

    k_summaries = []
    dist_rows = []
    for k in range(1, kmax + 1):
        dist_counts = per_k_dist_counts[k]
        stats_cache = {dkey: distribution_stats(dkey, k) for dkey in dist_counts}
        total_signed = sum(dist_counts.values())
        assert total_signed == comb(N, k) * (1 << k)
        max_def = max(stats_cache[d]["max_call_defect_unit_scale"] for d in dist_counts)
        min_scale = min(stats_cache[d]["critical_scale"] for d in dist_counts)
        # multiplicity attaining extrema (within numerical tolerance)
        max_count = sum(count for d, count in dist_counts.items() if abs(stats_cache[d]["max_call_defect_unit_scale"] - max_def) < 1e-12)
        min_scale_count = sum(count for d, count in dist_counts.items() if abs(stats_cache[d]["critical_scale"] - min_scale) < 1e-12)
        # most frequent distribution
        most_d, most_count = dist_counts.most_common(1)[0]
        # histogram of projection ranks/dimensions
        rank_hist = Counter()
        for skey, count in per_k_subspace_counts[k].items():
            rank_hist[int(round((len(skey)).bit_length() - 1))] += count
        k_summaries.append({
            "stage": label,
            "k": k,
            "signed_projection_count": total_signed,
            "support_count": comb(N,k),
            "distinct_projection_subspaces": len(per_k_subspace_counts[k]),
            "distinct_distributions": len(dist_counts),
            "projection_rank_histogram": {str(r): c for r, c in sorted(rank_hist.items())},
            "max_unit_call_defect": max_def,
            "count_attaining_max_unit_call_defect": max_count,
            "minimum_critical_scale": min_scale,
            "count_attaining_minimum_critical_scale": min_scale_count,
            "most_frequent_distribution": ";".join(f"{v}:{c}" for v,c in most_d),
            "most_frequent_distribution_count": most_count,
        })
        for dkey, count in sorted(dist_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            st = stats_cache[dkey]
            dist_rows.append({
                "stage": label,
                "k": k,
                "distribution": st["dist_key"],
                "signed_projection_count": count,
                "mean": st["mean"],
                "variance": st["variance"],
                "fourth_moment": st["fourth_moment"],
                "sixth_moment": st["sixth_moment"],
                "max_unit_call_defect": st["max_call_defect_unit_scale"],
                "argmax_threshold": st["argmax_threshold_unit_scale"],
                "critical_scale": st["critical_scale"],
            })
    return {
        "stage": label,
        "k_summaries": k_summaries,
        "distribution_rows": dist_rows,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kmax", type=int, default=DEFAULT_KMAX)
    args = ap.parse_args()
    kmax = args.kmax
    if kmax < 1 or kmax > 7:
        raise SystemExit("kmax must be between 1 and 7 for this exact sparse audit")

    stages = build_chain()
    stage_invariants = []
    all_summary_rows = []
    all_dist_rows = []
    for label, C, supp in stages:
        h = weight_hist(C)
        stage_invariants.append({
            "label": label,
            "neighbor_support_one_based": supp,
            "code_sha256": codeword_sha(C),
            "size": len(C),
            "dimension": gf2_rank(C, N),
            "self_dual": gf2_rank(C, N) == 12 and self_orthogonal(C),
            "doubly_even": all(wt(c) % 4 == 0 for c in C),
            "weight_histogram": {str(k): v for k, v in h.items()},
            "wt4_roots": h.get(4, 0),
            "min_weight_nonzero": min(k for k, v in h.items() if k > 0 and v > 0),
        })
        prof = stage_sparse_signed_profiles(label, C, kmax)
        all_summary_rows.extend(prof["k_summaries"])
        all_dist_rows.extend(prof["distribution_rows"])

    # endpoint improvement and excess over endpoint by k
    endpoint_by_k = {row["k"]: row for row in all_summary_rows if row["stage"] == "C3_Golay_endpoint"}
    enriched_summary = []
    for row in all_summary_rows:
        r = dict(row)
        end = endpoint_by_k[row["k"]]
        r["unit_call_defect_excess_over_endpoint_max"] = max(0.0, row["max_unit_call_defect"] - end["max_unit_call_defect"])
        r["critical_scale_loss_vs_endpoint"] = max(0.0, end["minimum_critical_scale"] - row["minimum_critical_scale"])
        enriched_summary.append(r)

    # Global pass criteria.
    endpoint = [r for r in enriched_summary if r["stage"] == "C3_Golay_endpoint"]
    before = [r for r in enriched_summary if r["stage"] != "C3_Golay_endpoint"]
    # For k<=3, all stages should be identical baseline; for k=4, root obstruction removed at endpoint.
    k4_endpoint = next(r for r in endpoint if r["k"] == 4)
    k4_start = next(r for r in enriched_summary if r["stage"] == "C0_H8_oplus_3" and r["k"] == 4)
    pass_checks = {
        "all_stage_codes_type_ii_self_dual": all(s["self_dual"] and s["doubly_even"] for s in stage_invariants),
        "root_chain_42_18_6_0": [s["wt4_roots"] for s in stage_invariants] == [42, 18, 6, 0],
        "exact_signed_sparse_audit_kmax": kmax,
        "signed_projection_count_formula_ok": all(r["signed_projection_count"] == comb(N, r["k"]) * (1 << r["k"]) for r in enriched_summary),
        "k4_endpoint_improves_critical_scale": k4_endpoint["minimum_critical_scale"] > k4_start["minimum_critical_scale"],
        "k4_endpoint_reduces_max_defect": k4_endpoint["max_unit_call_defect"] < k4_start["max_unit_call_defect"],
    }
    status = "HAMMING_GAUSSIAN_SPARSE_SIGNED_PROBE_PASS" if all(pass_checks.values()) else "HAMMING_GAUSSIAN_SPARSE_SIGNED_PROBE_FAIL"

    # Write artifacts.
    write_csv(OUT / "sparse_signed_stage_summary.csv", enriched_summary)
    write_csv(OUT / "sparse_signed_distribution_profiles.csv", all_dist_rows)
    write_csv(OUT / "stage_code_invariants.csv", stage_invariants)

    certificate = {
        "status": status,
        "scope": f"Exact exhaustive signed {-1,0,1} sparse one-dimensional call-order probes for supports 1..{kmax} over the four Hamming/Golay stages.",
        "boundary": "This is a sparse one-dimensional convex-order probe certificate. It does not prove full multivariate convex order or all dense sign-linear projections.",
        "pass_checks": pass_checks,
        "stage_invariants": stage_invariants,
        "stage_summary": enriched_summary,
    }
    cert_json = json.dumps(certificate, indent=2, sort_keys=True)
    (OUT / "hamming_gaussian_sparse_signed_certificate.json").write_text(cert_json)

    # Markdown report.
    def fmt(x):
        return f"{x:.12f}" if isinstance(x, float) else str(x)
    lines = []
    lines.append("# Hamming Gaussian sparse signed call-order probe audit")
    lines.append("")
    lines.append(f"Status: `{status}`")
    lines.append("")
    lines.append("## Main result")
    lines.append("")
    lines.append(f"Exhaustively tested all signed sparse linear projections `L=sum eps_i Y_i` with support size `1 <= k <= {kmax}` for each stage of the chain `H8^3 -> neighbor1 -> neighbor2 -> Golay`.")
    lines.append("")
    lines.append("For each projection distribution, the audit computed the full one-dimensional call-order defect against the matching Gaussian `N(0,k)` and the critical contraction scale needed for call domination.")
    lines.append("")
    lines.append("## Stage code invariants")
    lines.append("")
    lines.append("| stage | wt4 roots | min wt | Type II/self dual | code SHA256 prefix |")
    lines.append("|---|---:|---:|---:|---|")
    for s in stage_invariants:
        lines.append(f"| {s['label']} | {s['wt4_roots']} | {s['min_weight_nonzero']} | {s['self_dual'] and s['doubly_even']} | `{s['code_sha256'][:16]}` |")
    lines.append("")
    lines.append("## Sparse signed profile")
    lines.append("")
    lines.append("| stage | k | signed probes | distinct distributions | max unit call defect | min critical scale | excess over Golay max | scale loss vs Golay |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in enriched_summary:
        lines.append(f"| {r['stage']} | {r['k']} | {r['signed_projection_count']} | {r['distinct_distributions']} | {r['max_unit_call_defect']:.12f} | {r['minimum_critical_scale']:.12f} | {r['unit_call_defect_excess_over_endpoint_max']:.12f} | {r['critical_scale_loss_vs_endpoint']:.12f} |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("The previous four-coordinate unsigned probe was only one slice. This audit includes all signed sparse projections up to the selected sparsity bound. The endpoint Golay code removes the special weight-four root obstruction, but the exact signed profile shows how much universal Rademacher baseline defect remains at each sparsity.")
    lines.append("")
    lines.append("The decisive invariant remains the support-4 transition: the root chain `42 -> 18 -> 6 -> 0` is visible as a loss of the extra signed call-order obstruction and an improvement of the worst critical contraction scale at k=4.")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("This certificate is exact for sparse signed one-dimensional probes through kmax. It is not a proof of Talagrand's full convex-order theorem, and it does not cover arbitrary dense real coefficient vectors. The next target is to pass from finite sparse signed probes to a support-enumerator / dual-distance theorem that controls all coefficient vectors by symmetry and Krawtchouk/MacWilliams data.")
    (OUT / "hamming_gaussian_sparse_signed_report.md").write_text("\n".join(lines))

    manifest = {
        "status": status,
        "files": {},
    }
    for p in sorted(OUT.glob("*")):
        if p.is_file() and p.name != "manifest.json":
            manifest["files"][p.name] = sha256_bytes(p.read_bytes())
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))

    zip_path = OUT.parent / "hamming_gaussian_sparse_signed_package.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.glob("*")):
            if p.is_file():
                z.write(p, f"hamming_gaussian_sparse_signed/{p.name}")
    print(status)
    print(zip_path)

if __name__ == "__main__":
    main()
